from aiogram import Bot, types
from aiogram.types import InputMediaPhoto
from aiogram.fsm.context import FSMContext

from database.default_setting import load_list_admins
from database.orm_query import *

from handlers.menu_processing_admin import def_main_menu_admin
from handlers.menu_together_use import (def_pages,
                                        def_list_out_one_question_parents,
                                        def_question_change_photo,
                                        def_question_history,
                                        def_clear_question_message,
                                        def_question_main_user,
                                        def_start_timer_clear_messages, scheduler, TIME_CLEAR_MESSAGE,
                                        def_timer_clear_messages)

from keyboards.inline_together_use import get_empty_btns
from keyboards.inline_user import *

from utils.paginator import Paginator

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())


# ***********************************************************************************************
async def get_menu_content(
        message: types.Message,
        session: AsyncSession,
        bot: Bot,
        state: FSMContext,
        level: int,
        menu_name: str,
        product_id: int,
        category: int | None = None,
        page: int | None = None,
        read_description: bool | None = None,
):

    if level == 0:
        return await def_main_menu_user(session, state, bot, level)
    elif level == 1:
        return await def_catalog(session, bot, state)
    elif level == 2:
        return await def_type(message, bot, session, state, level, category, menu_name)
    elif level == 3:
        return await def_products(message, bot, session, state, category, menu_name)
    elif level == 4:
        return await def_product_change_photo(
            bot, session, state, product_id, category, page, menu_name, read_description)

    elif level == 10:
        return await def_information(session, level)
    elif level == 11:
        return await def_about(session, level)
    elif level == 12:
        return await def_for_devolep(session, state, level)

    elif level == 20:
        return await def_question_main(session, bot, state)
    elif level == 21:
        return await def_question_theme_choice(session, level)
    elif level == 22:
        return await def_new_question_ask(session, state, menu_name, category)
    elif level == 23:
        return await def_question_change_photo(
            session, bot, state, level, 21, menu_name, category, product_id, False, page)
    elif level == 24:
        return await def_list_out_one_question_parents(
            message, bot, session, state, menu_name, level, 21, 10, product_id, False)

    elif level == 25:
        return await def_question_history(
            message, bot, state, session, level, 20, False, False)
    elif level == 26:
        return await def_question_change_photo(
            session, bot, state, level, 20, menu_name, category, product_id, False, page)
    elif level == 27:
        return await def_list_out_one_question_parents(
            message, bot, session, state, menu_name, level, 25, 10, product_id, False)

    else:
        return await def_main_menu_user(session, state, bot, level)


# level=0
async def def_main_menu_user(session: AsyncSession, state: FSMContext, bot: Bot, level: int):
    # проверка на админа после перезагрузки сервера или смены интерфейса
    await load_list_admins(session, bot)  # загрузка из бд адресов админа и владельца

    data_state = await state.get_data()
    telegram_id = data_state['telegram_id']

    if telegram_id in bot.my_admins_list:
        return await def_main_menu_admin(session, bot, state, level)

    await def_clear_question_message(bot, state)
    await state.update_data({'get_message': ''})

    result = await orm_get_general(session, 'main')
    image = InputMediaPhoto(media=result.picture, caption='Основное меню')
    reply_markup = get_user_main_btns(level=level)
    return image, reply_markup


# level=1
async def def_catalog(session: AsyncSession, bot: Bot, state: FSMContext):
    return await def_question_main_user(session, bot, state, False)


# level=2
async def def_type(
        message: types.Message, bot: Bot, session: AsyncSession, state: FSMContext,
        level: int, category: int, menu_name: str):
    # поиск типов
    categories = await orm_get_prod_cat_no_types(session, menu_name)
    if len(categories) == 0:
        #  типов для этой категории нет, перехожу в товары
        return await def_products(message, bot, session, state, category, menu_name)

    image = InputMediaPhoto(media=categories[0].picture, caption=f'Типы категории: "{categories[0].cat_name}"')
    reply_markup = get_user_catalog_type_btns(level=level, categories=categories)
    return image, reply_markup


# level=3
async def def_products(
        message: types.Message, bot: Bot, session: AsyncSession, state: FSMContext,
        category: int, menu_name: str):

    cat_name = menu_name

    products = await orm_get_products(session, cat_id=category, frozen=False)

    image_first, reply_markup_first = await def_out_pictures_in_product(session, 1, products[0], cat_name, 1)

    message_show = {}
    count = 1
    while count <= len(products)-1:
        product = products[count]
        count += 1
        image, reply_markup = await def_out_pictures_in_product(session, 1, product, cat_name, 0)
        message_product = await message.answer_photo(
            photo=image.media, caption=image.caption, reply_markup=reply_markup, parse_mode='Markdown')
        message_show.update({product.id: message_product.message_id})

    await def_start_timer_clear_messages(session, bot, state, message_show, False, False)

    return image_first, reply_markup_first


