from .checkers.build import Build
from .checkers.catch2 import Catch2
from .checkers.clang_format import ClangFormat
from .checkers.cppcheck import Cppcheck
from .checkers_tools.checker_tool_config import BuildToolConfig, CppcheckToolConfig, ValgrindToolConfig, \
    ClangFormatToolConfig, Catch2ToolConfig
from .checkers_tools.checker_tool_result import BuildToolResult, CppcheckToolResult, ValgrindToolResult, \
    ClangFormatToolResult, Catch2ToolResult
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
    },
    "clang-format": {
        "checker": ClangFormat,
        "config_checker_tool": ClangFormatToolConfig,
        "result_checker_tool": ClangFormatToolResult
    },
    "catch2": {
        "checker": Catch2,
        "config_checker_tool": Catch2ToolConfig,
        "result_checker_tool": Catch2ToolResult
    }
}


# Return: None / Checker
def getCheckerByTool(tool_name: str) -> dict | None:
    if tool_name in TOOLS_CHECKERS:
        return TOOLS_CHECKERS[tool_name]
    return None

