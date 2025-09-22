from django.db import models


class Calibration(models.Model):
	name = models.CharField(max_length=20, unique=True)
	pixels_per_metric = models.FloatField()
	metric_name = models.CharField(max_length=5)
	range = models.CharField(max_length=50)
	active = models.IntegerField(default=0)
	powder = models.CharField(max_length=50, null=True, blank=True)

	class Meta:
		db_table = 'calibrations'
		managed = False


class User(models.Model):
	username = models.CharField(max_length=20, unique=True)
	password = models.CharField(max_length=50)

	class Meta:
		db_table = 'users'
		managed = False


class Config(models.Model):
	key = models.CharField(max_length=3, unique=True)
	value = models.CharField(max_length=20)

	class Meta:
		db_table = 'config'
		managed = False


class Company(models.Model):
	name = models.CharField(max_length=20, unique=True)
	logo = models.CharField(max_length=50)

	class Meta:
		db_table = 'company'
		managed = False


class ManualMeasurement(models.Model):
	time = models.CharField(max_length=50)
	value = models.CharField(max_length=50)

	class Meta:
		db_table = 'manual_measurements'
		managed = False


class HistoricReport(models.Model):
	datetime = models.CharField(max_length=50)
	calibration = models.CharField(max_length=20)
	correlation = models.FloatField()
	width_min = models.FloatField()
	width_max = models.FloatField()
	width_sd = models.FloatField()
	width_cv = models.FloatField()
	width_mean = models.FloatField()
	width_sum = models.FloatField()
	width_samples = models.FloatField()
	width_range = models.FloatField()
	height_min = models.FloatField()
	height_max = models.FloatField()
	height_sd = models.FloatField()
	height_cv = models.FloatField()
	height_mean = models.FloatField()
	height_sum = models.FloatField()
	height_samples = models.FloatField()
	height_range = models.FloatField()
	calibration_fk = models.ForeignKey(
		Calibration, on_delete=models.CASCADE, db_column='calibration_id'
	)

	class Meta:
		db_table = 'historic_reports'
		managed = False


class GlobalSetting(models.Model):
	line_color = models.CharField(max_length=7)

	class Meta:
		db_table = 'global_settings'
		managed = False


class Activation(models.Model):
	validation_code = models.CharField(max_length=50)
	validated = models.IntegerField()

	class Meta:
		db_table = 'activation'
		managed = False


class HistoricAnalysisData(models.Model):
	historic_report = models.ForeignKey(
		HistoricReport, on_delete=models.CASCADE, db_column='historic_reports_id'
	)
	range_class = models.CharField(max_length=20)
	object_length = models.FloatField()
	pct_object_length = models.FloatField()
	mean_object_length = models.FloatField()
	object_width = models.FloatField()
	pct_object_width = models.FloatField()
	mean_object_width = models.FloatField()
	long_crystals = models.FloatField(null=True, blank=True)

	class Meta:
		db_table = 'historic_analysis_data'
		managed = False


