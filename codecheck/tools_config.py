from .checkers.build import Build
from .checkers.cppcheck import Cppcheck
from .checkers_tools.checker_tool_config import BuildToolConfig, CppcheckToolConfig, ValgrindToolConfig
from .checkers_tools.checker_tool_result import BuildToolResult, CppcheckToolResult, ValgrindToolResult
from .checkers.valgrind import Valgrind

TOOLS_CHECKERS = {
    "build": {
        "checker": Build,
        "config_checker_tool": BuildToolConfig,
        "result_checker_tool": BuildToolResult
    },
    "cppcheck": {
        "checker": Cppcheck,
        "config_checker_tool": CppcheckToolConfig,
        "result_checker_tool": CppcheckToolResult
    },
    "valgrind": {
        "checker": Valgrind,
        "config_checker_tool": ValgrindToolConfig,
        "result_checker_tool": ValgrindToolResult
    }
}


# Return: None / Checker
def getCheckerByTool(tool_name: str) -> dict | None:
    if tool_name in TOOLS_CHECKERS:
        return TOOLS_CHECKERS[tool_name]
    return None

