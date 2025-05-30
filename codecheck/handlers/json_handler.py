import json
from typing import Optional, Dict, Any

import codecheck.handlers.file_handler as file_handler


def safety_loads(text_json: str, filename: str = "") -> Optional[Dict[str, Any]]:

    if filename != "":
        filename = f" '{filename}' "
    else:
        filename = " "

    try:
        return json.loads(text_json)
    except json.JSONDecodeError as e:
        print(f"Invalid{filename}JSON: {str(e)}")
        return None
    except TypeError:
        print(f"Передан не строковый объект{filename}")
        return None
    except ValueError as e:
        print(f"Validation{filename}error: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error{filename}processing: {str(e)}")
        return None


def read_json_from_file(filename: str) -> Optional[Dict[str, Any]]:
    content = file_handler.read_text_from_file(filename)
    if not content:
        return None

    if not content.strip().startswith(('{', '[')):
        print(f"File {filename} does not contain valid JSON")

    return safety_loads(content, filename)


def write_json_to_file(filename: str, output_json: {}) -> bool:
    # 1. Предварительная проверка данных
    try:
        json_str = json.dumps(output_json, ensure_ascii=False, indent=4)
    except (TypeError, ValueError) as e:
        print(f"Ошибка сериализации JSON: {e}")
        return False

    # 2. Запись с обработкой ошибок
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json_str)
            return True
    except IOError as e:
        print(f"Ошибка записи JSON: {e}")
        return False