class ManagementReportSettings(models.Model):
	mean_variable = models.IntegerField()
	cv_variable = models.IntegerField()
	perc_fino = models.IntegerField()
	perc_peq = models.IntegerField()
	perc_opt = models.IntegerField()
	perc_gran = models.IntegerField()
	perc_muygran = models.IntegerField()
	rel_la = models.IntegerField()
	perc_crst_alarg = models.IntegerField()
	pza_licor = models.IntegerField()
	pza_sirope = models.IntegerField()
	pza_masa_refino = models.IntegerField()
	pza_magma_b = models.IntegerField()
	pza_meladura = models.IntegerField()
	pza_masa_a = models.IntegerField()
	pza_lavado_a = models.IntegerField()
	pza_nutsch_a = models.IntegerField()
	pza_magma_c = models.IntegerField()
	pza_miel_a = models.IntegerField()
	pza_masa_b = models.IntegerField()
	pza_nutsch_b = models.IntegerField()
	pza_cr_des = models.IntegerField()
	pza_miel_b = models.IntegerField()
	pza_masa_c = models.IntegerField()
	pza_nutsch_c = models.IntegerField()
	pza_miel_final = models.IntegerField()
	bx_masa_c = models.IntegerField()
	bx_cristal_des = models.IntegerField()
	bx_nutsch_c = models.IntegerField()
	bx_masa_b = models.IntegerField()
	bx_masa_a = models.IntegerField()
	bx_magma_b = models.IntegerField()
	bx_masa_refino = models.IntegerField()
	bx_magma_c = models.IntegerField()
	bx_miel_final = models.IntegerField()
	bx_nutsch_b = models.IntegerField()
	bx_miel_b = models.IntegerField()
	bx_miel_a = models.IntegerField()
	bx_lavado_a = models.IntegerField()
	bx_nutsch_a = models.IntegerField()
	bx_sirope = models.IntegerField()
	bx_del_licor = models.IntegerField()
	bx_meladura = models.IntegerField()
	pol_azuc = models.IntegerField()
	sol_tota_hda_azu = models.IntegerField()
	rel_la_grapgh = models.IntegerField()

	class Meta:
		db_table = 'management_report_settings'
		managed = False


class AnalysisCategory(models.Model):
	historic_report = models.ForeignKey(
		HistoricReport, on_delete=models.CASCADE, db_column='historic_reports_id'
	)
	batch_number = models.CharField(max_length=20)
	username = models.CharField(max_length=20)
	baking_time = models.IntegerField(null=True, blank=True)
	mass_number = models.IntegerField(null=True, blank=True)

	class Meta:
		db_table = 'analysis_categories'
		managed = False


class NewParametersAnalysisCategory(models.Model):
	parameter = models.CharField(max_length=30)
	type = models.CharField(max_length=20)

	class Meta:
		db_table = 'new_parameters_analysis_categories'
		managed = False


class CrudoCalculation(models.Model):
	ti = models.IntegerField(null=True, blank=True)
	ft3_per_templa = models.IntegerField(null=True, blank=True)
	bx_masa_c = models.IntegerField(null=True, blank=True, db_column='bx_masa__c')
	no_templas = models.IntegerField(null=True, blank=True)
	porcentaje_cristales = models.IntegerField(null=True, blank=True)
	tamano_final_polv = models.IntegerField(null=True, blank=True)
	concentracion_slurry = models.IntegerField(null=True, blank=True)
	alcohol_slurry = models.IntegerField(null=True, blank=True)
	densidad_slurry = models.IntegerField(null=True, blank=True)

	class Meta:
		db_table = 'crudo_calculations'
		managed = False


class RefinoCalculation(models.Model):
	am_azucar = models.IntegerField(null=True, blank=True)
	temperatura = models.IntegerField(null=True, blank=True)
	volumen_tacho = models.IntegerField(null=True, blank=True)
	densidad_grano = models.IntegerField(null=True, blank=True)
	rendimiento_solidos = models.IntegerField(null=True, blank=True)
	concentracion_masacocida = models.IntegerField(null=True, blank=True)
	am_semilla_lock = models.IntegerField(null=True, blank=True)
	concentracion_slurry = models.IntegerField(null=True, blank=True)
	alcohol_slurry = models.IntegerField(null=True, blank=True)
	densidad_slurry = models.IntegerField(null=True, blank=True)

	class Meta:
		db_table = 'refino_calculations'
		managed = False


class SpecificReportingOrder(models.Model):
	value = models.CharField(max_length=25, null=True, blank=True)
	ordering = models.IntegerField(null=True, blank=True)

	class Meta:
		db_table = 'specific_reporting_order'
		managed = False


class GeneralReportingOrder(models.Model):
	value = models.CharField(max_length=25, null=True, blank=True)
	ordering = models.IntegerField(null=True, blank=True)

	class Meta:
		db_table = 'general_reporting_order'
		managed = False


class LaboratoryReportingOrder(models.Model):
	value = models.CharField(max_length=25, null=True, blank=True)
	ordering = models.IntegerField(null=True, blank=True)

	class Meta:
		db_table = 'laboratory_reporting_order'
		managed = False


