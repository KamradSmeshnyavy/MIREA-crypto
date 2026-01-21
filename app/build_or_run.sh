#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$PWD/.."
PYTHON="$PROJECT_ROOT/.venv/bin/python"
APP_DIR="$PROJECT_ROOT/app"
ENTRY="$APP_DIR/main.py"

if [[ ! -x "$PYTHON" ]]; then
  echo "Python venv not found: $PYTHON"
  exit 1
fi

if [[ ! -f "$ENTRY" ]]; then
  echo "Entry file not found: $ENTRY"
  exit 1
fi

echo "Выберите действие:"
select action in "Запуск без сборки" "Сборка приложения" "Запуск тестов" "Выход"; do
  case "$REPLY" in
  1)
    "$PYTHON" "$ENTRY"
    exit 0
    ;;
  2)
    echo "Выберите платформу сборки:"
    select platform in "macOS" "Windows" "Linux" "Назад"; do
      case "$REPLY" in
      1)
        if [[ "$(uname -s)" != "Darwin" ]]; then
          echo "Сборка macOS возможна только на macOS."
          exit 1
        fi
        "$PYTHON" -m pip install --upgrade pyinstaller
        "$PYTHON" -m PyInstaller --noconfirm --windowed --onefile \
          --name "crypto-practice" \
          --distpath "$APP_DIR/dist" \
          --workpath "$APP_DIR/build" \
          "$ENTRY"
        echo "Готово. Смотрите $APP_DIR/dist/"
        exit 0
        ;;
      2)
        case "$(uname -s)" in
        MINGW* | MSYS* | CYGWIN*)
          "$PYTHON" -m pip install --upgrade pyinstaller
          "$PYTHON" -m PyInstaller --noconfirm --windowed --onefile \
            --name "crypto-practice" \
            --distpath "$APP_DIR/dist" \
            --workpath "$APP_DIR/build" \
            "$ENTRY"
          echo "Готово. Смотрите $APP_DIR/dist/"
          exit 0
          ;;
        *)
          echo "Сборка Windows возможна только на Windows."
          exit 1
          ;;
        esac
        ;;
      3)
        if [[ "$(uname -s)" != "Linux" ]]; then
          echo "Сборка Linux возможна только на Linux."
          exit 1
        fi
        "$PYTHON" -m pip install --upgrade pyinstaller
        "$PYTHON" -m PyInstaller --noconfirm --windowed --onefile \
          --name "crypto-practice" \
          --distpath "$APP_DIR/dist" \
          --workpath "$APP_DIR/build" \
          "$ENTRY"
        echo "Готово. Смотрите $APP_DIR/dist/"
        exit 0
        ;;
      4)
        break
        ;;
      *)
        echo "Неверный выбор."
        ;;
      esac
    done
    ;;
  3)
    if [[ ! -d "$PROJECT_ROOT/tests" ]]; then
      echo "Каталог tests не найден: $PROJECT_ROOT/tests"
      exit 1
    fi
    "$PYTHON" -m pip install --upgrade pytest
    "$PYTHON" -m pytest "$PROJECT_ROOT/tests"
    exit 0
    ;;
  4)
    exit 0
    ;;
  *)
    echo "Неверный выбор."
    ;;
  esac
done
