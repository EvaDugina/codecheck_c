from codecheck.checkers.checker import Checker
from codecheck.io_model.model_data.check import CheckResult
from codecheck.io_model.model_data.language import Language
from codecheck.io_model.model_data.outcome import Outcome
from codecheck.io_model.model_data.param import Param


class Build(Checker):

    #
    # GETTERS
    #

    def _get_special_flags(self) -> list[str]:
        return ['-c'] + self._files_to_check

    #
    # WORK
    #

    def _run(self):

        compile_command = ''
        if self._tool_config.get_param(Param.LANGUAGE) == Language.C_PLUS_PLUS:
            compile_command = 'g++'
        elif self._tool_config.get_param(Param.LANGUAGE) == Language.C:
            compile_command = 'gcc'

        self._tool_config.set_param(Param.BIN, compile_command)
        result = self._run_subproccess()
        self._tool_config.set_param(Param.BIN, self._tool_config.get_name())

        return result

    def _update_tool_result_from_output(self, result):

        check = CheckResult(self._tool_result.get_check_params())

        if result.returncode == 0:
            check.set_param(Param.OUTCOME, Outcome.PASS)
        else:
            check.set_param(Param.OUTCOME, Outcome.FAIL)
            self._tool_result.set_param(Param.FULL_OUTPUT, f"{result.stderr}\n{result.stdout}")

        self._tool_result.set_check(check)

        self._tool_result.set_param(Param.OUTCOME, check.get_param(Param.OUTCOME))

        return
