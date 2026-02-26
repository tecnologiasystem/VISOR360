# 🔐 Sistema de Gestión de Permisos

Sistema completo para gestionar usuarios, roles, campañas e inversionistas en la aplicación Visor 360.

## 📋 Características

### 1. Gestión de Usuarios
- ✅ Crear, editar y eliminar usuarios
- ✅ Asignar roles a usuarios
- ✅ Ver permisos heredados del rol
- ✅ Ver campañas e inversionistas accesibles

### 2. Gestión de Roles
- ✅ Crear, editar y eliminar roles
- ✅ Configurar permisos por módulo:
  - Torre de Control
  - Financiero
  - Recursos Humanos
- ✅ Asignar campañas a roles
- ✅ Los inversionistas se heredan automáticamente de las campañas

### 3. Sistema de Permisos
- **Nivel 1 - Módulos**: Control de acceso a Torre, Financiero, RRHH
- **Nivel 2 - Campañas**: Qué campañas puede ver un rol (NPL COL, ACC, etc.)
- **Nivel 3 - Inversionistas**: Se heredan de las campañas asignadas

## 🗄️ Estructura de Base de Datos

```
RolQA
├── RolID (PK)
├── NombreRol
├── TorreDeControl (bit)
├── Financiero (bit)
└── RecursosHumanos (bit)

UsuariosQA
├── IDUsuarioQA (PK)
├── NombreUsuarioQA
├── EmailUsuarioQA
└── IDRol (FK → RolQA)

CampanasQA
├── IDCampanasQA (PK)
├── NombreCampana
└── IDUsuarioLider (FK → UsuariosQA)

InversionistaQA
├── IDInversionistaQA (PK)
├── NombreInversionistaQA
└── EsActivo (bit)

CampanasRolesQA (Relación N:M)
├── IDCampanasRolesQA (PK)
├── IDCampanasQA (FK → CampanasQA)
└── IDRol (FK → RolQA)

CampanasInversionistasQA (Relación N:M)
├── IDCampanasInversionistasQA (PK)
├── IDCampanasQA (FK → CampanasQA)
└── IDInversionistaQA (FK → InversionistaQA)
```

## 🚀 Instalación y Configuración

### 1. Crear las Tablas
```bash
# Ejecutar el script SQL para crear las tablas
sqlcmd -S localhost -d LOGS -i BE/database_roles_permisos.sql
```

### 2. Poblar Datos de Ejemplo
```bash
# Insertar roles, usuarios y campañas de ejemplo
sqlcmd -S localhost -d LOGS -i BE/database/seed_permisos_data.sql
```

### 3. Backend (FastAPI)
El backend ya está configurado con:
- ✅ `app/dal/permisos_dal.py` - Acceso a datos
- ✅ `app/bll/permisos_bll.py` - Lógica de negocio
- ✅ `app/api/permisos_api.py` - Endpoints REST
- ✅ Registrado en `main.py` como `/api/permisos`

### 4. Frontend (React)
- ✅ Componente: `src/pages/GestionPermisos.jsx`
- ✅ Ruta: `/permisos`
- ✅ Agregado al menú de navegación

## 📡 API Endpoints

### Usuarios
```
GET    /api/permisos/usuarios                  # Listar todos
GET    /api/permisos/usuarios/{id}            # Obtener uno con permisos
POST   /api/permisos/usuarios                  # Crear
PUT    /api/permisos/usuarios/{id}            # Actualizar
DELETE /api/permisos/usuarios/{id}            # Eliminar
```

### Roles
```
GET    /api/permisos/roles                     # Listar todos
POST   /api/permisos/roles                     # Crear
PUT    /api/permisos/roles/{id}               # Actualizar
DELETE /api/permisos/roles/{id}               # Eliminar (solo si sin usuarios)
```

### Campañas
```
GET    /api/permisos/campanas                  # Listar todas
GET    /api/permisos/roles/{id}/campanas      # Campañas de un rol
POST   /api/permisos/roles/{id_rol}/campanas/{id_campana}  # Asignar una
DELETE /api/permisos/roles/{id_rol}/campanas/{id_campana}  # Quitar una
PUT    /api/permisos/roles/{id}/campanas      # Actualizar todas (reemplazar)
```

### Inversionistas
```
GET    /api/permisos/inversionistas                     # Listar todos
GET    /api/permisos/campanas/{id}/inversionistas      # Por campaña
GET    /api/permisos/roles/{id}/inversionistas         # Por rol (heredados)
```

### Validación
```
GET    /api/permisos/usuarios/{id}/validar/{modulo}   # Validar permiso
       modulo: torre_control | financiero | recursos_humanos
```

## 💡 Ejemplos de Uso

### Crear un Usuario
```javascript
POST /api/permisos/usuarios
{
  "nombre": "María González",
  "email": "m.gonzalez@gnpl.com",
  "id_rol": 3
}
```

### Crear un Rol
```javascript
POST /api/permisos/roles
{
  "nombre_rol": "Analista Torre",
  "torre_control": true,
  "financiero": false,
  "recursos_humanos": false
}
```

