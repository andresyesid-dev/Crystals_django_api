## Guía Completa: Creación de Usuarios para API Crystals

### Problema Identificado
El proyecto tiene dos modelos User diferentes:
1. **`crystals_app.models.User`**: Modelo personalizado para datos de negocio (tabla `users`)
2. **`django.contrib.auth.models.User`**: Modelo estándar de Django para autenticación

**Para JWT y autenticación, usamos el modelo estándar de Django.**

### 1. Creación de Usuario Superusuario (Admin)

**Método 1: Usando manage.py (Recomendado)**
```bash
cd /Users/andresyesidmottasarmiento/OneDrive/Mac/Crystals_django_api
source env/bin/activate
python manage.py createsuperuser
```
Cuando te pida los datos:
- **Username**: `admin`
- **Email**: `admin@crystals.com` 
- **Password**: `admin123456`

**Método 2: Usando Django Shell**
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User

# Crear superusuario
admin_user = User.objects.create_superuser(
    username='admin',
    email='admin@crystals.com',
    password='admin123456'
)
print(f"Superusuario creado: {admin_user.username}")
```

### 2. Creación de Usuario Normal

**Usando Django Shell:**
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User

# Crear usuario normal
normal_user = User.objects.create_user(
    username='testuser',
    email='test@crystals.com',
    password='test123456'
)
print(f"Usuario normal creado: {normal_user.username}")

# Verificar que se creó correctamente
print(f"¿Es staff?: {normal_user.is_staff}")
print(f"¿Es superuser?: {normal_user.is_superuser}")
print(f"¿Está activo?: {normal_user.is_active}")
```

### 3. Verificar Usuarios Creados

```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User

# Listar todos los usuarios
users = User.objects.all()
for user in users:
    print(f"Username: {user.username}, Email: {user.email}, Staff: {user.is_staff}, Superuser: {user.is_superuser}")

# Verificar usuario específico
try:
    admin = User.objects.get(username='admin')
    print(f"Admin encontrado: {admin.username}, Staff: {admin.is_staff}")
except User.DoesNotExist:
    print("Usuario admin no encontrado")
```

### 4. Actualización de Colección Postman

Los usuarios ahora siguen la estructura estándar de Django:

**Usuarios de Prueba:**
- **Admin**: `admin` / `admin123456` (is_staff=True, is_superuser=True)
- **Normal**: `testuser` / `test123456` (is_staff=False, is_superuser=False)

### 5. Endpoints y Permisos

**Endpoints Públicos (sin autenticación):**
- `POST /api/auth/login/` - Login
- `POST /api/auth/refresh/` - Refresh token
- `POST /api/auth/verify/` - Verificar token

**Endpoints Autenticados (requieren JWT):**
- `GET /api/auth/profile/` - Perfil del usuario
- `POST /api/auth/logout/` - Logout

**Endpoints Solo Admin (requieren is_staff=True):**
- `GET /api/security/dashboard/` - Dashboard de seguridad
- `POST /api/security/block-ip/` - Bloquear IP
- `POST /api/security/unblock-ip/` - Desbloquear IP
- `GET /api/security/logs/` - Logs de seguridad

### 6. Respuestas de Login Actualizadas

**Login Exitoso (Admin):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@crystals.com",
        "is_staff": true,
        "is_superuser": true
    }
}
```

**Login Exitoso (Usuario Normal):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 2,
        "username": "testuser",
        "email": "test@crystals.com",
        "is_staff": false,
        "is_superuser": false
    }
}
```

### 7. Flujo de Pruebas en Postman

1. **Importar las colecciones** ya generadas
2. **Crear usuarios** usando los comandos de arriba
3. **Probar login admin** - debería funcionar todos los endpoints
4. **Probar login usuario normal** - endpoints de seguridad deberían dar 403
5. **Verificar tokens** y refresh

### 8. Comandos de Verificación Rápida

**Verificar que el servidor está corriendo:**
```bash
cd /Users/andresyesidmottasarmiento/OneDrive/Mac/Crystals_django_api
source env/bin/activate
python manage.py runserver
```

**Crear usuarios de prueba rápidamente:**
```bash
python manage.py shell -c "
from django.contrib.auth.models import User
User.objects.get_or_create(username='admin', defaults={'email': 'admin@crystals.com', 'is_staff': True, 'is_superuser': True})
admin = User.objects.get(username='admin')
admin.set_password('admin123456')
admin.save()

User.objects.get_or_create(username='testuser', defaults={'email': 'test@crystals.com'})
user = User.objects.get(username='testuser')
user.set_password('test123456')
user.save()

print('Usuarios creados: admin (superuser) y testuser (normal)')
"
```

### 9. Solución de Problemas Comunes

**Error: "Invalid credentials"**
- Verificar que el usuario existe con: `User.objects.filter(username='admin').exists()`
- Verificar password con: `admin.check_password('admin123456')`

**Error: "Admin privileges required"**
- Verificar que el usuario tenga `is_staff=True`
- Solo usuarios con `is_staff=True` pueden acceder a endpoints de seguridad

**Error de CSRF**
- Los endpoints ya tienen `@csrf_exempt` configurado
- Asegúrate de usar `Authorization: Bearer <token>` en headers

Ahora los usuarios creados con `createsuperuser` y los tokens JWT funcionarán correctamente en Postman.