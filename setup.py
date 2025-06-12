import os
from pathlib import Path
from setuptools import setup, find_packages


with open("README.md", "r") as readme_fp:
    readme = readme_fp.read()


def read_requirements():
    """Чтение зависимостей из requirements.txt"""
    with open('requirements.txt') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]


# Преобразуем относительный путь к codecheck_core в абсолютный
BASE_DIR = Path(__file__).parent
CORE_DIR = BASE_DIR / "submodules" / "codecheck_core"

# Проверяем существование директории
if not CORE_DIR.exists():
    raise RuntimeError(f"Directory '{CORE_DIR}' not found!")


setup(name="c-code-check",
      author="Igor Chernousov, Ivan Dugin",
      version="1.0.0",
      packages=find_packages(),

      # включение конфигурационных файлов
      package_data={
          'config_data_package': ['*'],
      },

      include_package_data=True,
      install_requires=[
          # Зависимость на локальный пакет (PEP 508 format)
          f"code-check-core @ file://{CORE_DIR.resolve()}",
          read_requirements()
      ],
      entry_points={
          "console_scripts": [
              "c_code_check = codecheck.__main__:main"  # Точка входа для CLI
          ]
      },
      python_requires='>=3.10',  # Указываем минимальную версию Python
)