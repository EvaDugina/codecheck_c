import re
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

    def __find_main_in_file(self, file_path):
        """Определяет тип точки входа в файле"""
        with open(file_path) as f:
            content = f.read()

        if re.search(r'int\s+main\s*\(', content):
            return 'standard'
        elif re.search(r'void\s+main\s*\(', content):
            return 'void'
        # elif re.search(r'test_main', content):
        #     return 'test'
        return None

    def __check_file_compilation(self, bin: str, file_path: str) -> bool:

        entry_type = self.__find_main_in_file(file_path)

        if not entry_type:
            print(f"Пропуск: {file_path} не содержит точку входа")
            return False

        custom_flags = {
            'standard': ["-g", file_path, "-o", test_executable_name],
            'void': ["-g", "-DINT_MAIN_FIX", file_path, "-o", test_executable_name],
            # 'test': "{bin} -g file.c -lcriterion -o tests"
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

    def _run(self):

        if self._tool_config.get_param_as_json(Param.COMPILER) == "gcc":
            bin = "gcc"
        else:
            bin = "g++"

        outputs: list = []

        for file_path in self._files_to_check:

            if self.__check_file_compilation(bin, file_path):

                custom_flags = '--xml=yes --xml-file=valgrind.xml ./{} > /dev/null'.format(test_executable_name).split(" ")
                self._run_command_with_timeout(
                    custom_flags=custom_flags,
                    files_to_wait=['valgrind.xml'],
                    is_only_custom_flags=True)

                custom_flags = './{} > /dev/null 2> ./{}'.format(test_executable_name, self._get_output_file_name()).split(" ")

                output = self._run_command_with_timeout(
                    custom_flags=custom_flags,
                    result_type=str,
                    is_only_custom_flags=True)

                outputs.append(output)

            else:
                continue

        return outputs

    def _update_tool_result_from_output(self, outputs: list):

        print(outputs)

        if len(outputs) == 0:
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
        for event, elem in self.iterate_xml_file('valgrind.xml'):  # incremental parsing
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
