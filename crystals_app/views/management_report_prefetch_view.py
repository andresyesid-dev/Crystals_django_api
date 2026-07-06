"""
Management Report Prefetch View (T1 — Endpoint compuesto de lectura)
====================================================================
Colapsa en UNA sola petición HTTP las 23 lecturas GET que el cliente de
escritorio dispara en paralelo al abrir la pantalla de reportes de gestión
(`CrystalsDatabase.prefetch_management_report_data`).

Problema que resuelve:
    El cliente lanza 23 GETs concurrentes (`execute_batch(batch,
    max_workers=len(batch))`). Contra los 3 workers sync de Gunicorn, 20 de
    esas peticiones quedan encoladas; cada una vuelve a pagar RTT de red,
    decode/validación de JWT y la cadena de middlewares de seguridad. La
    latencia de apertura de la pantalla queda dominada por la cola, no por
    el tiempo de cada query.

Contrato:
    GET /management-report/prefetch?start=YYYY-MM-DD HH:MM:00&end=YYYY-MM-DD HH:MM:00

    200 →
    {
        "status": "success",
        "results": {
            "historic_report_list":            <cuerpo del endpoint individual>,
            "management_report_settings_get":  <cuerpo del endpoint individual>,
            ... (las 23 claves, con el nombre EXACTO del dict ENDPOINTS del cliente)
        },
        "errors": { "<clave>": "<detalle>" }   # solo si alguna sub-vista falló
    }

Diseño:
    - Reutiliza las 23 vistas existentes SIN duplicar su lógica: cada una se
      invoca en proceso con el `request` real (mismo JWT ya validado, misma
      `META`, mismo `HTTP_X_FACTORY_ID`), sustituyendo temporalmente
      `request.GET` por los query params que esa vista espera. El re-decode
      del JWT dentro de cada sub-vista es in-process (~microsegundos) frente
      al RTT de red que se elimina.
    - El cuerpo de cada sub-respuesta se anida BYTE-EQUIVALENTE al que hoy
      devuelve el endpoint individual, para que el cliente reutilice su parseo
      actual clave por clave.
    - Aislamiento multi-tenant intacto: las sub-vistas siguen leyendo
      `factory_id` del header del request original; el compuesto no lo toca.
    - Una sub-vista que falle no tumba el lote: su entrada queda en `errors`
      y el resto se devuelve igual (el cliente ya tolera ausencia de clave).
"""

import json
import logging

from django.http import JsonResponse, QueryDict
from django.views.decorators.http import require_http_methods

from ..decorators import jwt_required, log_api_access

from .historicreport_view import get_historic_reports
from .historicanalysisdata_view import get_analysis_historic_data
from .laboratorydata_view import get_historic_laboratory_data
from .managementreportsettings_view import get_management_report_settings
from .managementreportlayout_view import get_management_report_layout
from .laboratoryreportingorder_view import get_laboratory_headers_ordering
from .generalreportingorder_view import get_general_headers_ordering
from .specificreportingorder_view import get_specific_headers_ordering
from .config_view import (
    get_DOP_config,
    get_calculated_data_period,
    get_language,
)
from .crystalsdataparametrization_view import get_crystals_data_parametrization
from .crystalsdataparametrizationma_view import get_crystals_data_parametrization_ma
from .crystalsdataparametrizationcv_view import get_crystals_data_parametrization_cv
from .crystalsdataparametrizationnwparams_view import (
    get_crystals_data_parametrization_nw_params,
)
from .calibration_view import (
    select_calibrations,
    select_historic_reports_calibrations,
)
from .analysiscategory_view import get_new_parameters_analysis_categories
from .laboratoryparametrization_view import get_laboratory_parametrization
from .laboratorycalculatedrefinoparametrization_view import (
    get_laboratory_calculated_refino_parametrization,
)
from .laboratorycalculatedmasaa_parametrization_view import (
    get_laboratory_calculated_masa_a_parametrization,
)
from .laboratorycalculatedmasab_parametrization_view import (
    get_laboratory_calculated_masa_b_parametrization,
)
from .laboratorycalculatedmasac_parametrization_view import (
    get_laboratory_calculated_masa_c_parametrization,
)

logger = logging.getLogger('crystals_api')

# Las 3 lecturas que dependen del rango de fechas necesitan start/end.
_DATE_RANGE_KEYS = frozenset({
    'historic_report_list',
    'historic_analysis_list',
    'laboratory_data_historic',
})

