"""
Views for managing laboratory parametrization tables
"""
from rest_framework.decorators import api_view
from crystals_app.decorators import jwt_required
from django.http import JsonResponse
from crystals_app.models import (
    LaboratoryParametrization,
    LaboratoryCalculatedRefinoParametrization,
    LaboratoryCalculatedMasaAParametrization,
    LaboratoryCalculatedMasaBParametrization,
    LaboratoryCalculatedMasaCParametrization,
    CrystalsDataParametrization
)
import logging

logger = logging.getLogger('crystals_api')

# 36 materials from MATERIALS constant
MATERIALS = [
    "pza_licor", "pza_sirope", "pza_masa_refino", "pza_magma_b", "pza_meladura",
    "pza_masa_a", "pza_lavado_a", "pza_nutsch_a", "pza_magma_c", "pza_miel_a",
    "pza_masa_b", "pza_nutsch_b", "pza_cr_des", "pza_miel_b", "pza_masa_c",
    "pza_nutsch_c", "pza_miel_final", "bx_masa_c", "bx_cristal_des", "bx_nutsch_c",
    "bx_masa_b", "bx_masa_a", "bx_magma_b", "bx_masa_refino", "bx_magma_c",
    "bx_miel_final", "bx_nutsch_b", "bx_miel_b", "bx_miel_a", "bx_lavado_a",
    "bx_nutsch_a", "bx_sirope", "bx_del_licor", "bx_meladura", "pol_azuc",
    "sol_tota_hda_azu"
]


@api_view(['POST'])
@jwt_required
def insert_laboratory_parametrization(request):
    """
    Insert default laboratory parametrization records (108 items = 36 materials x 3 categories).
    Only inserts if table is empty.
    """
    try:
        # Check if table already has data
        count = LaboratoryParametrization.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).count()
        if count > 0:
            return JsonResponse({
                'ok': True,
                'already_exists': True,
                'count': count,
                'message': 'Laboratory parametrization already initialized'
            })
        
        # Generate 108 records (36 materials x 3 categories)
        categories = ['Good', 'Regular', 'Bad']
        records = []
        for material in MATERIALS:
            for category in categories:
                records.append(LaboratoryParametrization(
                    material=material,
                    categoria=category,
                    range_from=None,
                    range_to=None,
                    factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)
                ))
        
        # Bulk create
        LaboratoryParametrization.objects.bulk_create(records)
        
        logger.info(f"✅ Inserted {len(records)} laboratory parametrization records")
        
        return JsonResponse({
            'ok': True,
            'created': len(records),
            'message': 'Laboratory parametrization initialized successfully'
        })
        
    except Exception as e:
        logger.error(f"Error inserting laboratory parametrization: {e}", exc_info=True)
        return JsonResponse({
            'ok': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@jwt_required
def insert_laboratory_calculated_refino(request):
    """
    Insert default refino calculated parametrization (12 items = 4 parameters x 3 categories).
    Only inserts if table is empty.
    """
    try:
        count = LaboratoryCalculatedRefinoParametrization.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).count()
        if count > 0:
            return JsonResponse({
                'ok': True,
                'already_exists': True,
                'count': count,
                'message': 'Refino calculated parametrization already initialized'
            })
        
        # 4 parameters x 3 categories
        parameters = ['caida', 'rendimientos', '%_cristales', 'agotamientos']
        categories = ['Good', 'Regular', 'Bad']
        records = []
        
        for parameter in parameters:
            for category in categories:
                records.append(LaboratoryCalculatedRefinoParametrization(
                    parameter=parameter,
                    categoria=category,
                    range_from=None,
                    range_to=None,
                    factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)
                ))
        
        LaboratoryCalculatedRefinoParametrization.objects.bulk_create(records)
        logger.info(f"✅ Inserted {len(records)} refino calculated parametrization records")
        
        return JsonResponse({
            'ok': True,
            'created': len(records),
            'message': 'Refino calculated parametrization initialized successfully'
        })
        
    except Exception as e:
        logger.error(f"Error inserting refino calculated parametrization: {e}", exc_info=True)
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


