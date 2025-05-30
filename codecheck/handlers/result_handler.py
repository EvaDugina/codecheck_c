#!/usr/bin/env python
# -*- coding: utf-8 -*-
from codecheck.io_model.io_error import get_error_text_by_error_code, ErrorCode


def handle_warning(warning_text: str):
    print("[W]: " + warning_text)


def handle_error(error_code: ErrorCode, text_more: str = None):
    print("[E]: " + get_error_text_by_error_code(error_code))
    if text_more is not None:
        print("--> " + text_more)
    exit(1)


def handle_success():
    print("Автоматичекая проверка завершена!")
