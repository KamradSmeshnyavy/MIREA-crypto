@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

for %%I in ("%SCRIPT_DIR%\..") do set "PROJECT_ROOT=%%~fI"
set "PYTHON=%PROJECT_ROOT%\.venv\Scripts\python.exe"
set "VENV_DIR=%PROJECT_ROOT%\.venv"
set "APP_DIR=%PROJECT_ROOT%\app"
set "ENTRY=%APP_DIR%\main.py"
set "TESTS_DIR=%PROJECT_ROOT%\tests"
set "REQ_ROOT=%PROJECT_ROOT%\requirements.txt"
set "REQ_APP=%APP_DIR%\requirements.txt"
set "SYS_PYTHON="

call :ensure_venv_and_deps
if errorlevel 1 exit /b 1

if not exist "%ENTRY%" (
  echo Entry file not found: "%ENTRY%"
  exit /b 1
)

:menu
echo.
echo Выберите действие:
echo 1^) Запуск без сборки
echo 2^) Сборка приложения ^(Windows^)
echo 3^) Запуск тестов
echo 4^) Выход
choice /c 1234 /n /m "#? "

if errorlevel 4 goto :end
if errorlevel 3 goto :tests
if errorlevel 2 goto :build
if errorlevel 1 goto :run
goto :menu

:run
"%PYTHON%" "%ENTRY%"
goto :end

:build
echo Устанавливаю/обновляю pyinstaller...
"%PYTHON%" -m pip install --upgrade pyinstaller
if errorlevel 1 exit /b 1

echo Собираю приложение для Windows...
"%PYTHON%" -m PyInstaller --noconfirm --windowed --onefile ^
  --name "crypto-practice" ^
  --distpath "%APP_DIR%\dist" ^
  --workpath "%APP_DIR%\build" ^
  "%ENTRY%"
if errorlevel 1 exit /b 1

echo Готово. Смотрите "%APP_DIR%\dist\"
goto :end

:tests
if not exist "%TESTS_DIR%" (
  echo Каталог tests не найден: "%TESTS_DIR%"
  exit /b 1
)

echo Устанавливаю/обновляю pytest...
"%PYTHON%" -m pip install --upgrade pytest
if errorlevel 1 exit /b 1

echo Запускаю тесты...
"%PYTHON%" -m pytest "%TESTS_DIR%"
goto :end

:end
endlocal
goto :eof

:ensure_venv_and_deps
if not exist "%PYTHON%" (
  echo Python venv not found. Создаю окружение...

  call :resolve_python
  if not defined SYS_PYTHON (
    echo Системный Python не найден. Пытаюсь установить автоматически...
    call :install_python
    if errorlevel 1 exit /b 1
    call :resolve_python
  )

  if not defined SYS_PYTHON (
    echo Не удалось найти Python после установки.
    exit /b 1
  )

  call :normalize_sys_python
  if not defined SYS_PYTHON (
    echo Найден некорректный путь к Python.
    exit /b 1
  )

  "%SYS_PYTHON%" -m venv "%VENV_DIR%"

  if errorlevel 1 (
    echo Не удалось создать виртуальное окружение.
    exit /b 1
  )
)

if not exist "%PYTHON%" (
  echo Python в venv не найден: "%PYTHON%"
  exit /b 1
)

echo Обновляю pip...
"%PYTHON%" -m pip install --upgrade pip
if errorlevel 1 exit /b 1

if exist "%REQ_ROOT%" (
  echo Устанавливаю зависимости из "%REQ_ROOT%"...
  "%PYTHON%" -m pip install -r "%REQ_ROOT%"
  if errorlevel 1 exit /b 1
  goto :eof
)

if exist "%REQ_APP%" (
  echo Устанавливаю зависимости из "%REQ_APP%"...
  "%PYTHON%" -m pip install -r "%REQ_APP%"
  if errorlevel 1 exit /b 1
  goto :eof
)

echo Файл requirements.txt не найден. Ставлю базовые зависимости...
"%PYTHON%" -m pip install --upgrade PySide6 pytest
if errorlevel 1 exit /b 1
goto :eof

:resolve_python
set "SYS_PYTHON="

where py >nul 2>&1
if not errorlevel 1 (
  for /f "usebackq delims=" %%P in (`py -3 -c "import sys; print(sys.executable)" 2^>nul`) do (
    if exist "%%~P" set "SYS_PYTHON=%%~P"
  )
)

if defined SYS_PYTHON goto :eof

where python >nul 2>&1
if not errorlevel 1 (
  for /f "usebackq delims=" %%P in (`python -c "import sys; print(sys.executable)" 2^>nul`) do (
    if exist "%%~P" set "SYS_PYTHON=%%~P"
  )
)

if defined SYS_PYTHON goto :eof

if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "SYS_PYTHON=%LocalAppData%\Programs\Python\Python312\python.exe"
if defined SYS_PYTHON goto :eof
if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set "SYS_PYTHON=%LocalAppData%\Programs\Python\Python311\python.exe"
if defined SYS_PYTHON goto :eof
if exist "%ProgramFiles%\Python312\python.exe" set "SYS_PYTHON=%ProgramFiles%\Python312\python.exe"
if defined SYS_PYTHON goto :eof
if exist "%ProgramFiles%\Python311\python.exe" set "SYS_PYTHON=%ProgramFiles%\Python311\python.exe"
goto :eof

:normalize_sys_python
set "SYS_PYTHON=%SYS_PYTHON:\=\%"
set "SYS_PYTHON=%SYS_PYTHON:"=%"
if not exist "%SYS_PYTHON%" set "SYS_PYTHON="
goto :eof

:install_python
where winget >nul 2>&1
if not errorlevel 1 (
  echo Устанавливаю Python 3 через winget...
  winget install --id Python.Python.3.12 --exact --accept-package-agreements --accept-source-agreements --scope user
  if not errorlevel 1 goto :eof
  echo winget-установка не удалась, пробую direct installer...
)

set "PY_URL=https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
set "PY_INSTALLER=%TEMP%\python-3.12.8-amd64.exe"

where powershell >nul 2>&1
if errorlevel 1 (
  echo Не найден PowerShell, не могу скачать Python автоматически.
  echo Установите Python вручную: https://www.python.org/downloads/windows/
  exit /b 1
)

echo Скачиваю Python installer...
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PY_URL%' -OutFile '%PY_INSTALLER%'"
if errorlevel 1 (
  echo Не удалось скачать Python installer.
  exit /b 1
)

echo Устанавливаю Python silently...
"%PY_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_pip=1 Include_launcher=1
if errorlevel 1 (
  echo Не удалось установить Python через installer.
  exit /b 1
)

echo Python установлен.
goto :eof
