# Generated manually to improve notify function for TimescaleDB chunks

from django.db import migrations


def improve_notify_function(apps, schema_editor):
    """
    Mejora la función de notificación para manejar chunks de TimescaleDB
    y enviar el nombre de la tabla original en lugar del chunk
    """
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            
            print("\n" + "="*70)
            print("🔧 MEJORANDO FUNCIÓN DE NOTIFICACIÓN PARA TIMESCALEDB")
            print("="*70 + "\n")
            
            # Crear función mejorada que detecta la tabla original de los chunks
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
            
            print("✅ Función de notificación mejorada: notify_crystals_results()")
            print("   • Detecta automáticamente chunks de TimescaleDB")
            print("   • Envía el nombre de la tabla original (no el chunk)")
            print("   • Incluye información del chunk para debugging")
            print("\n" + "="*70)
            print("✅ MEJORA COMPLETADA")
            print("="*70)
            print("\n💡 Formato del nuevo payload:")
            print("""   {
     "table": "numero",              ← Tabla original
     "chunk": "_hyper_8_1_chunk",    ← Chunk de TimescaleDB
     "operation": "INSERT",
     "timestamp": "2025-10-30...",
     "data": { ... }
   }""")
            print()


def revert_notify_function(apps, schema_editor):
    """
    Revierte a la versión anterior de la función
    """
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            
            # Restaurar función original
            cursor.execute("""
                CREATE OR REPLACE FUNCTION notify_crystals_results()
                RETURNS TRIGGER AS $$
                DECLARE
                    notification json;
                BEGIN
                    notification = json_build_object(
                        'table', TG_TABLE_NAME,
                        'operation', TG_OP,
                        'timestamp', CURRENT_TIMESTAMP,
                        'data', row_to_json(CASE 
                            WHEN TG_OP = 'DELETE' THEN OLD
                            ELSE NEW
                        END)
                    );
                    
                    PERFORM pg_notify('crystals_results', notification::text);
                    
                    IF TG_OP = 'DELETE' THEN
                        RETURN OLD;
                    ELSE
                        RETURN NEW;
                    END IF;
                END;
                $$ LANGUAGE plpgsql;
            """)
            print("✅ Función de notificación revertida a versión anterior")


class Migration(migrations.Migration):

    dependencies = [
        ('crystals_app', '0005_add_default_now_to_time'),
    ]

    operations = [
        migrations.RunPython(
            improve_notify_function,
            revert_notify_function
        ),
    ]
