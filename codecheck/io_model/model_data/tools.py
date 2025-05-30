import time
from enum import IntEnum

from codecheck.config import PATH_TO_OUTPUT_FILE
from codecheck.io_model.model_data.tool import Tool, ToolConfig, ToolResult, \
    get_check_name_from_json
from codecheck.handlers import result_handler, json_handler
from codecheck.io_model.io_error import Error, ErrorCode, get_error_by_error_code
from codecheck.tools_config import getCheckerByTool


class ReturnCode(IntEnum):
    SUCCESS = 0
    ERROR = 1


def get_return_code_by_return_code(return_code: int) -> ReturnCode:
    return ReturnCode(return_code)


class IOData:

    _tools: list = None

    #
    # GETTERS
    #

    def get_checker_tool_by_tool_name(self, tool_name: str) -> dict:
        return getCheckerByTool(tool_name)

    def get_tools_as_json(self) -> dict:
        tools = {}
        for tool in self.get_tools():
            tools |= tool.get_tool_json()
        return {"tools": tools}

    def _get_tool_index_by_name(self, tool_name: str) -> int | None:
        index = 0
        for tool in self.get_tools():
            if tool.get_name() == tool_name:
                return index
            index += 1
        return None

    #
    # SETTERS
    #

    def set_tool(self, tool: Tool) -> ToolResult:
        index_tool = self._get_tool_index_by_name(tool.get_name())
        if index_tool is None:
            self._tools.append(tool)
        else:
            self._tools[index_tool] = tool
        return self.get_tool_by_name(tool.get_name())

    def _set_tools(self, tools: list[Tool]):
        self._tools = tools

    def update_tools(self, tools: list[Tool]):
        for tool in tools:
            self.set_tool(tool)

    #
    # OVERRIDE
    #

    def _is_data_validate(self, data_json: dict) -> bool:
        pass

    def get_json(self) -> dict:
        pass

    def get_tools(self) -> list[Tool]:
        pass

    def get_tool_by_name(self, tool_name) -> ToolResult | ToolConfig | None:
        pass

    def _get_tools_from_json(self, data_json: dict) -> list[ToolConfig]:
        pass


class Result(IOData):

    _return_code: ReturnCode = None
    _error: Error = None

    def __init__(self, data_json: dict | None = None):

        self.set_error_result(ErrorCode.UNDEFINED)
        self._set_tools([])

        if data_json is not None:
            if not self._is_data_validate(data_json):
                return

            self._set_tools(self._get_tools_from_json(data_json))
            if not data_json['error_code'] == "":
                self.set_error(get_error_by_error_code(data_json['error_code']))
            self.set_return_code(get_return_code_by_return_code(data_json['return_code']))

    #
    # GETTERS
    #

    def get_json(self) -> dict:
        if self.get_return_code() is None:
            self.set_error_result(ErrorCode.UNDEFINED)
        return self.get_tools_as_json() | {
                   "error_code": self.get_error().get_error_code(),
                   "error_text": self.get_error().get_error_text(),
                   "return_code": self.get_return_code().value
               } | self.get_error().get_json()

    def get_error(self) -> Error:
        return self._error

    def get_return_code(self) -> ReturnCode:
        return self._return_code

    #
    # SETTERS
    #

    def set_success_result(self):
        self.set_error(Error(None))
        self.set_return_code(ReturnCode.SUCCESS)

    def set_error_result(self, error_code: ErrorCode):
        self.set_error(Error(error_code))
        self.set_return_code(ReturnCode.ERROR)

    def set_error(self, error: Error):
        self._error = error

    def set_return_code(self, return_code: ReturnCode):
        self._return_code = return_code

    #
    # ELSE
    #

    def update_result(self, new_tools: list[ToolResult], error: Error, return_code: ReturnCode):
        self.update_tools(new_tools)
        self.set_error(error)
        self.set_return_code(return_code)

    def _is_error(self) -> bool:
        return self.get_return_code() == ReturnCode.ERROR or self.get_return_code() is None

    #
    # OVERRIDE
    #

    def _is_data_validate(self, data_json: dict) -> bool:
        if data_json == {}:
            return False
        if 'tools' not in data_json or type(data_json['tools']) is list:
            return False
        if 'return_code' not in data_json:
            return False
        for error_field in self.get_error().get_error_fields():
            if error_field not in data_json:
                return False
        return True

    def get_tools(self) -> list[ToolResult]:
        return self._tools

    def get_tool_by_name(self, tool_name: str) -> ToolResult | None:
        index_tool = self._get_tool_index_by_name(tool_name)
        if index_tool is None:
            return None
        return self._tools[index_tool]

    def _get_tools_from_json(self, data_json: dict) -> list[ToolResult]:
        tools = []
        if 'tools' in data_json and type(data_json['tools']) is dict:
            for tool_name, tool_json in data_json['tools'].items():
                result_checker_tool = self.get_checker_tool_by_tool_name(tool_name)['result_checker_tool']()
                tool_result = ToolResult(
                    result_checker_tool.get_tool_params(),
                    result_checker_tool.get_check_params(),
                    tool_name,
                    get_check_name_from_json(tool_json))
                tool_result.update(tool_json)
                tools.append(tool_result)
        return tools


