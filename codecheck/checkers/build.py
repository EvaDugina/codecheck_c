import subprocess

from codecheck_core import Checker
from codecheck_core import CheckResult
from codecheck_core import Outcome
from codecheck_core import Param


class Build(Checker):

    #
    # GETTERS
    #

    def _get_special_flags(self) -> list[str]:
        return ['-c'] + self._files_to_check

    def _get_output_file_name(self) -> str:
        return f"output_{self._tool_config.get_name()}.txt"

    #
    # WORK
    #

    def _run(self):

        return self._run_command(result_type=subprocess.CompletedProcess)

    def _update_tool_result_from_output(self, result):

        check = CheckResult(self._tool_result.get_check_params())

        if result.returncode == 0:
            check.set_param(Param.OUTCOME, Outcome.PASS)
            self._tool_result.set_param(Param.FULL_OUTPUT, "Сборка выполнена успешно.")
        else:
            check.set_param(Param.OUTCOME, Outcome.FAIL)
            self._tool_result.set_param(Param.FULL_OUTPUT, f"{result.stderr}\n{result.stdout}")

        self._tool_result.set_check(check)

        self._tool_result.set_param(Param.OUTCOME, self._get_outcome_from_checks())

        return
