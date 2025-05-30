from enum import IntEnum

from codecheck.io_model.model_data.language import Language, get_language_by_text, get_language_text_by_language
from codecheck.io_model.model_data.outcome import Outcome, get_outcome_by_text, get_outcome_text_by_outcome


class Param(IntEnum):
    DISABLE_ERROR_CODES = 0
    TEST_PATH = 1
    LIMIT = 2
    SEVERITY_HIGHT_LIMIT = 3
    SEVERITY_MEDIUM_LIMIT = 4
    SEVERITY_LOW_LIMIT = 5
    TYPE = 6
    REFERENCE_DIRECTORY = 7
    OUTCOME = 9
    ENABLED = 10
    AUTOREJECT = 11
    FULL_OUTPUT = 12
    BIN = 13
    ARGUMENTS = 14
    SEVERITY_HIGHT_COUNT = 15
    SEVERITY_MEDIUM_COUNT = 16
    SEVERITY_LOW_COUNT = 17
    RESULT = 18
    ERROR = 19
    FAILED = 20
    PASSED = 21
    SECONDS = 22
    LANGUAGE = 23
    COMPILER = 24
    LEVEL = 25
    COMMENT = 26
    FILE = 27
    ERRORS = 28
    FAILURES = 29


PARAM_CONFIG = {
    Param.DISABLE_ERROR_CODES: {
        "field_name": "disable_error_codes",
        "param_type": list
    },
    Param.TEST_PATH: {
        "field_name": "test_path",
        "param_type": list
    },
    Param.LIMIT: {
        "field_name": "limit",
        "param_type": int
    },
    Param.SEVERITY_HIGHT_LIMIT: {
        "field_name": "severity_hight_limit",
        "param_type": int
    },
    Param.SEVERITY_MEDIUM_LIMIT: {
        "field_name": "severity_medium_limit",
        "param_type": int
    },
    Param.SEVERITY_LOW_LIMIT: {
        "field_name": "severity_low_limit",
        "param_type": int
    },
    Param.TYPE: {
        "field_name": "param_type",
        "param_type": str
    },
    Param.REFERENCE_DIRECTORY: {
        "field_name": "reference_directory",
        "param_type": str
    },
    Param.OUTCOME: {
        "field_name": "outcome",
        "param_type": Outcome
    },
    Param.ENABLED: {
        "field_name": "enabled",
        "param_type": bool
    },
    Param.AUTOREJECT: {
        "field_name": "autoreject",
        "param_type": bool
    },
    Param.FULL_OUTPUT: {
        "field_name": "full_output",
        "param_type": str
    },
    Param.BIN: {
        "field_name": "bin",
        "param_type": str
    },
    Param.ARGUMENTS: {
        "field_name": "arguments",
        "param_type": str
    },
    Param.SEVERITY_HIGHT_COUNT: {
        "field_name": "severity_hight_count",
        "param_type": int
    },
    Param.SEVERITY_MEDIUM_COUNT: {
        "field_name": "severity_medium_count",
        "param_type": int
    },
    Param.SEVERITY_LOW_COUNT: {
        "field_name": "severity_low_count",
        "param_type": int
    },
    Param.RESULT: {
        "field_name": "result",
        "param_type": int
    },
    Param.ERROR: {
        "field_name": "error",
        "param_type": int
    },
    Param.FAILED: {
        "field_name": "failed",
        "param_type": int
    },
    Param.PASSED: {
        "field_name": "passed",
        "param_type": int
    },
    Param.SECONDS: {
        "field_name": "seconds",
        "param_type": float
    },
    Param.LANGUAGE: {
        "field_name": "language",
        "param_type": Language
    },
    Param.COMPILER: {
        "field_name": "compiler",
        "param_type": str
    },
    Param.LEVEL: {
        "field_name": "level",
        "param_type": str
    },
    Param.COMMENT: {
        "field_name": ".comment",
        "param_type": str
    },
    Param.FILE: {
        "field_name": "file",
        "param_type": str
    },
    Param.ERRORS: {
        "field_name": "errors",
        "param_type": int
    },
    Param.FAILURES: {
        "field_name": "failures",
        "param_type": int
    },
}

#
# WORK WITH CustomParams
#


def get_params_available_types():
    return str | int | float | bool | list | Outcome | Language | None


def get_default_value_by_type(param_type: type) -> get_params_available_types():
    if param_type is str:
        return ""
    if param_type is int:
        return None
    if param_type is float:
        return None
    if param_type is bool:
        return None
    if param_type is list:
        return []
    if param_type is Outcome:
        return Outcome.UNDEFINED
    if param_type is Language:
        return None
    return None


def get_field_name_by_param(param: Param) -> str:
    return PARAM_CONFIG[param]['field_name']


def get_type_by_param(param: Param) -> type:
    return PARAM_CONFIG[param]['param_type']


def get_default_value_by_param(param: Param) -> get_params_available_types():
    return get_default_value_by_type(get_type_by_param(param))


def is_value_none(param: Param, value: get_params_available_types()) -> bool:
    return value == get_default_value_by_param(param)


def is_validate_param_type(param: Param, value: get_params_available_types()) -> bool:
    return value is None or type(value) == get_type_by_param(param)

#
#
#


def convert_json_value_to_param_type(param: Param, value) -> get_params_available_types():
    param_type = get_type_by_param(param)
    if param_type == Outcome:
        return get_outcome_by_text(value)
    if param_type == Language:
        return get_language_by_text(value)
    if param_type != type(value):
        return None
    return value


def convert_param_value_to_value_json(param: Param, value) -> get_params_available_types():
    param_type = get_type_by_param(param)
    if param_type == Outcome:
        return get_outcome_text_by_outcome(value)
    if param_type == Language:
        return get_language_text_by_language(value)
    return value


def get_param_by_field_name(field_name: str) -> Param | None:
    for key, value in PARAM_CONFIG.items():
        if value['field_name'] == field_name:
            return key
    return None


def convert_json_to_params(params_json: dict) \
        -> dict[Param, get_params_available_types()]:
    params = {}
    for key, value in params_json.items():
        param = get_param_by_field_name(key)
        if param is not None:
            value = convert_json_value_to_param_type(param, value)
            params[param] = value
    return params


def convert_params_to_json(params: dict[Param, get_params_available_types()]) \
        -> dict[str, get_params_available_types()]:
    params_json = {}
    for param, value in params.items():
        field_name = get_field_name_by_param(param)
        params_json[field_name] = convert_param_value_to_value_json(param, value)
    return params_json
