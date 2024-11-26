
from aiogram import F, types, Router, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from loguru import logger

from filters.class_filters import IsUser

from handlers.admin import def_main_menu_admin
from handlers.menu_processing_user import get_menu_content, def_information
from handlers.menu_together_use import def_list_out_one_question_parents

from database.orm_query import *
from database.default_setting import load_list_admins

from keyboards.inline_admin import get_admin_question_from_user_btns
from keyboards.inline_together_use import MenuCallBack
from keyboards.inline_user import get_user_main_btns

user_router = Router()


@user_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession, state: FSMContext, bot: Bot):
    # проверка наличия БД
    await message.delete()

    telegram_id = message.from_user.id
    result = await orm_get_users(session=session)
    if len(result) == 0:
        # БД чистая, первый будет superadmin
        await orm_add_user(session=session, telegram_id=telegram_id, name=message.from_user.first_name)
        await orm_add_admin(session=session, telegram_id=telegram_id, superadmin=True)

        bot.my_admins_list.append(telegram_id)
        bot.superadmin = telegram_id

        logger.info("Зарегистрирован superadmin",
                    telegram_id=telegram_id,
                    name=message.from_user.first_name)
        del_message = await message.answer('Бот "Ariars" приветствует своего разработчика!,\n'
                                           'Вставьте фото по умолчанию')
        await state.update_data({'del_message': del_message})
        await state.update_data({'get_message': 'default'})
    else:
        await state.update_data({'telegram_id': telegram_id})
        await state.update_data({'scheduler_job_id': ''})
        await state.update_data({'get_message': ''})
        await state.update_data({'edit_message': ''})

        result = await orm_get_general(session, 'hello_description')
        picture = result.picture
        caption = result.description
        reply_markup = get_user_main_btns(level=0)

        # проверка на наличие пользователя
        result = await orm_get_user(session=session, telegram_id=telegram_id)
        if result == None:
            # запись нового пользователя
            await orm_add_user(session=session, telegram_id=telegram_id, name=message.from_user.first_name)

        # зашел зарегистрированный пользователь
        logger.info("Пользователь вошел в бот",
                    telegram_id=telegram_id,
                    name=message.from_user.first_name)

        # проверка на админа и владельца
        await load_list_admins(session, bot)  # загрузка из бд адресов админа и владельца
        if telegram_id in bot.my_admins_list:
            # админ, он уйдет в админку
            if telegram_id == bot.superadmin:
                caption = 'Бот "Ariars" приветствует своего владельца!'
            else:
                caption = 'Бот "Ariars" приветствует своего администратора!'
            image, reply_markup = await def_main_menu_admin(session, bot, state, level=0)

        edit_message = await message.answer_photo(photo=picture, caption=caption, reply_markup=reply_markup)
        await state.update_data({'edit_message': edit_message.message_id})



@user_router.callback_query(MenuCallBack.filter(), IsUser())
async def user_menu(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession, bot: Bot, state: FSMContext):
    image, reply_markup = await get_menu_content(
            callback.message,
            session,
            bot,
            state,
            level=callback_data.level,
            menu_name=callback_data.menu_name,
            product_id=callback_data.product_id,
            category=callback_data.category,
            page=callback_data.page,
            read_description=callback_data.read_description)

    # if image != None:
    #     edit_message = await callback.message.edit_media(media=image, reply_markup=reply_markup, parse_mode='Markdown')
    #     await state.update_data({'edit_message': edit_message.message_id})
    #     await callback.answer()
    if image != None:
        data_state = await state.get_data()
        edit_message = data_state['edit_message']
        await bot.edit_message_media(media=image,
                                     chat_id=callback.from_user.id,
                                     message_id=edit_message,
                                     reply_markup=reply_markup)


async def def_refresh_message(bot: Bot, data_state: dict, telegram_id: int, image, reply_markup):
    edit_message = data_state['edit_message']
    # await edit_message.edit_media(media=image, reply_markup=reply_markup)
    await bot.edit_message_media(media=image,
                                 chat_id=telegram_id,
                                 message_id=edit_message,
                                 reply_markup=reply_markup)


# ******************************************************************************************************
@user_router.message(F.photo, IsUser())
async def def_message_foto(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot):
    picture = message.photo[-1].file_id
    caption = message.caption
    if caption == None:
        caption = ""

    data_state = await state.get_data()
    get_message = data_state['get_message']
    await message.delete()

    if get_message.startswith("newquestionphoto_"):
        await def_photo_new_question(message, bot, session, state, data_state, picture, caption)


