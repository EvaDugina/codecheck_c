import xml.etree.ElementTree as ET
from xml.dom import minidom

from codecheck_core import Checker
from codecheck_core import CheckResult
from codecheck_core import Outcome
from codecheck_core import Param


class ClangFormat(Checker):

    #
    # GETTERS
    #

    def _get_special_flags(self) -> list[str]:
        return []

    def _get_output_file_name(self) -> str:
        return f"output_{self._tool_config.get_name()}.xml"

    #
    # WORK
    #

    def _run(self) -> list[ET.Element]:

        self.copy_to_test_folder('for_testing/.clang-format', '.clang-format')

        outputs: list = []

        for file_name in self._files_to_check:

            custom_flags: list[str] = [file_name]
            custom_flags += ["--style=file", "--output-replacements-xml"]

            output = self._run_command(
                custom_flags=custom_flags,
                result_type=bytes,
                is_only_custom_flags=True
            )

            file_elem = ET.Element('file', name=str(file_name))
            replacements = ET.fromstring(output)
            file_elem.extend(replacements)

            outputs.append(file_elem)

        return outputs

    def _update_tool_result_from_output(self, outputs: list[ET.Element]):

        replacements = 0
        for output in outputs:
            for elem in output.iter():
                if elem.tag == 'replacement':
                    replacements += 1
                    # elem.clear()

        check_config = self._tool_config.get_checks()[0]
        check_result = CheckResult(self._tool_result.get_check_params())

        check_result.set_param(Param.RESULT, replacements)

        if check_config.get_param(Param.LIMIT) >= check_result.get_param(Param.RESULT):
            check_result.set_param(Param.OUTCOME, Outcome.PASS)
        else:
            check_result.set_param(Param.OUTCOME, Outcome.FAIL)

        self._tool_result.set_check(check_result)

        full_output: ET.Element = ET.Element('clang-format-report')
        for output in outputs:
            full_output.append(output)

        full_output_str = ET.tostring(full_output, encoding="unicode", short_empty_elements=False)\
            .replace("\r\n", "\n").replace("\n", "").replace("  ", " ").replace("  ", " ")
        formatted_full_output_str = minidom.parseString(full_output_str).toprettyxml(indent="\t")

        self._tool_result.set_param(Param.FULL_OUTPUT, str(formatted_full_output_str))
        self._tool_result.set_param(Param.OUTCOME, self._get_outcome_from_checks())

        return
