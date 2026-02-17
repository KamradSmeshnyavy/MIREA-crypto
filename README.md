# MIREA Crypto Practice

Учебное приложение на `PySide6` с реализацией криптографических алгоритмов и GUI.

## Содержимое проекта

- Приложение: [app/main.py](app/main.py)
- Linux/macOS скрипт: [app/build_or_run.sh](app/build_or_run.sh)
- Windows скрипт: [app/build_or_run_windows.bat](app/build_or_run_windows.bat)
- Тесты: [tests/test_algorithms.py](tests/test_algorithms.py)
- Зависимости: [requirements.txt](requirements.txt)

## Быстрый запуск (вручную)

### Windows (cmd)

1. Перейдите в корень проекта.
2. Создайте окружение:

```bat
py -3 -m venv .venv
```

3. Установите зависимости:

```bat
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

4. Запустите приложение:

```bat
.venv\Scripts\python.exe app\main.py
```

### macOS / Linux

1. Перейдите в корень проекта.
2. Создайте окружение и установите зависимости:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

3. Запустите приложение:

```bash
.venv/bin/python app/main.py
```

## Запуск через скрипты

### Windows

Из папки [app](app):

```bat
build_or_run_windows.bat
```

Скрипт умеет:
- запускать приложение;
- запускать тесты;
- собирать `.exe` через `PyInstaller`;
- автоматически создавать `.venv` и ставить зависимости.

### macOS / Linux

Из папки [app](app):

```bash
./build_or_run.sh
```

## Тесты

Запуск тестов вручную:

### Windows

```bat
.venv\Scripts\python.exe -m pytest tests
```

### macOS / Linux

```bash
.venv/bin/python -m pytest tests
```

Признак успешного прохождения: в конце вывода есть строка вида `N passed` и код завершения `0`.

## Сборка приложения

Для сборки используется `PyInstaller`.

- Через меню скриптов: [app/build_or_run.sh](app/build_or_run.sh), [app/build_or_run_windows.bat](app/build_or_run_windows.bat)
- Результат сборки: каталог [app/dist](app/dist)

## Примечания

- На Windows приложение должно использовать Qt-платформу `windows` автоматически.
- На macOS используется `cocoa`.
- На Linux используется `xcb` (если доступен в системе).
