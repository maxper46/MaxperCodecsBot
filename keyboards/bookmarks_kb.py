from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.lexicon import LEXICON
from keyboards.callbacks import ButtonCallbackFactory


def create_bookmarks_keyboard(*args: str) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    for ind, button in enumerate(args):
        kb_builder.row(InlineKeyboardButton(
            text=button,
            callback_data=ButtonCallbackFactory(category=2, index=ind).pack()
        ))
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON['edit_bookmarks_button'],
            callback_data='edit_bookmarks'
        ),
        InlineKeyboardButton(
            text=LEXICON['cancel'],
            callback_data='cancel'
        ),
        width=2
    )
    return kb_builder.as_markup()


def create_edit_keyboard(*args: str) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    for ind, button in enumerate(args):
        kb_builder.row(InlineKeyboardButton(
            text=f'{LEXICON["del"]} {button}',
            callback_data=f'{ind}del'
        ))
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON['cancel'],
            callback_data='cancel'
        )
    )
    return kb_builder.as_markup()
