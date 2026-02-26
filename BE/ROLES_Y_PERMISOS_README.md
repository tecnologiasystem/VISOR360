# Sistema de Roles y Permisos - Documentación

## 📋 Resumen
Este sistema maneja la autenticación y autorización de usuarios mediante roles con acceso simple (Sí/No) a cada módulo del sistema.

## 🗄️ Estructura de Base de Datos

### Tabla Rol:
```sql
RolID INT PRIMARY KEY
NombreRol VARCHAR(100)
TorreDeControl BIT    -- 1 = Sí, 0 = No
Financiero BIT        -- 1 = Sí, 0 = No  
RecursosHumanos BIT   -- 1 = Sí, 0 = No
```

### Tabla Usuario (modificada):
Se agregó la columna `RolID` para asignar un rol a cada usuario.

### Módulos del Sistema:
- **Torre de Control**
- **Financiero**
- **Recursos Humanos**

## 🔐 Flujo de Autenticación

### 1. Login (ya existente)
```http
POST /usuarios/login
Content-Type: application/json

{
  "correo": "usuario@ejemplo.com",
  "clave": "contraseña123"
}
```

**Respuesta:**
```json
{
  "UsuarioID": 5
}
```

### 2. Obtener Usuario con Rol y Permisos (NUEVA API)
```http
GET /roles/usuario/5/permisos
```

**Respuesta:**
```json
{
  "usuario": {
    "UsuarioID": 5,
    "Correo": "usuario@ejemplo.com",
    "NombreCompleto": "Juan Pérez"
  },
  "rol": {
    "RolID": 2,
    "NombreRol": "Gerente Financiero"
  },
  "permisos": {
    "torre_de_control": true,
    "financiero": true,
    "recursos_humanos": false
  }
}
```

## 📌 Endpoints Disponibles

### 1. Obtener permisos de un usuario (Principal)
```http
GET /roles/usuario/{usuario_id}/permisos
```
- Devuelve UsuarioID, RolID y acceso a cada módulo (true/false)
- Usa este endpoint después del login

### 2. Listar todos los roles
```http
GET /roles/listar
```
**Respuesta:**
```json
{
  "total_roles": 4,
  "roles": [
    {
      "RolID": 1,
      "NombreRol": "Administrador",
      "TorreDeControl": true,
      "Financiero": true,
      "RecursosHumanos": true,
      "FechaCreacion": "2025-11-25 10:30:00"
    },
    {
      "RolID": 2,
      "NombreRol": "Gerente Financiero",
      "TorreDeControl": true,
      "Financiero": true,
      "RecursosHumanos": false,
      "FechaCreacion": "2025-11-25 10:30:00"
    }
  ]
}
```

### 3. Obtener un rol específico
```http
GET /roles/{rol_id}
```

## 🎭 Roles por Defecto

1. **Administrador** (RolID: 1)
   - Torre de Control: ✅ Sí
   - Financiero: ✅ Sí
   - Recursos Humanos: ✅ Sí

2. **Gerente Financiero** (RolID: 2)
   - Torre de Control: ✅ Sí
   - Financiero: ✅ Sí
   - Recursos Humanos: ❌ No

3. **Gerente RRHH** (RolID: 3)
   - Torre de Control: ❌ No
   - Financiero: ❌ No
   - Recursos Humanos: ✅ Sí

4. **Analista Financiero** (RolID: 4)
   - Torre de Control: ✅ Sí
   - Financiero: ❌ No
   - Recursos Humanos: ❌ No

## 🚀 Pasos de Implementación

### 1. Ejecutar el script SQL
Ejecuta el archivo `database_roles_permisos.sql` en tu base de datos para crear la tabla Rol y los roles iniciales.

### 2. Asignar roles a usuarios existentes
```sql
-- Ejemplo: asignar rol de Administrador al usuario con ID 1
UPDATE Usuario SET RolID = 1 WHERE UsuarioID = 1;

-- Ejemplo: asignar rol de Gerente Financiero al usuario con ID 2
UPDATE Usuario SET RolID = 2 WHERE UsuarioID = 2;
```
sss

```javascript
// 1. Login
const loginResponse = await fetch('/usuarios/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    correo: 'usuario@ejemplo.com',
    clave: 'password123'
  })
});
const { UsuarioID } = await loginResponse.json();

// 2. Obtener permisos del usuario
const permisosResponse = await fetch(`/roles/usuario/${UsuarioID}/permisos`);
const userData = await permisosResponse.json();

// 3. Guardar en estado o localStorage
localStorage.setItem('usuario', JSON.stringify(userData));

// 4. Verificar permisos antes de mostrar módulos
if (userData.permisos.torre_de_control) {
  // Mostrar módulo Torre de Control
}

if (userData.permisos.financiero) {
  // Mostrar módulo Financiero
}

if (userData.permisos.recursos_humanos) {
  // Mostrar módulo Recursos Humanos
}
```

## 📝 Notas Importantes

- Cada usuario debe tener un `RolID` asignado en la tabla Usuario
- Los permisos son simples: cada rol tiene acceso (Sí/No) a cada módulo
- Puedes crear nuevos roles según tus necesidades
- La API principal es `/roles/usuario/{usuario_id}/permisos` que se usa después del login

## 🔧 Personalización

### Crear un nuevo rol:
```sql
INSERT INTO Rol (NombreRol, TorreDeControl, Financiero, RecursosHumanos) 
VALUES ('Supervisor', 1, 0, 1);
-- Este rol tiene acceso a Torre de Control y Recursos Humanos, pero no a Financiero
```

### Modificar permisos de un rol existente:
```sql
-- Dar acceso a Financiero al rol Gerente RRHH (RolID = 3)
UPDATE Rol 
SET Financiero = 1 
WHERE RolID = 3;
```

### Ver todos los roles con sus permisos:
```sql
SELECT 
    RolID,
    NombreRol,
    CASE WHEN TorreDeControl = 1 THEN 'Sí' ELSE 'No' END AS TorreDeControl,
    CASE WHEN Financiero = 1 THEN 'Sí' ELSE 'No' END AS Financiero,
    CASE WHEN RecursosHumanos = 1 THEN 'Sí' ELSE 'No' END AS RecursosHumanos
FROM Rol;
```
