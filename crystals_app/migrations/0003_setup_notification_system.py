# Generated migration - Consolidated from 0004 and 0006
# PostgreSQL NOTIFY system with TimescaleDB chunk detection

from django.db import migrations


def create_notify_system(apps, schema_editor):
    """
    Crea la función de notificación mejorada y los triggers para todas las hipertablas
    """
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            
            print("\n" + "="*70)
            print("📡 CONFIGURANDO SISTEMA DE NOTIFICACIONES POSTGRESQL")
            print("="*70 + "\n")
            
            # 1. Crear función de notificación mejorada con detección de chunks
            print("📡 Creando función de notificación PostgreSQL...")
            cursor.execute("""
                CREATE OR REPLACE FUNCTION notify_crystals_results()
                RETURNS TRIGGER AS $$
                DECLARE
                    notification json;
                    original_table text;
                    hypertable_id int;
                BEGIN
                    -- Determinar el nombre de la tabla original
                    -- Si es un chunk de TimescaleDB, obtener la tabla principal
                    IF TG_TABLE_NAME LIKE '_hyper_%_chunk' THEN
                        -- Extraer el hypertable_id del nombre del chunk
                        -- Formato: _hyper_ID_CHUNK_chunk
                        hypertable_id := split_part(TG_TABLE_NAME, '_', 3)::int;
                        
                        -- Consultar el nombre real de la hipertabla
                        SELECT ht.table_name INTO original_table
                        FROM _timescaledb_catalog.hypertable ht
                        WHERE ht.id = hypertable_id;
                        
                        -- Si no se encuentra, usar el nombre del chunk
                        IF original_table IS NULL THEN
                            original_table := TG_TABLE_NAME;
                        END IF;
                    ELSE
                        -- No es un chunk, usar el nombre directo
                        original_table := TG_TABLE_NAME;
                    END IF;
                    
                    -- Crear payload JSON con información del cambio
                    notification = json_build_object(
                        'table', original_table,
                        'chunk', TG_TABLE_NAME,
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
            print("   • Detecta automáticamente chunks de TimescaleDB")
            print("   • Envía nombre de tabla original + chunk para debugging")
            print("   • Captura INSERT, UPDATE, DELETE")
            
            # 2. Lista de hipertablas para crear triggers
            # NOTA: Solo las tablas que son hypertables (sin FK a otras hypertables)
            hypertables = [
                'historic_reports',
                'laboratory_data',
                'numero',
                'analysis_results',
                # También monitoreamos las tablas con FK aunque no sean hypertables
                'analysis_categories',
                'historic_analysis_data'
            ]
            
            # 3. Crear triggers para cada hipertabla
            print("\n📡 Creando triggers para las hipertablas...")
            for table in hypertables:
                trigger_name = f"trigger_notify_{table}"
                
                # Verificar si el trigger ya existe y eliminarlo
                cursor.execute(f"""
                    DROP TRIGGER IF EXISTS {trigger_name} ON {table};
                """)
                
                # Crear el trigger que se ejecuta después de INSERT, UPDATE o DELETE
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
            print("\n💡 Formato del payload:")
            print("""   {
     "table": "numero",              ← Tabla original
     "chunk": "_hyper_8_1_chunk",    ← Chunk de TimescaleDB (para debugging)
     "operation": "INSERT",
     "timestamp": "2025-10-30...",
     "data": { ... }
   }""")
            print("\n" + "="*70)


def reverse_notify_system(apps, schema_editor):
    """
    Elimina los triggers y la función de notificación
    """
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            
            # Lista de tablas monitoreadas
            hypertables = [
                'historic_reports',
                'laboratory_data',
                'numero',
                'analysis_results',
                'analysis_categories',
                'historic_analysis_data'
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
        ('crystals_app', '0002_create_all_tables_with_timescaledb'),
    ]

    operations = [
        migrations.RunPython(
            create_notify_system,
            reverse_notify_system
        ),
    ]
