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

  where py >nul 2>&1
  if not errorlevel 1 (
    py -3 -m venv "%VENV_DIR%"
  ) else (
    where python >nul 2>&1
    if errorlevel 1 (
      echo Не найден системный Python.
      echo Установите Python 3 и добавьте его в PATH.
      exit /b 1
    )
    python -m venv "%VENV_DIR%"
  )

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
