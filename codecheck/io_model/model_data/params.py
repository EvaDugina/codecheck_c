from handlers import result_handler
from io_model.io_error import ErrorCode
from io_model.model_data.param import Param
import io_model.model_data.param as param_handler


class Params:

    __params: dict[Param, param_handler.get_params_available_types()] = None

    def __init__(self, params_json: dict[str, param_handler.get_params_available_types()] | None):
        if params_json is None:
            self.__params = {}
            return
        self.__params = param_handler.convert_json_to_params(params_json)

    #
    # GETTERS
    #

    def get_json(self) -> dict[str, param_handler.get_params_available_types()]:
        return param_handler.convert_params_to_json(self.__params)

    def get_value(self, param: Param) -> param_handler.get_params_available_types():
        if self.has_value(param):
            return self.__get_value(param)
        return None

    def __get_params(self) -> dict[Param, param_handler.get_params_available_types()]:
        return self.__params

    def __get_value(self, param: Param) -> param_handler.get_params_available_types():
        return self.__params[param]

    #
    # SETTERS
    #

    def set_value(self, param: Param, value: param_handler.get_params_available_types()):
        if not param_handler.is_validate_param_type(param, value):
            result_handler.handle_error(ErrorCode.ERROR_INCORRECT_TYPES, f"in Params: {param} -> {value}")
            return
        self.__set_value(param, value)

    def __set_value(self, param: Param, value: param_handler.get_params_available_types()):
        self.__params[param] = value

    #
    # ELSE
    #

    def has_value(self, param: Param) -> bool:
        if self.is_param(param):
            return not param_handler.is_value_none(param, self.__get_value(param))
        return False

    def is_param(self, param: Param) -> bool:
        return param in self.__params

    def has_not_init_params(self, necessary_params: list[Param]) -> bool:
        for param in necessary_params:
            if not self.is_param(param):
                return True
        return False

    def update_values_by_json(self, params_json: dict):
        if params_json == {}:
            return
        new_params = param_handler.convert_json_to_params(params_json)
        for key, value in new_params.items():
            self.set_value(key, value)
