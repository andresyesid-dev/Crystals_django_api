"""
Reconciliación de deuda de migraciones HEREDADA (no es parte del login de
fábrica; se incluye porque bloqueaba `makemigrations --check`).

`blocked_ips` y `analysis_results.factory_id` YA EXISTEN en Supabase pero nunca
tuvieron migración que los registrara en el grafo de Django (se aplicaron a
mano en producción). Por eso Django los detecta como cambios pendientes.

Esta migración registra ese estado en el grafo SIN ejecutar DDL
(SeparateDatabaseAndState con database_operations vacío): el modelo/campo pasan
a estar "conocidos" por Django, pero como la tabla y la columna ya están en la
base, NO se intenta crearlas de nuevo (eso fallaría con "ya existe").

Si algún día se levanta una base DESDE CERO, habría que crear estas estructuras
por otra vía (o convertir esto en operaciones de base reales). En la Supabase
actual de producción, aplicar esta migración es seguro y es un no-op de esquema.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crystals_app', '0017_credentials_factory_seed'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            # Sin operaciones de base: la tabla y la columna ya existen en Supabase.
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name='BlockedIP',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('ip_address', models.CharField(max_length=50, unique=True)),
                        ('hostname', models.CharField(blank=True, max_length=255, null=True)),
                        ('blocked_at', models.DateTimeField(auto_now_add=True)),
                        ('reason', models.CharField(default='Repeated failed login attempts', max_length=255)),
                    ],
                    options={
                        'db_table': 'blocked_ips',
                        'managed': True,
                    },
                ),
                migrations.AddField(
                    model_name='analysisresults',
                    name='factory_id',
                    field=models.IntegerField(default=1),
                ),
            ],
        ),
    ]
