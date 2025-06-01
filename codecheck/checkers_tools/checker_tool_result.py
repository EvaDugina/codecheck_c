from codecheck_core import CheckerToolResult, Param


class BuildToolResult(CheckerToolResult):

    result_tool_params: list[Param] = [

    ]

    result_check_params: list[Param] = [
    ]

    def __init__(self):
        super().__init__(self.result_tool_params, self.result_check_params)


class CppcheckToolResult(CheckerToolResult):

    result_tool_params: list[Param] = [

    ]

    result_check_params: list[Param] = [
        Param.RESULT
    ]

    def __init__(self):
        super().__init__(self.result_tool_params, self.result_check_params)


class ValgrindToolResult(CheckerToolResult):

    result_tool_params: list[Param] = [

    ]

    result_check_params: list[Param] = [
        Param.RESULT
    ]

    def __init__(self):
        super().__init__(self.result_tool_params, self.result_check_params)

