import subprocess


from codecheck_core import Checker
from codecheck_core import CheckResult
from codecheck_core import Outcome
from codecheck_core import Param

test_executable_name = "test"


class Valgrind(Checker):

    #
    #
    #

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
            files_to_wait=['valgrind.xml'],
            is_only_custom_flags=True)

        custom_flags = './{} > /dev/null 2> ./{}'.format(test_executable_name, self._get_output_file_name()).split(" ")

        return self._run_command_without_result(
            custom_flags=custom_flags,
            result_type=str,
            is_only_custom_flags=True)

    def _update_tool_result_from_output(self, output):

        # print("OUTPUT: " + output)

        leaks_count = 0
        errors_count = 0
        for event, elem in self.iterate_xml('valgrind.xml'):  # incremental parsing
            if elem.tag == 'kind':
                if elem.text.startswith('Leak_'):
                    leaks_count += 1
                else:
                    errors_count += 1
                elem.clear()

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

        self._tool_result.set_param(Param.FULL_OUTPUT, output)
        self._tool_result.set_param(Param.OUTCOME, self._get_outcome_from_checks())

        return
