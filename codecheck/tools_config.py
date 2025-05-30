from codecheck.checkers.build import Build
from codecheck.checkers_tools.checker_tool_config import BuildToolConfig
from codecheck.checkers_tools.checker_tool_result import BuildToolResult

TOOLS_CHECKERS = {
    "build": {
        "checker": Build,
        "config_checker_tool": BuildToolConfig,
        "result_checker_tool": BuildToolResult
    }
}


# Return: None / Checker
def getCheckerByTool(tool_name: str) -> dict | None:
    if tool_name in TOOLS_CHECKERS:
        return TOOLS_CHECKERS[tool_name]
    return None

