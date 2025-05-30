from codecheck.io_model.model_data.param import Param
from codecheck.io_model.model_data.params import Params
import codecheck.io_model.model_data.param as param_handler


class DataBlock:

    __name: str | None = None
    __params: Params = None

    def __init__(self, name: str | None, necessary_params: list[Param]):
        self.__set_name(name)
        self.__init_params_from_json()
        for check_param in necessary_params:
            self.set_param(check_param, param_handler.get_default_value_by_param(check_param))

    #
    # GETTERS
    #

    def get_name(self) -> str:
        if not self.has_name():
            return 'default'
        return self.__name

    def get_param(self, param: Param) -> param_handler.get_params_available_types():
        if type(param) is Param:
            return self.__params.get_value(param)
        return None

    def _get_params_as_json(self) -> dict:
        return self.__params.get_json()

    #
    # SETTERS
    #

    def set_param(self, param: Param, value):
        self.__params.set_value(param, value)

    def _update_params_from_json(self, params_json: dict):
        self.__params.update_values_by_json(params_json)

    def __set_name(self, name: str | None):
        self.__name = name

    def __init_params_from_json(self, params_json: dict | None = None):
        self.__params = Params(params_json)
        if params_json is not None:
            self.__params.update_values_by_json(params_json)

    #
    # ELSE
    #

    def is_param_equal(self, param: Param, value: param_handler.get_params_available_types()) -> bool:
        return self.get_param(param) == value

    def has_name(self) -> bool:
        return self.__name is not None

    def is_param_not_null(self, param: Param) -> bool:
        return self.__params.has_value(param)

    def has_not_init_params(self, necessary_params: list[Param]) -> bool:
        return self.__params.has_not_init_params(necessary_params)

    #
    # NEED TO OVERRIDE
    #

    def get_json(self) -> dict:
        pass
