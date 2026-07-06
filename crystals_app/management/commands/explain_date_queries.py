"""
T5 — Verificación de uso de índice en las consultas de rango de fechas.

Corre EXPLAIN (ANALYZE, BUFFERS) sobre las 3 consultas reales del ORM que
filtran por rango de fecha y reporta, para cada una, si PostgreSQL usa un
Index Scan (objetivo) o un Seq Scan (índice ignorado → revisar collation /
particionado). Es la herramienta de "medición limpia" para confirmar el efecto
de los índices de la migración 0016 ANTES de añadir caché (T4).

Uso:
    railway run python manage.py explain_date_queries \
        --factory 1 --start "2026-01-01 00:00:00" --end "2026-12-31 23:59:59"

    # rango por defecto: último año natural, factory_id=1
    railway run python manage.py explain_date_queries

Interpretación:
    - "Index Scan using idx_..." o "Bitmap Index Scan on idx_..."  → OK
    - "Seq Scan on <tabla>"                                         → el índice
      no se está usando. Causas típicas: tabla muy pequeña (el planner prefiere
      seq scan, normal en datos de prueba), desajuste de collation en el
      CharField, o particionado que impide el pruning. Revisar con infra.
"""

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import connection

from crystals_app.models import (
    HistoricReport,
    HistoricAnalysisData,
    LaboratoryData,
)


class Command(BaseCommand):
    help = "EXPLAIN ANALYZE de las 3 consultas de rango de fechas (T5)."

    def add_arguments(self, parser):
        parser.add_argument('--factory', type=int, default=1,
                            help="factory_id a usar en los filtros (default 1)")
        parser.add_argument('--start', type=str, default=None,
                            help="Inicio del rango 'YYYY-MM-DD HH:MM:SS'")
        parser.add_argument('--end', type=str, default=None,
                            help="Fin del rango 'YYYY-MM-DD HH:MM:SS'")

    def handle(self, *args, **options):
        factory_id = options['factory']
        end = options['end'] or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start = options['start'] or (
            (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
        )

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"EXPLAIN ANALYZE — factory_id={factory_id} "
            f"rango=[{start} .. {end}]\n"
        ))

        querysets = [
            (
                "get_historic_reports  (historic_reports.datetime)",
                HistoricReport.objects.filter(
                    datetime__gte=start, datetime__lte=end, factory_id=factory_id,
                ),
                "idx_histrep_factory_datetime",
            ),
            (
                "get_analysis_historic_data  (JOIN historic_report.datetime)",
                HistoricAnalysisData.objects.filter(
                    historic_report__datetime__gte=start,
                    historic_report__datetime__lte=end,
                    factory_id=factory_id,
                ).select_related('historic_report'),
                "idx_histanal_factory_report / idx_histrep_factory_datetime",
            ),
            (
                "get_historic_laboratory_data  (laboratory_data.date_and_time)",
                LaboratoryData.objects.filter(
                    id__gt=0, date_and_time__gte=start, date_and_time__lte=end,
                    factory_id=factory_id,
                ),
                "idx_labdata_factory_datetime",
            ),
        ]

        for label, qs, expected_index in querysets:
            self.stdout.write(self.style.HTTP_INFO(f"\n=== {label} ==="))
            self.stdout.write(f"Índice esperado: {expected_index}")

            sql, params = qs.query.sql_with_params()
            plan_lines = self._explain(sql, params)
            plan_text = "\n".join(plan_lines)
            self.stdout.write(plan_text)

            uses_index = ('Index Scan' in plan_text
                          or 'Index Only Scan' in plan_text
                          or 'Bitmap Index Scan' in plan_text)
            if uses_index:
                self.stdout.write(self.style.SUCCESS("→ Usa índice: OK"))
            else:
                self.stdout.write(self.style.WARNING(
                    "→ NO usa índice (Seq Scan). Si hay datos suficientes, "
                    "revisar collation del CharField y particionado con infra."
                ))

        self.stdout.write("")

    def _explain(self, sql, params):
        with connection.cursor() as cursor:
            cursor.execute(f"EXPLAIN (ANALYZE, BUFFERS) {sql}", params)
            return [row[0] for row in cursor.fetchall()]
