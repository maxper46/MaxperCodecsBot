from aiogram import F, Router, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from filters.filters import (IsDelBookmarkCallbackData,
                             IsArticleNumberCorrectMessageData)
from keyboards.callbacks import ButtonCallbackFactory
from keyboards.bookmarks_kb import (create_bookmarks_keyboard,
                                    create_edit_keyboard)
from keyboards.pagination_kb import create_pagination_keyboard
from keyboards.select_kb import create_select_keyboard
from lexicon.lexicon import LEXICON
from services.file_handling import prepare_article
from keyboards.buttons import buttons_gen
from database.methods import bot_database as db

router = Router()


# Этот хэндлер будет срабатывать на команду "/start" -
# добавлять пользователя в базу данных, если его там еще не было
# и отправлять ему приветственное сообщение
@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(LEXICON[message.text])
    if_user = await db.is_user_exists(message.from_user.id)
    if not if_user:
        await db.create_if_not_exists(user_id=message.from_user.id, current_doc=1, current_art='1',
                                      current_page=1, current_message_id=0, bookmarks={})


# Этот хэндлер будет срабатывать на команду "/help"
# и отправлять пользователю сообщение со списком доступных команд в боте
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(LEXICON[message.text])


# Этот хэндлер будет срабатывать на команду "/continue"
# и отправлять пользователю страницу книги, на которой пользователь
# остановился в процессе взаимодействия с ботом
@router.message(Command(commands='continue'))
async def process_continue_command(message: Message, bot: Bot):
    current_message_id = await db.get_current_message_id(message.from_user.id)
    if current_message_id:
        await bot.edit_message_reply_markup(message_id=current_message_id, chat_id=message.chat.id)
    current_doc, current_article, current_page = await db.get_current_info(message.from_user.id)
    doc = await db.get_doc_data(current_doc, current_article)
    text = f'Статья {current_article}. {doc['title']}\n\n{doc['text']}'
    article = prepare_article(text)
    buttons = buttons_gen(current_page, len(article), doc['prev'], doc['next'])
    mess = await message.answer(
        text=article[current_page],
        reply_markup=create_pagination_keyboard(
            *buttons
        )
    )
    await db.set_current_message_id(message.from_user.id, mess.message_id)


# Этот хэндлер будет срабатывать на команду "/select"
# и запрашивать у пользователя документ для дальнейшей работы,
@router.message(Command(commands='select'))
async def process_select_command(message: Message):
    titles_list = await db.get_titles_list()
    await message.answer(
        text=LEXICON[message.text],
        reply_markup=create_select_keyboard(
            *titles_list
            )
        )


# Этот хэндлер будет срабатывать на команду "/bookmarks"
# и отправлять пользователю список сохраненных закладок,
# если они есть или сообщение о том, что закладок нет
@router.message(Command(commands='bookmarks'))
async def process_bookmarks_command(message: Message):
    bookmarks = await db.get_bookmarks(message.from_user.id)
    if bookmarks:
        bookmarks_values = list(bookmarks.values())
        await message.answer(
            text=LEXICON[message.text],
            reply_markup=create_bookmarks_keyboard(
                *bookmarks_values
            )
        )
    else:
        await message.answer(text=LEXICON['no_bookmarks'])


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "вперед"
# во время взаимодействия пользователя с сообщением-книгой
@router.callback_query(F.data == 'forward')
async def process_backward_press(callback: CallbackQuery):
    current_doc, current_article, prev_page = await db.get_current_info(callback.from_user.id)
    await db.set_current_page(callback.from_user.id, prev_page + 1)
    current_doc, current_article, current_page = await db.get_current_info(callback.from_user.id)
    doc = await db.get_doc_data(current_doc, current_article)
    text = f'Статья {current_article}. {doc['title']}\n\n{doc['text']}'
    article = prepare_article(text)
    buttons = buttons_gen(current_page, len(article), doc['prev'], doc['next'])
    await callback.message.edit_text(
        text=article[current_page],
        reply_markup=create_pagination_keyboard(
            *buttons
        )
    )
    await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "назад"
