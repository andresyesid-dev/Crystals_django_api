"""
Default Data Insertion Views

Endpoints for inserting seed/default data with factory_id support.
All endpoints are idempotent and use factory_id from HTTP header.
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import IntegrityError
from ..models import (
    User, Config, GlobalSetting, Company, Activation,
    ManagementReportLayout, ManagementReportSettings
)
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
def insert_default_users(request):
    """Insert default admin user for the factory."""
    factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
    
    try:
        # Check if admin user exists for this factory
        if User.objects.filter(username='admin', factory_id=factory_id).exists():
            return Response({
                'success': True,
                'created': False,
                'message': 'Admin user already exists'
            })
        
        # Create admin user
        User.objects.create(
            username='admin',
            password='$p5k2$$dYnR.Z1Y$E83bbM0gY6fhiP1sWLUcieTw3ON68FVU',
            factory_id=factory_id
        )
        
        return Response({
            'success': True,
            'created': True,
            'message': 'Admin user created'
        })
    except Exception as e:
        logger.error(f"Error inserting default user: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
def insert_default_config(request):
    """Insert default configuration values for the factory."""
    factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
    
    defaults = [
        {'key': 'language', 'value': 'en'},
        {'key': 'DOP graph divided', 'value': 'on'},
        {'key': 'calculated data period', 'value': 'individual'}
    ]
    
    created_count = 0
    try:
        for item in defaults:
            if not Config.objects.filter(key=item['key'], factory_id=factory_id).exists():
                Config.objects.create(
                    key=item['key'],
                    value=item['value'],
                    factory_id=factory_id
                )
                created_count += 1
        
        return Response({
            'success': True,
            'created': created_count,
            'total': len(defaults)
        })
    except Exception as e:
        logger.error(f"Error inserting default config: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
def insert_default_global_settings(request):
    """Insert default global settings for the factory."""
    factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
    
    try:
        # Check if settings exist for this factory
        if GlobalSetting.objects.filter(factory_id=factory_id).exists():
            return Response({
                'success': True,
                'created': False,
                'message': 'Global settings already exist'
            })
        
        # Create settings
        GlobalSetting.objects.create(
            line_color='#55ffff',
            factory_id=factory_id
        )
        
        return Response({
            'success': True,
            'created': True,
            'message': 'Global settings created'
        })
    except Exception as e:
        logger.error(f"Error inserting default global settings: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
def insert_default_company(request):
    """Insert default company record for the factory."""
    factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
    
    try:
        # Check if company exists for this factory
        if Company.objects.filter(factory_id=factory_id).exists():
            return Response({
                'success': True,
                'created': False,
                'message': 'Company record already exists'
            })
        
        # Create company
        Company.objects.create(
            name='',
            logo='',
            factory_id=factory_id
        )
        
        return Response({
            'success': True,
            'created': True,
            'message': 'Company record created'
        })
    except Exception as e:
        logger.error(f"Error inserting default company: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
def insert_default_activation(request):
    """Insert default activation record for the factory."""
    factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
    validation_code = request.data.get('code', '$p5k2$$lDD.2q8l$FSS9CFIP2YEihV.qk4W1oVD2NO6z3Vzn')
    
    try:
        # Check if activation exists for this factory
        if Activation.objects.filter(factory_id=factory_id).exists():
            return Response({
                'success': True,
                'created': False,
                'message': 'Activation record already exists'
            })
        
        # Create activation
        Activation.objects.create(
            validation_code=validation_code,
            validated=0,
            factory_id=factory_id
        )
        
        return Response({
            'success': True,
            'created': True,
            'message': 'Activation record created'
        })
    except Exception as e:
        logger.error(f"Error inserting default activation: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
def insert_default_mgmt_layout(request):
    """Insert default management report layout for the factory."""
    factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
    
    default_layout = [
        (1, 0, 0, "general_data_table", "table"),
        (1, 0, 1, "mean_line_chart", "graph"),
        (1, 0, 2, "dop_bar_chart", "graph"),
        (1, 1, 0, "specific_data_table", "table"),
        (1, 1, 1, "cv_line_chart", "graph"),
        (2, 0, 0, "general_laboratory_table", "table"),
        (2, 0, 1, "specific_laboratory_table", "table"),
        (2, 0, 2, "calculated_laboratory_data", "table"),
        (2, 1, 0, "fall_of_purity_laboratory_data", "graph"),
        (2, 1, 1, "percentage_of_crystals_per_mass", "graph"),
        (2, 1, 2, "calculated_individual_reports", "table")
    ]
    
    created_count = 0
    try:
        for screen_number, row, column, element_id, element_type in default_layout:
            if not ManagementReportLayout.objects.filter(element_id=element_id, factory_id=factory_id).exists():
                ManagementReportLayout.objects.create(
                    screen_number=screen_number,
                    row=row,
                    column=column,
                    element_id=element_id,
                    element_type=element_type,
                    factory_id=factory_id
                )
                created_count += 1
        
        return Response({
            'success': True,
            'created': created_count,
            'total': len(default_layout)
        })
    except Exception as e:
        logger.error(f"Error inserting default mgmt layout: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
def insert_default_mgmt_settings(request):
    """Insert default management report settings for the factory."""
    factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
    
    try:
        # Check if settings already exist
        if ManagementReportSettings.objects.filter(factory_id=factory_id).exists():
            return Response({
                'success': True,
                'created': False,
                'message': 'Management report settings already exist'
            })
        
        # All fields default to 1
        settings = {
            'factory_id': factory_id,
            'mean_variable': 1,
            'cv_variable': 1,
            'perc_fino': 1,
            'perc_peq': 1,
            'perc_opt': 1,
            'perc_gran': 1,
            'perc_muygran': 1,
            'rel_la': 1,
            'perc_crst_alarg': 1,
            'perc_powder': 1,
            'amount_perc_fino': 1,
            'amount_perc_peq': 1,
            'amount_perc_opt': 1,
            'amount_perc_gran': 1,
            'amount_perc_muy_gran': 1,
            'amount_total': 1,
            'rel_la_grapgh': 1
        }
        
        # Add all material fields
        materials = [
            'pza_licor', 'pza_sirope', 'pza_masa_refino', 'pza_magma_b', 'pza_meladura',
            'pza_masa_a', 'pza_lavado_a', 'pza_nutsch_a', 'pza_magma_c', 'pza_miel_a',
            'pza_masa_b', 'pza_nutsch_b', 'pza_cr_des', 'pza_miel_b', 'pza_masa_c',
            'pza_nutsch_c', 'pza_miel_final', 'bx_masa_c', 'bx_cristal_des', 'bx_nutsch_c',
            'bx_masa_b', 'bx_masa_a', 'bx_magma_b', 'bx_masa_refino', 'bx_magma_c',
            'bx_miel_final', 'bx_nutsch_b', 'bx_miel_b', 'bx_miel_a', 'bx_lavado_a',
            'bx_nutsch_a', 'bx_sirope', 'bx_del_licor', 'bx_meladura', 'pol_azuc',
            'sol_tota_hda_azu'
        ]
        
        for material in materials:
            settings[material] = 1
        
        ManagementReportSettings.objects.create(**settings)
        
        return Response({
            'success': True,
            'created': True,
            'message': 'Management report settings created'
        })
    except Exception as e:
        logger.error(f"Error inserting default mgmt settings: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)
