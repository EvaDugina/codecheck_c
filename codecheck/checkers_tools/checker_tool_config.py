from codecheck.checkers_tools.checker_tool import CheckerToolConfig
from codecheck.io_model.model_data.param import Param


class BuildToolConfig(CheckerToolConfig):

    config_tool_params: list[Param] = [
        Param.LANGUAGE
    ]

    config_check_params: list[Param] = [

    ]

    def __init__(self):
        super().__init__(self.config_tool_params, self.config_check_params)


