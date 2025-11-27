"""
Views for managing laboratory data
"""
from rest_framework.decorators import api_view
from crystals_app.decorators import jwt_required
from django.http import JsonResponse
from crystals_app.models import LaboratoryData
import logging

logger = logging.getLogger('crystals_api')


@api_view(['POST'])
@jwt_required
def insert_laboratory_data_default(request):
    """
    Insert default laboratory data record with id=0 and all material fields as null.
    Only inserts if table is empty.
    """
    try:
        # Check if table already has data
        count = LaboratoryData.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).count()
        if count > 0:
            return JsonResponse({
                'ok': True,
                'already_exists': True,
                'count': count,
                'message': 'Laboratory data already has records'
            })
        
        # Create record with id=0 and all materials as null
        # Django ORM doesn't allow explicit id=0 in PostgreSQL easily,
        # so we create the first record and it will get id=1
        # If you specifically need id=0, we'd need to use raw SQL
        default_record = LaboratoryData.objects.create(
            date_and_time=None,
            factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)
            # All 36 material fields are already null by default (blank=True, null=True)
        )
        
        logger.info(f"✅ Inserted default laboratory data record with id={default_record.id}")
        
        return JsonResponse({
            'ok': True,
            'created': 1,
            'record_id': default_record.id,
            'message': 'Laboratory data default record initialized successfully'
        })
        
    except Exception as e:
        logger.error(f"Error inserting laboratory data default record: {e}", exc_info=True)
        return JsonResponse({
            'ok': False,
            'error': str(e)
        }, status=500)
