# codecheck
### Utility for automatic code check with various tools
### Supports:
- valgrind
- cppcheck
- clang-format (codestyle)
- copydetect
### Install     
Clone the repository and run command in root directory:
```
pip install .
```
### Usage
```
codecheck [-h] -c config.json [-f .clang-format] files [files ...]
```     
| Argument     | Description |
| ------------ | ----------- |
| -h, --help   | show help message and exit|
| -c, --conf   | path to JSON configuration file (default: None) |
| -f, --format | path to clang-format configuration (default: None) |