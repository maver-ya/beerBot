import os
from pathlib import Path


def create_beer_bot_structure(base_dir="beer_bot"):
    """Создает структуру проекта beer_bot с пустыми файлами"""

    # Определяем структуру
    structure = {
        "": [
            "requirements.txt",
            "README.md",
            ".env.example",
            "docker-compose.yml"
        ],
        "bot": [
            "main.py",
            "config.py",
            "logger_conf.py",
            "__init__.py"
        ],
        "bot/db": [
            "base.py",
            "session.py",
            "__init__.py"
        ],
        "bot/db/models": [
            "__init__.py",
            "user.py",
            "chat.py",
            "drink.py",
            "achievement.py"
        ],
        "bot/handlers": [
            "__init__.py",
            "start.py",
            "drink.py",
            "stats.py",
            "achievements.py",
            "admin.py",
            "help.py"
        ],
        "bot/services": [
            "__init__.py",
            "stats.py",
            "achievements.py",
            "warnings.py",
            "calculator.py"
        ],
        "bot/states": [
            "__init__.py",
            "drink.py",
            "admin.py"
        ],
        "bot/keyboards": [
            "__init__.py",
            "reply.py",
            "inline.py",
            "builders.py"
        ],
        "bot/middlewares": [
            "__init__.py",
            "throttling.py"
        ],
        "bot/utils": [
            "__init__.py",
            "helpers.py",
            "validators.py"
        ],
        "alembic": [
            "env.py",
            "README",
            "script.py.mako"
        ],
        "alembic/versions": [],
        "tests": [
            "__init__.py",
            "conftest.py",
            "test_handlers.py",
            "test_services.py"
        ],
        "migrations": [],
        "logs": [],
        "data": []
    }

    # Создаем базовую директорию
    base_path = Path(base_dir)

    print(f"Создание структуры проекта beer_bot в: {base_path.absolute()}")
    print("=" * 60)

    # Создаем все директории и файлы
    for directory, files in structure.items():
        # Создаем путь к директории
        dir_path = base_path / directory

        # Создаем директорию (и все родительские, если нужно)
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Создана папка: {dir_path}")

        # Создаем файлы в директории
        for filename in files:
            file_path = dir_path / filename

            # Создаем пустой файл
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("")

            print(f"  📄 Создан файл: {file_path}")

    print("\n" + "=" * 60)
    print(f"✅ Структура проекта успешно создана в папке: {base_path.absolute()}")
    print("=" * 60)


# Запуск создания структуры
if __name__ == "__main__":
    create_beer_bot_structure('D:\\pythonProject\\beerBot')