class Config(IOData):

    _config_json: dict = None

    def __init__(self, data_json: dict | None):

        self._config_json = data_json

        if not self._is_data_validate(data_json):
            result_handler.handle_error(ErrorCode.ERROR_CONFIGURATION_FILE, f"in Data Config:\n{data_json}")
            return

        self._set_tools(self._get_tools_from_json(data_json))

    #
    # GETTERS
    #

    def get_config_json(self) -> dict:
        return self._config_json

    #
    # OVERRIDE
    #

    def _is_data_validate(self, data_json: dict) -> bool:
        if data_json is None or data_json == {}:
            return False
        if 'tools' not in data_json or type(data_json['tools']) is list:
            return False
        return True

    def get_json(self) -> dict:
        return self.get_tools_as_json()

    def get_tools(self) -> list[ToolConfig]:
        return self._tools

    def get_tool_by_name(self, tool_name) -> ToolConfig | None:
        index_tool = self._get_tool_index_by_name(tool_name)
        if index_tool is None:
            return None
        return self._tools[index_tool]

    def _get_tools_from_json(self, data_json: dict) -> list[ToolConfig]:
        tools = []
        for tool_name, tool_json in data_json['tools'].items():
            config_checker_tool = self.get_checker_tool_by_tool_name(tool_name)['config_checker_tool']()
            tools.append(ToolConfig(
                config_checker_tool.get_tool_params(),
                config_checker_tool.get_check_params(),
                tool_name,
                tool_json))
        return tools


#
#
#

FLAG_IS_UPDATING = False


def waiting_for_updating():
    while FLAG_IS_UPDATING:
        time.sleep(0.5)
    return


def get_current_result() -> Result:
    current_json = json_handler.read_json_from_file(PATH_TO_OUTPUT_FILE)
    return Result(current_json)


def append_tool_result_to_file(tools_result: list[ToolResult]):
    global FLAG_IS_UPDATING

    waiting_for_updating()

    FLAG_IS_UPDATING = True

    current_result: Result = get_current_result()
    for tool_result in tools_result:
        current_result.set_tool(tool_result)
    json_handler.write_json_to_file(PATH_TO_OUTPUT_FILE, current_result.get_json())

    FLAG_IS_UPDATING = False

    return


def synch_result_to_file(result: Result):

    global FLAG_IS_UPDATING

    waiting_for_updating()

    FLAG_IS_UPDATING = True

    current_result: Result = get_current_result()
    current_result.update_result(result.get_tools(), result.get_error(), result.get_return_code())
    json_handler.write_json_to_file(PATH_TO_OUTPUT_FILE, current_result.get_json())

    FLAG_IS_UPDATING = False