async def def_out_pictures_in_product(
        session: AsyncSession, page: int, product: Products, cat_name: str,
        first: int, read_description: bool = False):
    pictures = await orm_get_product_pictures(session, product.id)
    paginator = Paginator(pictures, page=page)
    picture = paginator.get_page()[0]
    pagination_btns = def_pages(paginator)

    caption = (f"*{cat_name} {product.name}*\n"
               f"*Цвет:* _{product.color}_\n"
               f"*Размер:* _{product.size}_\n"
               f"*Пол:* _{product.gender}_\n"
               f"*Состав:*\n_{product.composition}_\n")
    if read_description:
        caption += f"*Описание🔼:* _{product.description}_\n"
    else:
        caption += f"*Описание🔽*\n"
    caption += f"\nфото {paginator.page} из {paginator.pages}"

    image = InputMediaPhoto(media=picture.picture, caption=caption, parse_mode='Markdown')
    reply_markup = get_user_products_btns(cat_name=cat_name,
                                          page=page,
                                          pagination_btns=pagination_btns,
                                          product_id=product.id,
                                          link=product.link,
                                          first=first,
                                          read_description=read_description)
    return image, reply_markup


# level=4
async def def_product_change_photo(
        bot: Bot, session: AsyncSession, state: FSMContext, product_id, category: int, page: int,
        menu_name: str, read_description: bool):

    cat_name = menu_name
    product = await orm_get_product_id(session, id=product_id)

    data_state = await state.get_data()
    telegram_id = data_state['telegram_id']
    if category == 1:
        #  первое сообщение
        first = 1
        edit_message = data_state['edit_message']
    else:
        first = 0
        message_show = data_state['message_show']
        edit_message = message_show[str(product.id)]

    image, reply_markup = await def_out_pictures_in_product(session, page, product, cat_name, first, read_description)
    # await edit_message.edit_media(media=image, reply_markup=reply_markup)
    await bot.edit_message_media(media=image,
                                 chat_id=telegram_id,
                                 message_id=edit_message,
                                 reply_markup=reply_markup)

    scheduler_job_id = data_state['scheduler_job_id']
    if scheduler_job_id != '':
        if scheduler.get_job(scheduler_job_id) != None:
            # scheduler.reschedule_job(job_id=scheduler_job_id, trigger='interval', seconds=TIME_CLEAR_MESSAGE)
            scheduler.reschedule_job(job_id=scheduler_job_id, trigger='interval', hours=TIME_CLEAR_MESSAGE)

        else:
            scheduler_job = scheduler.add_job(func=def_timer_clear_messages,
                                              trigger='interval',
                                              hours=TIME_CLEAR_MESSAGE,
                                              # seconds=TIME_CLEAR_MESSAGE,
                                              args=(session, bot, state, False, telegram_id, False))
            await state.update_data({'scheduler_job_id': scheduler_job.id})

    return None, None


# ***********************************************************************************************
# level=20
async def def_question_main(session: AsyncSession, bot: Bot, state: FSMContext):
    return await def_question_main_user(session, bot, state, True)


# level=21
async def def_question_theme_choice(session: AsyncSession, level: int):
    themes = await orm_get_category_questions(session)
    result = await orm_get_general(session, 'question')
    image = InputMediaPhoto(media=result.picture, caption='Выберите тему для вопроса:')
    reply_markup = get_user_question_theme_choice_btns(level=level, categories=themes)
    return image, reply_markup


# level=22
async def def_new_question_ask(session: AsyncSession, state: FSMContext, menu_name: str, category: int):
    await state.update_data({'get_message': 'new_question_text'})
    await state.update_data({'category_question_id': category})
    # await state.update_data({'cat_name': menu_name})

    theme = await orm_get_name_category_question(session, menu_name)
    image = InputMediaPhoto(
        media=theme.picture, caption=f'{theme.description} \n\n*Напишите вопрос.*', parse_mode='Markdown')
    reply_markup = get_empty_btns(level_back=21)
    return image, reply_markup


# ***********************************************************************************************
async def def_information(session, level):
    result = await orm_get_general(session, 'information')
    image = InputMediaPhoto(media=result.picture, caption='Информация')
    reply_markup = get_user_information_btns(level=level)
    return image, reply_markup


async def def_about(session, level):
    result = await orm_get_general(session, 'about_description')
    image = InputMediaPhoto(media=result.picture, caption=result.description)
    reply_markup = get_user_about_btns(level=level)
    return image, reply_markup


async def def_for_devolep(session, state, level):
    await state.update_data({'get_message': 'for_devoloper'})
    result = await orm_get_general(session, 'for_devoloper')

    caption = ('У вас есть замечание или предложение по работе бота?\n'
               'Оставьте сообщение разработчику.\n'
               'Для обратной связи укажите номер контактного телефона.')

    image = InputMediaPhoto(media=result.picture, caption=caption)
    reply_markup = get_user_about_btns(level=level)
    return image, reply_markup