# во время взаимодействия пользователя с сообщением-книгой
@router.callback_query(F.data == 'backward')
async def process_backward_press(callback: CallbackQuery):
    current_doc, current_article, next_page = await db.get_current_info(callback.from_user.id)
    await db.set_current_page(callback.from_user.id, next_page - 1)
    current_doc, current_article, current_page = await db.get_current_info(callback.from_user.id)
    doc = await db.get_doc_data(current_doc, current_article)
    text = f'Статья {current_article}. {doc['title']}\n\n{doc['text']}'
    article = prepare_article(text)
    buttons = buttons_gen(current_page, len(article), doc['prev'], doc['next'])
    await callback.message.edit_text(
        text=article[current_page],
        reply_markup=create_pagination_keyboard(
            *buttons
        )
    )
    await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# с названием документа из списка документов
@router.callback_query(ButtonCallbackFactory.filter(F.category == 1))
async def process_category_press(callback: CallbackQuery,
                                 callback_data: ButtonCallbackFactory):
    index = callback_data.index
    await db.set_current_doc(callback.from_user.id, index)
    doc_title = await db.get_doc_data(index, 'doc_title')
    first_number = await db.get_doc_data(index, 'first_number')
    last_number = await db.get_doc_data(index, 'last_number')
    await callback.message.edit_text(text=f'{doc_title}\n\n'
                                          f'Введите номер статьи, которую хотите посмотреть\n'
                                          f'от {first_number} до {last_number}\n'
                                          f'Введите /select, чтобы выбрать другой документ.\n'
                                          f'Введите /start, чтобы вернуться к началу.')


# Этот хэндлер выводит выбранную пользователем статью
@router.message(IsArticleNumberCorrectMessageData())
async def process_document_load(message: Message, bot: Bot):
    current_message_id = await db.get_current_message_id(message.from_user.id)
    if current_message_id:
        await bot.edit_message_reply_markup(message_id=current_message_id, chat_id=message.chat.id, reply_markup=None)
    article_numb = str(message.text)
    await db.set_current_art(message.from_user.id, article_numb)
    current_doc, current_article, current_page = await db.get_current_info(message.from_user.id)
    doc = await db.get_doc_data(current_doc, current_article)
    text = f'Статья {current_article}. {doc['title']}\n\n{doc['text']}'
    article = prepare_article(text)
    buttons = buttons_gen(current_page, len(article), doc['prev'], doc['next'])
    mess = await message.answer(
        text=article[current_page],
        reply_markup=create_pagination_keyboard(
            *buttons
        )
    )
    await db.set_current_message_id(message.from_user.id, mess.message_id)


# Этот хендлер будет срабатывать на нажатие инлайн-кнопки "Предыдущая"
# при чтении документа
@router.callback_query(F.data == 'previous')
async def process_previous_document(callback: CallbackQuery):
    current_doc, prev_article, _ = await db.get_current_info(callback.from_user.id)
    tmp_curr = await db.get_doc_data(current_doc, prev_article)
    current_article = dict(tmp_curr)['prev']
    await db.set_current_art(callback.from_user.id, current_article)
    current_doc, current_article, current_page = await db.get_current_info(callback.from_user.id)
    doc = await db.get_doc_data(current_doc, current_article)
    text = f'Статья {current_article}. {doc['title']}\n\n{doc['text']}'
    article = prepare_article(text)
    buttons = buttons_gen(current_page, len(article), doc['prev'], doc['next'])
    await callback.message.edit_text(
        text=article[current_page],
        reply_markup=create_pagination_keyboard(
            *buttons
        )
    )
    await callback.answer()


