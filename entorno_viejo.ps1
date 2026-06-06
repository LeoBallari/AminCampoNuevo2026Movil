# 1. Limpieza absoluta de variables de entornos virtuales previos
Remove-Item Env:\VIRTUAL_ENV -ErrorAction SilentlyContinue
$env:Path = ($env:Path -split ';' | Where-Object { $_ -notmatch 'venv' }) -join ';'

# 2. Asegurar que estamos en la raíz y luego ir a frontend (viejo)
cd C:\Python\AminCampoNuevo2026Movil
cd frontend

# 3. Activar el entorno virtual viejo
..\venv\Scripts\activate

# 4. Forzar la ruta de Java 17 al principio del Path
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot"
$env:Path = "$env:JAVA_HOME\bin;" + $env:Path

# 5. Limpiar la pantalla y verificar
Clear-Host
Write-Host "=============================================" -ForegroundColor Yellow
Write-Host " ENTORNO VIEJO ACTIVADO (Flet 0.28.3 + JDK 17)" -ForegroundColor Yellow
Write-Host "=============================================" -ForegroundColor Yellow
python --version
java -version
if (Get-Command flet -ErrorAction SilentlyContinue) { flet --version } else { Write-Host "Flet: No instalado" }
Write-Host "=============================================" -ForegroundColor Yellow