@api_view(['POST'])
@jwt_required
def insert_laboratory_calculated_masa_a(request):
    """
    Insert default masa A calculated parametrization (12 items).
    Only inserts if table is empty.
    """
    try:
        count = LaboratoryCalculatedMasaAParametrization.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).count()
        if count > 0:
            return JsonResponse({
                'ok': True,
                'already_exists': True,
                'count': count,
                'message': 'Masa A calculated parametrization already initialized'
            })
        
        parameters = ['caida', 'rendimientos', '%_cristales', 'agotamientos']
        categories = ['Good', 'Regular', 'Bad']
        records = []
        
        for parameter in parameters:
            for category in categories:
                records.append(LaboratoryCalculatedMasaAParametrization(
                    parameter=parameter,
                    categoria=category,
                    range_from=None,
                    range_to=None,
                    factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)
                ))
        
        LaboratoryCalculatedMasaAParametrization.objects.bulk_create(records)
        logger.info(f"✅ Inserted {len(records)} masa A calculated parametrization records")
        
        return JsonResponse({
            'ok': True,
            'created': len(records),
            'message': 'Masa A calculated parametrization initialized successfully'
        })
        
    except Exception as e:
        logger.error(f"Error inserting masa A calculated parametrization: {e}", exc_info=True)
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


@api_view(['POST'])
@jwt_required
def insert_laboratory_calculated_masa_b(request):
    """
    Insert default masa B calculated parametrization (12 items).
    Only inserts if table is empty.
    """
    try:
        count = LaboratoryCalculatedMasaBParametrization.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).count()
        if count > 0:
            return JsonResponse({
                'ok': True,
                'already_exists': True,
                'count': count,
                'message': 'Masa B calculated parametrization already initialized'
            })
        
        parameters = ['caida', 'rendimientos', '%_cristales', 'agotamientos']
        categories = ['Good', 'Regular', 'Bad']
        records = []
        
        for parameter in parameters:
            for category in categories:
                records.append(LaboratoryCalculatedMasaBParametrization(
                    parameter=parameter,
                    categoria=category,
                    range_from=None,
                    range_to=None,
                    factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)
                ))
        
        LaboratoryCalculatedMasaBParametrization.objects.bulk_create(records)
        logger.info(f"✅ Inserted {len(records)} masa B calculated parametrization records")
        
        return JsonResponse({
            'ok': True,
            'created': len(records),
            'message': 'Masa B calculated parametrization initialized successfully'
        })
        
    except Exception as e:
        logger.error(f"Error inserting masa B calculated parametrization: {e}", exc_info=True)
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


@api_view(['POST'])
@jwt_required
def insert_laboratory_calculated_masa_c(request):
    """
    Insert default masa C calculated parametrization (12 items).
    Only inserts if table is empty.
    """
    try:
        count = LaboratoryCalculatedMasaCParametrization.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).count()
        if count > 0:
            return JsonResponse({
                'ok': True,
                'already_exists': True,
                'count': count,
                'message': 'Masa C calculated parametrization already initialized'
            })
        
        parameters = ['caida', 'rendimientos', '%_cristales', 'agotamientos']
        categories = ['Good', 'Regular', 'Bad']
        records = []
        
        for parameter in parameters:
            for category in categories:
                records.append(LaboratoryCalculatedMasaCParametrization(
                    parameter=parameter,
                    categoria=category,
                    range_from=None,
                    range_to=None,
                    factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)
                ))
        
        LaboratoryCalculatedMasaCParametrization.objects.bulk_create(records)
        logger.info(f"✅ Inserted {len(records)} masa C calculated parametrization records")
        
        return JsonResponse({
            'ok': True,
            'created': len(records),
            'message': 'Masa C calculated parametrization initialized successfully'
        })
        
    except Exception as e:
        logger.error(f"Error inserting masa C calculated parametrization: {e}", exc_info=True)
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


@api_view(['POST'])
@jwt_required
def insert_crystals_data_parametrization(request):
    """
    Insert default crystals data parametrization (21 items = 7 parameters x 3 categories).
    Only inserts if table is empty.
    """
    try:
        count = CrystalsDataParametrization.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).count()
        if count > 0:
            return JsonResponse({
                'ok': True,
                'already_exists': True,
                'count': count,
                'message': 'Crystals data parametrization already initialized'
            })
        
        # 7 crystal parameters
        parameters = [
            '%_fino.', '%_peq.', '%_opt.', '%_gran.', 
            '%_muy_gran.', 'rel._l/a', '%_crist._alarg'
        ]
        categories = ['Good', 'Regular', 'Bad']
        records = []
        
        for parameter in parameters:
            for category in categories:
                records.append(CrystalsDataParametrization(
                    parameter=parameter,
                    categoria=category,
                    range_from=None,
                    range_to=None,
                    factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)
                ))
        
        CrystalsDataParametrization.objects.bulk_create(records)
        logger.info(f"✅ Inserted {len(records)} crystals data parametrization records")
        
        return JsonResponse({
            'ok': True,
            'created': len(records),
            'message': 'Crystals data parametrization initialized successfully'
        })
        
    except Exception as e:
        logger.error(f"Error inserting crystals data parametrization: {e}", exc_info=True)
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)
