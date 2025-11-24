from django.urls import path
from .views import (
	activation_view,
	analysiscategory_view,
	auth_view,
	brixcalculatordata_view,
	calibration_view,
	company_view,
	config_view,
	crudocalculation_view,
	crystalsdataparametrization_view,
	crystalsdataparametrizationcv_view,
	crystalsdataparametrizationma_view,
	crystalsdataparametrizationnwparams_view,
	generalreportingorder_view,
	globalsetting_view,
	historicanalysisdata_view,
	historicreport_view,
	labmaterialssettings_view,
	laboratorycalculatedmasaa_parametrization_view,
	laboratorycalculatedmasab_parametrization_view,
	laboratorycalculatedmasac_parametrization_view,
	laboratorycalculatedrefinoparametrization_view,
	laboratorydata_view,
	laboratoryparametrization_view,
	laboratoryreportingorder_view,
	laboratorysettingsexcel_view,
	managementreportlayout_view,
	managementreportsettings_view,
	manualmeasurement_view,
	newparametersanalysiscategory_view,
	processcodedata_view,
	refinocalculation_view,
	security_view,
	specificreportingorder_view,
	user_view,
)
# New default data insertion views
from .views import (
	reporting_order_view,
	laboratory_parametrization_view as lab_param_insert_view,
	laboratory_data_view as lab_data_insert_view,
)

# Authentication and Security URLs
auth_urls = [
	path('auth/login/', auth_view.login, name='login'),
	path('auth/logout/', auth_view.logout, name='logout'),
	path('auth/refresh/', auth_view.refresh_token, name='refresh_token'),
	path('auth/verify/', auth_view.verify_token, name='verify_token'),
	path('auth/profile/', auth_view.user_profile, name='user_profile'),
]

security_urls = [
	path('security/dashboard/', security_view.security_dashboard, name='security_dashboard'),
	path('security/block-ip/', security_view.block_ip_endpoint, name='block_ip'),
	path('security/unblock-ip/', security_view.unblock_ip_endpoint, name='unblock_ip'),
	path('security/logs/', security_view.security_logs, name='security_logs'),
]

# Per-model route lists
activation_urls = [
	path('activation/validate', activation_view.validate_software),
	path('activation/status', activation_view.check_if_software_is_active),
]

analysiscategory_urls = [
	path('analysis-category/add-values', analysiscategory_view.add_analysis_cat_values),
	path('analysis-category/add-new', analysiscategory_view.add_new_parameters_analysis_categories),
	path('analysis-category/get-new', analysiscategory_view.get_new_parameters_analysis_categories),
	path('analysis-category/delete', analysiscategory_view.delete_parameter_analysis_category),
]

brixcalculator_urls = [
	path('brix/data', brixcalculatordata_view.get_brix_calculator_data),
	path('brix/update', brixcalculatordata_view.update_brix_calculator_data),
]

calibration_urls = [
	path('calibration/list', calibration_view.select_calibrations),
	path('calibration/historic', calibration_view.select_historic_reports_calibrations),
	path('calibration/excluded', calibration_view.select_excluded_reports_calibrations),
	path('calibration/active', calibration_view.select_active_calibration),
	path('calibration/activate', calibration_view.set_calibration_as_active),
	path('calibration/create', calibration_view.create_calibration),
	path('calibration/update', calibration_view.update_calibration),
	path('calibration/delete', calibration_view.delete_calibration),
	path('calibration/get', calibration_view.get_calibration),
	path('calibration/update-order', calibration_view.update_calibration_order),
	path('calibration/table-info', calibration_view.get_calibrations_table_info),
	path('calibration/update-table', calibration_view.update_calibration_table),
]

company_urls = [
	path('company/get', company_view.get_company),
	path('company/update-name', company_view.update_company_name),
	path('company/update-logo', company_view.update_company_logo),
]

config_urls = [
	path('config/language/get', config_view.get_language),
	path('config/language/update', config_view.update_language),
	path('config/dop/get', config_view.get_DOP_config),
	path('config/dop/update', config_view.update_DOP_config),
	path('config/calculated-period/get', config_view.get_calculated_data_period),
	path('config/calculated-period/update', config_view.update_calculated_data_period),
]

crudocalculation_urls = [
	path('crudo/get', crudocalculation_view.get_crudo_calculations),
	path('crudo/insert', crudocalculation_view.insert_crudo_calculations),
]

refinocalculation_urls = [
	path('refino/get', refinocalculation_view.get_refino_calculations),
	path('refino/insert', refinocalculation_view.insert_refino_calculations),
]

globalsetting_urls = [
	path('global-settings/line-color/get', globalsetting_view.get_line_color),
	path('global-settings/line-color/update', globalsetting_view.update_line_color),
]

manualmeasurement_urls = [
	path('manual-measurements/list', manualmeasurement_view.select_manual_measurements),
	path('manual-measurements/add', manualmeasurement_view.add_manual_measurement),
	path('manual-measurements/update', manualmeasurement_view.update_manual_measurement),
	path('manual-measurements/clear', manualmeasurement_view.clear_manual_measurement_db),
]

