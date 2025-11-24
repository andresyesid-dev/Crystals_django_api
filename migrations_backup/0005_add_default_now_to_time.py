# Generated manually to add DEFAULT NOW() to time fields

from django.db import migrations


def add_default_now_to_time_fields(apps, schema_editor):
    """
    Agrega DEFAULT NOW() a las columnas 'time' para que se asignen automáticamente
    """
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            
            print("\n" + "="*70)
            print("🔧 AGREGANDO DEFAULT NOW() A CAMPOS 'time'")
            print("="*70 + "\n")
            
            # Lista de tablas con campo time
            tables = [
                'analysis_categories',
                'historic_analysis_data',
                'historic_reports',
                'laboratory_data',
                'numero',
                'analysis_results'
            ]
            
            for table in tables:
                try:
                    # Agregar DEFAULT NOW() a la columna time
                    cursor.execute(f"""
                        ALTER TABLE {table} 
                        ALTER COLUMN time SET DEFAULT NOW();
                    """)
                    print(f"✅ Tabla '{table}': columna 'time' ahora tiene DEFAULT NOW()")
                    
                except Exception as e:
                    print(f"⚠️  Error al modificar tabla '{table}': {e}")
            
            print("\n" + "="*70)
            print("✅ MODIFICACIÓN COMPLETADA")
            print("="*70)
            print("\n💡 Ahora puedes hacer INSERT sin especificar 'time':")
            print("   INSERT INTO numero (valor) VALUES (42.5);")
            print("   -- PostgreSQL asignará automáticamente NOW() a 'time'")
            print("\n💡 También puedes especificar el valor manualmente:")
            print("   INSERT INTO numero (valor, time) VALUES (42.5, '2025-01-15 10:30:00');")
            print("\n")


def remove_default_from_time_fields(apps, schema_editor):
    """
    Elimina el DEFAULT de las columnas 'time'
    """
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            
            tables = [
                'analysis_categories',
                'historic_analysis_data',
                'historic_reports',
                'laboratory_data',
                'numero',
                'analysis_results'
            ]
            
            for table in tables:
                try:
                    cursor.execute(f"""
                        ALTER TABLE {table} 
                        ALTER COLUMN time DROP DEFAULT;
                    """)
                    print(f"✅ Tabla '{table}': DEFAULT eliminado de columna 'time'")
                    
                except Exception as e:
                    print(f"⚠️  Error al revertir tabla '{table}': {e}")


class Migration(migrations.Migration):

    dependencies = [
        ('crystals_app', '0004_create_notify_triggers'),
    ]

    operations = [
        migrations.RunPython(
            add_default_now_to_time_fields,
            remove_default_from_time_fields
        ),
    ]
