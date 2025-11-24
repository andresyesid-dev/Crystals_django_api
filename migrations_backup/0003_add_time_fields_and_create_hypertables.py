# Generated manually for TimescaleDB hypertables

from django.db import migrations, models
import django.utils.timezone


def create_hypertables(apps, schema_editor):
    """Convierte las tablas en hipertablas de TimescaleDB"""
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            # Crear extensión TimescaleDB si no existe
            try:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
                print("✅ Extensión TimescaleDB habilitada")
            except Exception as e:
                print(f"⚠️  Error al crear extensión TimescaleDB: {e}")
                return
            
            # Para TimescaleDB, necesitamos eliminar la constraint de primary key
            # y recrearla incluyendo la columna time
            hypertables_config = [
                ('analysis_categories', 'time'),
                ('historic_analysis_data', 'time'),
                ('historic_reports', 'time'),
                ('laboratory_data', 'time'),
                ('numero', 'time'),
                ('analysis_results', 'time')
            ]
            
            for table, time_column in hypertables_config:
                try:
                    # Obtener el nombre de la constraint de primary key
                    cursor.execute(f"""
                        SELECT constraint_name 
                        FROM information_schema.table_constraints 
                        WHERE table_name = '{table}' 
                        AND constraint_type = 'PRIMARY KEY';
                    """)
                    pk_constraint = cursor.fetchone()
                    
                    if pk_constraint:
                        pk_name = pk_constraint[0]
                        # Eliminar el primary key constraint (con CASCADE si es necesario)
                        cursor.execute(f"ALTER TABLE {table} DROP CONSTRAINT {pk_name} CASCADE;")
                        # Crear un nuevo primary key compuesto con id y time
                        cursor.execute(f"ALTER TABLE {table} ADD PRIMARY KEY (id, {time_column});")
                        print(f"✅ Primary key actualizada para {table}")
                    
                    # Crear la hipertabla
                    cursor.execute(f"""
                        SELECT create_hypertable(
                            '{table}', 
                            '{time_column}', 
                            if_not_exists => TRUE,
                            migrate_data => TRUE
                        );
                    """)
                    print(f"✅ Hipertabla creada: {table}")
                    
                except Exception as e:
                    print(f"⚠️  Error al crear hipertabla {table}: {e}")


def reverse_hypertables(apps, schema_editor):
    """Revierte las hipertablas"""
    # TimescaleDB no permite revertir fácilmente hipertablas
    # Necesitarías eliminar y recrear las tablas
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('crystals_app', '0002_initial'),
    ]

    operations = [
        # Crear nuevos modelos
        migrations.CreateModel(
            name='AnalysisResults',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('mean', models.FloatField(default=0.0)),
                ('cv', models.FloatField(default=0.0)),
                ('pct_fine', models.FloatField(default=0.0)),
                ('pct_small', models.FloatField(default=0.0)),
                ('pct_optimal', models.FloatField(default=0.0)),
                ('pct_large', models.FloatField(default=0.0)),
                ('pct_very_large', models.FloatField(default=0.0)),
                ('ratio_l_to_w', models.FloatField(default=0.0)),
                ('elongated_crystals', models.FloatField(default=0.0)),
                ('pct_powder', models.FloatField(default=0.0)),
                ('historic_report_id', models.BigIntegerField(default=0)),
            ],
            options={
                'db_table': 'analysis_results',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Numero',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.FloatField(default=0.0)),
                ('time', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
            ],
            options={
                'db_table': 'numero',
                'managed': True,
            },
        ),
        
        # Agregar campos time a las tablas existentes
        migrations.AddField(
            model_name='analysiscategory',
            name='time',
            field=models.DateTimeField(default=django.utils.timezone.now, db_index=True),
        ),
        migrations.AddField(
            model_name='historicanalysisdata',
            name='time',
            field=models.DateTimeField(default=django.utils.timezone.now, db_index=True),
        ),
        migrations.AddField(
            model_name='historicreport',
            name='time',
            field=models.DateTimeField(default=django.utils.timezone.now, db_index=True),
        ),
        migrations.AddField(
            model_name='laboratorydata',
            name='time',
            field=models.DateTimeField(default=django.utils.timezone.now, db_index=True),
        ),
        
        # Convertir las tablas en hipertablas de TimescaleDB
        migrations.RunPython(create_hypertables, reverse_hypertables),
    ]
