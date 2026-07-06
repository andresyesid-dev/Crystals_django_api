"""
Login de fábrica en la nube: tabla `credentials_factory` + seed de las 5
fábricas.

El modelo CredentialsFactory es `managed = False` (Django no gestiona su
esquema), así que esta migración:

  1. Crea la tabla con SQL idempotente (CREATE TABLE IF NOT EXISTS). No es
     particionada ni multi-tenant — es un catálogo global de 5 filas.
  2. Siembra los 5 hashes bcrypt del cliente con update_or_create (idempotente:
     re-ejecutar no duplica ni pisa con datos viejos de forma inconsistente).

Los hashes son EXACTAMENTE los del cliente (espejo de su SQLite), almacenados
como str para que `bcrypt.checkpw(pwd, stored.encode())` funcione en la view.
"""

from django.db import migrations, models


# (factory_id, factory_name, bcrypt_hash) — espejo de la SQLite del cliente.
FACTORY_SEED = [
    (1, "Alta Mogiana", "$2b$12$Yw5N41IzPK/Dhxo.bbJUo.CEytKHRcp9ChhNpznb3TpmoAs2IJE16"),
    (2, "Incauca",      "$2b$12$t2vTmT8chYRsrKFTaqMEEuQ3tm0rNxvAUNakgBCe9JS7bD/TqeOyy"),
    (3, "Laura",        "$2b$12$KG5Zb/Pmj8Sc/glbwL4Jw.e1VQ/ehdSQ8nyNgVXFobXpNclE5ELi."),
    (4, "Andres",       "$2b$12$rWPEkNbPbk6PnPWPXKHTBeGeDFR1EK/QsTiB2UWWOa0NpMOlOGN2m"),
    (5, "Sebastian",    "$2b$12$K795MkXoboSvrBpLMDiUxu2ZoMLr.ea0VGeC7xV32abCojKMxw4uy"),
]


def seed_factories(apps, schema_editor):
    CredentialsFactory = apps.get_model('crystals_app', 'CredentialsFactory')
    for factory_id, name, pwd_hash in FACTORY_SEED:
        CredentialsFactory.objects.update_or_create(
            factory_id=factory_id,
            defaults={'factory_name': name, 'password': pwd_hash},
        )


def unseed_factories(apps, schema_editor):
    CredentialsFactory = apps.get_model('crystals_app', 'CredentialsFactory')
    CredentialsFactory.objects.filter(
        factory_id__in=[fid for fid, _, _ in FACTORY_SEED]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('crystals_app', '0016_add_date_range_indexes'),
    ]

    operations = [
        # Se separa ESTADO de BASE DE DATOS:
        #   - state_operations: registra CreateModel(managed=False) en el grafo de
        #     Django para que makemigrations deje de pedir crear el modelo. Es un
        #     no-op de esquema (no genera DDL).
        #   - database_operations: el DDL real (idempotente) + el seed.
        # Así esta migración queda autocontenida y no arrastra la deuda heredada
        # (BlockedIP, analysisresults.factory_id), que es responsabilidad aparte.
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='CredentialsFactory',
                    fields=[
                        ('factory_id', models.IntegerField(primary_key=True, serialize=False)),
                        ('factory_name', models.CharField(max_length=100)),
                        ('password', models.CharField(max_length=255)),
                    ],
                    options={
                        'db_table': 'credentials_factory',
                        'managed': False,
                    },
                ),
            ],
            database_operations=[
                # IF NOT EXISTS: segura aunque la tabla ya exista en Supabase.
                migrations.RunSQL(
                    sql="""
                        CREATE TABLE IF NOT EXISTS credentials_factory (
                            factory_id    integer PRIMARY KEY,
                            factory_name  varchar(100) NOT NULL,
                            password      varchar(255) NOT NULL
                        );
                    """,
                    reverse_sql="DROP TABLE IF EXISTS credentials_factory;",
                ),
            ],
        ),
        migrations.RunPython(seed_factories, unseed_factories),
    ]
