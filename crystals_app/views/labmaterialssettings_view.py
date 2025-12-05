from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import LabMaterialsSettings
import json


@require_http_methods(["GET"])
@jwt_required
@sensitive_endpoint
@log_api_access
def get_lab_materials_settings(request: HttpRequest):
    try:
        data = [model_to_dict(o) for o in LabMaterialsSettings.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1))]
        return JsonResponse({"message": "✅ Configuración de materiales obtenida exitosamente", "results": data})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener configuración de materiales", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def insert_lab_materials_settings(request: HttpRequest):
    """
    Inserta los 19 materiales base con visible=1 SOLO si la tabla está vacía.
    Si recibe un payload con updates, actúa como update (parche para clientes que usan insert para guardar).
    """
    try:
        # Check for update payload first
        try:
            body = json.loads(request.body or b"{}")
            if "updates" in body:
                return update_lab_materials_settings(request)
        except Exception:
            pass
            
        # Check for 'values' payload (list of booleans) from client
        try:
            body = json.loads(request.body or b"{}")
            if "values" in body:
                values = body["values"]
                base_materials = [
                    'licor', 'sirope', 'masa_refino', 'magma_b', 'meladura',
                    'masa_a', 'lavado_a', 'nutsch_a', 'magma_c', 'miel_a',
                    'masa_b', 'nutsch_b', 'cr_des', 'miel_b', 'masa_c',
                    'nutsch_c', 'miel_final', 'pol_azuc', 'sol_tota_hda_azu'
                ]
                # Ensure values list matches length
                updated_count = 0
                for i, material in enumerate(base_materials):
                    if i < len(values):
                        visible = 1 if values[i] else 0
                        LabMaterialsSettings.objects.filter(
                            material=material, 
                            factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)
                        ).update(visible=visible)
                        updated_count += 1
                return JsonResponse({
                    "message": f"✅ Materiales actualizados exitosamente ({updated_count} registros)", 
                    "ok": True, 
                    "updated": updated_count
                })
        except Exception:
            pass

        # Verificar si la tabla está vacía
        if LabMaterialsSettings.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).count() > 0:
            return JsonResponse({
                "message": "ℹ️ Materiales ya existen en la base de datos",
                "ok": True,
                "already_exists": True
            })
        
        # Lista de los 19 materiales base
        base_materials = [
            'licor', 'sirope', 'masa_refino', 'magma_b', 'meladura',
            'masa_a', 'lavado_a', 'nutsch_a', 'magma_c', 'miel_a',
            'masa_b', 'nutsch_b', 'cr_des', 'miel_b', 'masa_c',
            'nutsch_c', 'miel_final', 'pol_azuc', 'sol_tota_hda_azu'
        ]
        
        # Insertar cada material con visible=1 (por defecto)
        for material_name in base_materials:
            LabMaterialsSettings.objects.create(
                material=material_name,
                visible=1,
                factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)
            )
        
        return JsonResponse({
            "message": f"✅ {len(base_materials)} materiales base insertados exitosamente",
            "ok": True,
            "created": len(base_materials)
        })
    except Exception as e:
        return JsonResponse({
            "message": "❌ Error al insertar materiales",
            "error": str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST", "PATCH"])
@jwt_required
@sensitive_endpoint
@log_api_access
def update_lab_materials_settings(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        updates = body.get("updates") or []
        updated = 0
        for item in updates:
            material = item.get("material")
            visible = item.get("visible")
            if material is not None and visible is not None:
                updated += LabMaterialsSettings.objects.filter(material=material, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).update(visible=int(bool(visible)))
        return JsonResponse({"message": f"✅ Materiales actualizados exitosamente ({updated} registros)", "ok": True, "updated": updated})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al actualizar materiales", "error": str(e)}, status=500)
