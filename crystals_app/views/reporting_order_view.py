"""
Views for managing reporting order tables (specific, general, laboratory)
"""
from rest_framework.decorators import api_view
from crystals_app.decorators import jwt_required
from django.http import JsonResponse
from crystals_app.models import (
    SpecificReportingOrder,
    GeneralReportingOrder,
    LaboratoryReportingOrder
)
import logging

logger = logging.getLogger('crystals_api')


@api_view(['POST'])
@jwt_required
def insert_specific_reporting_order(request):
    """
    Insert default specific reporting order records (22 items).
    Only inserts if table is empty.
    """
    try:
        # Check if table already has data
        count = SpecificReportingOrder.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).count()
        if count > 0:
            return JsonResponse({
                'ok': True,
                'already_exists': True,
                'count': count,
                'message': 'Specific reporting order already initialized'
            })
        
        # Default data (22 records)
        default_data = [
            {'value': 'WEIGHTS PER SHIFT', 'ordering': 0},
            {'value': 'TACHO', 'ordering': 1},
            {'value': 'DATE AND TIME', 'ordering': 2},
            {'value': 'TACHERO', 'ordering': 3},
            {'value': 'BAKING TIME', 'ordering': 4},
            {'value': 'MASS NUMBER', 'ordering': 5},
            {'value': 'Mean', 'ordering': 6},
            {'value': 'CV', 'ordering': 7},
            {'value': '% Fino.', 'ordering': 8},
            {'value': '% Peq.', 'ordering': 9},
            {'value': '% Opt.', 'ordering': 10},
            {'value': '% Gran.', 'ordering': 11},
            {'value': '% Muy gran.', 'ordering': 12},
            {'value': 'REL. L/A', 'ordering': 13},
            {'value': '% crist. alarg', 'ordering': 14},
            {'value': '% Powder', 'ordering': 15},
            {'value': 'Amount % Fino.', 'ordering': 16},
            {'value': 'Amount % Peq.', 'ordering': 17},
            {'value': 'Amount % Opt.', 'ordering': 18},
            {'value': 'Amount % Gran.', 'ordering': 19},
            {'value': 'Amount % Muy gran.', 'ordering': 20},
            {'value': 'Total Amount', 'ordering': 21}
        ]
        
        # Bulk create
        records = [SpecificReportingOrder(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1), **item) for item in default_data]
        SpecificReportingOrder.objects.bulk_create(records)
        
        logger.info(f"✅ Inserted {len(default_data)} specific reporting order records")
        
        return JsonResponse({
            'ok': True,
            'created': len(default_data),
            'message': 'Specific reporting order initialized successfully'
        })
        
    except Exception as e:
        logger.error(f"Error inserting specific reporting order: {e}", exc_info=True)
        return JsonResponse({
            'ok': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@jwt_required
def insert_general_reporting_order(request):
    """
    Insert default general reporting order records (18 items).
    Only inserts if table is empty.
    """
    try:
        # Check if table already has data
        count = GeneralReportingOrder.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).count()
        if count > 0:
            return JsonResponse({
                'ok': True,
                'already_exists': True,
                'count': count,
                'message': 'General reporting order already initialized'
            })
        
        # Default data (18 records)
        default_data = [
            {'value': 'Calibration', 'ordering': 0},
            {'value': 'Mean', 'ordering': 1},
            {'value': 'MA Objective', 'ordering': 2},
            {'value': 'CV', 'ordering': 3},
            {'value': 'CV Objective', 'ordering': 4},
            {'value': '% Fino.', 'ordering': 5},
            {'value': '% Peq.', 'ordering': 6},
            {'value': '% Opt.', 'ordering': 7},
            {'value': '% Gran.', 'ordering': 8},
            {'value': '% Muy gran.', 'ordering': 9},
            {'value': 'REL. L/A', 'ordering': 10},
            {'value': '% crist. alarg', 'ordering': 11},
            {'value': 'Amount % Fino.', 'ordering': 12},
            {'value': 'Amount % Peq.', 'ordering': 13},
            {'value': 'Amount % Opt.', 'ordering': 14},
            {'value': 'Amount % Gran.', 'ordering': 15},
            {'value': 'Amount % Muy gran.', 'ordering': 16},
            {'value': 'Total Amount', 'ordering': 17}
        ]
        
        # Bulk create
        records = [GeneralReportingOrder(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1), **item) for item in default_data]
        GeneralReportingOrder.objects.bulk_create(records)
        
        logger.info(f"✅ Inserted {len(default_data)} general reporting order records")
        
        return JsonResponse({
            'ok': True,
            'created': len(default_data),
            'message': 'General reporting order initialized successfully'
        })
        
    except Exception as e:
        logger.error(f"Error inserting general reporting order: {e}", exc_info=True)
        return JsonResponse({
            'ok': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@jwt_required
def insert_laboratory_reporting_order(request):
    """
    Insert default laboratory reporting order records (37 items).
    Only inserts if table is empty.
    """
    try:
        # Check if table already has data
        count = LaboratoryReportingOrder.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).count()
        if count > 0:
            return JsonResponse({
                'ok': True,
                'already_exists': True,
                'count': count,
                'message': 'Laboratory reporting order already initialized'
            })
        
        # Default data (37 records)
        default_data = [
            {'value': 'DATE AND TIME', 'ordering': 0},
            {'value': 'PZA LICOR', 'ordering': 1},
            {'value': 'PZA SIROPE', 'ordering': 2},
            {'value': 'PZA MASA REFINO', 'ordering': 3},
            {'value': 'PZA MAGMA B', 'ordering': 4},
            {'value': 'PZA MELADURA', 'ordering': 5},
            {'value': 'PZA MASA A', 'ordering': 6},
            {'value': 'PZA LAVADO A', 'ordering': 7},
            {'value': 'PZA NUTSCH A', 'ordering': 8},
            {'value': 'PZA MAGMA C', 'ordering': 9},
            {'value': 'PZA MIEL A', 'ordering': 10},
            {'value': 'PZA MASA B', 'ordering': 11},
            {'value': 'PZA NUTSCH B', 'ordering': 12},
            {'value': 'PZA CR DES', 'ordering': 13},
            {'value': 'PZA MIEL B', 'ordering': 14},
            {'value': 'PZA MASA C', 'ordering': 15},
            {'value': 'PZA NUTSCH C', 'ordering': 16},
            {'value': 'PZA MIEL FINAL', 'ordering': 17},
            {'value': 'BX MASA C', 'ordering': 18},
            {'value': 'BX CRISTAL DES', 'ordering': 19},
            {'value': 'BX NUTSCH C', 'ordering': 20},
            {'value': 'BX MASA B', 'ordering': 21},
            {'value': 'BX MASA A', 'ordering': 22},
            {'value': 'BX MAGMA B', 'ordering': 23},
            {'value': 'BX MASA REFINO', 'ordering': 24},
            {'value': 'BX MAGMA C', 'ordering': 25},
            {'value': 'BX MIEL FINAL', 'ordering': 26},
            {'value': 'BX NUTSCH B', 'ordering': 27},
            {'value': 'BX MIEL B', 'ordering': 28},
            {'value': 'BX MIEL A', 'ordering': 29},
            {'value': 'BX LAVADO A', 'ordering': 30},
            {'value': 'BX NUTSCH A', 'ordering': 31},
            {'value': 'BX SIROPE', 'ordering': 32},
            {'value': 'BX DEL LICOR', 'ordering': 33},
            {'value': 'BX MELADURA', 'ordering': 34},
            {'value': 'POL AZUC', 'ordering': 35},
            {'value': 'SOL TOTA HDA AZU', 'ordering': 36}
        ]
        
        # Bulk create
        records = [LaboratoryReportingOrder(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1), **item) for item in default_data]
        LaboratoryReportingOrder.objects.bulk_create(records)
        
        logger.info(f"✅ Inserted {len(default_data)} laboratory reporting order records")
        
        return JsonResponse({
            'ok': True,
            'created': len(default_data),
            'message': 'Laboratory reporting order initialized successfully'
        })
        
    except Exception as e:
        logger.error(f"Error inserting laboratory reporting order: {e}", exc_info=True)
        return JsonResponse({
            'ok': False,
            'error': str(e)
        }, status=500)
