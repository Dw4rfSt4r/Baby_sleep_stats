@echo off

:: Создание виртуального окружения
echo Создание виртуального окружения...
uv venv

:: Активация виртуального окружения
call .venv\Scripts\activate

:: Установка зависимостей
echo Установка зависимостей...
uv pip install -r requirements-dev.txt

:: Создание структуры проекта
echo Создание структуры проекта...
mkdir sleep_tracker\core\models
mkdir sleep_tracker\core\exceptions
mkdir sleep_tracker\services\storage
mkdir sleep_tracker\services\tracker
mkdir sleep_tracker\services\reports
mkdir sleep_tracker\interfaces\cli
mkdir sleep_tracker\interfaces\telegram
mkdir sleep_tracker\data
mkdir sleep_tracker\tests

:: Создание __init__.py файлов
for /d /r sleep_tracker %%d in (*) do type nul > "%%d\__init__.py"

echo Настройка проекта завершена! 