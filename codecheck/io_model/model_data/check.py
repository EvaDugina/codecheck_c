from codecheck.handlers import result_handler
from codecheck.io_model.io_error import ErrorCode
from codecheck.io_model.model_data.model_data_block import DataBlock
from codecheck.io_model.model_data.param import Param


def is_check_validate(check_json: dict) -> bool:
    if check_json is None or check_json == {}:
        return False
    return True


class Check(DataBlock):

    def __init__(self, check_params: list[Param], check_params_json: dict | None = None):
        if check_params_json is None or 'check' not in check_params_json:
            name = None
        else:
            name = check_params_json['check']
        super().__init__(name, check_params)
        if check_params_json is not None:
            self._update_params_from_json(check_params_json)

    #
    # OVERRIDED
    #

    def get_json(self) -> dict:
        name_json = {}
        if self.has_name():
            name_json = {"check": self.get_name()}
        return name_json | self._get_params_as_json()


class CheckResult(Check):

    def __init__(self, check_params: list[Param], check_json: dict | None = None, name: str = None):
        if name is not None:
            super().__init__(check_params, {"check": name})
        else:
            super().__init__(check_params)
        if check_json is None:
            return

        self._update_params_from_json(check_json)


class CheckConfig(Check):

    def __init__(self, check_params: list[Param], check_json: dict):
        super().__init__(check_params, check_json)
        if self.has_not_init_params(check_params):
            result_handler.handle_error(
                ErrorCode.ERROR_CONFIGURATION_FILE,
                f"in Check Config:\n"
                f"NECESSARY_PARAMS: {check_params}\n"
                f"JSON: {check_json}")
            return


