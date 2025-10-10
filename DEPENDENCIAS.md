# 📦 Dependencias del Proyecto Crystals Django API

## 🚀 Instalación

### Producción
```bash
pip install -r requirements.txt
```

### Desarrollo
```bash
pip install -r requirements-dev.txt
```

## 📋 Dependencias Principales

### Core Framework
- **Django 4.2.24**: Framework web principal
- **djangorestframework 3.16.1**: API REST framework
- **psycopg2-binary 2.9.10**: Conector PostgreSQL/TimescaleDB

### 🔐 Autenticación & Seguridad
- **djangorestframework_simplejwt 5.5.1**: Autenticación JWT
- **PyJWT 2.10.1**: Librería JWT
- **django-ratelimit 4.1.0**: Rate limiting y protección contra ataques
- **django-cors-headers 4.9.0**: Manejo de CORS

### 🛠️ Utilidades
- **python-decouple 3.8**: Gestión de configuración y variables de entorno
- **requests 2.32.5**: Cliente HTTP para testing y scripts

### 🔧 Dependencias de Sistema
- **certifi, charset-normalizer, idna, urllib3**: Dependencias de requests
- **asgiref, sqlparse, typing_extensions**: Dependencias de Django

## 🧪 Dependencias de Desarrollo (Opcionales)

### Testing
- **pytest**: Framework de testing
- **pytest-django**: Integración Django con pytest
- **pytest-cov**: Cobertura de código

### Calidad de Código
- **black**: Formateador de código
- **flake8**: Linter
- **isort**: Organizador de imports

### Desarrollo
- **django-debug-toolbar**: Toolbar de debug
- **django-extensions**: Extensiones útiles para desarrollo
- **drf-spectacular**: Documentación automática de API

## 📝 Notas de Versiones

- **Django 4.2.24**: LTS version, soporte hasta abril 2026
- **DRF 3.16.1**: Compatible con Django 4.2
- **JWT 5.5.1**: Última versión estable con soporte completo para DRF 3.16

## 🔄 Actualización de Dependencias

```bash
# Generar requirements actualizado
pip freeze > requirements.txt

# Verificar vulnerabilidades
pip audit

# Actualizar pip
pip install --upgrade pip
```