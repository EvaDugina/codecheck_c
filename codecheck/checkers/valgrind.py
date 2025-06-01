import os
import subprocess
import xml.etree.ElementTree as ET

from codecheck_core import Checker
from codecheck_core import CheckResult
from codecheck_core import Outcome
from codecheck_core import Param

test_executable_name = "test"


class Valgrind(Checker):

    #
    # GETTERS
    #

    def _get_special_flags(self) -> list[str]:
        return ['-c'] + self._files_to_check

    #
    # WORK
    #

    def _run(self):
        custom_flags = ["-o"] + [test_executable_name]
        if self._tool_config.get_param_as_json(Param.COMPILER) == "gcc":
            bin = "gcc"
        else:
            bin = "g++"
        self._run_command_without_result(
            bin=bin,
            filenames=self._files_to_check,
            custom_flags=custom_flags,
            is_only_custom_flags=True)

        custom_flags = '--xml=yes --xml-file=valgrind.xml ./{} > /dev/null'.format(test_executable_name).split(" ")
        self._run_command_without_result(
            custom_flags=custom_flags,
            files_to_wait=["valgrind.xml"],
            is_only_custom_flags=True)

        custom_flags = './{} > /dev/null 2> ./{}'.format(test_executable_name, self._get_output_file_name()).split(" ")
        self._run_command_without_result(
            custom_flags=custom_flags,
            files_to_wait=["valgrind.xml", self._get_output_file_name()],
            is_only_custom_flags=True)

        return self._run_command(result_type=subprocess.CompletedProcess)

    def _update_tool_result_from_output(self, result):

        leaks_count = 0
        errors_count = 0
        for event, elem in ET.iterparse('valgrind.xml'):  # incremental parsing
            if elem.tag == 'kind':
                if elem.text.startswith('Leak_'):
                    leaks_count += 1
                else:
                    errors_count += 1
                elem.clear()
        os.remove(test_executable_name)
        os.remove('valgrind.xml')

        flag_autoreject = False
        for check_config in self._tool_config.get_checks():
            check_result = CheckResult(name=check_config.get_name(), check_params=self._tool_result.get_check_params())

            if check_config.get_name() == 'leaks':
                check_result.set_param(Param.RESULT, leaks_count)
            else:
                check_result.set_param(Param.RESULT, errors_count)

            if flag_autoreject and check_config.get_param(Param.AUTOREJECT):
                check_result.set_param(Param.OUTCOME, Outcome.REJECT)
            else:
                if check_config.get_param(Param.LIMIT) >= check_result.get_param(Param.RESULT):
                    check_result.set_param(Param.OUTCOME, Outcome.PASS)
                else:
                    check_result.set_param(Param.OUTCOME, Outcome.FAIL)
                    flag_autoreject = True

            self._tool_result.set_check(check_result)

        self._tool_result.set_param(Param.OUTCOME, self._get_outcome_from_checks())

        if self._tool_result.get_param(Param.OUTCOME):
            self._tool_result.set_param(Param.FULL_OUTPUT, 'Проверка пройдена!')

        return
