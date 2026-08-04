# Generated for enable_aditional_ranges feature

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crystals_app', '0019_error_log'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnableAditionalRanges',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calibration', models.CharField(max_length=50)),
                ('enable', models.IntegerField(default=1)),
                ('factory_id', models.IntegerField(default=1)),
            ],
            options={
                'db_table': 'enable_aditional_ranges',
                'managed': True,
            },
        ),
    ]
