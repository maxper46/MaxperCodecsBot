from aiogram.filters.callback_data import CallbackData


class ButtonCallbackFactory(CallbackData, prefix='ind'):
    category: int
    index: int
