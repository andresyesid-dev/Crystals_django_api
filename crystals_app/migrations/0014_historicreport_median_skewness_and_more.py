from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crystals_app', '0013_alter_laboratorydata_bx_cristal_des_and_more'),
    ]

    operations = [
        # HistoricReport: 4 new float columns for median and skewness
        migrations.AddField(
            model_name='historicreport',
            name='height_median',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
        migrations.AddField(
            model_name='historicreport',
            name='height_skewness',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
        migrations.AddField(
            model_name='historicreport',
            name='width_median',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
        migrations.AddField(
            model_name='historicreport',
            name='width_skewness',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
        # ManagementReportSettings: 2 new integer toggle columns
        migrations.AddField(
            model_name='managementreportsettings',
            name='median_variable',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
        migrations.AddField(
            model_name='managementreportsettings',
            name='skewness_variable',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
    ]
