# Sistema de Seguridad y Autenticación JWT - Crystals API

## 🔐 Implementación Completa de Seguridad

### Características Implementadas

✅ **Autenticación JWT con tokens de acceso y refresh**
✅ **Sistema de permisos basado en roles**
✅ **Rate limiting y protección contra ataques**
✅ **Monitoreo de seguridad en tiempo real**
✅ **Logging avanzado de eventos de seguridad**
✅ **Middleware de protección multicapa**
✅ **Detección de patrones sospechosos**
✅ **Bloqueo automático de IPs maliciosas**

---

## 📡 Endpoints de Autenticación

### 1. Login (Obtener Token JWT)
```bash
POST /auth/login/
Content-Type: application/json

{
    "username": "usuario",
    "password": "contraseña"
}
```

**Respuesta exitosa:**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "usuario"
    },
    "token_type": "Bearer",
    "expires_in": 3600
}
```

### 2. Refresh Token
```bash
POST /auth/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 3. Logout
```bash
POST /auth/logout/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 4. Verificar Token
```bash
GET /auth/verify/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### 5. Perfil de Usuario
```bash
GET /auth/profile/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## 🛡️ Uso de la API Protegida

### Headers Requeridos
```bash
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Ejemplo de Llamada Protegida
```bash
GET /calibration/list
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## 🚨 Monitoreo de Seguridad (Solo Administradores)

### 1. Dashboard de Seguridad
```bash
GET /security/dashboard/
Authorization: Bearer <admin_token>
```

**Respuesta:**
```json
{
    "status": "success",
    "data": {
        "summary": {
            "failed_logins": 15,
            "suspicious_requests": 3,
            "rate_limit_hits": 8
        },
        "hourly_events": {
            "2025-09-28T14": 25,
            "2025-09-28T15": 18
        },
        "top_ips": {
            "192.168.1.100": 45,
            "10.0.0.1": 23
        },
        "recent_events": [...]
    }
}
```

### 2. Bloquear IP
```bash
POST /security/block-ip/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "ip_address": "192.168.1.100",
    "duration_hours": 24,
    "reason": "Suspicious activity detected"
}
```

### 3. Desbloquear IP
```bash
POST /security/unblock-ip/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "ip_address": "192.168.1.100"
}
```

### 4. Logs de Seguridad
```bash
GET /security/logs/?limit=50&event_type=LOGIN_FAILED
Authorization: Bearer <admin_token>
```

---

## 🎛️ Sistema de Permisos

### Roles Implementados
- **admin**: Acceso completo (all)
- **manager**: Lectura, escritura, calibración, reportes
- **operator**: Lectura y calibración
- **viewer**: Solo lectura

### Decoradores de Protección
```python
@jwt_required                    # Requiere autenticación
@permission_required('read')     # Requiere permiso específico
@admin_required                  # Solo administradores
@sensitive_endpoint              # Endpoints sensibles con logging extra
@rate_limit_protected           # Limitación de velocidad
```

---

## ⚡ Rate Limiting

### Límites Configurados
- **Login**: 5 intentos por minuto por IP
- **API General**: 100 requests por minuto por IP
- **Endpoints Sensibles**: 5 requests por minuto
- **Token Refresh**: 3 intentos por minuto

### Respuesta de Rate Limit
```json
{
    "error": "Rate limit exceeded",
    "status": 429
}
```

---

## 🔍 Detección de Amenazas

### Patrones Detectados Automáticamente
- **SQL Injection**: `UNION SELECT`, `OR 1=1`, `DROP TABLE`
- **Directory Traversal**: `../../../`, `..\\`
- **XSS**: `<script>`, `javascript:`
- **User Agents Sospechosos**: `sqlmap`, `nikto`, `nmap`
- **Ataques de Fuerza Bruta**: Múltiples intentos de login fallidos

### Acciones Automáticas
- **Bloqueo temporal de IP** (después de 5 intentos fallidos)
- **Logging de seguridad** con todos los detalles
- **Alertas por email** (si está configurado)
- **Respuesta inmediata** con código 403/429

---

## 📊 Logging de Seguridad

### Archivos de Log
- `crystals_api.log` - Logs generales de la aplicación
- `security.log` - Eventos de seguridad específicos

### Eventos Registrados
- `LOGIN_SUCCESS/FAILED` - Intentos de autenticación
- `JWT_INVALID/MISSING` - Problemas con tokens
- `SUSPICIOUS_REQUEST_BLOCKED` - Requests bloqueados
- `RATE_LIMIT_EXCEEDED` - Límites excedidos
- `IP_BLOCKED/UNBLOCKED` - Gestión de IPs
- `BRUTE_FORCE_DETECTED` - Ataques detectados

### Formato de Log
```
[SECURITY] 2025-09-28 15:30:45 WARNING LOGIN_FAILED - Wrong password for user: admin - IP: 192.168.1.100 - User: admin
```

---

## 🔧 Configuración Adicional

### Variables de Entorno (Opcional)
```env
# Email para alertas de seguridad
SECURITY_ALERT_EMAIL=admin@empresa.com
DEFAULT_FROM_EMAIL=noreply@crystals-api.com

# Lista blanca de IPs (producción)
IP_WHITELIST=192.168.1.0/24,10.0.0.0/16
```

### Headers de Seguridad Agregados
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

---

## 🚀 Migración de Endpoints Existentes

Los siguientes endpoints ya están protegidos:
- `/calibration/*` - Requiere autenticación y permisos
- `/user/validate` - Rate limiting aplicado
- Todos los endpoints sensibles tienen logging

### Para Proteger Endpoints Adicionales
```python
from crystals_app.decorators import jwt_required, permission_required

@jwt_required
@permission_required('read')
def mi_endpoint_protegido(request):
    # Tu código aquí
    pass
```

---

## ⚠️ Consideraciones de Seguridad

1. **Tokens JWT**: Expiran en 1 hora, refresh tokens en 7 días
2. **Rate Limiting**: Se aplica por IP, ajustar según necesidades
3. **CORS**: Configurado para desarrollo, ajustar para producción
4. **HTTPS**: Obligatorio en producción
5. **Logging**: Revisar regularmente los logs de seguridad
6. **Alertas**: Configurar email para recibir notificaciones

---

## 🧪 Ejemplos de Testing

### Test de Autenticación
```bash
# 1. Login
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# 2. Usar token en request protegido
curl -X GET http://localhost:8000/calibration/list \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# 3. Refresh token
curl -X POST http://localhost:8000/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "refresh_token_aqui"}'
```

### Test de Rate Limiting
```bash
# Múltiples requests rápidos para activar rate limiting
for i in {1..10}; do
  curl -X POST http://localhost:8000/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"username": "wrong", "password": "wrong"}'
done
```

---

## 🎯 Próximos Pasos Recomendados

1. **Configurar HTTPS** en producción
2. **Establecer alertas por email** para eventos críticos  
3. **Implementar backup** de logs de seguridad
4. **Configurar monitoreo** con herramientas externas
5. **Realizar pruebas de penetración** regulares
6. **Actualizar dependencias** de seguridad regularmente

---

**¡Tu API Crystals ahora tiene un sistema de seguridad de nivel empresarial! 🛡️**