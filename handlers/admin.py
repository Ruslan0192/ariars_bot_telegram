from aiogram import F, Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto

# from loguru import logger

from filters.class_filters import IsAdmin
from handlers.menu_together_use import def_list_out_one_question_parents

from keyboards.inline_user import MenuCallBack, get_user_answer_from_admin_btns
from keyboards.inline_admin import get_admin_products_btns

from database.orm_query import *
from database.default_setting import *

from handlers.menu_processing_user import def_main_menu_user
from handlers.menu_processing_admin import (get_admin_menu_content,
                                            def_main_menu_admin,
                                            def_themes,
                                            def_general,
                                            def_type_catalog,
                                            def_products,
                                            def_choice_product_color,
                                            def_choice_product_size,
                                            def_choice_product_gender,
                                            def_choice_product_composition,
                                            def_choice_product_description, def_choice_product_photo,
                                            def_choice_product_link, def_choice_product_end, def_theme_edit_photo,
                                            def_theme_edit_name
                                            )
admin_router = Router()


@admin_router.message(CommandStart(), IsAdmin())
async def start_cmd(message: types.Message, session: AsyncSession, state: FSMContext):
    await message.delete()
    result = await orm_get_general(session, 'hello_description')
    image, reply_markup = await def_main_menu_admin(session, state, level=0)
    edit_message = await message.answer_photo(photo=result.picture, caption=result.description, reply_markup=reply_markup)
    await state.update_data({'edit_message': edit_message})


@admin_router.callback_query(MenuCallBack.filter(), IsAdmin())
async def admin_menu(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession, bot: Bot, state: FSMContext):
    image, reply_markup = await get_admin_menu_content(
            callback.message,
            session,
            bot,
            state,
            level=callback_data.level,
            menu_name=callback_data.menu_name,
            product_id=callback_data.product_id,
            category=callback_data.category,
            page=callback_data.page,
            telegram_id=callback.from_user.id)

    if image != None:
        edit_message = await callback.message.edit_media(media=image, reply_markup=reply_markup, parse_mode='Markdown')
        await state.update_data({'edit_message': edit_message})
        await callback.answer()
    #
    # if callback_data.level < 21:
    #     edit_message = await callback.message.edit_media(media=image, reply_markup=reply_markup)
    #     await state.update_data({'edit_message': edit_message})
    #     await callback.answer()


async def def_refresh_message(data_state, image, reply_markup):
    edit_message = data_state['edit_message']
    await edit_message.edit_media(media=image, reply_markup=reply_markup)


# ******************************************************************************************************
@admin_router.message(F.photo, IsAdmin())
async def def_message_foto(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot):
    picture = message.photo[-1].file_id

    data_state = await state.get_data()
    get_message = data_state['get_message']
    await message.delete()

    if get_message == 'default':
        await def_photo_default(message, state, session, picture, data_state)
    elif get_message == 'developer':
        await def_photo_developer(state, session, picture, data_state)
    elif get_message.startswith("editthemephoto_"):
        await def_photo_change_theme_question(message, state, session, picture, data_state, get_message)
    elif get_message.startswith("general_"):
        await def_photo_general_(message, state, session, picture, data_state, get_message)
    elif get_message == "type_catalog":
        await def_photo_type_catalog(state, session, picture, data_state)
    elif get_message == "product_photo":
        await def_photo_product(session, state, picture, data_state)
    # elif get_message == "product_description":
    #     await def_serial_photo_product(state, picture, data_state)

async def def_photo_default(message: types.Message, state: FSMContext, session: AsyncSession, picture, data_state):
    # сохраняю картинки по умолчанию
    await save_default_in_base(session, picture)
    await save_default_question(session, picture)
    await state.update_data({'get_message': f'developer'})

    caption = 'Вставьте фото разработчика'
    image = InputMediaPhoto(media=picture, caption=caption)

    del_message = data_state['del_message']
    await del_message.delete()
    edit_message = await message.answer_photo(photo=image.media, caption=image.caption, reply_markup=None)
    await state.update_data({'edit_message': edit_message})


async def def_photo_developer(state: FSMContext, session: AsyncSession, picture, data_state):
    # сохраняю картинку для разработчика
    await orm_add_general(session,
                          id_name='for_devoloper',
                          name='',
                          description='',
                          value=0,
                          picture=picture,
                          )

    image, reply_markup = await def_main_menu_admin(session, state, level=0)
    await def_refresh_message(data_state, image, reply_markup)
    await state.update_data({'get_message': ''})


async def def_photo_change_theme_question(message: types.Message, state: FSMContext, session: AsyncSession, picture, data_state, get_message):
    # сохраняю картинку и описание для настроек темы вопросов
    theme_name = get_message.split("_")[-1]
    description = message.caption
    if description == None:
        theme = await orm_get_name_category_question(session, theme_name)
        description = theme.description

    await orm_change_category_question(session, name=theme_name, description=description, picture=picture)

    await state.update_data({'get_message': ''})

    image, reply_markup = await def_themes(session, state, 11, data_state['page'])
    await def_refresh_message(data_state, image, reply_markup)


