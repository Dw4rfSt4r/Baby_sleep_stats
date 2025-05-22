#!/bin/bash

# Создание виртуального окружения
echo "Создание виртуального окружения..."
uv venv

# Активация виртуального окружения
source .venv/bin/activate

# Установка зависимостей
echo "Установка зависимостей..."
uv pip install -r requirements-dev.txt

# Создание структуры проекта
echo "Создание структуры проекта..."
mkdir -p sleep_tracker/{core/{models,exceptions},services/{storage,tracker,reports},interfaces/{cli,telegram},data,tests}

# Создание __init__.py файлов
find sleep_tracker -type d -exec touch {}/__init__.py \;

echo "Настройка проекта завершена!" 