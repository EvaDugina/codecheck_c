from enum import IntEnum

OUTCOME_TEXT = {
    0: "pass",
    1: "fail",
    2: "reject",
    3: "skip",
    4: "undefined",
}


class Outcome(IntEnum):
    PASS = 0
    FAIL = 1
    REJECT = 2
    SKIP = 3
    UNDEFINED = 4


def get_outcome_by_text(outcome_text: str) -> Outcome | None:
    for key, value in OUTCOME_TEXT.items():
        if value == outcome_text:
            return Outcome(key)
    return Outcome.UNDEFINED


def get_outcome_text_by_outcome(outcome: Outcome) -> str:
    return OUTCOME_TEXT[outcome.value]