async def def_photo_general_(message: types.Message, state: FSMContext, session: AsyncSession, picture, data_state, get_message):
    # сохраняю картинку и описание для настроек
    id_general = int(get_message.split("_")[-1])
    if data_state['description'] != '':
        description = message.caption
        if description == None:
            description = data_state['description']
    else:
        description = ''
    await orm_change_general(session, id_general, picture, description)

    await state.update_data({'get_message': ''})

    image, reply_markup = await def_general(session, state,14, data_state['page'])
    await def_refresh_message(data_state, image, reply_markup)


async def def_photo_type_catalog(state: FSMContext, session: AsyncSession, picture, data_state):
    # сохраняю картинку для категории
    id_cat_type = data_state['id_cat_type']
    await orm_change_prod_cat_photo(session, id_cat_type, picture)

    image, reply_markup = await def_products(session, state, 3, id_cat_type, 1)
    await def_refresh_message(data_state, image, reply_markup)


async def def_photo_product(session: AsyncSession, state: FSMContext, picture: str, data_state: dict):
    product_pictures = data_state['product_pictures']
    product_pictures.append(picture)
    await state.update_data({'product_pictures': product_pictures})

    image, reply_markup = await def_choice_product_photo(session, state, 33, len(product_pictures))
    await def_refresh_message(data_state, image, reply_markup)


# ******************************************************************************************************
@admin_router.message(F.text, IsAdmin())
async def def_message_text(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot):
    await message.delete()

    data_state = await state.get_data()
    get_message = data_state['get_message']

    if message.text == 'user':
        await def_admin_to_user(session, state, bot, message.from_user.id, data_state)

    elif get_message == "new_theme":
        await def_text_new_theme(message, state, session, data_state)
    elif get_message.startswith("theme_"):
        await def_text_edit_theme(message, state, session, data_state, get_message)

    elif get_message == "catalog":
        await def_text_catalog(message, state, session, data_state)
    elif get_message == "type_catalog":
        await def_text_type_catalog(message, state, session, data_state)
    elif get_message == "product_name":
        await def_text_product(message, state, session, data_state)
    elif get_message == "product_price":
        await def_text_product_price(message, state, session, data_state)
    elif get_message == "product_color":
        await def_text_product_color(message, state, session, data_state)
    elif get_message == "product_size":
        await def_text_product_size(message, state, session, data_state)
    elif get_message == "product_gender":
        await def_text_product_gender(message, state, session, data_state)
    elif get_message == "product_composition":
        await def_text_product_composition(message, state, session, data_state)
    elif get_message == "product_description":
        await def_text_product_description(message, state, data_state)
    elif get_message == "product_link":
        await def_text_product_link(message, state, session, data_state)

    elif get_message.startswith("textanswerquestion_"):
        await def_text_answer_question(message, state, session, bot, data_state, get_message)


async def def_admin_to_user(session: AsyncSession, state: FSMContext, bot: Bot, telegram_id: int, data_state):
    # переход в режим покупателя
    await orm_change_admin_user(session, telegram_id)
    # await load_list_admins(session, bot)  # загрузка из бд адресов админа и владельца

    image, reply_markup = await def_main_menu_user(session, state, bot, telegram_id,0)
    await def_refresh_message(data_state, image, reply_markup)


async def def_text_new_theme(message: types.Message, state: FSMContext, session: AsyncSession, data_state):
    # сохраняю новую категорию товара
    theme_name = message.text
    #     проверка на дубликат
    result = await orm_get_name_category_question(session=session, name=theme_name)
    if result == None:
        # не было, ввожу новое имя
        await orm_add_category_question(session=session, name=theme_name, description='', picture='')

    await state.update_data({'get_message': f'editthemephoto_{theme_name}'})

    result = await orm_get_general(session, 'question')

    caption = (f"Тема: {theme_name}\n\nВставьте фото c описанием темы вопросов")
    image = InputMediaPhoto(media=result.picture, caption=caption)

    await def_refresh_message(data_state, image, None)


async def def_text_edit_theme(message: types.Message, state: FSMContext, session: AsyncSession, data_state, get_message):
    theme_name_old = get_message.split("_")[-1]
    theme_name = message.text

    # проверка на дубликат
    result = await orm_get_name_category_question(session=session, name=theme_name)
    if result == None:
        # есть дубликат
        if theme_name != theme_name_old:
            # не текущее, перезапрашиваю имя
            image, reply_markup = await def_theme_edit_name(session, state, theme_name_old, True)
            await def_refresh_message(data_state, image, reply_markup)
    else:
        # не было, перезаписываю имя
        await orm_change_name_category_question(session, result.id, theme_name)

    image, reply_markup = await def_theme_edit_photo(session, state, theme_name)
    await def_refresh_message(data_state, image, reply_markup)


async def def_text_catalog(message: types.Message, state: FSMContext, session: AsyncSession, data_state):
    # сохраняю новую категорию товара
    cat_name = message.text
    #     проверка на дубликат
    result = await orm_get_prod_cat(session=session, name=cat_name)
    if result == None:
        await orm_add_prod_cat(session=session, name=cat_name)
        await orm_add_prod_cat_type(session=session, cat_name=cat_name, type_name='')

    image, reply_markup = await def_type_catalog(session, state, cat_name)
    await def_refresh_message(data_state, image, reply_markup)


