.PHONY: help install dev-install clean format lint test

help:  ## Показать это сообщение
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install:  ## Установить зависимости проекта
	uv pip install .

dev-install:  ## Установить зависимости для разработки
	uv pip install -e ".[dev]"

clean:  ## Очистить кэш и временные файлы
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

format:  ## Отформатировать код с помощью ruff
	ruff check . --fix
	ruff format .

lint:  ## Проверить код с помощью ruff и mypy
	ruff check .
	mypy sleep_tracker

test:  ## Запустить тесты
	pytest tests/ -v 