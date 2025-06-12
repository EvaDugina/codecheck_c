# c_code_check
Utility for automatic code check with various tools

### Supports:
- valgrind
- cppcheck
- clang-format (codestyle)
- copydetect
- catch2

### Install     
Clone the repository and run command in root directory:
```bash
pip install .
```
### Usage
```bash
c_code_check [-h] -c config.json [files ...]
```     
| Argument     | Description |
| ------------ | ----------- |
| -h, --help   | show help message and exit|
| -c, --conf   | path to JSON configuration file (default: None) |
| -f, --format | path to clang-format configuration (default: None) |

### Запуск Docker
```bash
docker build -t c_code_check .
docker run -it --rm -v .:/tmp c_code_check
```

---

### Примеры корректного вывода программы

```bash
# c_code_check
Запуск автоматической проверки...
BUILD checked!
CPPCHECK checked!
CLANG-FORMAT checked!
VALGRIND checked!
COPYDETECT checked!
CATCH2 checked!
Автоматичекая проверка завершена!
====
время: 28.0 сек
```

```bash
# c_code_check -c examples/config_all_console.json examples/code_example_1.c     
Запуск автоматической проверки...
BUILD checked!
CPPCHECK checked!
CLANG-FORMAT checked!
COPYDETECT checked!
VALGRIND checked!
CATCH2 checked!
Автоматичекая проверка завершена!
====
время: 28.4 сек
```
----

# API

### TOOLS (общая структура)

##### in config
```python
{
    "tools": {
        ...
    }
}
```

##### in result
```python
{
    "tools": {
        ...
    },
    "error_code": "", # в случае return_code == 1 здесь код ошибки
    "error_text": "", # в случае return_code == 1 здесь текст ошибки
    "return_code": 0 # значения: 0 / 1
}
```

### TOOL (инструмент проверки)
```<tool>```: build / cppcheck / valgrind / clang-format / catch2 / copydetect

##### in config
```python
{
    "<tool>": {
        "enabled": bool, # означает: включена / не включена
        "autoreject": bool, # означает: отклонять / не отклонять при не прохождении предыдущих проверок
        "bin": str, # значения: gcc / g++ / cppcheck / valgrind / clang-format / catch2 / copydetect
        "arguments": str, #строка аргументов вводимых в консоль
        # ВАРИАТИВНЫЕ АРГУМЕНТЫ:
        "compiler": str, # значения (для Valgrind): gcc / g++ 
        "test_path": [str], # значения (для Catch2): пути до файлов автоматических тестов
    }
}
```

##### in result
```python
{
    "<tool>": {
        "outcome": str, # значения: pass / fail / reject / skip / undefined
        "full_output": str, # значение: файл с подробным выводом проверки
    }
}
```

### CHECK (проверка)

##### in config
```python
{
    "check": str, # уникальное название проверки
    "enabled": bool, # означает: включена / не включена
    "autoreject": bool, # означает: отклонять / не отклонять при не прохождении предыдущих проверок
    "limit": int, # пороговые значения, при превышении которых outcome = "fail" 
    # ВАРИАТИВНЫЕ АРГУМЕНТЫ
    "level": str, # значения (для Clang-Format): strict
}
```

##### in result
```python
{
    "check": str, # уникальное название проверки
    "result": int, # количество ошибок
    "outcome": str, # значения: pass / fail / reject / skip / undefined
    # ВАРИАТИВНЫЕ АРГУМЕНТЫ
    "error": int, # значения (для Catch2): Количество ошибок выполнения
    "failed": int # значения (для Catch2): Количество проваленных тестов
}
```

### OUTCOME
outcome: pass / fail / reject / skip / undefined

```python
{
    "outcome": "pass",      # проверка пройдена
    "outcome": "fail",      # провеока не пройдена
    "outcome": "reject",    # проверка отклонена из-за предыдщуей ошибки
    "outcome": "skip",      # проверка пропущена (не включена)
    "outcome": "undefined", # произошла неизвестная ошибка
}
```

----

# Перспективы

ISSUES:
- Реализовать многопоточку для Catch2
- Заменить все запуски либо на ```subproccess.popen()``` либо на ```subproccess.run()```
- Отрефакторить Checkers и Checker
- Сделать красивый Readme с примерами вывода, инструкциями, флагами для проверок