# Plan de prefetch: clave (nombre EXACTO del ENDPOINTS del cliente) -> función
# de vista existente. El orden replica el del batch del cliente para que la
# respuesta sea fácil de comparar 1:1 durante la verificación.
_PREFETCH_PLAN = (
    ('historic_report_list',            get_historic_reports),
    ('management_report_settings_get',  get_management_report_settings),
    ('laboratory_headers_order_get',    get_laboratory_headers_ordering),
    ('mgmt_report_layout_get',          get_management_report_layout),
    ('config_dop_get',                  get_DOP_config),
    ('crystals_data_param_get',         get_crystals_data_parametrization),
    ('crystals_data_param_ma_get',      get_crystals_data_parametrization_ma),
    ('crystals_data_param_cv_get',      get_crystals_data_parametrization_cv),
    ('general_headers_order_get',       get_general_headers_ordering),
    ('calibration_historic',            select_historic_reports_calibrations),
    ('historic_analysis_list',          get_analysis_historic_data),
    ('analysis_cat_get_new',            get_new_parameters_analysis_categories),
    ('crystals_data_param_nw_get',      get_crystals_data_parametrization_nw_params),
    ('specific_headers_order_get',      get_specific_headers_ordering),
    ('calibration_list',                select_calibrations),
    ('laboratory_data_historic',        get_historic_laboratory_data),
    ('lab_param_get',                   get_laboratory_parametrization),
    ('lab_calc_refino_param_get',       get_laboratory_calculated_refino_parametrization),
    ('lab_calc_masa_a_param_get',       get_laboratory_calculated_masa_a_parametrization),
    ('lab_calc_masa_b_param_get',       get_laboratory_calculated_masa_b_parametrization),
    ('lab_calc_masa_c_param_get',       get_laboratory_calculated_masa_c_parametrization),
    ('config_calculated_period_get',    get_calculated_data_period),
    ('config_language_get',             get_language),
)


def _build_query(date_range, needs_dates):
    """Devuelve un QueryDict inmutable con los params que la sub-vista espera.

    Las sub-vistas leen exclusivamente `request.GET.get('start'/'end')`; las
    demás no leen query params. Devolver un QueryDict vacío para esas últimas
    reproduce con exactitud su comportamiento individual.
    """
    qd = QueryDict(mutable=True)
    if needs_dates:
        qd['start'] = date_range['start']
        qd['end'] = date_range['end']
    qd._mutable = False
    return qd


def _invoke(view_func, request, query):
    """Invoca una sub-vista con el request real y su QueryDict sustituido.

    Restaura `request.GET` siempre (incluso si la vista lanza), para no
    contaminar la siguiente invocación ni la respuesta del propio compuesto.
    Devuelve (payload_dict, error_str). Exactamente uno es None.
    """
    original_get = request.GET
    request.GET = query
    try:
        response = view_func(request)
    except Exception as exc:  # la sub-vista reventó: aislar y continuar
        return None, str(exc)
    finally:
        request.GET = original_get

    content = response.content
    if not content:
        # Respuesta sin cuerpo: el cliente lo trata como {"status": "success"}.
        return {"status": "success"}, None
    try:
        return json.loads(content), None
    except (ValueError, TypeError) as exc:
        return None, f"respuesta no-JSON ({exc})"


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def management_report_prefetch(request):
    """Devuelve en una sola respuesta las 23 lecturas del prefetch de gestión."""
    start = request.GET.get('start')
    end = request.GET.get('end')
    if not start or not end:
        return JsonResponse(
            {
                "status": "error",
                "error": "Los parámetros 'start' y 'end' son requeridos "
                         "(YYYY-MM-DD HH:MM:SS)",
            },
            status=400,
        )

    date_range = {'start': start, 'end': end}
    results = {}
    errors = {}

    for key, view_func in _PREFETCH_PLAN:
        query = _build_query(date_range, key in _DATE_RANGE_KEYS)
        payload, error = _invoke(view_func, request, query)
        if error is not None:
            errors[key] = error
            logger.warning(
                "[prefetch] sub-vista '%s' falló: %s", key, error
            )
            continue
        results[key] = payload

    response_body = {"status": "success", "results": results}
    if errors:
        response_body["errors"] = errors
    return JsonResponse(response_body)