historicreport_urls = [
	path('historic-report/add', historicreport_view.add_historic_report),
	path('historic-report/list', historicreport_view.get_historic_reports),
	path('historic-report/list-by-process', historicreport_view.get_historic_reports_for_process),
	path('historic-report/last', historicreport_view.get_last_report),
	path('historic-report/order-of-last', historicreport_view.get_order_last_report),
	path('historic-report/delete-last', historicreport_view.delete_last_report_db),
	path('historic-report/delete-management', historicreport_view.delete_management_record),
]

historicanalysisdata_urls = [
	path('historic-analysis/add', historicanalysisdata_view.add_historic_analysis_data),
	path('historic-analysis/list', historicanalysisdata_view.get_analysis_historic_data),
]

managementreportsettings_urls = [
	path('management-report-settings/get', managementreportsettings_view.get_management_report_settings),
	path('management-report-settings/insert', managementreportsettings_view.insert_management_report_settings),
	path('management-report-settings/update', managementreportsettings_view.update_management_report_settings),
	path('management-report-settings/insert-default', managementreportsettings_view.insert_default_management_report_settings),
]

reportingorder_general_urls = [
	path('reporting-order/general/get', generalreportingorder_view.get_general_headers_ordering),
	path('reporting-order/general/update', generalreportingorder_view.update_general_headers_order),
]

reportingorder_specific_urls = [
	path('reporting-order/specific/get', specificreportingorder_view.get_specific_headers_ordering),
	path('reporting-order/specific/update', specificreportingorder_view.update_specific_headers_order),
	path('reporting-order/specific/insert-single', specificreportingorder_view.insert_new_parameter_single_val),
]

reportingorder_laboratory_urls = [
	path('reporting-order/laboratory/get', laboratoryreportingorder_view.get_laboratory_headers_ordering),
	path('reporting-order/laboratory/update', laboratoryreportingorder_view.update_laboratory_headers_order),
]

brixcalc_urls = [
	path('brix-calc/get', brixcalculatordata_view.get_brix_calculator_data),
	path('brix-calc/update', brixcalculatordata_view.update_brix_calculator_data),
]

processcode_urls = [
	path('process-code/get', processcodedata_view.get_process_code_data),
	path('process-code/update', processcodedata_view.update_process_code_data),
]

laboratoryparametrization_urls = [
	path('lab-param/get', laboratoryparametrization_view.get_laboratory_parametrization),
	path('lab-param/update', laboratoryparametrization_view.update_laboratory_parametrization),
]

lab_calculated_refino_urls = [
	path('lab-param-calc/refino/get', laboratorycalculatedrefinoparametrization_view.get_laboratory_calculated_refino_parametrization),
	path('lab-param-calc/refino/update', laboratorycalculatedrefinoparametrization_view.update_laboratory_calculated_refino_parametrization),
]

lab_calculated_masaa_urls = [
	path('lab-param-calc/masa-a/get', laboratorycalculatedmasaa_parametrization_view.get_laboratory_calculated_masa_a_parametrization),
	path('lab-param-calc/masa-a/update', laboratorycalculatedmasaa_parametrization_view.update_laboratory_calculated_masa_a_parametrization),
]

lab_calculated_masab_urls = [
	path('lab-param-calc/masa-b/get', laboratorycalculatedmasab_parametrization_view.get_laboratory_calculated_masa_b_parametrization),
	path('lab-param-calc/masa-b/update', laboratorycalculatedmasab_parametrization_view.update_laboratory_calculated_masa_b_parametrization),
]

lab_calculated_masac_urls = [
	path('lab-param-calc/masa-c/get', laboratorycalculatedmasac_parametrization_view.get_laboratory_calculated_masa_c_parametrization),
	path('lab-param-calc/masa-c/update', laboratorycalculatedmasac_parametrization_view.update_laboratory_calculated_masa_c_parametrization),
]

crystals_param_urls = [
	path('crystals-param/get', crystalsdataparametrization_view.get_crystals_data_parametrization),
	path('crystals-param/update', crystalsdataparametrization_view.update_crystals_data_parametrization),
	path('crystals-param/exist', crystalsdataparametrization_view.exist_parameter_crystals_data_parametrization),
]

crystals_param_new_urls = [
	path('crystals-param-new/get', crystalsdataparametrizationnwparams_view.get_crystals_data_parametrization_nw_params),
	path('crystals-param-new/update', crystalsdataparametrizationnwparams_view.update_crystals_data_parametrization_nw_params),
	path('crystals-param-new/add', crystalsdataparametrizationnwparams_view.add_new_newprms_parameters),
]

