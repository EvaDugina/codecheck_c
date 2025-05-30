from enum import IntEnum

ERROR_TEXT = {
    0: "Неизвестная внутренняя ошибка!",
    101: "Ошибка! Невозможно прочитать файл конфигурации!",
    102: "Ошибка! Некорректный файл конфигурации!",
    111: "Ошибка! Отсутствуют файлы для проверки!",
    103: "Ошибка! Некорректный инструмент проверки!",
    104: "Ошибка! Некорректная передача файлов для проверки!",
    105: "Ошибка! Отсутствует необходимая структура для осуществления проверки!",
    106: "Ошибка! Отсутствуют файлы автотеста!",
    107: "Ошибка! Неверные типы!"
}


class ErrorCode(IntEnum):
    UNDEFINED = 0
    ERROR_READING_CONFIGURATION_FILE = 101
    ERROR_CONFIGURATION_FILE = 102
    ERROR_NO_FILES_TO_CHECK = 111
    ERROR_GET_CHECKER_BY_TOOL_NAME = 103
    ERROR_VALIDATE_FILES_TO_CHECK = 104
    ERROR_NO_STRUCTURE_FOR_CHECKING = 105
    ERROR_NO_AUTOTEST_FILES = 106
    ERROR_INCORRECT_TYPES = 107


class Error:

    __error_code: ErrorCode | None = None
    __error_text: str | None = None

    def __init__(self, error_code: ErrorCode | None):
        if error_code is None:
            self.__error_code = None
            self.__error_text = None
            return

        self.__error_code = error_code
        self.__error_text = ERROR_TEXT[self.__error_code.value]

    #
    # GETTERS
    #

    @staticmethod
    def get_error_fields() -> list[str]:
        return ["error_code", "error_text"]

    def get_error_code(self):
        if self.__error_code is None:
            return ""
        return self.__error_code

    def get_error_text(self):
        if self.__error_text is None:
            return ""
        return self.__error_text

    def get_json(self) -> dict:
        return {"error_code": self.get_error_code(), "error_text": self.get_error_text()}


def get_error_text_by_error_code(error_code: ErrorCode):
    return ERROR_TEXT[error_code.value]


def get_error_by_error_code(error_code: int) -> Error | None:
    return Error(ErrorCode(error_code))