# Этот хендлер будет срабатывать на нажатие инлайн-кнопки "Следующая"
# при чтении документа
@router.callback_query(F.data == 'next')
async def process_previous_document(callback: CallbackQuery):
    current_doc, next_article, _ = await db.get_current_info(callback.from_user.id)
    tmp_curr = await db.get_doc_data(current_doc, next_article)
    current_article = dict(tmp_curr)['next']
    await db.set_current_art(callback.from_user.id, current_article)
    current_doc, current_article, current_page = await db.get_current_info(callback.from_user.id)
    doc = await db.get_doc_data(current_doc, current_article)
    text = f'Статья {current_article}. {doc['title']}\n\n{doc['text']}'
    article = prepare_article(text)
    buttons = buttons_gen(current_page, len(article), doc['prev'], doc['next'])
    await callback.message.edit_text(
        text=article[current_page],
        reply_markup=create_pagination_keyboard(
            *buttons
        )
    )
    await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# с номером текущей страницы и добавлять текущую страницу в закладки
@router.callback_query(lambda x: '/' in x.data and x.data.replace('/', '').isdigit())
async def process_page_press(callback: CallbackQuery):
    bookm_counter = await db.bookmarks_counter(callback.from_user.id)
    if bookm_counter < 30:
        current_doc, current_article, current_page = await db.get_current_info(callback.from_user.id)
        key = ' '.join([str(current_doc), current_article, str(current_page)])
        is_exist = await db.is_bookmark_exists(callback.from_user.id, key)
        if is_exist:
            await callback.answer(LEXICON['already_added'])
        else:
            doc_title = await db.get_doc_data(current_doc, 'doc_title')
            bookmark = f'{doc_title}, ст. {current_article}'
            await db.add_bookmark(callback.from_user.id, key, bookmark)
            await callback.answer(LEXICON['bookmark_added'])
    else:
        await callback.answer(LEXICON['many_bookmarks'])


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# с закладкой из списка закладок
@router.callback_query(ButtonCallbackFactory.filter(F.category == 2))
async def process_bookmark_press(callback: CallbackQuery,
                                 callback_data: ButtonCallbackFactory, bot: Bot):
    current_message_id = await db.get_current_message_id(callback.from_user.id)
    if current_message_id:
        await bot.edit_message_reply_markup(message_id=current_message_id, chat_id=callback.message.chat.id)
    index = callback_data.index
    bookmarks = await db.get_bookmarks(callback.from_user.id)
    key = list(bookmarks.keys())[index]
    current_doc, current_article, current_page = key.split()
    current_doc, current_page = int(current_doc), int(current_page)
    await db.set_current_doc(callback.from_user.id, current_doc, current_article, current_page)
    doc = await db.get_doc_data(current_doc, current_article)
    text = f'Статья {current_article}. {doc['title']}\n\n{doc['text']}'
    article = prepare_article(text)
    buttons = buttons_gen(current_page, len(article), doc['prev'], doc['next'])
    mess = await callback.message.edit_text(
        text=article[current_page],
        reply_markup=create_pagination_keyboard(
            *buttons
        )
    )
    await db.set_current_message_id(callback.from_user.id, mess.message_id)


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# "редактировать" под списком закладок
@router.callback_query(F.data == 'edit_bookmarks')
async def process_edit_press(callback: CallbackQuery):
    bookmarks = await db.get_bookmarks(callback.from_user.id)
    bookmarks_values = list(bookmarks.values())
    await callback.message.edit_text(
        text=LEXICON[callback.data],
        reply_markup=create_edit_keyboard(
            *bookmarks_values
        )
    )


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# "отменить" во время работы со списком закладок (просмотр и редактирование)
@router.callback_query(F.data == 'cancel')
async def process_cancel_press(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON['cancel_text'])


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# с закладкой из списка закладок к удалению
@router.callback_query(IsDelBookmarkCallbackData())
async def process_del_bookmark_press(callback: CallbackQuery):
    bookmarks = await db.get_bookmarks(callback.from_user.id)
    key = list(bookmarks.keys())[int(callback.data[:-3])]
    await db.del_bookmark(callback.from_user.id, key)
    bookmarks = await db.get_bookmarks(callback.from_user.id)
    if bookmarks:
        bookmarks_values = list(bookmarks.values())
        await callback.message.edit_text(
            text=LEXICON['edit_bookmarks'],
            reply_markup=create_edit_keyboard(
                *bookmarks_values
            )
        )
    else:
        await callback.message.answer(text=LEXICON['no_bookmarks'])
