import json
import os
import subprocess
from typing import final

from codecheck.config import PATH_TO_STUDENT_CODE, PATH_TO_AUTOTEST
from codecheck.handlers import result_handler
from codecheck.io_model.io_error import ErrorCode
from codecheck.io_model.model_data.check import Check
from codecheck.io_model.model_data.outcome import Outcome
from codecheck.io_model.model_data.param import Param
from codecheck.io_model.model_data.tool import ToolConfig, ToolResult


class Checker:
    _tool_config: ToolConfig = None
    _tool_result: ToolResult = None

    _files_to_check = []

    @final
    def __init__(self, tool_config: ToolConfig, files_to_check: list[str], tool_result: ToolResult):
        self._tool_config = tool_config
        self._tool_result = tool_result
        self._files_to_check = files_to_check

    #
    # GETTERS
    #

    @final
    def _get_flags(self) -> list[str]:
        if self._tool_config.is_param_not_null(Param.ARGUMENTS):
            return self._get_special_flags() + self._tool_config.get_param(Param.ARGUMENTS).split(" ")
        return self._get_special_flags()

    def _get_special_flags(self) -> list[str]:
        return []

    @final
    def get_outcome(self, check_results: list[Check]) -> Outcome:
        for check_result in check_results:
            if check_result.get_param(Param.OUTCOME) == Outcome.REJECT:
                return Outcome.REJECT
            if check_result.get_param(Param.OUTCOME) == Outcome.FAIL:
                return Outcome.FAIL
        return Outcome.PASS

    def _get_subproccess_run_params(self) -> dict:
        return {
            "capture_output": True,
            "text": True,
            "check": False,
            "cwd": PATH_TO_AUTOTEST
        }

    #
    # ELSE
    #

    @final
    def start(self) -> ToolResult:

        if not os.path.exists(f"{PATH_TO_STUDENT_CODE}"):
            result_handler.handle_error(ErrorCode.ERROR_NO_STRUCTURE_FOR_CHECKING,
                                        f"Путь {PATH_TO_STUDENT_CODE} не существует!")
        result = self._run()

        if type(result) is dict and 'error' in result:
            error_text = result['error']
            if 'stderr' in result:
                error_text += "\n" + result['stderr']
            self._tool_result.set_param(Param.FULL_OUTPUT, error_text)
            print(error_text)
        else:
            self._update_tool_result_from_output(result)

        # Удаляем все упоминания о структуре из файлов вывода
        if self._tool_result.is_param_not_null(Param.FULL_OUTPUT):
            self._tool_result.set_param(
                Param.FULL_OUTPUT,
                self._tool_result.get_param(Param.FULL_OUTPUT)
                    .replace(PATH_TO_AUTOTEST + os.sep, "")
            )

        self._write_full_output_to_file()

        print(f"{self._tool_config.get_name().upper()} checked!")

        return self._tool_result

    def _run(self) -> dict | str:
        return self._run_subproccess()

    @final
    def _run_subproccess(self, more_args: list[str] | None = None, filename: str = None, result_type: type = None):
        command = [self._tool_config.get_param(Param.BIN)]
        if filename is not None:
            command.append(filename)
        command.extend(self._get_flags())
        if more_args is not None:
            command += more_args

        result = None
        try:
            result = subprocess.run(
                command, **self._get_subproccess_run_params()
            )

            if result_type == dict:
                return json.loads(result.stdout)
            else:
                return result

        except subprocess.CalledProcessError as e:
            return {
                "error": f"{self._tool_config.get_param(Param.BIN)} failed with code {e.returncode}",
                "stderr": e.stderr
            }
        except FileNotFoundError:
            return {
                "error": f"{self._tool_config.get_param(Param.BIN)} file not found!"
            }

        except json.JSONDecodeError:
            # Ошибка парсинга JSON
            if result.stderr == "" or result.returncode == 0:
                return result.stdout
            else:
                return {
                    "error": "Invalid JSON output!"
                }

        except Exception as e:
            return {
                "error": f"{self._tool_config.get_name().upper()}_ERROR: Undefined Exception: {e}"
            }

    def _write_full_output_to_file(self):

        output_file_name = f"output_{self._tool_config.get_name()}.txt"
        with open(output_file_name, "w", encoding="utf-8") as output_file:
            output_file.write(self._tool_result.get_param(Param.FULL_OUTPUT))
        self._tool_result.set_param(Param.FULL_OUTPUT, output_file_name)

    def _update_tool_result_from_output(self, output_json: dict):
        pass
