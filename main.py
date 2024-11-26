import asyncio
import json
import os
import redis

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from dotenv import find_dotenv, load_dotenv

from handlers.menu_together_use import scheduler

load_dotenv(find_dotenv())

from database.middleware import DataBaseSession
from database.engine import create_db, session_maker, drop_db

from handlers.user import user_router
from handlers.admin import admin_router

from loguru import logger
# from notifiers.logging import NotificationHandler

bot = Bot(token=os.getenv('TOKEN'))
bot.my_admins_list = []
bot.supeadmin = 0

storage = RedisStorage.from_url(os.getenv('REDIS_URL'))
dp = Dispatcher(storage=storage)
dp.include_router(admin_router)
dp.include_router(user_router)

# Конфигурирую  logger
LOG_FILE = 'logger/info.json'


async def on_startup():
    new_start = False
    if new_start:
        # await drop_db()
        await create_db()
        print('База создана')
        try:
            os.remove(LOG_FILE)
        except ():
            print('Файла лога и так нет')
    else:
        db_redis = redis.Redis()
        keys_redis = db_redis.keys()
        for key_redis in keys_redis:
            value_b = db_redis[key_redis]
            value_dict = json.loads(value_b.decode("utf-8"))
            if value_dict['scheduler_job_id'] != '':
                telegram_id = value_dict['telegram_id']
                message_show = value_dict['message_show']
                messages_delete = list(message_show.values())
                await bot.delete_messages(telegram_id, messages_delete)

    logger.add(LOG_FILE, format='{extra[telegram_id]} {extra[name]} {time} {level} {message}',
               level='INFO',
               rotation='1 month',
               compression='zip',
               colorize=True,
               serialize=True
               )

    # # прописываем параметры телеграм бота
    # params = {
    #     'token': os.getenv('TOKEN'),
    #     'chat_id': os.getenv('ADMIN')
    # }
    # tg_handler = NotificationHandler("telegram", defaults=params)
    # # добавляем в logger правило, что все логи уровня info и выше отсылаются в телегу
    # logger.add(tg_handler, level="ERROR")

    logger.info("Бот успешно запущен!", telegram_id=0, name='bot')


async def on_shutdown():
    print('бот остановился')
    # logger.critical("Бот остановился!", user_id=0, name='bot', calc_id=0)


async def main():

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    # scheduler.ctx.add_instance(instance=bot, declared_class=Bot)
    scheduler.start()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

asyncio.run(main())