class LaboratoryParametrization(models.Model):
	material = models.CharField(max_length=50)
	categoria = models.CharField(max_length=20)
	range_from = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	range_to = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

	class Meta:
		db_table = 'laboratory_parametrization'
		managed = False


class LaboratoryCalculatedRefinoParametrization(models.Model):
	parameter = models.CharField(max_length=50)
	categoria = models.CharField(max_length=20)
	range_from = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	range_to = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

	class Meta:
		db_table = 'laboratory_calculated_refino_parametrization'
		managed = False


class LaboratoryCalculatedMasaAParametrization(models.Model):
	parameter = models.CharField(max_length=50)
	categoria = models.CharField(max_length=20)
	range_from = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	range_to = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

	class Meta:
		db_table = 'laboratory_calculated_masa_a_parametrization'
		managed = False


class LaboratoryCalculatedMasaBParametrization(models.Model):
	parameter = models.CharField(max_length=50)
	categoria = models.CharField(max_length=20)
	range_from = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	range_to = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

	class Meta:
		db_table = 'laboratory_calculated_masa_b_parametrization'
		managed = False


class LaboratoryCalculatedMasaCParametrization(models.Model):
	parameter = models.CharField(max_length=50)
	categoria = models.CharField(max_length=20)
	range_from = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	range_to = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

	class Meta:
		db_table = 'laboratory_calculated_masa_c_parametrization'
		managed = False


class CrystalsDataParametrization(models.Model):
	parameter = models.CharField(max_length=50)
	categoria = models.CharField(max_length=20)
	range_from = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	range_to = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

	class Meta:
		db_table = 'crystals_data_parametrization'
		managed = False


class CrystalsDataParametrizationNewParams(models.Model):
	parameter = models.CharField(max_length=50)
	categoria = models.CharField(max_length=20)
	range_from = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	range_to = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

	class Meta:
		db_table = 'crystals_data_parametrization_nw_params'
		managed = False


class CrystalsDataParametrizationMA(models.Model):
	parameter = models.CharField(max_length=50)
	categoria = models.CharField(max_length=20)
	tolerance = models.IntegerField(null=True, blank=True)
	range_from = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	range_to = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

	class Meta:
		db_table = 'crystals_data_parametrization_ma'
		managed = False


class CrystalsDataParametrizationCV(models.Model):
	parameter = models.CharField(max_length=50)
	categoria = models.CharField(max_length=20)
	tolerance = models.IntegerField(null=True, blank=True)
	range_from = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	range_to = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

	class Meta:
		db_table = 'crystals_data_parametrization_cv'
		managed = False


class BrixCalculatorData(models.Model):
	tc = models.FloatField(primary_key=True)
	pureza = models.FloatField()
	ss = models.FloatField()
	brx = models.FloatField()

	class Meta:
		db_table = 'brix_calculator_data'
		managed = False


class ProcessCodeData(models.Model):
	process = models.FloatField(primary_key=True)
	code = models.TextField()

	class Meta:
		db_table = 'process_code_data'
		managed = False


class ManagementReportLayout(models.Model):
	screen_number = models.IntegerField()
	row = models.IntegerField()
	column = models.IntegerField()
	element_id = models.TextField()
	element_type = models.TextField()

	class Meta:
		db_table = 'management_report_layout'
		managed = False


class LabMaterialsSettings(models.Model):
	material = models.CharField(max_length=50)
	visible = models.IntegerField(default=1)

	class Meta:
		db_table = 'lab_materials_settings'
		managed = False


