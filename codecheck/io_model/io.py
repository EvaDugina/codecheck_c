from codecheck.config import PATH_TO_OUTPUT_FILE, PATH_TO_STUDENT_CODE
from codecheck.handlers import result_handler, json_handler, file_handler
from codecheck.handlers.result_handler import handle_success
from codecheck.io_model.io_error import ErrorCode
from codecheck.io_model.model_data.tools import Config, Result, synch_result_to_file


def is_integer(s) -> bool:
    try:
        int(s)
        return True
    except ValueError:
        return False


def is_validate_args_files_to_check(args_files_to_check: [str]) -> bool:
    if not args_files_to_check or len(args_files_to_check) < 1:
        return False
    return True


def convertFiledsOfJsonToCorrectTypes(config_json) -> dict:
    for key in config_json:
        if type(config_json[key]) is bool or type(config_json[key]) is int:
            continue
        elif config_json[key] == "false" or config_json[key] == "true":
            config_json[key] = config_json[key] == "true"
        elif type(config_json[key]) == str and is_integer(config_json[key]):
            config_json[key] = int(config_json[key])
        elif type(config_json[key]) == list and len(config_json[key]) > 0:
            if type(config_json[key][0]) == str:
                continue
            inside_list = list()
            for elem in config_json[key]:
                inside_list.append(convertFiledsOfJsonToCorrectTypes(elem))
            config_json[key] = inside_list
        elif type(config_json[key]) == dict:
            config_json[key] = convertFiledsOfJsonToCorrectTypes(config_json[key])

    return config_json


class Input:

    _config: Config = None
    _files_to_check: list[str] = []

    def __init__(self, args_config_file_path: str, args_files_to_check: [str]):
        self._config = self._get_config_from_file(args_config_file_path)
        if self._config is None:
            result_handler.handle_error(ErrorCode.ERROR_CONFIGURATION_FILE, f"in Input:\nNo input!")
            return

        if not is_validate_args_files_to_check(args_files_to_check):
            result_handler.handle_error(ErrorCode.ERROR_NO_FILES_TO_CHECK)
            return
        self._files_to_check = file_handler.copy_files_to_autotesting_folder(args_files_to_check, PATH_TO_STUDENT_CODE)

    #
    # GETTERS
    #

    def get_base_config_json(self) -> {}:
        return self._config.get_config_json()

    def get_config(self) -> Config:
        return self._config

    def get_config_tools(self):
        return self._config.get_tools()

    def get_files_to_check(self) -> [str]:
        return self._files_to_check

    def _get_config_from_file(self, args_config_file_path: str) -> Config | None:
        config_json = json_handler.read_json_from_file(args_config_file_path)
        if config_json is None:
            return None
        return Config(convertFiledsOfJsonToCorrectTypes(config_json))


class Output:

    _result: Result = None

    def __init__(self):
        self.set_result(Result())
        self.set_empty_result()
        self.fix_result()

    #
    # GETTERS
    #

    def get_result(self) -> Result:
        return self._result

    #
    # SETTERS
    #

    def set_result(self, result: Result):
        self._result = result

    def set_empty_result(self):
        self.get_result().set_error_result(ErrorCode.UNDEFINED)
        self.fix_result()

    def set_success_result(self):
        self.get_result().set_success_result()
        self.fix_result()
        handle_success()

    #
    # ELSE
    #

    def fix_result(self):
        synch_result_to_file(self.get_result())

