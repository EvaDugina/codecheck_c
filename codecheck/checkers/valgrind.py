import os.path
import re
import subprocess
import xml.etree.ElementTree as ET

from codecheck_core import Checker
from codecheck_core import CheckResult
from codecheck_core import Outcome
from codecheck_core import Param


class Valgrind(Checker):

    #
    #
    #

    def _get_special_flags(self) -> list[str]:
        return []

    def _get_output_file_name(self) -> str:
        return f"output_{self._tool_config.get_name()}.txt"

    #
    # WORK
    #

    def _run(self) -> list[dict[str, str]]:

        if self._tool_config.get_param_as_json(Param.COMPILER) == "gcc":
            bin = "gcc"
        else:
            bin = "g++"

        results: list = []

        for file_path in self._files_to_check:

            # print(f"Checking {file_path} for main()...")

            o_file_name = "test"
            o_file_name = os.path.basename(file_path).split(".")[0]

            if self.__check_file_compilation(bin, file_path, o_file_name):

                # print(f"Has main() {file_path}!")

                custom_flags = ['--xml=yes', '--xml-file=valgrind.xml', f'./{o_file_name}']
                self._run_command_with_timeout(
                    custom_flags=custom_flags,
                    result_type=str,
                    files_to_wait=['valgrind.xml'],
                    is_only_custom_flags=True)

                custom_flags = [f'./{o_file_name}']

                output = self._run_command_with_timeout(
                    custom_flags=custom_flags,
                    result_type=str,
                    is_only_custom_flags=True)

                results.append({"xml": self.read_file_from_test_folder("valgrind.xml"), "output": output})

            else:
                continue

        return results

    def _update_tool_result_from_output(self, results: list[dict[str, str]]):

        if len(results) == 0:
            for check_config in self._tool_config.get_checks():
                check_result = CheckResult(name=check_config.get_name(),
                                           check_params=self._tool_result.get_check_params())
                check_result.set_param(Param.RESULT, 0)
                check_result.set_param(Param.OUTCOME, Outcome.UNDEFINED)
                self._tool_result.set_check(check_result)

            self._tool_result.set_param(Param.FULL_OUTPUT, f"Ошибка! Отсутствует точка входа!")
            self._tool_result.set_param(Param.OUTCOME, Outcome.FAIL)

            return

        leaks_count = 0
        errors_count = 0
        for result in results:
            for elem in ET.fromstring(result["xml"]).iter():
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

        full_output = ""
        for result in results:
            if full_output != "":
                full_output += "\n\n"
            full_output += result['output']

        self._tool_result.set_param(Param.FULL_OUTPUT, full_output)
        self._tool_result.set_param(Param.OUTCOME, self._get_outcome_from_checks())

        return

    def __find_main_in_file(self, file_path):

        """Определяет тип точки входа в файле"""
        content = self.read_file_from_test_folder(file_path)

        if re.search(r'int\s+main\s*\(', content):
            return 'standard'
        elif re.search(r'void\s+main\s*\(', content):
            return 'void'
        # elif re.search(r'test_main', content):
        #     return 'test'
        return None

    def __check_file_compilation(self, bin: str, file_path: str, o_file_name: str) -> bool:

        entry_type = self.__find_main_in_file(file_path)

        if entry_type is None:
            print(f"Пропуск: {file_path} не содержит точку входа")
            return False

        custom_flags = {
            'standard': ["-g", file_path, "-o", o_file_name],
            'void': ["-g", "-DINT_MAIN_FIX", file_path, "-o", o_file_name],
            # 'test': "{bin} -g file.c -lcriterion -o o_file_name"
        }[entry_type]

        result = self._run_command(
            bin=bin,
            result_type=subprocess.CompletedProcess,
            custom_flags=custom_flags,
            is_only_custom_flags=True)

        if result.returncode != 0:
            print(f"Ошибка компиляции: {result.stderr.decode()}")
            return False

        return True