class LaboratorySettingsExcel(models.Model):
	# For each material, two columns: <material>_letter (char1) and <material>_number (int)
	pza_licor_letter = models.CharField(max_length=1, null=True, blank=True)
	pza_licor_number = models.IntegerField(null=True, blank=True)
	pza_sirope_letter = models.CharField(max_length=1, null=True, blank=True)
	pza_sirope_number = models.IntegerField(null=True, blank=True)
	pza_masa_refino_letter = models.CharField(max_length=1, null=True, blank=True)
	pza_masa_refino_number = models.IntegerField(null=True, blank=True)
	pza_magma_b_letter = models.CharField(max_length=1, null=True, blank=True)
	pza_magma_b_number = models.IntegerField(null=True, blank=True)
	pza_meladura_letter = models.CharField(max_length=1, null=True, blank=True)
	pza_meladura_number = models.IntegerField(null=True, blank=True)
	pza_masa_a_letter = models.CharField(max_length=1, null=True, blank=True)
	pza_masa_a_number = models.IntegerField(null=True, blank=True)
	pza_lavado_a_letter = models.CharField(max_length=1, null=True, blank=True)
	pza_lavado_a_number = models.IntegerField(null=True, blank=True)
	pza_nutsch_a_letter = models.CharField(max_length=1, null=True, blank=True)
	pza_nutsch_a_number = models.IntegerField(null=True, blank=True)
	pza_magma_c_letter = models.CharField(max_length=1, null=True, blank=True)
	pza_magma_c_number = models.IntegerField(null=True, blank=True)
	pza_miel_a_letter = models.CharField(max_length=1, null=True, blank=True)
	pza_miel_a_number = models.IntegerField(null=True, blank=True)
	pza_masa_b_letter = models.CharField(max_length=1, null=True, blank=True)
	pza_masa_b_number = models.IntegerField(null=True, blank=True)
	pza_nutsch_b_letter = models.CharField(max_length=1, null=True, blank=True)
	pza_nutsch_b_number = models.IntegerField(null=True, blank=True)
	pza_cr_des_letter = models.CharField(max_length=1, null=True, blank=True)
	pza_cr_des_number = models.IntegerField(null=True, blank=True)
	pza_miel_b_letter = models.CharField(max_length=1, null=True, blank=True)
	pza_miel_b_number = models.IntegerField(null=True, blank=True)
	pza_masa_c_letter = models.CharField(max_length=1, null=True, blank=True)
	pza_masa_c_number = models.IntegerField(null=True, blank=True)
	pza_nutsch_c_letter = models.CharField(max_length=1, null=True, blank=True)
	pza_nutsch_c_number = models.IntegerField(null=True, blank=True)
	pza_miel_final_letter = models.CharField(max_length=1, null=True, blank=True)
	pza_miel_final_number = models.IntegerField(null=True, blank=True)

	bx_masa_c_letter = models.CharField(max_length=1, null=True, blank=True)
	bx_masa_c_number = models.IntegerField(null=True, blank=True)
	bx_cristal_des_letter = models.CharField(max_length=1, null=True, blank=True)
	bx_cristal_des_number = models.IntegerField(null=True, blank=True)
	bx_nutsch_c_letter = models.CharField(max_length=1, null=True, blank=True)
	bx_nutsch_c_number = models.IntegerField(null=True, blank=True)
	bx_masa_b_letter = models.CharField(max_length=1, null=True, blank=True)
	bx_masa_b_number = models.IntegerField(null=True, blank=True)
	bx_masa_a_letter = models.CharField(max_length=1, null=True, blank=True)
	bx_masa_a_number = models.IntegerField(null=True, blank=True)
	bx_magma_b_letter = models.CharField(max_length=1, null=True, blank=True)
	bx_magma_b_number = models.IntegerField(null=True, blank=True)
	bx_masa_refino_letter = models.CharField(max_length=1, null=True, blank=True)
	bx_masa_refino_number = models.IntegerField(null=True, blank=True)
	bx_magma_c_letter = models.CharField(max_length=1, null=True, blank=True)
	bx_magma_c_number = models.IntegerField(null=True, blank=True)
	bx_miel_final_letter = models.CharField(max_length=1, null=True, blank=True)
	bx_miel_final_number = models.IntegerField(null=True, blank=True)
	bx_nutsch_b_letter = models.CharField(max_length=1, null=True, blank=True)
	bx_nutsch_b_number = models.IntegerField(null=True, blank=True)
	bx_miel_b_letter = models.CharField(max_length=1, null=True, blank=True)
	bx_miel_b_number = models.IntegerField(null=True, blank=True)
	bx_miel_a_letter = models.CharField(max_length=1, null=True, blank=True)
	bx_miel_a_number = models.IntegerField(null=True, blank=True)
	bx_lavado_a_letter = models.CharField(max_length=1, null=True, blank=True)
	bx_lavado_a_number = models.IntegerField(null=True, blank=True)
	bx_nutsch_a_letter = models.CharField(max_length=1, null=True, blank=True)
	bx_nutsch_a_number = models.IntegerField(null=True, blank=True)
	bx_sirope_letter = models.CharField(max_length=1, null=True, blank=True)
	bx_sirope_number = models.IntegerField(null=True, blank=True)
	bx_del_licor_letter = models.CharField(max_length=1, null=True, blank=True)
	bx_del_licor_number = models.IntegerField(null=True, blank=True)
	bx_meladura_letter = models.CharField(max_length=1, null=True, blank=True)
	bx_meladura_number = models.IntegerField(null=True, blank=True)
	pol_azuc_letter = models.CharField(max_length=1, null=True, blank=True)
	pol_azuc_number = models.IntegerField(null=True, blank=True)
	sol_tota_hda_azu_letter = models.CharField(max_length=1, null=True, blank=True)
	sol_tota_hda_azu_number = models.IntegerField(null=True, blank=True)

	class Meta:
		db_table = 'laboratory_settings_excel'
		managed = False


