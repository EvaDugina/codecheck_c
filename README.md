# codecheck
### Utility for automatic code check with various tools
### Supports:
- valgrind
- cppcheck
- clang-format (codestyle)
- copydetect
### Usage
```
codecheck [-h] -c config.json [-f .clang-format] files [files ...]
```     
| Argument     | Description |
| ------------ | ----------- |
| -h, --help   | show help message and exit|
| -c, --conf   | path to JSON configuration file (default: None) |
| -f, --format | path to clang-format configuration (default: None) |