async def def_text_type_catalog(message: types.Message, state: FSMContext, session: AsyncSession, data_state):
    # сохраняю новый тип категории товара
    cat_name = data_state['cat_name']
    type_name = message.text
    #     проверка на дубликат
    result = await orm_get_prod_cat_type(session=session, cat_name=cat_name, type_name=type_name)
    if result == None:
        # проверка на первую запись типа
        result = await orm_get_prod_cat_type(session=session, cat_name=cat_name, type_name='')
        if result == None:
            # типы уже были данной категории
            id_cat_type = await orm_add_prod_cat_type(session=session, cat_name=cat_name, type_name=type_name)
        else:
            # типов не было перезаписваю категорию
            id_cat_type = result.id
            await orm_change_prod_cat_type_name(session=session, id=id_cat_type, type_name=type_name)
    else:
        id_cat_type = result.id

    await state.update_data({'id_cat_type': id_cat_type})

    caption = f"Вставьте фото для категории {cat_name}"
    result = await orm_get_general(session, 'catalog')
    image = InputMediaPhoto(media=result.picture, caption=caption)
    reply_markup = get_admin_products_btns(level=2, category=0, menu_name='photo', product_id=0)
    await def_refresh_message(data_state, image, reply_markup)


async def def_text_product(message: types.Message, state: FSMContext, session: AsyncSession, data_state):
    # сохраняю новый товар
    product_name = message.text
    await state.update_data({'product_name': product_name})

    if data_state['product_id_current'] == 0:
        # начали новый товар
        await state.update_data({'product_price': 0})
        await state.update_data({'product_color': ''})
        await state.update_data({'product_size': ''})
        await state.update_data({'product_gender': ''})
        await state.update_data({'product_composition': ''})
        await state.update_data({'product_description': ''})
        await state.update_data({'product_link': ''})

        await state.update_data({'product_pictures': []})

    image, reply_markup = await def_choice_product_photo(session, state, 33, 1)
    await def_refresh_message(data_state, image, reply_markup)


async def def_text_product_price(message: types.Message, state: FSMContext, session: AsyncSession, data_state):
    # сохраняю стоимость товара
    price = round(float(message.text), 2)
    await state.update_data({'product_price': price})

    image, reply_markup = await def_choice_product_color(session, state, 35)
    await def_refresh_message(data_state, image, reply_markup)


async def def_text_product_color(message: types.Message, state: FSMContext, session: AsyncSession, data_state):
    # сохраняю цвет товара
    await orm_add_product_color(session, message.text)
    image, reply_markup = await def_choice_product_size(session, state, 36, message.text)
    await def_refresh_message(data_state, image, reply_markup)


async def def_text_product_size(message: types.Message, state: FSMContext, session: AsyncSession, data_state):
    # сохраняю размер товара
    await orm_add_product_size(session, message.text)
    image, reply_markup = await def_choice_product_gender(session, state, 37, message.text)
    await def_refresh_message(data_state, image, reply_markup)


async def def_text_product_gender(message: types.Message, state: FSMContext, session: AsyncSession, data_state):
    # сохраняю пол товара
    await orm_add_product_gender(session, message.text)
    image, reply_markup = await def_choice_product_composition(session, state, 38, message.text)
    await def_refresh_message(data_state, image, reply_markup)


async def def_text_product_composition(message: types.Message, state: FSMContext, session: AsyncSession, data_state):
    # сохраняю состав товара
    await orm_add_product_composition(session, message.text)
    image, reply_markup = await def_choice_product_description(state, 39, message.text)
    await def_refresh_message(data_state, image, reply_markup)


async def def_text_product_description(message: types.Message, state: FSMContext, data_state):
    # сохраняю описание товара
    await state.update_data({'product_description': message.text})
    image, reply_markup = await def_choice_product_link(state, 40)
    await def_refresh_message(data_state, image, reply_markup)


async def def_text_product_link(message: types.Message, state: FSMContext, session: AsyncSession, data_state):
    # принимаю ссылку
    await state.update_data({'product_link': message.text})
    image, reply_markup = await def_choice_product_end(session, state)
    await def_refresh_message(data_state, image, reply_markup)


# *****************************************************************************************
async def def_text_answer_question(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot, data_state, get_message):
    # сохраняю ответ для покупателя
    id_question = int(get_message.split("_")[-1])
    await orm_answer_question(session, id_question, message.text)

    # отправляю ответ покупателю
    telegram_id = data_state['telegram_id']
    reply_markup = get_user_answer_from_admin_btns(answer_id=id_question)
    await bot.send_message(chat_id=telegram_id,
                           text=f'Вам пришел ответ на ваш вопрос!',
                           reply_markup=reply_markup)

    await state.update_data({'get_message': f''})
    await state.update_data({'telegram_id': None})

    return await def_list_out_one_question_parents(
        message, session, state, '', 23, 10, 30, id_question, True)



