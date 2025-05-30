from codecheck.io_model.model_data.param import Param


class CheckerTool:

    __tool_params: list[Param] = []
    __check_params: list[Param] = []

    def __init__(self, tool_params: list[Param], check_params: list[Param]):
        self.__tool_params = tool_params
        self.__check_params = check_params

    #
    # GETTERS
    #

    def get_tool_params(self) -> list[Param]:
        return self.__tool_params

    def get_check_params(self) -> list[Param]:
        return self.__check_params


class CheckerToolConfig(CheckerTool):

    def __init__(self, tool_params: list[Param], check_params: list[Param]):
        tool_params = list(set(tool_params) | {Param.ENABLED, Param.AUTOREJECT})
        check_params = list(set(check_params) | {Param.ENABLED, Param.AUTOREJECT})
        super().__init__(tool_params, check_params)


class CheckerToolResult(CheckerTool):

    def __init__(self, tool_params: list[Param], check_params: list[Param]):
        tool_params = list(set(tool_params) | {Param.FULL_OUTPUT, Param.OUTCOME})
        check_params = list(set(check_params) | {Param.OUTCOME})
        super().__init__(tool_params, check_params)
