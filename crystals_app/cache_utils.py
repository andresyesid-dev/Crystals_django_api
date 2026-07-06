"""
Cache Utilities (T4 — Caché en memoria por fábrica para endpoints estáticos)
============================================================================
Cachea las lecturas GET de datos casi estáticos (configuraciones,
parametrizaciones, calibraciones, orden de encabezados, brix) para evitar
golpear PostgreSQL/Supabase en cada petición. Diseñado para que el endpoint
compuesto (T1) se beneficie automáticamente en sus 20 sub-consultas estáticas.

Decisiones de diseño (acordadas en PLAN_OPTIMIZACION_ONLINE.md, Tarea 4):

1. AISLAMIENTO MULTI-TENANT EN LA CLAVE.
   La clave de caché SIEMPRE incluye el factory_id del header X-Factory-ID.
   Sin esto, una fábrica podría recibir datos de otra: es el riesgo #1 de toda
   la iniciativa. La caché vive en Django ANTES de la base de datos, así que
   el RLS de PostgreSQL no protege de esta fuga — la separación la garantiza
   exclusivamente esta clave.

2. TTL CORTO + INVALIDACIÓN EXPLÍCITA POR VERSIÓN DE GRUPO.
   El usuario edita estos datos (parametrizaciones, calibraciones) y la pantalla
   los re-lee de inmediato; un TTL de minutos haría que viera el valor viejo y
   parecería pérdida de datos. Por eso:
     - TTL corto por defecto (DEFAULT_TTL = 90 s) como red de seguridad.
     - Invalidación inmediata: cada escritura llama bump_cache_version(group,
       factory_id), que incrementa un contador de versión del grupo. La clave de
       lectura incluye esa versión, así que al subir la versión TODAS las
       lecturas cacheadas de ese grupo quedan obsoletas de un plumazo, sin
       enumerar clave por clave (a prueba de olvidos: una escritura nueva solo
       necesita bump del grupo, no conocer cada endpoint).

3. ROBUSTO ANTE LocMemCache POR PROCESO.
   El backend actual (LocMemCache) es por worker de Gunicorn: 3 workers = 3
   cachés. El esquema de versión hace que el worker que ESCRIBE incremente su
   propia versión y sirva datos frescos de inmediato; los otros workers como
   mucho sirven datos viejos hasta que expira el TTL corto. Si en el futuro
   Railway provee Redis, basta cambiar el backend en settings.CACHES: este
   código no cambia y la invalidación pasa a ser global e instantánea.

4. NUNCA CACHEAR ERRORES.
   Solo se cachean respuestas con status 200; un fallo transitorio de BD no debe
   quedar "pegado" en la caché.

Lo que NO se debe cachear con esto: endpoints con rango de fechas (historic_*,
lab-data/historic), lab-data/get (datos activos), auth, security, ni escrituras.
"""

import logging
from functools import wraps

from django.core.cache import cache

logger = logging.getLogger('crystals_app')

# TTL por defecto de las lecturas estáticas (segundos). Corto a propósito: es la
# red de seguridad; la consistencia real la da la invalidación por versión.
DEFAULT_TTL = 90

# TTL largo para datos verdaderamente inmutables (tabla de referencia Brix).
IMMUTABLE_TTL = 1800

# Prefijo de las claves de versión de grupo.
_VERSION_PREFIX = 'cachever'


def _factory_id(request):
    """factory_id del header, normalizado a str para construir claves estables."""
    return str(request.META.get('HTTP_X_FACTORY_ID', 1))


def _version_key(group, factory_id):
    return f'{_VERSION_PREFIX}:{group}:f{factory_id}'


def _get_group_version(group, factory_id):
    """Versión actual del grupo para esta fábrica (1 si nunca se inicializó).

    Se usa add() para fijar la versión inicial sin pisar una concurrente.
    """
    key = _version_key(group, factory_id)
    version = cache.get(key)
    if version is None:
        # add() solo escribe si la clave no existe: evita una carrera entre
        # dos lecturas simultáneas que inicializarían la versión a la vez.
        cache.add(key, 1, None)  # None = sin expiración para el contador
        version = cache.get(key) or 1
    return version


def bump_cache_version(group, factory_id):
    """Invalida TODAS las lecturas cacheadas de un grupo para una fábrica.

    Llamar desde cada vista de escritura que modifique datos del grupo. Sube el
    contador de versión; como la clave de lectura incluye la versión, las
    entradas viejas dejan de ser alcanzables (y expiran solas por su TTL).

    `factory_id` puede venir como int o str; se normaliza.
    """
    factory_id = str(factory_id)
    key = _version_key(group, factory_id)
    try:
        # incr() es atómico en el backend; si la clave no existe aún, la creamos.
        cache.incr(key)
    except ValueError:
        cache.set(key, 2, None)  # arrancó en 1 implícito → siguiente es 2
    logger.debug("cache bump group=%s factory=%s", group, factory_id)


def cached_per_factory(group, ttl=DEFAULT_TTL):
    """Decorador para vistas GET sin parámetros variables (salvo el factory_id).

    Cachea el cuerpo de la respuesta por (group, factory_id, versión_de_grupo).
    Solo cachea status 200. En cualquier otro caso, deja pasar la respuesta sin
    cachearla.

    Debe envolver la función de vista DESPUÉS de @jwt_required (es decir, ir más
    abajo en la lista de decoradores), para que la autenticación corra siempre,
    incluso en un cache hit, y el header X-Factory-ID esté disponible.
    """
    def decorator(view_func):
        # Identificador estable y ÚNICO de esta vista. El grupo se usa solo para
        # la invalidación (un bump del grupo invalida todas sus vistas); la clave
        # de caché debe distinguir cada vista, o dos endpoints del mismo grupo
        # (p. ej. calibration/list y calibration/active) colisionarían y uno
        # devolvería la respuesta del otro.
        view_id = f'{view_func.__module__}.{view_func.__qualname__}'

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            factory_id = _factory_id(request)
            version = _get_group_version(group, factory_id)
            cache_key = f'view:{group}:{view_id}:f{factory_id}:v{version}'

            cached = cache.get(cache_key)
            if cached is not None:
                status, content, content_type = cached
                from django.http import HttpResponse
                response = HttpResponse(
                    content, status=status, content_type=content_type
                )
                response['X-Cache'] = 'HIT'
                return response

            response = view_func(request, *args, **kwargs)

            # Solo cachear respuestas exitosas y no-streaming.
            if (getattr(response, 'status_code', None) == 200
                    and not getattr(response, 'streaming', False)):
                try:
                    cache.set(
                        cache_key,
                        (
                            response.status_code,
                            response.content,
                            response.get('Content-Type', 'application/json'),
                        ),
                        ttl,
                    )
                    response['X-Cache'] = 'MISS'
                except Exception as exc:
                    logger.warning("no se pudo cachear %s: %s", cache_key, exc)
            return response
        return wrapper
    return decorator
