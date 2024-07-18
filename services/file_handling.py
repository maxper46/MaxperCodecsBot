import os
import sys


PAGE_SIZE = 800


def _get_part_text(text: str, start: int, page_size: int) -> tuple[str, int] | None:
    # we use HTML parse mode in our bot, so we need to edit some symbols
    text = text.replace('<', '&lt').replace('>', '&gt').replace('&', '&amp')
    end = start + page_size
    if end >= len(text):
        return text[start:], len(text) - start

    for i in range(end - 1, start - 1, -1):
        if text[i] in ",.!:;?":
            return text[start:i + 1], i + 1 - start


def prepare_article(text: str) -> dict:
    book = {}
    page_number, begin_page = 1, 0
    while begin_page < len(text):
        page_text, page_size = _get_part_text(text, begin_page, PAGE_SIZE)
        book[page_number] = page_text.lstrip()
        begin_page += page_size
        page_number += 1
    return book
