# Generated manually for PostgreSQL NOTIFY triggers

from django.db import migrations


def create_notify_function_and_triggers(apps, schema_editor):
    """
    Crea la función de notificación y los triggers para todas las hipertablas
    """
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            
            # 1. Crear la función de notificación que se ejecutará en los triggers
            print("📡 Creando función de notificación PostgreSQL...")
            cursor.execute("""
                CREATE OR REPLACE FUNCTION notify_crystals_results()
                RETURNS TRIGGER AS $$
                DECLARE
                    notification json;
                BEGIN
                    -- Crear payload JSON con información del cambio
                    notification = json_build_object(
                        'table', TG_TABLE_NAME,
                        'operation', TG_OP,
                        'timestamp', CURRENT_TIMESTAMP,
                        'data', row_to_json(CASE 
                            WHEN TG_OP = 'DELETE' THEN OLD
                            ELSE NEW
                        END)
                    );
                    
                    -- Enviar notificación al canal 'crystals_results'
                    PERFORM pg_notify('crystals_results', notification::text);
                    
                    -- Retornar el registro apropiado según la operación
                    IF TG_OP = 'DELETE' THEN
                        RETURN OLD;
                    ELSE
                        RETURN NEW;
                    END IF;
                END;
                $$ LANGUAGE plpgsql;
            """)
            print("✅ Función de notificación creada: notify_crystals_results()")
            
            # 2. Lista de hipertablas para crear triggers
            hypertables = [
                'analysis_categories',
                'historic_analysis_data',
                'historic_reports',
                'laboratory_data',
                'numero',
                'analysis_results'
            ]
            
            # 3. Crear triggers para cada hipertabla
            print("\n📡 Creando triggers para las hipertablas...")
            for table in hypertables:
                trigger_name = f"trigger_notify_{table}"
                
                # Verificar si el trigger ya existe y eliminarlo
                cursor.execute(f"""
                    DROP TRIGGER IF EXISTS {trigger_name} ON {table};
                """)
                
                # Crear el trigger que se ejecuta después de INSERT o UPDATE
                cursor.execute(f"""
                    CREATE TRIGGER {trigger_name}
                    AFTER INSERT OR UPDATE OR DELETE ON {table}
                    FOR EACH ROW
                    EXECUTE FUNCTION notify_crystals_results();
                """)
                
                print(f"✅ Trigger creado: {trigger_name} en tabla {table}")
            
            print("\n" + "="*70)
            print("🎉 SISTEMA DE NOTIFICACIONES CONFIGURADO EXITOSAMENTE")
            print("="*70)
            print(f"\n📢 Canal de notificación: 'crystals_results'")
            print(f"📊 Tablas monitoreadas: {len(hypertables)}")
            print(f"🔔 Eventos capturados: INSERT, UPDATE, DELETE")
            print("\n" + "="*70)


def reverse_notify_function_and_triggers(apps, schema_editor):
    """
    Elimina los triggers y la función de notificación
    """
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            
            # Lista de hipertablas
            hypertables = [
                'analysis_categories',
                'historic_analysis_data',
                'historic_reports',
                'laboratory_data',
                'numero',
                'analysis_results'
            ]
            
            # Eliminar triggers
            print("\n🗑️  Eliminando triggers...")
            for table in hypertables:
                trigger_name = f"trigger_notify_{table}"
                try:
                    cursor.execute(f"""
                        DROP TRIGGER IF EXISTS {trigger_name} ON {table};
                    """)
                    print(f"✅ Trigger eliminado: {trigger_name}")
                except Exception as e:
                    print(f"⚠️  Error al eliminar trigger {trigger_name}: {e}")
            
            # Eliminar función de notificación
            print("\n🗑️  Eliminando función de notificación...")
            try:
                cursor.execute("""
                    DROP FUNCTION IF EXISTS notify_crystals_results() CASCADE;
                """)
                print("✅ Función de notificación eliminada")
            except Exception as e:
                print(f"⚠️  Error al eliminar función: {e}")


class Migration(migrations.Migration):

    dependencies = [
        ('crystals_app', '0003_add_time_fields_and_create_hypertables'),
    ]

    operations = [
        migrations.RunPython(
            create_notify_function_and_triggers,
            reverse_notify_function_and_triggers
        ),
    ]
