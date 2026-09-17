# Visor360

Aplicación fullstack compuesta por:

- Backend en Python con FastAPI
- Frontend en React + Vite
- Base de datos SQL Server
- Configuración para despliegue en IIS

## Estructura del proyecto

- `BE/` → API backend
- `FE/` → frontend React
- `web.config` → configuración de IIS para el frontend

## Requisitos previos

Antes de levantar el proyecto, asegúrate de tener instalado:

- Python 3.10 o superior
- Node.js 18 o superior
- npm
- SQL Server Driver ODBC 17 para Windows
- Acceso a la base de datos utilizada por la API

> Importante: el backend usa `pyodbc` y depende de la conexión a SQL Server configurada en `BE/app/database.py`.

## 1) Levantar el backend

Desde la carpeta raíz del proyecto:

```bash
cd BE
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Luego inicia la API:

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

La API quedará disponible en:

- http://localhost:8001
- Documentación Swagger: http://localhost:8001/docs
- Redoc: http://localhost:8001/redoc

Si quieres verificar que levantó correctamente, revisa el endpoint raíz:

```bash
curl http://localhost:8001/
```

Debe devolver algo como:

```json
{"message": "Bienvenido a la API de Visor360 🚀"}
```

## 2) Levantar el frontend

Abre otra terminal y ejecuta:

```bash
cd FE
npm install
npm run dev
```

El frontend quedará disponible en:

- http://localhost:5175

La configuración de Vite ya está preparada para hacer proxy de `/api` hacia el backend en `http://localhost:8001` según se ve en `FE/vite.config.js`.

## 3) Ejecutarlo en conjunto

Para trabajar en desarrollo normalmente debes correr ambos procesos:

1. Backend en `BE/`
2. Frontend en `FE/`

El frontend consumirá la API a través de la ruta `/api`, mientras que el backend escucha en el puerto `8001`.

## 4) Build de producción

Cuando quieras compilar el frontend para producción:

```bash
cd FE
npm run build
```

Esto genera la carpeta `dist/` lista para desplegar en IIS o cualquier servidor estático.

## 5) Variables y configuración importante

### Backend
El backend usa conexiones directas a SQL Server en:

- `BE/app/database.py`

Si cambian credenciales, host o base de datos, debes ajustarlas allí antes de iniciar la API.

### Frontend
La configuración del cliente API está en:

- `FE/src/api.js`

Y el proxy de desarrollo está en:

- `FE/vite.config.js`

## 6) Solución de problemas comunes

### Error: `pyodbc` no se instala
Asegúrate de tener instalado el driver ODBC de Microsoft:

- ODBC Driver 17 for SQL Server

### Error de conexión a SQL Server
Revisa:

- El servidor
- La base de datos
- El usuario
- La contraseña
- El archivo `BE/app/database.py`

### El frontend no carga datos
Verifica que el backend esté levantado en puerto `8001` y que el frontend pueda llegar a `/api`.

### El puerto 5175 ya está ocupado
Puedes cambiar el puerto en `FE/vite.config.js` o ejecutar:

```bash
npm run dev -- --host 0.0.0.0 --port 4173
```

## 7) Flujo recomendado para empezar

```bash
cd BE
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

En otra terminal:

```bash
cd FE
npm install
npm run dev
```

## 8) Despliegue

Para un despliegue en Windows Server/IIS, el frontend puede servir el contenido generado por `npm run build` y el backend puede correr como servicio o aplicación FastAPI con uvicorn detrás de IIS o un reverse proxy.

El archivo `web.config` ya está preparado como base para IIS.

---

Si quieres, también puedo dejarte un segundo README más orientado a producción o crear un script de arranque para levantar backend y frontend con un solo comando.
