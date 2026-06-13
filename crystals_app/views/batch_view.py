"""
Batch View (Fase 0 — Estructura de endpoints batch atomicos)
=============================================================
Endpoint unico para ejecutar multiples operaciones de escritura en UNA
transaccion de base de datos.

Problema que resuelve (auditoria, familia F2):
    Los flujos multi-item del cliente (reordenar headers, reordenar
    calibraciones, guardar parametrizaciones, borrados grupales) hoy emiten
    N peticiones HTTP secuenciales. Un corte de conexion a mitad del bucle
    deja la base de la nube en un estado parcial irreparable y ademas
    congela la UI durante N round-trips.

Contrato:
    POST /batch/atomic
    {
        "operations": [
            {"table": "general_reporting_order",
             "action": "update",
             "filter": {"id": 3},
             "values": {"ordering": 1}},
            {"table": "calibration",
             "action": "update",
             "filter": {"id": 7},
             "values": {"ordering": null}},
            ...
        ]
    }

    Respuesta 200: {"status": "success", "applied": N}
    Respuesta 4xx: {"error": "...", "failed_operation": i}
                   (la transaccion completa se revierte: cero efectos)

Seguridad:
    - Solo tablas en la whitelist explicita (BATCH_MODEL_WHITELIST).
    - Solo acciones create/update/delete.
    - Aislamiento multi-tenant: el filtro factory_id se inyecta SIEMPRE
      del header X-Factory-ID; el cliente no puede tocar otra fabrica.
    - Limite de operaciones por lote (MAX_OPERATIONS).
"""

import json

from django.apps import apps
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..decorators import jwt_required, log_api_access

# Tablas habilitadas para escritura por lote. Clave publica -> modelo Django.
# Nombres verificados contra crystals_app/models.py.
BATCH_MODEL_WHITELIST = {
    'calibration': 'Calibration',
    'general_reporting_order': 'GeneralReportingOrder',
    'specific_reporting_order': 'SpecificReportingOrder',
    'laboratory_reporting_order': 'LaboratoryReportingOrder',
    'laboratory_parametrization': 'LaboratoryParametrization',
    'laboratory_calculated_refino_parametrization': 'LaboratoryCalculatedRefinoParametrization',
    'laboratory_calculated_masa_a_parametrization': 'LaboratoryCalculatedMasaAParametrization',
    'laboratory_calculated_masa_b_parametrization': 'LaboratoryCalculatedMasaBParametrization',
    'laboratory_calculated_masa_c_parametrization': 'LaboratoryCalculatedMasaCParametrization',
    'crystals_data_parametrization': 'CrystalsDataParametrization',
    'crystals_data_parametrization_nw_params': 'CrystalsDataParametrizationNewParams',
    'crystals_data_parametrization_ma': 'CrystalsDataParametrizationMA',
    'crystals_data_parametrization_cv': 'CrystalsDataParametrizationCV',
    'management_report_layout': 'ManagementReportLayout',
    'process_code_data': 'ProcessCodeData',
    'brix_calculator_data': 'BrixCalculatorData',
    'laboratory_data': 'LaboratoryData',
    'laboratory_settings_excel': 'LaboratorySettingsExcel',
}

ALLOWED_ACTIONS = ('create', 'update', 'delete')
MAX_OPERATIONS = 500


class _BatchError(Exception):
    """Error de validacion/ejecucion de una operacion del lote."""

    def __init__(self, message, index):
        super().__init__(message)
        self.index = index


def _model_has_field(model, field_name):
    return any(f.name == field_name for f in model._meta.get_fields())


def _apply_operation(operation, index, factory_id):
    table = operation.get('table')
    action = operation.get('action')

    if table not in BATCH_MODEL_WHITELIST:
        raise _BatchError(f"Tabla no permitida en batch: '{table}'", index)
    if action not in ALLOWED_ACTIONS:
        raise _BatchError(f"Accion no permitida: '{action}'", index)

    model = apps.get_model('crystals_app', BATCH_MODEL_WHITELIST[table])
    values = operation.get('values') or {}
    filters = dict(operation.get('filter') or {})

    # Aislamiento multi-tenant: factory_id viene SIEMPRE del header.
    has_factory = _model_has_field(model, 'factory_id')
    if has_factory:
        filters['factory_id'] = factory_id
        # En creates, forzar la fabrica del header (ignorar la del payload).
        if action == 'create':
            values = dict(values)
            values['factory_id'] = factory_id
    values.pop('id', None)  # el id nunca se actualiza por valores

    if action == 'create':
        model.objects.create(**values)
        return 1

    if not operation.get('filter'):
        raise _BatchError(
            f"La accion '{action}' requiere un 'filter' explicito", index
        )

    queryset = model.objects.filter(**filters)

    if action == 'update':
        if not values:
            raise _BatchError("update sin 'values'", index)
        return queryset.update(**values)

    # delete
    deleted, _detail = queryset.delete()
    return deleted


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@log_api_access
def atomic_batch(request):
    """Ejecuta una lista de operaciones de escritura en una transaccion."""
    try:
        body = json.loads(request.body or b'{}')
    except (ValueError, TypeError):
        return JsonResponse({"error": "JSON invalido"}, status=400)

    operations = body.get('operations')
    if not isinstance(operations, list) or not operations:
        return JsonResponse(
            {"error": "Se requiere 'operations' (lista no vacia)"}, status=400
        )
    if len(operations) > MAX_OPERATIONS:
        return JsonResponse(
            {"error": f"Maximo {MAX_OPERATIONS} operaciones por lote"},
            status=400,
        )

    try:
        factory_id = int(request.META.get('HTTP_X_FACTORY_ID', 1))
    except (ValueError, TypeError):
        factory_id = 1

    applied = 0
    try:
        with transaction.atomic():
            for index, operation in enumerate(operations):
                if not isinstance(operation, dict):
                    raise _BatchError("Operacion invalida (se espera objeto)", index)
                applied += _apply_operation(operation, index, factory_id)
    except _BatchError as exc:
        return JsonResponse(
            {"error": str(exc), "failed_operation": exc.index}, status=400
        )
    except Exception as exc:  # FieldError, IntegrityError, etc. -> rollback
        return JsonResponse(
            {"error": f"Batch revertido: {exc}"}, status=400
        )

    return JsonResponse({"status": "success", "applied": applied})
