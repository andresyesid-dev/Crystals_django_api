"""
T5 — Índices compuestos para las consultas de rango de fechas.

Crea tres índices B-tree compuestos que cubren los únicos endpoints donde el
tiempo de base de datos puede dominar (filtros por rango de `datetime` /
`date_and_time`):

    idx_histrep_factory_datetime      (historic_reports: factory_id, datetime)
    idx_histanal_factory_report       (historic_analysis_data: factory_id, historic_reports_id)
    idx_labdata_factory_datetime      (laboratory_data: factory_id, date_and_time)

Aunque los campos de fecha son CharField, el cliente siempre los escribe en
formato ISO 'YYYY-MM-DD HH:MM:SS', que es lexicográficamente == cronológicamente
ordenable; por eso un B-tree sobre el texto acelera las comparaciones de rango
`>=` / `<=`. La columna de igualdad (factory_id) va primero y la de rango
después: orden óptimo para un índice compuesto.

NOTA (por qué NO se usa CONCURRENTLY):
`historic_reports`, `historic_analysis_data` y `laboratory_data` son tablas
PARTICIONADAS (_p1.._p7). PostgreSQL NO permite `CREATE INDEX CONCURRENTLY`
sobre una tabla particionada ("cannot create index on partitioned table
... concurrently"). En su lugar se usa `AddIndex` normal: PostgreSQL crea el
índice en la tabla padre y lo propaga a cada partición. Esto toma un lock
breve de escritura mientras construye; es aceptable porque el volumen actual
es bajo y se aplica en ventana de mantenimiento (`railway run ... migrate`).
Por eso la migración vuelve a ser atómica (atomic = True por defecto).
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crystals_app', '0015_add_median_skewness_to_reporting_orders'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='historicreport',
            index=models.Index(
                fields=['factory_id', 'datetime'],
                name='idx_histrep_factory_datetime',
            ),
        ),
        migrations.AddIndex(
            model_name='historicanalysisdata',
            index=models.Index(
                fields=['factory_id', 'historic_report'],
                name='idx_histanal_factory_report',
            ),
        ),
        migrations.AddIndex(
            model_name='laboratorydata',
            index=models.Index(
                fields=['factory_id', 'date_and_time'],
                name='idx_labdata_factory_datetime',
            ),
        ),
    ]
