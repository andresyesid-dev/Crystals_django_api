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
    ManagementReportLayout, ManagementReportSettings,
    SpecificReportingOrder, GeneralReportingOrder, LaboratoryReportingOrder
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
            password='$p5k2$$QDK9VNxv$CDaB6.VfKuEQgMwtaybnDczD93T0.t3N',
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
        
        # Initialize reporting orders as well (since client doesn't call them explicitly)
        _init_reporting_orders(factory_id)
        
        return Response({
            'success': True,
            'created': created_count,
            'total': len(defaults)
        })
    except Exception as e:
        logger.error(f"Error inserting default config: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


def _init_reporting_orders(factory_id):
    """Helper to initialize reporting orders if empty."""
    try:
        # 1. Specific Reporting Order
        if not SpecificReportingOrder.objects.filter(factory_id=factory_id).exists():
            specific_data = [
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
            SpecificReportingOrder.objects.bulk_create([
                SpecificReportingOrder(factory_id=factory_id, **item) for item in specific_data
            ])

        # 2. General Reporting Order
        if not GeneralReportingOrder.objects.filter(factory_id=factory_id).exists():
            general_data = [
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
            GeneralReportingOrder.objects.bulk_create([
                GeneralReportingOrder(factory_id=factory_id, **item) for item in general_data
            ])

        # 3. Laboratory Reporting Order
        if not LaboratoryReportingOrder.objects.filter(factory_id=factory_id).exists():
            lab_data = [
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
            LaboratoryReportingOrder.objects.bulk_create([
                LaboratoryReportingOrder(factory_id=factory_id, **item) for item in lab_data
            ])
    except Exception as e:
        logger.error(f"Error initializing reporting orders: {e}")


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


@api_view(['POST'])
def insert_default_lab_materials_settings(request):
    """Insert default lab materials settings (rows of materials) for the factory."""
    factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
    
    try:
        from ..models import LabMaterialsSettings
        
        # Default materials list (matching client and labmaterialssettings_view.py)
        materials = [
            'licor', 'sirope', 'masa_refino', 'magma_b', 'meladura',
            'masa_a', 'lavado_a', 'nutsch_a', 'magma_c', 'miel_a',
            'masa_b', 'nutsch_b', 'cr_des', 'miel_b', 'masa_c',
            'nutsch_c', 'miel_final', 'pol_azuc', 'sol_tota_hda_azu'
        ]
        
        # Check if settings already exist
        existing = LabMaterialsSettings.objects.filter(factory_id=factory_id)
        if existing.exists():
            # Check if we have the old "pza_" prefixed records and fix them
            pza_records = existing.filter(material__startswith='pza_')
            if pza_records.exists():
                logger.info("Found legacy 'pza_' records. Migrating to standard names...")
                for record in pza_records:
                    new_name = record.material.replace('pza_', '')
                    # Check if the new name is in our target list
                    if new_name in materials:
                        # Check if target already exists (duplicate)
                        if not LabMaterialsSettings.objects.filter(factory_id=factory_id, material=new_name).exists():
                            record.material = new_name
                            record.save()
                        else:
                            # If target exists, just delete the old one
                            record.delete()
                
                # Also clean up any bx_ records if they are not used by client
                existing.filter(material__startswith='bx_').delete()
                
                return Response({
                    'success': True,
                    'created': False,
                    'updated': True,
                    'message': 'Lab materials settings migrated to standard names'
                })

            return Response({
                'success': True,
                'created': False,
                'message': 'Lab materials settings already exist'
            })
        
        created_count = 0
        for material in materials:
            LabMaterialsSettings.objects.create(
                material=material,
                visible=1,
                factory_id=factory_id
            )
            created_count += 1
        
        return Response({
            'success': True,
            'created': True,
            'count': created_count,
            'message': 'Lab materials settings created'
        })
    except Exception as e:
        logger.error(f"Error inserting default lab materials settings: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
def insert_default_lab_settings_excel(request):
    """Insert default laboratory settings excel (single record with '...') for the factory."""
    factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
    
    try:
        from ..models import LaboratorySettingsExcel
        
        # Define defaults
        defaults = {
            'pza_licor_letter': '...', 'pza_licor_number': '...',
            'pza_sirope_letter': '...', 'pza_sirope_number': '...',
            'pza_masa_refino_letter': '...', 'pza_masa_refino_number': '...',
            'pza_magma_b_letter': '...', 'pza_magma_b_number': '...',
            'pza_meladura_letter': '...', 'pza_meladura_number': '...',
            'pza_masa_a_letter': '...', 'pza_masa_a_number': '...',
            'pza_lavado_a_letter': '...', 'pza_lavado_a_number': '...',
            'pza_nutsch_a_letter': '...', 'pza_nutsch_a_number': '...',
            'pza_magma_c_letter': '...', 'pza_magma_c_number': '...',
            'pza_miel_a_letter': '...', 'pza_miel_a_number': '...',
            'pza_masa_b_letter': '...', 'pza_masa_b_number': '...',
            'pza_nutsch_b_letter': '...', 'pza_nutsch_b_number': '...',
            'pza_cr_des_letter': '...', 'pza_cr_des_number': '...',
            'pza_miel_b_letter': '...', 'pza_miel_b_number': '...',
            'pza_masa_c_letter': '...', 'pza_masa_c_number': '...',
            'pza_nutsch_c_letter': '...', 'pza_nutsch_c_number': '...',
            'pza_miel_final_letter': '...', 'pza_miel_final_number': '...',
            'bx_masa_c_letter': '...', 'bx_masa_c_number': '...',
            'bx_cristal_des_letter': '...', 'bx_cristal_des_number': '...',
            'bx_nutsch_c_letter': '...', 'bx_nutsch_c_number': '...',
            'bx_masa_b_letter': '...', 'bx_masa_b_number': '...',
            'bx_masa_a_letter': '...', 'bx_masa_a_number': '...',
            'bx_magma_b_letter': '...', 'bx_magma_b_number': '...',
            'bx_masa_refino_letter': '...', 'bx_masa_refino_number': '...',
            'bx_magma_c_letter': '...', 'bx_magma_c_number': '...',
            'bx_miel_final_letter': '...', 'bx_miel_final_number': '...',
            'bx_nutsch_b_letter': '...', 'bx_nutsch_b_number': '...',
            'bx_miel_b_letter': '...', 'bx_miel_b_number': '...',
            'bx_miel_a_letter': '...', 'bx_miel_a_number': '...',
            'bx_lavado_a_letter': '...', 'bx_lavado_a_number': '...',
            'bx_nutsch_a_letter': '...', 'bx_nutsch_a_number': '...',
            'bx_sirope_letter': '...', 'bx_sirope_number': '...',
            'bx_del_licor_letter': '...', 'bx_del_licor_number': '...',
            'bx_meladura_letter': '...', 'bx_meladura_number': '...',
            'pol_azuc_letter': '...', 'pol_azuc_number': '...',
            'sol_tota_hda_azu_letter': '...', 'sol_tota_hda_azu_number': '...',
            'factory_id': factory_id
        }

        # Check if settings already exist
        obj = LaboratorySettingsExcel.objects.filter(factory_id=factory_id).first()
        
        if obj:
            # If exists but has NULL values (e.g. pza_licor_letter is None or empty), update it
            if not obj.pza_licor_letter or obj.pza_licor_letter == "":
                for key, value in defaults.items():
                    setattr(obj, key, value)
                obj.save()
                return Response({
                    'success': True,
                    'created': False,
                    'updated': True,
                    'message': 'Laboratory settings excel updated with defaults (fixed NULLs)'
                })
            
            return Response({
                'success': True,
                'created': False,
                'message': 'Laboratory settings excel already exist and are valid'
            })

        # Create default record
        # We try to force id=0, but if it fails we let DB decide
        defaults['id'] = 0
        LaboratorySettingsExcel.objects.create(**defaults)
        
        return Response({
            'success': True,
            'created': True,
            'message': 'Laboratory settings excel created with defaults'
        })
    except Exception as e:
        logger.error(f"Error inserting default lab settings excel: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
def insert_default_crystals_data_parametrization(request):
    """Insert default crystals data parametrization for the factory."""
    factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
    
    try:
        from ..models import CrystalsDataParametrization
        
        # Check if settings already exist
        if CrystalsDataParametrization.objects.filter(factory_id=factory_id).exists():
            return Response({
                'success': True,
                'created': False,
                'message': 'Crystals data parametrization already exists'
            })
            
        parameters = [
            "%_fino.",
            "%_peq.",
            "%_opt.",
            "%_gran.",
            "%_muy_gran.",
            "rel._l/a",
            "%_crist._alarg",
        ]
        categories = ["Good", "Regular", "Bad"]
        
        created_count = 0
        for parameter in parameters:
            for category in categories:
                CrystalsDataParametrization.objects.create(
                    parameter=parameter,
                    categoria=category,
                    range_from=0,
                    range_to=0,
                    factory_id=factory_id
                )
                created_count += 1
        
        return Response({
            'success': True,
            'created': True,
            'count': created_count,
            'message': 'Crystals data parametrization created'
        })
    except Exception as e:
        logger.error(f"Error inserting default crystals data parametrization: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)




@api_view(['POST'])
def insert_default_laboratory_parametrization(request):
    """Insert default laboratory parametrization for the factory."""
    factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
    
    try:
        from ..models import LaboratoryParametrization
        
        # Check if settings already exist
        if LaboratoryParametrization.objects.filter(factory_id=factory_id).exists():
            return Response({
                'success': True,
                'created': False,
                'message': 'Laboratory parametrization already exists'
            })
            
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
        categories = ["Good", "Regular", "Bad"]
        
        created_count = 0
        batch = []
        for material in materials:
            for category in categories:
                batch.append(LaboratoryParametrization(
                    material=material,
                    categoria=category,
                    range_from=0,
                    range_to=0,
                    factory_id=factory_id
                ))
                created_count += 1
        
        LaboratoryParametrization.objects.bulk_create(batch)
        
        return Response({
            'success': True,
            'created': True,
            'count': created_count,
            'message': 'Laboratory parametrization created'
        })
    except Exception as e:
        logger.error(f"Error inserting default laboratory parametrization: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
def insert_default_laboratory_calculated_refino_parametrization(request):
    """Insert default laboratory calculated refino parametrization."""
    factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
    try:
        from ..models import LaboratoryCalculatedRefinoParametrization
        if LaboratoryCalculatedRefinoParametrization.objects.filter(factory_id=factory_id).exists():
            return Response({'success': True, 'created': False, 'message': 'Already exists'})
            
        parameters = ["caida", "rendimientos", "%_cristales", "agotamientos"]
        categories = ["Good", "Regular", "Bad"]
        batch = [
            LaboratoryCalculatedRefinoParametrization(
                parameter=p, categoria=c, range_from=0, range_to=0, factory_id=factory_id
            ) for p in parameters for c in categories
        ]
        LaboratoryCalculatedRefinoParametrization.objects.bulk_create(batch)
        return Response({'success': True, 'created': True, 'count': len(batch)})
    except Exception as e:
        logger.error(f"Error inserting default refino param: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
def insert_default_laboratory_calculated_masa_a_parametrization(request):
    """Insert default laboratory calculated masa a parametrization."""
    factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
    try:
        from ..models import LaboratoryCalculatedMasaAParametrization
        if LaboratoryCalculatedMasaAParametrization.objects.filter(factory_id=factory_id).exists():
            return Response({'success': True, 'created': False, 'message': 'Already exists'})
            
        parameters = ["caida", "rendimientos", "%_cristales", "agotamientos"]
        categories = ["Good", "Regular", "Bad"]
        batch = [
            LaboratoryCalculatedMasaAParametrization(
                parameter=p, categoria=c, range_from=0, range_to=0, factory_id=factory_id
            ) for p in parameters for c in categories
        ]
        LaboratoryCalculatedMasaAParametrization.objects.bulk_create(batch)
        return Response({'success': True, 'created': True, 'count': len(batch)})
    except Exception as e:
        logger.error(f"Error inserting default masa a param: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
def insert_default_laboratory_calculated_masa_b_parametrization(request):
    """Insert default laboratory calculated masa b parametrization."""
    factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
    try:
        from ..models import LaboratoryCalculatedMasaBParametrization
        if LaboratoryCalculatedMasaBParametrization.objects.filter(factory_id=factory_id).exists():
            return Response({'success': True, 'created': False, 'message': 'Already exists'})
            
        parameters = ["caida", "rendimientos", "%_cristales", "agotamientos"]
        categories = ["Good", "Regular", "Bad"]
        batch = [
            LaboratoryCalculatedMasaBParametrization(
                parameter=p, categoria=c, range_from=0, range_to=0, factory_id=factory_id
            ) for p in parameters for c in categories
        ]
        LaboratoryCalculatedMasaBParametrization.objects.bulk_create(batch)
        return Response({'success': True, 'created': True, 'count': len(batch)})
    except Exception as e:
        logger.error(f"Error inserting default masa b param: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
def insert_default_laboratory_calculated_masa_c_parametrization(request):
    """Insert default laboratory calculated masa c parametrization."""
    factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
    try:
        from ..models import LaboratoryCalculatedMasaCParametrization
        if LaboratoryCalculatedMasaCParametrization.objects.filter(factory_id=factory_id).exists():
            return Response({'success': True, 'created': False, 'message': 'Already exists'})
            
        parameters = ["caida", "rendimientos", "%_cristales", "agotamientos"]
        categories = ["Good", "Regular", "Bad"]
        batch = [
            LaboratoryCalculatedMasaCParametrization(
                parameter=p, categoria=c, range_from=0, range_to=0, factory_id=factory_id
            ) for p in parameters for c in categories
        ]
        LaboratoryCalculatedMasaCParametrization.objects.bulk_create(batch)
        return Response({'success': True, 'created': True, 'count': len(batch)})
    except Exception as e:
        logger.error(f"Error inserting default masa c param: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
def insert_default_laboratory_data(request):
    """Insert default laboratory data (single record with '...') for the factory."""
    factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
    
    try:
        from ..models import LaboratoryData
        
        # Check if data already exists
        if LaboratoryData.objects.filter(factory_id=factory_id).exists():
            return Response({
                'success': True,
                'created': False,
                'message': 'Laboratory data already exists'
            })
            
        # Define fields to populate with "..."
        fields = [
            'date_and_time',
            'pza_licor', 'pza_sirope', 'pza_masa_refino', 'pza_magma_b', 'pza_meladura',
            'pza_masa_a', 'pza_lavado_a', 'pza_nutsch_a', 'pza_magma_c', 'pza_miel_a',
            'pza_masa_b', 'pza_nutsch_b', 'pza_cr_des', 'pza_miel_b', 'pza_masa_c',
            'pza_nutsch_c', 'pza_miel_final', 'bx_masa_c', 'bx_cristal_des', 'bx_nutsch_c',
            'bx_masa_b', 'bx_masa_a', 'bx_magma_b', 'bx_masa_refino', 'bx_magma_c',
            'bx_miel_final', 'bx_nutsch_b', 'bx_miel_b', 'bx_miel_a', 'bx_lavado_a',
            'bx_nutsch_a', 'bx_sirope', 'bx_del_licor', 'bx_meladura', 'pol_azuc',
            'sol_tota_hda_azu'
        ]
        
        data = {field: '...' for field in fields}
        data['factory_id'] = factory_id
        
        LaboratoryData.objects.create(**data)
        
        return Response({
            'success': True,
            'created': True,
            'message': 'Laboratory data created with default values'
        })
    except Exception as e:
        logger.error(f"Error inserting default laboratory data: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
def insert_default_brix_calculator(request):
    """Insert default brix calculator data (temperatures 60.0-70.0)."""
    factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
    
    try:
        from ..models import BrixCalculatorData
        
        # Check if data already exists
        if BrixCalculatorData.objects.filter(factory_id=factory_id).exists():
            return Response({
                'success': True,
                'created': False,
                'message': 'Brix calculator data already exists'
            })
            
        # Range 60.0 to 70.0 with step 0.25 -> 41 items
        items = []
        val = 60.0
        while val <= 70.01:
             items.append(round(val, 2))
             val += 0.25
        
        batch = [
            BrixCalculatorData(
                tc=tc, pureza=0, ss=0, brx=0, factory_id=factory_id
            ) for tc in items
        ]
        
        BrixCalculatorData.objects.bulk_create(batch)
        
        return Response({
            'success': True,
            'created': True,
            'count': len(batch),
            'message': 'Default brix calculator data inserted'
        })
    except Exception as e:
        logger.error(f"Error inserting default brix calc data: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)
