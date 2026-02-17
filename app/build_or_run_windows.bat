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
set "LOCAL_APPDATA=%LocalAppData%"
if "%LOCAL_APPDATA%"=="" set "LOCAL_APPDATA=%USERPROFILE%\AppData\Local"
set "PROGRAM_FILES=%ProgramFiles%"
if "%PROGRAM_FILES%"=="" set "PROGRAM_FILES=C:\Program Files"

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
  call :normalize_sys_python
  if "%SYS_PYTHON%"=="" (
    echo Системный Python не найден. Пытаюсь установить автоматически...
    call :install_python
    if errorlevel 1 exit /b 1
    call :resolve_python
    call :normalize_sys_python
  )

  if "%SYS_PYTHON%"=="" (
    echo Не удалось найти Python после установки.
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

if exist "%SystemRoot%\py.exe" (
  for /f "usebackq delims=" %%P in (`"%SystemRoot%\py.exe" -3 -c "import sys; print(sys.executable)" 2^>nul`) do call :set_python_candidate "%%P"
)

if not "%SYS_PYTHON%"=="" goto :eof

if exist "%LOCAL_APPDATA%\Programs\Python\Launcher\py.exe" (
  for /f "usebackq delims=" %%P in (`"%LOCAL_APPDATA%\Programs\Python\Launcher\py.exe" -3 -c "import sys; print(sys.executable)" 2^>nul`) do call :set_python_candidate "%%P"
)

if not "%SYS_PYTHON%"=="" goto :eof

where py >nul 2>&1
if not errorlevel 1 (
  for /f "usebackq delims=" %%P in (`py -3 -c "import sys; print(sys.executable)" 2^>nul`) do call :set_python_candidate "%%P"
)

if not "%SYS_PYTHON%"=="" goto :eof

where python >nul 2>&1
if not errorlevel 1 (
  for /f "usebackq delims=" %%P in (`python -c "import sys; print(sys.executable)" 2^>nul`) do call :set_python_candidate "%%P"
)

if not "%SYS_PYTHON%"=="" goto :eof

if exist "%LOCAL_APPDATA%\Programs\Python\Python312\python.exe" set "SYS_PYTHON=%LOCAL_APPDATA%\Programs\Python\Python312\python.exe"
if defined SYS_PYTHON goto :eof
if exist "%LOCAL_APPDATA%\Programs\Python\Python311\python.exe" set "SYS_PYTHON=%LOCAL_APPDATA%\Programs\Python\Python311\python.exe"
if defined SYS_PYTHON goto :eof
if exist "%PROGRAM_FILES%\Python312\python.exe" set "SYS_PYTHON=%PROGRAM_FILES%\Python312\python.exe"
if defined SYS_PYTHON goto :eof
if exist "%PROGRAM_FILES%\Python311\python.exe" set "SYS_PYTHON=%PROGRAM_FILES%\Python311\python.exe"
if defined SYS_PYTHON goto :eof
if exist "%LOCAL_APPDATA%\Microsoft\WindowsApps\python.exe" set "SYS_PYTHON=%LOCAL_APPDATA%\Microsoft\WindowsApps\python.exe"
if defined SYS_PYTHON goto :eof

call :set_python_from_reg "HKCU\Software\Python\PythonCore\3.12\InstallPath"
if defined SYS_PYTHON goto :eof
call :set_python_from_reg "HKLM\Software\Python\PythonCore\3.12\InstallPath"
if defined SYS_PYTHON goto :eof
call :set_python_from_reg "HKCU\Software\Python\PythonCore\3.11\InstallPath"
if defined SYS_PYTHON goto :eof
call :set_python_from_reg "HKLM\Software\Python\PythonCore\3.11\InstallPath"
if defined SYS_PYTHON goto :eof

for /f "usebackq delims=" %%P in (`where /r "%LOCAL_APPDATA%\Programs\Python" python.exe 2^>nul`) do call :set_python_candidate "%%P"
if defined SYS_PYTHON goto :eof
for /f "usebackq delims=" %%P in (`where /r "%PROGRAM_FILES%" python.exe 2^>nul`) do call :set_python_candidate "%%P"
goto :eof

:set_python_candidate
set "CANDIDATE=%~1"
if "%CANDIDATE%"=="" goto :eof
if exist "%CANDIDATE%" set "SYS_PYTHON=%CANDIDATE%"
goto :eof

:set_python_from_reg
set "REG_KEY=%~1"
set "REG_PATH="
for /f "tokens=2,*" %%A in ('reg query "%REG_KEY%" /ve 2^>nul ^| find /i "REG_"') do set "REG_PATH=%%B"
if "%REG_PATH%"=="" goto :eof
set "REG_PATH=%REG_PATH:"=%"
if exist "%REG_PATH%python.exe" set "SYS_PYTHON=%REG_PATH%python.exe"
if exist "%REG_PATH%" if /i "%REG_PATH:~-10%"=="python.exe" set "SYS_PYTHON=%REG_PATH%"
goto :eof

:normalize_sys_python
set "SYS_PYTHON=%SYS_PYTHON:"=%"
if "%SYS_PYTHON%"=="" set "SYS_PYTHON=" & goto :eof
if not exist "%SYS_PYTHON%" set "SYS_PYTHON="
goto :eof

:install_python
where winget >nul 2>&1
if not errorlevel 1 (
  echo Устанавливаю Python 3 через winget...
  winget install --id Python.Python.3.12 --exact --accept-package-agreements --accept-source-agreements --scope user
  if errorlevel 1 (
    echo winget-установка не удалась, пробую direct installer...
  ) else (
    call :resolve_python
    call :normalize_sys_python
    if not "%SYS_PYTHON%"=="" goto :eof
    echo Python через winget установлен, но не найден. Пробую direct installer...
  )
)

set "PY_URL=https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe"
set "PY_INSTALLER=%TEMP%\python-3.12.10-amd64.exe"

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
call :resolve_python
call :normalize_sys_python
goto :eof
