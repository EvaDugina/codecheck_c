import xml.etree.ElementTree as ET
from importlib.resources import files
from xml.dom import minidom

from codecheck_core import Checker
from codecheck_core import CheckResult
from codecheck_core import Outcome
from codecheck_core import Param


class ClangTidy(Checker):

    #
    # GETTERS
    #

    def _get_special_flags(self) -> list[str]:
        return []

    def _get_output_file_name(self) -> str:
        return f"output_{self._tool_config.get_name()}.txt"

    #
    # WORK
    #

    def _run(self) -> list[ET.Element]:

        # clang_format_path = str(files('config_data_package').joinpath('clang-tidy'))
        # self.copy_to_test_folder(clang_format_path, '.clang-tidy')

        outputs: list = []

        if self._tool_config.is_param_not_null(Param.ENABLE_ERROR_CODES):
            checks = ",".join(self._tool_config.get_param(Param.ENABLE_ERROR_CODES))
        else:
            checks = "*"

        for file_name in self._files_to_check:

            custom_flags = [
                f'-checks="{checks}"', '-header-filter=".*"', file_name,
                "--", f"-I/{self._get_student_code_folder()}"
            ]

            if self._tool_config.is_param_not_null(Param.ARGUMENTS):
                for arg in self._tool_config.get_param(Param.ARGUMENTS).split(" "):
                    if len(arg) > 0:
                        custom_flags.append(arg)

            output = self._run_command(
                custom_flags=custom_flags,
                result_type=bytes,
                is_only_custom_flags=True
            )

            outputs.append(output)

        return outputs

    def _update_tool_result_from_output(self, outputs: list[str]):

        check_config = self._tool_config.get_checks()[0]
        check_result = CheckResult(self._tool_result.get_check_params())

        full_output = ""
        for output in outputs:
            full_output += output + "\n\n"

        result = full_output.count('warning:')
        check_result.set_param(Param.RESULT, result)

        if check_config.get_param(Param.LIMIT) >= check_result.get_param(Param.RESULT):
            check_result.set_param(Param.OUTCOME, Outcome.PASS)
        else:
            check_result.set_param(Param.OUTCOME, Outcome.FAIL)

        self._tool_result.set_check(check_result)

        self._tool_result.set_param(Param.FULL_OUTPUT, full_output)

        return