class LaboratoryData(models.Model):
	date_and_time = models.CharField(max_length=50, null=True, blank=True)
	pza_licor = models.IntegerField(null=True, blank=True)
	pza_sirope = models.IntegerField(null=True, blank=True)
	pza_masa_refino = models.IntegerField(null=True, blank=True)
	pza_magma_b = models.IntegerField(null=True, blank=True)
	pza_meladura = models.IntegerField(null=True, blank=True)
	pza_masa_a = models.IntegerField(null=True, blank=True)
	pza_lavado_a = models.IntegerField(null=True, blank=True)
	pza_nutsch_a = models.IntegerField(null=True, blank=True)
	pza_magma_c = models.IntegerField(null=True, blank=True)
	pza_miel_a = models.IntegerField(null=True, blank=True)
	pza_masa_b = models.IntegerField(null=True, blank=True)
	pza_nutsch_b = models.IntegerField(null=True, blank=True)
	pza_cr_des = models.IntegerField(null=True, blank=True)
	pza_miel_b = models.IntegerField(null=True, blank=True)
	pza_masa_c = models.IntegerField(null=True, blank=True)
	pza_nutsch_c = models.IntegerField(null=True, blank=True)
	pza_miel_final = models.IntegerField(null=True, blank=True)
	bx_masa_c = models.IntegerField(null=True, blank=True)
	bx_cristal_des = models.IntegerField(null=True, blank=True)
	bx_nutsch_c = models.IntegerField(null=True, blank=True)
	bx_masa_b = models.IntegerField(null=True, blank=True)
	bx_masa_a = models.IntegerField(null=True, blank=True)
	bx_magma_b = models.IntegerField(null=True, blank=True)
	bx_masa_refino = models.IntegerField(null=True, blank=True)
	bx_magma_c = models.IntegerField(null=True, blank=True)
	bx_miel_final = models.IntegerField(null=True, blank=True)
	bx_nutsch_b = models.IntegerField(null=True, blank=True)
	bx_miel_b = models.IntegerField(null=True, blank=True)
	bx_miel_a = models.IntegerField(null=True, blank=True)
	bx_lavado_a = models.IntegerField(null=True, blank=True)
	bx_nutsch_a = models.IntegerField(null=True, blank=True)
	bx_sirope = models.IntegerField(null=True, blank=True)
	bx_del_licor = models.IntegerField(null=True, blank=True)
	bx_meladura = models.IntegerField(null=True, blank=True)
	pol_azuc = models.IntegerField(null=True, blank=True)
	sol_tota_hda_azu = models.IntegerField(null=True, blank=True)

	class Meta:
		db_table = 'laboratory_data'
		managed = False

