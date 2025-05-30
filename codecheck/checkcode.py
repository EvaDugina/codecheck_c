import multiprocessing

from codecheck.config import PATH_TO_AUTOTEST
from codecheck.decorators.decorators import time_decorator
from codecheck.handlers import file_handler
from codecheck.io_model.io import Output, Input
from codecheck.io_model.model_data.outcome import Outcome
from codecheck.io_model.model_data.param import Param
from codecheck.io_model.model_data.tools import Config, append_tool_result_to_file


COUNT_PROCCESS = 2
TOOLS_PER_PROCCESS = 2

#
# WORK
#


@time_decorator
def start(args_config_file_path: str, args_files_to_check: [str]):

    file_handler.prepare_autotest_folder()
    file_handler.clear_output()

    output = Output()

    input = Input(args_config_file_path, args_files_to_check)
    run_tools_in_parallel(input.get_config(), input.get_files_to_check())

    output.set_success_result()

    # file_handler.remove_autotest_directory()


#
#
#

global_flag_reject_all: bool = False
global_count_tools: int | None = None


def get_count_procceses() -> int:
    global global_count_tools

    for i in range(1, COUNT_PROCCESS+1):
        if global_count_tools <= i * TOOLS_PER_PROCCESS:
            return i
    return COUNT_PROCCESS


def generate_tools_array(config: Config) -> list[list[dict]]:

    list_tools_for_parallel = []
    for index in range(get_count_procceses()):
        list_tools_for_parallel.append([])

    index = 0
    for tool_config in config.get_tools():
        list_tools_for_parallel[index % get_count_procceses()].append({
            "tool_config": tool_config
        } | config.get_checker_tool_by_tool_name(tool_config.get_name()))
        index += 1

    return list_tools_for_parallel


def run_tools_in_parallel(config: Config, files_to_check: list[str]):
    global global_count_tools

    print("Запуск автоматической проверки...")

    # Определеяем количество процессов и распределяем tools между ними
    global_count_tools = len(config.get_tools())
    list_tools_for_parallel = generate_tools_array(config)

    count_proccesses = get_count_procceses()
    with multiprocessing.Pool(processes=count_proccesses) as pool:
        for i in range(1, count_proccesses + 1):
            pool.apply_async(run_tool, args=(i, list_tools_for_parallel[i - 1], files_to_check, ))
        pool.close()
        pool.join()

    return


def run_tool(proccess_index: int, tools_settings: list[dict], files_to_check: list[str]):
    global global_flag_reject_all

    # print(f"PROCCESS {proccess_index} STARTED!")

    for tool_settings in tools_settings:

        tool_config = tool_settings['tool_config']

        # Начинаем генерировать вывод
        result_checker_tool = tool_settings['result_checker_tool']()
        tool_result = tool_config.generate_tool_result(
            result_checker_tool.get_tool_params(), result_checker_tool.get_check_params()
        )
        append_tool_result_to_file([tool_result])

        # Перемещаем все файлы автотеста в соответствующую папку
        if tool_config.is_param_not_null(Param.TEST_PATH):
            tool_config.set_param(
                Param.TEST_PATH,
                file_handler.copy_files_to_autotesting_folder(tool_config.get_param(Param.TEST_PATH), PATH_TO_AUTOTEST)
            )

        # Если autoreject и есть не пройденные проверки - пропускаем
        if tool_config.get_param(Param.AUTOREJECT) and global_flag_reject_all:
            tool_result.set_param(Param.OUTCOME, Outcome.REJECT)
            append_tool_result_to_file([tool_result])
            continue

        # Определяем класс, осуществляющий проверку
        checker = tool_settings['checker']
        if checker is None:
            continue

        # Инициализируем класс, осуществляющий проверку
        if not tool_config.get_param(Param.ENABLED):
            tool_result.set_param(Param.OUTCOME, Outcome.SKIP)
            append_tool_result_to_file([tool_result])
            continue

        # Выполняем проверку и фиксируем результат
        checker = checker(tool_config, files_to_check, tool_result)
        tool_result = checker.start()
        append_tool_result_to_file([tool_result])

        # Если language == FAIl, отменяем все следующие с autoreject=True
        if tool_result.get_param(Param.OUTCOME) == Outcome.FAIL:
            global_flag_reject_all = True

    # print(f"PROCCESS {proccess_index} ENDED!")


