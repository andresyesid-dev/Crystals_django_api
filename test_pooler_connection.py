#!/usr/bin/env python3
"""
Script para probar la conexión a Supabase usando el Connection Pooler
"""
import psycopg2
import sys

# Configuración usando el Pooler
config = {
    'host': 'aws-1-us-east-1.pooler.supabase.com',
    'port': '5432',
    'database': 'postgres',
    'user': 'postgres.iwmrkcuuhvygchesovwl',
    'password': 'Soporte!2025',
    'sslmode': 'require',
    'connect_timeout': 10
}

print("🔧 Probando conexión a Supabase Connection Pooler...")
print(f"📡 Host: {config['host']}")
print(f"🔌 Port: {config['port']}")
print(f"👤 User: {config['user']}")
print()

try:
    print("⏳ Conectando...")
    conn = psycopg2.connect(**config)
    print("✅ ¡Conexión exitosa al pooler de Supabase!")
    print()
    
    # Ejecutar consulta de prueba
    cursor = conn.cursor()
    cursor.execute('SELECT version();')
    version = cursor.fetchone()[0]
    print(f"📊 PostgreSQL Version:")
    print(f"   {version[:100]}")
    print()
    
    # Verificar que podemos leer tablas
    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
    table_count = cursor.fetchone()[0]
    print(f"📋 Tablas en el esquema 'public': {table_count}")
    print()
    
    cursor.close()
    conn.close()
    
    print("=" * 60)
    print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
    print("=" * 60)
    print()
    print("Tu API de Django ahora debería funcionar correctamente.")
    print("Ejecuta: python manage.py runserver")
    print()
    sys.exit(0)
    
except psycopg2.OperationalError as e:
    print("❌ Error de conexión:")
    print(f"   {e}")
    print()
    print("💡 Posibles causas:")
    print("   1. Password incorrecto")
    print("   2. Usuario incorrecto (debe ser: postgres.PROJECT_REF)")
    print("   3. Proyecto de Supabase pausado")
    print("   4. Firewall bloqueando el puerto 5432")
    print()
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error inesperado: {type(e).__name__}")
    print(f"   {e}")
    sys.exit(1)
