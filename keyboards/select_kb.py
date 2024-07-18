from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.callbacks import ButtonCallbackFactory
from lexicon.lexicon import LEXICON


def create_select_keyboard(*args: str) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    for ind, button in enumerate(args):
        kb_builder.row(InlineKeyboardButton(
            text=button,
            callback_data=ButtonCallbackFactory(category=1, index=ind + 1).pack()
        ))
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON['cancel'],
            callback_data='cancel'
        )
    )
    return kb_builder.as_markup()
