#!/usr/bin/env python3
"""
Script para agregar decoradores JWT a todas las views que no los tengan
"""

import os
import re
from pathlib import Path

# Directorio de views
VIEWS_DIR = "/Users/andresyesidmottasarmiento/OneDrive/Mac/Crystals_django_api/crystals_app/views"

# Patrones para identificar funciones de view
VIEW_FUNCTION_PATTERN = r'^def\s+(\w+)\s*\('
DECORATOR_PATTERNS = [
    r'@jwt_required',
    r'@permission_required',
    r'@log_api_access'
]

# Imports necesarios
REQUIRED_IMPORTS = "from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint"

def has_jwt_decorators(content):
    """Verificar si el archivo ya tiene decoradores JWT"""
    return any(re.search(pattern, content, re.MULTILINE) for pattern in DECORATOR_PATTERNS)

def has_required_imports(content):
    """Verificar si el archivo tiene los imports necesarios"""
    return "jwt_required" in content and "from ..decorators import" in content

def get_view_functions(content):
    """Obtener todas las funciones de view del archivo"""
    lines = content.split('\n')
    functions = []
    
    for i, line in enumerate(lines):
        if re.match(VIEW_FUNCTION_PATTERN, line.strip()):
            # Buscar decoradores anteriores
            decorators = []
            j = i - 1
            while j >= 0 and lines[j].strip().startswith('@'):
                decorators.insert(0, lines[j].strip())
                j -= 1
            
            function_name = re.search(VIEW_FUNCTION_PATTERN, line.strip()).group(1)
            functions.append({
                'name': function_name,
                'line': i,
                'decorators': decorators,
                'has_jwt': any('jwt_required' in dec for dec in decorators)
            })
    
    return functions

def add_decorators_to_file(file_path):
    """Agregar decoradores JWT a un archivo específico"""
    print(f"\n🔍 Procesando: {file_path.name}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip archivos que ya tienen decoradores JWT
    if has_jwt_decorators(content):
        print(f"  ✅ Ya tiene decoradores JWT")
        return False
    
    # Skip auth_view.py y security_view.py (ya están configurados)
    if file_path.name in ['auth_view.py', 'security_view.py']:
        print(f"  ⏭️  Archivo de sistema, omitiendo")
        return False
    
    lines = content.split('\n')
    
    # Agregar imports si no existen
    if not has_required_imports(content):
        import_added = False
        for i, line in enumerate(lines):
            if line.startswith('from ..models import') or line.startswith('from django.'):
                lines.insert(i + 1, REQUIRED_IMPORTS)
                import_added = True
                print(f"  📦 Agregados imports de decoradores")
                break
        
        if not import_added:
            # Si no encontramos un lugar apropiado, agregar después de los imports existentes
            for i, line in enumerate(lines):
                if line.startswith('import ') and not lines[i+1].startswith('import'):
                    lines.insert(i + 1, REQUIRED_IMPORTS)
                    print(f"  📦 Agregados imports de decoradores")
                    break
    
    # Obtener funciones de view
    updated_content = '\n'.join(lines)
    functions = get_view_functions(updated_content)
    
    if not functions:
        print(f"  ⚠️  No se encontraron funciones de view")
        return False
    
    # Agregar decoradores a funciones que no los tengan
    lines = updated_content.split('\n')
    offset = 0
    
    for func in functions:
        if not func['has_jwt']:
            line_idx = func['line'] + offset
            
            # Determinar qué decoradores agregar basado en el tipo de función
            new_decorators = []
            
            # Siempre agregar JWT
            new_decorators.append('@jwt_required')
            
            # Determinar permisos basado en el nombre de la función
            if any(keyword in func['name'].lower() for keyword in ['create', 'insert', 'add', 'update', 'delete', 'set']):
                if 'company' in func['name'].lower() or 'config' in func['name'].lower() or 'admin' in func['name'].lower():
                    new_decorators.append("@permission_required('admin')")
                else:
                    new_decorators.append("@permission_required('write')")
                new_decorators.append('@sensitive_endpoint')
            else:
                new_decorators.append("@permission_required('read')")
            
            new_decorators.append('@log_api_access')
            
            # Insertar decoradores antes de la función
            for j, decorator in enumerate(new_decorators):
                lines.insert(line_idx + j, decorator)
                offset += 1
            
            print(f"  🔒 Agregados decoradores a función: {func['name']}")
    
    # Escribir archivo actualizado
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    return True

def main():
    """Función principal"""
    print("🚀 Agregando decoradores JWT a todas las views...")
    
    views_path = Path(VIEWS_DIR)
    if not views_path.exists():
        print(f"❌ Directorio no encontrado: {VIEWS_DIR}")
        return
    
    updated_files = []
    
    for py_file in views_path.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
            
        if add_decorators_to_file(py_file):
            updated_files.append(py_file.name)
    
    print(f"\n✅ Proceso completado!")
    print(f"📊 Archivos actualizados: {len(updated_files)}")
    
    if updated_files:
        print("📝 Archivos modificados:")
        for file in updated_files:
            print(f"  • {file}")
    
    print("\n🔐 Ahora todos los endpoints requieren autenticación JWT")

if __name__ == "__main__":
    main()