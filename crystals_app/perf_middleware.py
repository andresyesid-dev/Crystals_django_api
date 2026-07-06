"""
Performance Instrumentation Middleware (T0 — Línea base de medición)
=====================================================================
Mide el tiempo de procesamiento de CADA petición dentro del servidor y lo
deja disponible por dos vías, sin alterar la lógica de negocio:

  1. Header `Server-Timing` en la respuesta (estándar web). El cliente de
     escritorio puede leerlo (`response.headers['Server-Timing']`) para
     separar el tiempo de SERVIDOR del RTT de red total que mide por su lado.
     También es visible en las DevTools de cualquier navegador.

  2. Log estructurado en `performance.log` (logger `crystals_perf`): una línea
     por petición con método, ruta, factory_id, status, duración en ms y
     tamaño del cuerpo en bytes. Es la fuente para comparar objetivamente el
     antes/después del endpoint compuesto (T1) y de la compresión GZip (T3).

Por qué un middleware y no instrumentar vista por vista:
    El cuello de botella reportado es de latencia agregada (23 GETs encolados
    contra 3 workers), no de una vista concreta. Medir en el borde del
    servidor captura el costo real percibido por petición — incluida la parte
    que aportan los middlewares de seguridad — sin tocar las 39 vistas.

Coste: una resta de `time.perf_counter()` y un `logger.info` por petición.
Despreciable frente al trabajo de cualquier endpoint. Diseñado para quedarse
activo en producción como telemetría permanente de baja frecuencia.
"""

import logging
import time

from django.utils.deprecation import MiddlewareMixin

perf_logger = logging.getLogger('crystals_perf')


class PerformanceTimingMiddleware(MiddlewareMixin):
    """Cronometra cada petición y publica la duración en header + log."""

    def process_request(self, request):
        # perf_counter: reloj monotónico de alta resolución, inmune a ajustes
        # de hora del sistema (a diferencia de time.time()).
        request._perf_start = time.perf_counter()
        return None

    def process_response(self, request, response):
        start = getattr(request, '_perf_start', None)
        if start is None:
            # La petición no pasó por process_request (p. ej. respuesta
            # generada por un middleware anterior). Nada que medir.
            return response

        duration_ms = (time.perf_counter() - start) * 1000.0

        # Header Server-Timing estándar: el cliente y las DevTools lo entienden.
        # Formato: "<nombre>;dur=<ms>". No se sobrescribe si ya existe.
        timing_value = f'app;dur={duration_ms:.1f}'
        existing = response.get('Server-Timing')
        response['Server-Timing'] = (
            f'{existing}, {timing_value}' if existing else timing_value
        )

        # El tamaño solo está disponible de forma fiable en respuestas no
        # streaming; para streaming se omite (no se materializa el cuerpo).
        if getattr(response, 'streaming', False):
            body_bytes = -1
        else:
            try:
                body_bytes = len(response.content)
            except Exception:
                body_bytes = -1

        factory_id = request.META.get('HTTP_X_FACTORY_ID', '-')

        perf_logger.info(
            "%s %s factory=%s status=%s dur_ms=%.1f bytes=%s",
            request.method,
            request.get_full_path(),
            factory_id,
            response.status_code,
            duration_ms,
            body_bytes,
        )
        return response