crystals_param_ma_urls = [
	path('crystals-param-ma/get', crystalsdataparametrizationma_view.get_crystals_data_parametrization_ma),
	path('crystals-param-ma/update', crystalsdataparametrizationma_view.update_crystals_data_parametrization_ma),
	path('crystals-param-ma/update-specific', crystalsdataparametrizationma_view.update_specific_parametrization_ma),
	path('crystals-param-ma/add', crystalsdataparametrizationma_view.add_new_ma_parameters),
]

crystals_param_cv_urls = [
	path('crystals-param-cv/get', crystalsdataparametrizationcv_view.get_crystals_data_parametrization_cv),
	path('crystals-param-cv/update', crystalsdataparametrizationcv_view.update_crystals_data_parametrization_cv),
	path('crystals-param-cv/update-specific', crystalsdataparametrizationcv_view.update_specific_parametrization_cv),
	path('crystals-param-cv/add', crystalsdataparametrizationcv_view.add_new_cv_parameters),
]

lab_materials_settings_urls = [
	path('lab-materials/get', labmaterialssettings_view.get_lab_materials_settings),
	path('lab-materials/insert', labmaterialssettings_view.insert_lab_materials_settings),
	path('lab-materials/update', labmaterialssettings_view.update_lab_materials_settings),
]

management_report_layout_urls = [
	path('management-report-layout/get', managementreportlayout_view.get_management_report_layout),
	path('management-report-layout/tab', managementreportlayout_view.get_tab_management_report_layout),
	path('management-report-layout/insert', managementreportlayout_view.insert_management_report_layout),
	path('management-report-layout/update', managementreportlayout_view.update_management_report_layout),
	path('management-report-layout/defaults', managementreportlayout_view.set_default_management_report_layout),
	path('management-report-layout/insert-default', managementreportlayout_view.insert_default_management_report_layout),
]

laboratory_settings_excel_urls = [
	path('lab-excel/get-letters', laboratorysettingsexcel_view.get_laboratory_settings_excel_letters),
	path('lab-excel/get-numbers', laboratorysettingsexcel_view.get_laboratory_settings_excel_numbers),
	path('lab-excel/update', laboratorysettingsexcel_view.update_laboratory_settings_excel),
]

laboratory_data_urls = [
	path('lab-data/get', laboratorydata_view.get_laboratory_data),
	path('lab-data/update', laboratorydata_view.update_laboratory_data),
	path('lab-data/add', laboratorydata_view.add_laboratory_data),
	path('lab-data/historic', laboratorydata_view.get_historic_laboratory_data),
	path('lab-data/delete', laboratorydata_view.delete_laboratory_data_record),
]

user_urls = [
	path('user/validate', user_view.validate_user_credentials),
	path('user/create', user_view.create_user),
]

# Default data insertion URLs
default_data_urls = [
	# Reporting order tables
	path('reporting-order/specific/insert', reporting_order_view.insert_specific_reporting_order),
	path('reporting-order/general/insert', reporting_order_view.insert_general_reporting_order),
	path('reporting-order/laboratory/insert', reporting_order_view.insert_laboratory_reporting_order),
	
	# Laboratory parametrization tables
	path('laboratory-parametrization/insert', lab_param_insert_view.insert_laboratory_parametrization),
	path('laboratory-parametrization/refino/insert', lab_param_insert_view.insert_laboratory_calculated_refino),
	path('laboratory-parametrization/masa-a/insert', lab_param_insert_view.insert_laboratory_calculated_masa_a),
	path('laboratory-parametrization/masa-b/insert', lab_param_insert_view.insert_laboratory_calculated_masa_b),
	path('laboratory-parametrization/masa-c/insert', lab_param_insert_view.insert_laboratory_calculated_masa_c),
	path('crystals-parametrization/insert', lab_param_insert_view.insert_crystals_data_parametrization),
	
	# Laboratory data default record
	path('laboratory-data/insert-default', lab_data_insert_view.insert_laboratory_data_default),
]

urlpatterns = (
	auth_urls
	+ security_urls
	+ activation_urls
	+ analysiscategory_urls
	+ brixcalculator_urls
	+ calibration_urls
	+ company_urls
	+ config_urls
	+ crudocalculation_urls
	+ refinocalculation_urls
	+ globalsetting_urls
	+ manualmeasurement_urls
	+ historicreport_urls
	+ historicanalysisdata_urls
	+ managementreportsettings_urls
	+ reportingorder_general_urls
	+ reportingorder_specific_urls
	+ reportingorder_laboratory_urls
	+ brixcalc_urls
	+ processcode_urls
	+ laboratoryparametrization_urls
	+ lab_calculated_refino_urls
	+ lab_calculated_masaa_urls
	+ lab_calculated_masab_urls
	+ lab_calculated_masac_urls
	+ crystals_param_urls
	+ crystals_param_new_urls
	+ crystals_param_ma_urls
	+ crystals_param_cv_urls
	+ lab_materials_settings_urls
	+ management_report_layout_urls
	+ laboratory_settings_excel_urls
	+ laboratory_data_urls
	+ user_urls
	+ default_data_urls
)
