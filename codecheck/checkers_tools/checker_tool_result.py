from codecheck.checkers_tools.checker_tool import CheckerToolResult
from codecheck.io_model.model_data.param import Param


class BuildToolResult(CheckerToolResult):

    result_tool_params: list[Param] = [

    ]

    result_check_params: list[Param] = [
    ]

    def __init__(self):
        super().__init__(self.result_tool_params, self.result_check_params)
