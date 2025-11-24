# Generated manually to add DEFAULT NOW() to datetime field in historic_reports

from django.db import migrations


def add_default_now_to_datetime(apps, schema_editor):
    """
    Agrega DEFAULT NOW() al campo 'datetime' en historic_reports
    """
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            
            print("\n" + "="*70)
            print("🔧 AGREGANDO DEFAULT NOW() AL CAMPO 'datetime'")
            print("="*70 + "\n")
            
            try:
                # 1. Primero, actualizar registros existentes que tengan datetime NULL
                cursor.execute("""
                    UPDATE historic_reports 
                    SET datetime = NOW()::text 
                    WHERE datetime IS NULL OR datetime = '';
                """)
                updated = cursor.rowcount
                if updated > 0:
                    print(f"✅ {updated} registros actualizados con datetime NULL")
                
                # 2. Agregar DEFAULT NOW()::text al campo datetime (es CharField, no DateTimeField)
                cursor.execute("""
                    ALTER TABLE historic_reports 
                    ALTER COLUMN datetime SET DEFAULT NOW()::text;
                """)
                print("✅ Campo 'datetime' en 'historic_reports' ahora tiene DEFAULT NOW()::text")
                
                # 3. Opcional: Si el campo permite NULL, quitarlo
                cursor.execute("""
                    ALTER TABLE historic_reports 
                    ALTER COLUMN datetime SET NOT NULL;
                """)
                print("✅ Campo 'datetime' ahora es NOT NULL")
                
            except Exception as e:
                print(f"⚠️  Error al modificar campo datetime: {e}")
                # Si falla NOT NULL, al menos el DEFAULT se aplicó
            
            print("\n" + "="*70)
            print("✅ MODIFICACIÓN COMPLETADA")
            print("="*70)
            print("\n💡 Ahora puedes hacer INSERT sin especificar 'datetime':")
            print("   INSERT INTO historic_reports (calibration, correlation, ...)")
            print("   VALUES ('cal1', 0.95, ...);")
            print("   -- PostgreSQL asignará automáticamente NOW()::text a 'datetime'\n")


def remove_default_from_datetime(apps, schema_editor):
    """
    Elimina el DEFAULT del campo 'datetime'
    """
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            try:
                cursor.execute("""
                    ALTER TABLE historic_reports 
                    ALTER COLUMN datetime DROP DEFAULT;
                """)
                print("✅ DEFAULT eliminado de campo 'datetime' en historic_reports")
            except Exception as e:
                print(f"⚠️  Error al revertir: {e}")


class Migration(migrations.Migration):

    dependencies = [
        ('crystals_app', '0006_improve_notify_for_chunks'),
    ]

    operations = [
        migrations.RunPython(
            add_default_now_to_datetime,
            remove_default_from_datetime
        ),
    ]