### Asignar Campañas a un Rol
```javascript
PUT /api/permisos/roles/3/campanas
{
  "ids_campanas": [1, 2]  // NPL COL y ACC
}
```

### Obtener Usuario con Permisos
```javascript
GET /api/permisos/usuarios/35
```
**Respuesta:**
```json
{
  "success": true,
  "data": {
    "id_usuario": 35,
    "nombre": "Juan Camilo Castillo",
    "email": "j.castillo@gnpl.com",
    "id_rol": 1,
    "nombre_rol": "Administrador",
    "permisos_modulos": {
      "torre_control": true,
      "financiero": true,
      "recursos_humanos": true
    },
    "campanas": [
      {"id_campana": 1, "nombre_campana": "NPL COL"},
      {"id_campana": 2, "nombre_campana": "ACC"}
    ],
    "inversionistas": [
      {"id_inversionista": 1, "nombre_inversionista": "BANCOOMEVA"},
      {"id_inversionista": 2, "nombre_inversionista": "IFC"},
      ...
    ]
  }
}
```

## 🎨 Interfaz de Usuario

### Página de Gestión de Permisos (`/permisos`)

**Tab 1: Usuarios**
- Tabla con usuarios, emails, roles y permisos
- Botón "Nuevo Usuario" para crear
- Acciones: Editar, Eliminar
- Tags visuales para permisos de módulos

**Tab 2: Roles**
- Tabla con roles y sus permisos
- Botón "Nuevo Rol" para crear
- Botón "Campañas" para asignar campañas al rol
- Acciones: Editar, Eliminar

**Modal Asignar Campañas**
- Transfer component de Ant Design
- Muestra campañas disponibles vs asignadas
- Búsqueda integrada
- Guarda todas las asignaciones al confirmar

## 🔒 Flujo de Permisos

1. **Admin crea un Rol**
   - Define nombre: "Gerente Financiero"
   - Marca permisos: Torre Control ✓, Financiero ✓

2. **Admin asigna Campañas al Rol**
   - Selecciona: NPL COL, ACC
   - Los inversionistas de estas campañas se heredan automáticamente

3. **Admin crea Usuario**
   - Nombre: "María González"
   - Email: "m.gonzalez@gnpl.com"
   - Asigna Rol: "Gerente Financiero"

4. **Usuario obtiene permisos**
   - ✅ Puede ver Torre de Control y Financiero
   - ✅ Puede ver datos de NPL COL y ACC
   - ✅ Puede ver todos los inversionistas de esas campañas
   - ❌ NO puede ver Recursos Humanos

## 📊 Datos de Ejemplo Incluidos

### Roles
- **Administrador**: Acceso completo
- **Gerente Torre Control**: Solo Torre
- **Gerente Financiero**: Torre + Financiero
- **Gerente RRHH**: Solo RRHH
- **Analista**: Solo visualización Torre

### Usuarios
- Juan Camilo Castillo (Administrador)
- Edilma Fontecha (Gerente Financiero)

### Campañas
- **NPL COL**: BANCOOMEVA, IFC, CREDIVALORES, PA, TUYA
- **ACC**: ACCION, ADAMANTINE, INTERASEO, JCAP, PRA, GERENTE

## 🔄 Próximos Pasos

### Para integrar permisos en las vistas existentes:

1. **Filtrar datos por campaña/inversionista**
```javascript
// En KpiTablero.jsx, Torre de Control, etc.
const campanasPermitidas = user.campanas.map(c => c.nombre_campana);
const inversionistasPermitidos = user.inversionistas.map(i => i.nombre_inversionista);

// Filtrar data
const dataFiltrada = data.filter(item => 
  campanasPermitidas.includes(item.campana) &&
  inversionistasPermitidos.includes(item.inversionista)
);
```

2. **Validar permisos de módulo**
```javascript
// En ProtectedRoute o componentes
const tienePermisoTorre = await api.get(`/permisos/usuarios/${userId}/validar/torre_control`);
if (!tienePermisoTorre.data.data.tiene_permiso) {
  navigate('/sin-acceso');
}
```

3. **Ocultar opciones según permisos**
```javascript
// En GestionMetas.jsx
{user.permisos?.torre_control && (
  <Button>Modificar Metas</Button>
)}
```

## 📝 Notas Técnicas

- Los inversionistas se asignan a nivel de **campaña**, no de rol
- Un rol puede tener múltiples campañas
- Los usuarios heredan todos los permisos de su rol
- Para cambiar permisos de un usuario, cambiar su rol o modificar el rol mismo
- Al eliminar un rol, debe no tener usuarios asignados

## 🐛 Troubleshooting

**Error: "No se puede eliminar el rol"**
- Verificar que no haya usuarios con ese rol asignado
- Reasignar usuarios a otro rol primero

**Usuario no ve campañas**
- Verificar que el rol tenga campañas asignadas en `CampanasRolesQA`
- Ejecutar: `SELECT * FROM CampanasRolesQA WHERE IDRol = X`

**Inversionistas no aparecen**
- Verificar relación en `CampanasInversionistasQA`
- Los inversionistas vienen de las campañas, no se asignan directamente

## 📞 Soporte

Para dudas o problemas, contactar al equipo de desarrollo.
