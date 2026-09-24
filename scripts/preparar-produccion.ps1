# ============================================================
# VISOR360 - Preparar la maquina de produccion (172.17.20.121)
# ============================================================
# Que hace este script:
#   1. Verifica que estas en la raiz del repo clonado.
#   2. Instala dependencias del backend (venv + requirements.txt).
#   3. Instala dependencias del frontend y genera el build (dist/).
#   4. AVISA de los archivos que NO viajan por git y hay que copiar a mano:
#        - BE/.env             (credenciales; recrear desde BE/.env.example)
#        - BE/datos/*.xlsx     (Excel financiero, ~19 MB)
#
# NO hace:
#   - No inventa credenciales ni las descarga. El .env lo pones tu.
#   - No configura IIS (eso es en el Administrador de IIS; ver README/prod).
#
# Uso (desde la raiz del repo, en PowerShell):
#   powershell -ExecutionPolicy Bypass -File .\scripts\preparar-produccion.ps1
# ============================================================

$ErrorActionPreference = "Stop"

function Info($m)  { Write-Host "[INFO]  $m" -ForegroundColor Cyan }
function Ok($m)    { Write-Host "[OK]    $m" -ForegroundColor Green }
function Warn($m)  { Write-Host "[AVISO] $m" -ForegroundColor Yellow }
function Fail($m)  { Write-Host "[ERROR] $m" -ForegroundColor Red }

# --- 0. Comprobar que estamos en la raiz del repo ---
if (-not (Test-Path ".\BE\main.py") -or -not (Test-Path ".\FE\package.json")) {
    Fail "No encuentro BE\main.py y FE\package.json. Ejecuta el script desde la RAIZ del repo VISOR360."
    exit 1
}
Ok "Raiz del repo detectada: $(Get-Location)"

# --- 1. Backend: venv + dependencias ---
Info "Preparando backend (BE)..."
Push-Location ".\BE"
if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Info "Creando entorno virtual .venv..."
    python -m venv .venv
} else {
    Info "Entorno virtual .venv ya existe."
}
Info "Instalando requirements.txt..."
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip | Out-Null
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
Ok "Backend instalado."
Pop-Location

# --- 2. Frontend: npm install + build ---
Info "Preparando frontend (FE)..."
Push-Location ".\FE"
Info "npm install..."
& npm install
Info "npm run build (genera dist/ para IIS)..."
& npm run build
Ok "Frontend compilado en FE\dist."
Pop-Location

# --- 3. Verificar los archivos que NO viajan por git ---
Write-Host ""
Info "Comprobando archivos que NO vienen de git (hay que copiarlos a mano):"

$envOk = Test-Path ".\BE\.env"
if ($envOk) {
    Ok "BE\.env existe."
} else {
    Warn "FALTA BE\.env  ->  copialo desde la maquina origen, o recrealo desde BE\.env.example"
    Warn "            (sin el, las conexiones a SQL Server fallan; el modulo financiero NO usa SQL)"
}

$excel = Get-ChildItem ".\BE\datos" -Filter "*.xlsx" -ErrorAction SilentlyContinue
if ($excel) {
    Ok "Excel financiero presente: $($excel[0].Name) ($([math]::Round($excel[0].Length/1MB,2)) MB)"
} else {
    Warn "FALTA el Excel en BE\datos\  ->  copia 'Dashboard Excel Tables ...xlsx' desde la maquina origen"
    Warn "            (sin el, el tablero de Analisis Financiero no muestra datos)"
}

# --- 4. Recordatorio final ---
Write-Host ""
Write-Host "================= SIGUIENTE PASOS (manuales) =================" -ForegroundColor Yellow
Write-Host "1) IIS:" -ForegroundColor Yellow
Write-Host "   - Crea el sitio apuntando a  ...\VISOR360\FE\dist" -ForegroundColor Yellow
Write-Host "   - Asegura que IIS tenga ARR (Application Request Routing) + URL Rewrite" -ForegroundColor Yellow
Write-Host "     para que 'web.config' proxye /api -> http://localhost:8001" -ForegroundColor Yellow
Write-Host ""
Write-Host "2) Backend (como servicio de Windows, ej. NSSM):" -ForegroundColor Yellow
Write-Host "   .\BE\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8001" -ForegroundColor Yellow
Write-Host "   (trabajando desde la carpeta BE)" -ForegroundColor Yellow
Write-Host ""
Write-Host "3) ROTAR las contrasenas SQL expuestas (172.18.79.20 y 172.18.72.111)" -ForegroundColor Red
Write-Host "   y actualizar BE\.env con las nuevas." -ForegroundColor Red
Write-Host "==============================================================" -ForegroundColor Yellow