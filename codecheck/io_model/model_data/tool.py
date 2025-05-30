from shutil import which

from codecheck.io_model.io_error import ErrorCode
from codecheck.io_model.model_data.check import Check, CheckResult, CheckConfig
from codecheck.io_model.model_data.param import Param
from codecheck.io_model.model_data.model_data_block import DataBlock
from codecheck.handlers import result_handler


class Tool(DataBlock):

    __checks: list[Check] = None
    __checks_field: str = None
    __check_params: list[Param] = None

    def __init__(self, tool_params: list[Param], check_params: list[Param], name: str, checks_field: str):
        super().__init__(name, tool_params)
        if checks_field is None:
            result_handler.handle_error(ErrorCode.ERROR_CONFIGURATION_FILE,
                                        f"in Tool Config {name} (no checks, no check)")
            return
        self.__check_params = check_params
        self.__set_checks_field_name(checks_field)
        self._set_checks([])

    #
    # GETTERS
    #

    def get_checks(self) -> list[Check]:
        return self.__checks

    def get_tool_json(self) -> dict:
        return {self.get_name(): self.get_json()}

    def _get_check_by_name(self, check_name: str) -> Check | None:
        if self.__has_check(check_name):
            return self.__checks[self.__get_check_index(check_name)]
        return None

    def _get_checks_field_name(self) -> str:
        if self.get_checks() is not None and len(self.get_checks()) > 1:
            return "checks"
        return self.__checks_field

    def get_check_params(self) -> list[Param]:
        return self.__check_params

    def __get_check_index(self, check_name: str) -> int | None:
        index = 0
        for check in self.get_checks():
            if check.get_name() == check_name:
                return index
            index += 1
        return None

    def __get_json_from_checks(self) -> list | dict:
        if self._get_checks_field_name() == "check":
            for check in self.get_checks():
                return check.get_json()
            return {}
        checks_list = []
        for check in self.get_checks():
            checks_list.append(check.get_json())
        return checks_list

    #
    # SETTERS
    #

    def set_check(self, check: Check):
        if self.__has_check(check.get_name()):
            self.__checks[self.__get_check_index(check.get_name())] = check
        else:
            self.__checks.append(check)

    def _set_checks(self, checks: list[Check]):
        self.__checks = checks

    def __set_checks_field_name(self, checks_field: str):
        self.__checks_field = checks_field

    #
    # ELSE
    #

    def __has_check(self, check_name: str) -> bool:
        return self.__get_check_index(check_name) is not None

    #
    # OVERRIDED
    #

    def get_json(self) -> dict:
        checks_list = {self._get_checks_field_name(): self.__get_json_from_checks()}
        return self._get_params_as_json() | checks_list

    #
    # NEED TO OVERRIDE
    #

    def _get_checks_from_json(self, tool_json: dict) -> list[Check]:
        pass

    def _get_internal_obj(self, check_json: dict) -> CheckResult | CheckConfig:
        pass


class ToolResult(Tool):

    def __init__(self, result_tool_params: list[Param], result_check_params: list[Param], tool_name: str, checks_field: str):
        super().__init__(result_tool_params, result_check_params, tool_name, checks_field)

    def create_check(self, result_check_params: list[Param]) -> Check:
        new_check = CheckResult(result_check_params)
        self.set_check(new_check)
        return self._get_check_by_name(new_check.get_name())

    def update(self, tool_result_json: dict):
        self._update_params_from_json(tool_result_json)
        self._set_checks(self._get_checks_from_json(tool_result_json))

    #
    # OVERRIDED
    #

    def _get_internal_obj(self, check_result_json: dict):
        return CheckResult(self.get_check_params(), check_result_json)

    def _get_checks_from_json(self, tool_result_json: dict) -> list[Check]:
        checks = []
        if 'checks' in tool_result_json:
            checks_list = tool_result_json['checks']
            for check_json in checks_list:
                checks.append(self._get_internal_obj(check_json))
        elif 'check' in tool_result_json:
            check_json = tool_result_json['check']
            if not check_json == {}:
                checks.append(self._get_internal_obj(check_json))
        return checks


def get_check_name_from_json(tool_json: dict) -> str | None:
    if "checks" in tool_json:
        return "checks"
    elif "check" in tool_json:
        return "check"
    return None


class ToolConfig(Tool):

    def __init__(self, config_tool_params: list[Param], config_check_params: list[Param], tool_name: str, tool_json: dict):
        super().__init__(config_tool_params, config_check_params, tool_name, get_check_name_from_json(tool_json))

        self._update_params_from_json(tool_json)

        if self.has_not_init_params(config_tool_params):
            result_handler.handle_error(
                ErrorCode.ERROR_CONFIGURATION_FILE,
                f"in Tool Config:\n"
                f"NECESSARY_PARAMS: {config_tool_params}\n"
                f"JSON: {tool_json}")
            return

        self._set_checks(self._get_checks_from_json(tool_json))

        if not self._is_bin_installed():
            self.set_param(Param.ENABLED, False)
            result_handler.handle_warning(f"Проверка {self.get_name()} пропущена! Не установлены инструменты проверки!")

    #
    # ELSE
    #

    def generate_tool_result(self, result_tool_params: list[Param], result_check_params: list[Param]) -> ToolResult:
        return ToolResult(result_tool_params, result_check_params, self.get_name(), self._get_checks_field_name())

    def _is_bin_installed(self) -> bool:
        if self.is_param_not_null(Param.BIN):
            if self.get_param(Param.ENABLED) and which(self.get_param(Param.BIN)) is None:
                result_handler.handle_warning("Tool " + self.get_param(Param.BIN) + " not installed, skipping..")
                return False
        return True

    #
    # OVERRIDED
    #

    def _get_internal_obj(self, check_config_json: dict):
        return CheckConfig(self.get_check_params(), check_config_json)

    def _get_checks_from_json(self, tool_config_json: dict) -> list[Check]:
        checks_list: list = []

        auto_enabled = None
        if 'checks' in tool_config_json:
            checks_list = tool_config_json['checks']
        elif 'check' in tool_config_json:
            checks_list = [tool_config_json['check']]
            auto_enabled = self.get_param(Param.ENABLED)

        checks = []
        for check_json in checks_list:
            if auto_enabled is not None:
                check_json['enabled'] = auto_enabled
            checks.append(self._get_internal_obj(check_json))
        return checks

