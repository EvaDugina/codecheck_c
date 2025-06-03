from codecheck_core import CheckResult
from codecheck_core import Checker
from codecheck_core import Outcome
from codecheck_core import Param


class Cppcheck(Checker):

    #
    # GETTERS
    #

    def _get_special_flags(self) -> list[str]:
        enabled_types = []
        for check in self._tool_config.get_checks():
            if check.get_name() != 'error':
                enabled_types.append(check.get_name())
        flag = '--enable='
        flag += ','.join(enabled_types)
        return [flag, "--xml", f"--output-file={self._get_output_file_name()}", self._get_student_code_folder()]

    def _get_output_file_name(self) -> str:
        return f"output_{self._tool_config.get_name()}.xml"

    def _get_error_message_if_no_output(self) -> str:
        return "Отсутствует файл результата!"

    #
    # WORK
    #

    def _run(self):

        self._run_command_with_timeout(
            files_to_wait=[self._get_output_file_name()],
        )
        return None

    def _update_tool_result_from_output(self, result):

        # print("_update_tool_result_from_output()")

        errors_count = {}
        try:
            for event, elem in self.iterate_xml_file(self._get_output_file_name()):  # incremental parsing
                if elem.tag == 'error':
                    severity = elem.get('severity')
                    if errors_count.get(severity) is None:
                        errors_count[severity] = 1
                    else:
                        errors_count[severity] += 1
                    elem.clear()
        except Exception as e:
            print("Exception:" + str(e))

        flag_autoreject = False
        for check_config in self._tool_config.get_checks():
            check_result = CheckResult(name=check_config.get_name(), check_params=self._tool_result.get_check_params())

            if check_config.get_name() in errors_count:
                check_result.set_param(Param.RESULT, errors_count[check_config.get_name()])
            else:
                check_result.set_param(Param.RESULT, 0)

            if flag_autoreject and check_config.get_param(Param.AUTOREJECT):
                check_result.set_param(Param.OUTCOME, Outcome.REJECT)
            else:
                if check_config.get_param(Param.LIMIT) >= check_result.get_param(Param.RESULT):
                    check_result.set_param(Param.OUTCOME, Outcome.PASS)
                else:
                    check_result.set_param(Param.OUTCOME, Outcome.FAIL)
                    flag_autoreject = True

            self._tool_result.set_check(check_result)

        self._tool_result.set_param(Param.FULL_OUTPUT, "")
        self._tool_result.set_param(Param.OUTCOME, self._get_outcome_from_checks())

        return
