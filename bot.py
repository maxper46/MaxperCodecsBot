#!/usr/bin/env python

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram.fsm.state import State, StatesGroup
from config import Config, load_config, redis_db_args
from handlers import other_handlers, user_handlers
from keyboards.main_menu import set_main_menu


logger = logging.getLogger(__name__)


class UserInfo(StatesGroup):
    message_id = State()


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    config: Config = load_config()
    redis: Redis = Redis(**redis_db_args())
    storage = RedisStorage(redis=redis)

    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=storage)

    await set_main_menu(bot)

    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())