async def def_photo_new_question(message: types.Message, bot: Bot, session: AsyncSession, state: FSMContext, data_state, picture, caption):
    # сохраняю фото к вопросу
    question_id = int(data_state['get_message'].split("_")[-1])
    # сохраняю фото к вопросу
    await orm_add_questions_pictures(session, question_id, picture, caption)

    await def_list_out_one_question_parents(
        message, bot, session, state, '', 24, 21, 20, question_id, False)


# ****************************************************************************************************
@user_router.message(F.text, IsUser())
async def def_message_text(message: types.Message, state: FSMContext, session: AsyncSession, bot:Bot):
    data_state = await state.get_data()
    get_message = data_state['get_message']
    await message.delete()

    if message.text == 'admin':
        await def_user_to_admin(state, session, bot, message.from_user.id, data_state)
    elif get_message == 'new_question_text':
        await def_text_new_question(message, state, session, bot, data_state)
    elif get_message.startswith("textanswerquestion_"):
        await def_text_answer_question(message, state, session, bot, data_state, get_message)
    elif get_message == 'for_devoloper':
        await def_text_for_devoloper(message, state, session, bot, data_state)


async def def_user_to_admin(state: FSMContext, session: AsyncSession, bot: Bot, telegram_id: int, data_state: dict):
    # переход в режим покупателя
    admins = await orm_get_admins_no_work(session=session)
    for admin in admins:
        if telegram_id == admin.telegram_id:
            await orm_change_user_admin(session, telegram_id)
            await load_list_admins(session, bot)  # загрузка из бд адресов админа и владельца

            image, reply_markup = await def_main_menu_admin(session, bot, state, level=0)
            await def_refresh_message(bot, data_state, telegram_id, image, reply_markup)


async def def_text_new_question(
        message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot, data_state: dict):
    # запись нового вопроса
    question_text = message.text

    question_id = await orm_add_question(session=session,
                                         telegram_id=message.from_user.id,
                                         category_question_id=data_state['category_question_id'],
                                         parents_id=0,
                                         question_text=question_text,
                                         answer_text='')

    # отправляю уведомление всем админам
    reply_markup = get_admin_question_from_user_btns(question_id=question_id)
    for telegram_id in bot.my_admins_list:
        await bot.send_message(chat_id=telegram_id,
                               text=f'Вам пришел вопрос от покупателя!',
                               reply_markup=reply_markup)

    # для записи фото
    await state.update_data({'get_message': f'newquestionphoto_{question_id}'})
    # для вывода карточки с фото
    await def_list_out_one_question_parents(
        message, bot, session, state, '', 24, 21, 20, question_id, False)



async def def_text_answer_question(
        message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot, data_state, get_message):
    # пишим еще вопрос от покупателя
    # сохраняю продолжение переписки покупателя
    id_question = int(get_message.split("_")[-1])
    question_text = message.text

    # делаю не активным текущее сообщение
    await orm_question_frozen(session, id_question)

   # проверка прародителя
    if data_state['parents_id'] == 0:
        parents_id = id_question
    else:
        parents_id = data_state['parents_id']

    question_id = await orm_add_question(session=session,
                                         telegram_id=message.from_user.id,
                                         category_question_id=data_state['theme'],
                                         parents_id=parents_id,
                                         question_text=question_text,
                                         answer_text='')

    # отправляю уведомление всем админам
    reply_markup = get_admin_question_from_user_btns(question_id=question_id)
    for telegram_id in bot.my_admins_list:
        await bot.send_message(chat_id=telegram_id,
                               text=f'Вам пришел вопрос от покупателя!',
                               reply_markup=reply_markup)

    # await def_clear_question_message(state)
    # для записи фото
    await state.update_data({'get_message': f'newquestionphoto_{question_id}'})
    # для вывода карточки с фото
    await def_list_out_one_question_parents(
        message, bot, session, state, '', 24, 21, 20, question_id, False)


# *****************************************************************************
async def def_text_for_devoloper(
        message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot, data_state: dict):
    # отправка вопроса разработчику
    await state.update_data({'get_message': ''})

    question_text = f'Вопрос разработчику от {message.from_user.first_name} (id: {message.from_user.id}):\n\n{message.text}'

    await orm_add_question_for_devoloper(session, question_text)

    # отправляю уведомление
    await bot.send_message(chat_id=177378414, text=question_text)
    # ухожу в раздел информация
    image, reply_markup = await def_information(session, 10)
    await def_refresh_message(bot, data_state, message.from_user.id, image, reply_markup)

