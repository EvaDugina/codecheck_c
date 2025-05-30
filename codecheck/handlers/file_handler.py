import os
import shutil
from typing import Optional

from codecheck.config import PATH_TO_OUTPUT_FILE, PATH_TO_AUTOTEST, PATH_TO_STUDENT_CODE, STUDENT_CODE_FOLDER


def get_path_without_autotesting_structure(path):
    return path.replace(f"{PATH_TO_STUDENT_CODE}/", "")


def read_text_from_file(filename: str) -> Optional[str]:

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
            return content

    except FileNotFoundError:
        print(f"Файл {filename} не найден!")
        return None

    except PermissionError:
        print(f"К файлу {filename} нет прав доступа!")
        return None

    except UnicodeDecodeError:
        print(f"Ошибка кодировки файла {filename}!")
        return None

    except Exception as e:
        print(f"Неизвестная ошибка чтения файла {filename}: {e}")
        return None


def write_text_to_file(filename: str, file_text: str) -> bool:

    try:
        with open(filename, 'w', encoding='utf-8') as file:  # 'x' - эксклюзивное создание
            file.write(file_text)
            return True
    except FileExistsError:
        print(f"Файл {filename} уже существует!")
        return False
    except PermissionError:
        print(f"Нет прав на запись в директорию для создания файла {filename}!")
        return False
    except OSError as e:
        print(f"Ошибка при создании файла {filename}: {e}")
        return False


def remove_all_files_not_folders_from_folder(folder_path: str):
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)


def prepare_autotest_folder():
    if not os.path.exists(PATH_TO_AUTOTEST):
        os.mkdir(PATH_TO_AUTOTEST)
    else:
        remove_all_files_not_folders_from_folder(PATH_TO_AUTOTEST)
    if not os.path.exists(PATH_TO_STUDENT_CODE):
        os.mkdir(PATH_TO_STUDENT_CODE)
    else:
        remove_all_files_not_folders_from_folder(PATH_TO_STUDENT_CODE)


def clear_output():
    write_text_to_file(PATH_TO_OUTPUT_FILE, "")


def copy_file_to_folder(file_path: str, new_file_path: str) -> bool:
    try:
        if os.path.exists(new_file_path):
            os.remove(new_file_path)
        shutil.copy(file_path, new_file_path)
        return True
    except Exception as e:
        print(f"Не удалось скопировать файл {file_path} в директорию {new_file_path}\nError: {e}\n")
        return False


def copy_files_to_autotesting_folder(files: list[str], folder_path: str) -> list[str]:
    copied_files: list[str] = []
    for file_path in files:
        file_name = os.path.basename(file_path)
        new_file_path = f"{folder_path}/{file_name}"
        copy_file_to_folder(file_path, new_file_path)
        if folder_path == PATH_TO_AUTOTEST:
            copied_files.append(file_name)
        else:
            copied_files.append(STUDENT_CODE_FOLDER + "/" + file_name)
    return copied_files



def clear_directory(directory_path):
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)


def remove_autotest_directory():
    shutil.rmtree(PATH_TO_STUDENT_CODE)
    shutil.rmtree(PATH_TO_AUTOTEST)