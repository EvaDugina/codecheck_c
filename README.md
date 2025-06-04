# codecheck
Utility for automatic code check with various tools

### Supports:
- valgrind
- cppcheck
- clang-format (codestyle)
- copydetect
- catch2

### Install     
Clone the repository and run command in root directory:
```
pip install .
```
### Usage
```
codecheck [-h] -c config.json [files ...]
```     
| Argument     | Description |
| ------------ | ----------- |
| -h, --help   | show help message and exit|
| -c, --conf   | path to JSON configuration file (default: None) |
| -f, --format | path to clang-format configuration (default: None) |

### Запуск Docker
docker build -t codecheck .
docker run -it --rm -v ./:/tmp codecheck

---

### Примеры корректного вывода программы

```commandline
# codecheck
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

```commandline
# codecheck -c examples/config_all_console.json examples/code_example_1.c     
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

# Перспективы

ISSUES:
- Реализовать многопоточку для Catch2
- Заменить все запуски либо на ```subproccess.popen()``` либо на ```subproccess.run()```
- Отрефакторить Checkers и Checker
- Сделать красивый Readme с примерами вывода, инструкциями, флагами для проверок