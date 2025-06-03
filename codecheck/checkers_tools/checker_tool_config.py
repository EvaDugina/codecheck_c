from codecheck_core import CheckerToolConfig, Param


class BuildToolConfig(CheckerToolConfig):

    config_tool_params: list[Param] = [
    ]

    config_check_params: list[Param] = [

    ]

    def __init__(self):
        super().__init__(self.config_tool_params, self.config_check_params)


class CppcheckToolConfig(CheckerToolConfig):

    config_tool_params: list[Param] = [

    ]

    config_check_params: list[Param] = [
        Param.LIMIT
    ]

    def __init__(self):
        super().__init__(self.config_tool_params, self.config_check_params)


class ValgrindToolConfig(CheckerToolConfig):

    config_tool_params: list[Param] = [
        Param.COMPILER
    ]

    config_check_params: list[Param] = [
        Param.LIMIT
    ]

    def __init__(self):
        super().__init__(self.config_tool_params, self.config_check_params)


class ClangFormatToolConfig(CheckerToolConfig):

    config_tool_params: list[Param] = [
    ]

    config_check_params: list[Param] = [
        Param.LIMIT
    ]

    def __init__(self):
        super().__init__(self.config_tool_params, self.config_check_params)


