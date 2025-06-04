import os
import xml.etree.ElementTree as ET

from codecheck_core import Checker
from codecheck_core import CheckResult
from codecheck_core import Outcome
from codecheck_core import Param


class Catch2(Checker):

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

    def _run(self):

        self.copy_to_test_folder('for_testing/catch2.hpp', 'catch2.hpp')

        results = []

        for test_path in self._tool_config.get_param(Param.TEST_PATH):
            compilation_custom_flags: list = [test_path]

            if "." not in test_path:
                base_test_name = test_path
            else:
                base_test_name = os.path.basename(test_path).split(".")[0]

            for file_path in self._files_to_check:

                if "." not in file_path:
                    continue

                compilation_custom_flags.append(file_path)

                # base_file_name = os.path.basename(file_path).split(".")[0]
                # compilation_custom_flags.append(base_file_name + '.o')

            compilation_custom_flags += ['-o', base_test_name, "-I", "/stable"]

            try:
                self._run_command_with_timeout(
                    bin='g++',
                    custom_flags=compilation_custom_flags,
                    is_only_custom_flags=True
                )
            except Exception as e:
                print("Exception: " + str(e))
                continue

            run_test_custom_flags = ['--reporter', 'junit']
            result_xml = self._run_command_with_timeout(
                bin=f'./{base_test_name}',
                custom_flags=run_test_custom_flags,
                result_type=str,
                is_only_custom_flags=True
            )
            # print(result_xml)

            result_output = self._run_command_with_timeout(
                bin=f'./{base_test_name}',
                result_type=str,
                is_only_custom_flags=True
            )
            # print(result_output)

            results.append({
                "test_name": base_test_name,
                "xml": result_xml,
                "output": result_output
            })

        return results

    def _update_tool_result_from_output(self, results):

        # print("_update_tool_result_from_output")

        if len(results) == 0:
            for test_path in self._tool_config.get_param(Param.TEST_PATH):
                if "." not in test_path:
                    base_test_name = test_path
                else:
                    base_test_name = os.path.basename(test_path).split(".")[0]
                check_result = CheckResult(name=base_test_name,
                                           check_params=self._tool_result.get_check_params())
                check_result.set_param(Param.RESULT, 0)
                check_result.set_param(Param.OUTCOME, Outcome.UNDEFINED)
                self._tool_result.set_check(check_result)

            self._tool_result.set_param(Param.FULL_OUTPUT, f"Ошибка! Отсутствуют результаты!")
            self._tool_result.set_param(Param.OUTCOME, Outcome.FAIL)

            return

        flag_autoreject = False
        check_config = self._tool_config.get_checks()[0]
        full_output = ""
        for result in results:

            check_result = CheckResult(name=check_config.get_name(), check_params=self._tool_result.get_check_params())

            error = 0
            failed = 0
            for elem in ET.fromstring(result["xml"]).iter():
                if elem.tag == 'testsuite':
                    error += int(elem.get('errors'))
                    failed += int(elem.get('failures'))
                    elem.clear()

            check_result.set_param(Param.ERROR, error)
            check_result.set_param(Param.FAILED, failed)

            full_output += result['output'] + "\n\n"

            if flag_autoreject and check_config.get_param(Param.AUTOREJECT):
                check_result.set_param(Param.OUTCOME, Outcome.REJECT)
            else:
                if error == 0 and failed <= check_config.get_param(Param.LIMIT):
                    check_result.set_param(Param.OUTCOME, Outcome.PASS)
                else:
                    check_result.set_param(Param.OUTCOME, Outcome.FAIL)
                    flag_autoreject = True

            self._tool_result.set_check(check_result)

        self._tool_result.set_param(Param.FULL_OUTPUT, full_output)
        self._tool_result.set_param(Param.OUTCOME, self._get_outcome_from_checks())
