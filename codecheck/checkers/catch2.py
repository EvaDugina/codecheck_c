import os
import re
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

        # files_with_main = []

        for file_path in self._files_to_check:
            if self.__prepare_file(file_path):
                pass
                # files_with_main.append(file_path)

        results = []

        for test_path in self._tool_config.get_param(Param.TEST_PATH):

            if "." not in test_path:
                base_test_name = test_path
            else:
                base_test_name = os.path.basename(test_path).split(".")[0]

            # for file_path in files_with_main:

            compilation_custom_flags: list = [test_path] #+ [filepath]

            for file_name in self._files_to_check:
                if "." not in file_name:
                    continue
                # if file_name not in files_with_main:
                compilation_custom_flags.append(file_name)

            compilation_custom_flags += ['-o', base_test_name, "-I", "./", "-DCATCH_TESTS"]

            is_correct, std_output = self._run_command_with_timeout(
                bin='g++',
                custom_flags=compilation_custom_flags,
                is_listen_exit_code=True,
                is_only_custom_flags=True
            )
            if not is_correct:
                results.append({
                    "test_name": base_test_name,
                    "xml": None,
                    "output": std_output
                })
                continue

            run_test_custom_flags = ['--reporter', 'junit']
            is_correct, result_xml = self._run_command_with_timeout(
                bin=f'./{base_test_name}',
                custom_flags=run_test_custom_flags,
                result_type=str,
                is_only_custom_flags=True
            )
            # print(result_xml)

            is_correct, result_output = self._run_command_with_timeout(
                bin=f'./{base_test_name}',
                result_type=str,
                is_only_custom_flags=True
            )

            results.append({
                "test_name": f"{base_test_name}", #+ {os.path.basename(file_path)},
                "xml": result_xml,
                "output": result_output
            })

        return results

    def _update_tool_result_from_output(self, results):

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
            full_output += "----> TEST: " + result['test_name'] + "\n" + result['output'] + "\n\n"

            if result["xml"] is None:
                check_result.set_param(Param.ERROR, 0)
                check_result.set_param(Param.FAILED, 0)
                check_result.set_param(Param.OUTCOME, Outcome.REJECT)
                self._tool_result.set_check(check_result)
                continue

            error = 0
            failed = 0
            for elem in ET.fromstring(result["xml"]).iter():
                if elem.tag == 'testsuite':
                    error += int(elem.get('errors'))
                    failed += int(elem.get('failures'))
                    elem.clear()

            check_result.set_param(Param.ERROR, error)
            check_result.set_param(Param.FAILED, failed)

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

    #
    # CUSTOM
    #

    def __remove_main_function(self, source_code):
        """
        Удаляет функцию main из исходного кода C++, сохраняя остальное содержимое.
        Работает для стандартных вариантов объявления main.
        """
        # Шаблоны для поиска объявления main
        patterns = [
            r'int\s+main\s*\([^)]*\)\s*{',  # int main(...) {
            r'void\s+main\s*\([^)]*\)\s*{',  # void main(...) {
            r'main\s*\([^)]*\)\s*{'  # main(...) {
        ]

        # Поиск начала функции main
        start_match = None
        for pattern in patterns:
            start_match = re.search(pattern, source_code)
            if start_match:
                break

        if not start_match:
            return source_code  # main не найден

        start_index = start_match.start()
        brace_stack = []
        current_index = start_match.end() - 1  # Индекс после найденного совпадения

        # Поиск парных фигурных скобок
        for i in range(start_index, len(source_code)):
            char = source_code[i]

            if char == '{':
                brace_stack.append(i)
            elif char == '}':
                if brace_stack:
                    brace_stack.pop()
                    if not brace_stack:  # Нашли закрывающую скобку для main
                        end_index = i
                        # Удаляем от начала объявления main до закрывающей скобки
                        return source_code[:start_index] + source_code[end_index + 1:]
                # Если стек пуст при закрывающей скобке - ошибка в коде

        return source_code  # Не нашли парную скобку

    def __wrap_main_with_guard(self, source_code) -> [bool, str]:
        """
        Обертывает функцию main в директивы #ifndef CATCH_TESTS ... #endif
        Возвращает модифицированный исходный код
        """
        # Шаблоны для поиска различных вариантов main
        patterns = [
            r'int\s+main\s*\([^)]*\)\s*{',    # int main(...) {
            r'void\s+main\s*\([^)]*\)\s*{',   # void main(...) {
            r'main\s*\([^)]*\)\s*{'            # main(...) {
        ]

        # Поиск начала функции main
        start_match = None
        for pattern in patterns:
            start_match = re.search(pattern, source_code)
            if start_match:
                break

        if not start_match:
            return False, source_code  # main не найдена

        start_index = start_match.start()
        brace_stack = []
        current_index = start_match.end() - 1  # Индекс открывающей фигурной скобки

        # Поиск парной закрывающей скобки
        for i in range(current_index, len(source_code)):
            char = source_code[i]

            if char == '{':
                brace_stack.append(i)
            elif char == '}':
                if brace_stack:
                    brace_stack.pop()
                    if not brace_stack:  # Нашли закрывающую скобку для main
                        end_index = i
                        # Формируем модифицированный код
                        return True, (
                            source_code[:start_index] +
                            "\n#ifndef CATCH_TESTS\n" +
                            source_code[start_index:end_index+1] +
                            "\n#endif" +
                            source_code[end_index+1:]
                        )

        return False, source_code  # Не нашли парную скобку

    def __prepare_file(self, file_path: str) -> bool:
        """Обрабатывает файл: удаляет main и сохраняет результат"""
        code = self.read_file_from_test_folder(file_path)

        is_find_main, new_code = self.__wrap_main_with_guard(code)
        if not is_find_main:
            return False

        self.write_to_file_from_test_folder(file_path, new_code)
        return True
