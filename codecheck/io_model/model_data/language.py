from enum import IntEnum

LANGUAGE_TEXT = {
    0: "C++",
    1: "C",
}


class Language(IntEnum):
    C_PLUS_PLUS = 0
    C = 1


def get_language_by_text(language_text: str) -> Language | None:
    for key, value in LANGUAGE_TEXT.items():
        if value == language_text:
            return Language(key)
    return None


def get_language_text_by_language(language: Language) -> str:
    return LANGUAGE_TEXT[language.value]
