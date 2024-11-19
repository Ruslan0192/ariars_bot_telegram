from aiogram import Bot, types
from aiogram.types import InputMediaPhoto
from aiogram.fsm.context import FSMContext

from dotenv import find_dotenv, load_dotenv

from handlers.menu_together_use import def_pages, def_list_out_one_question_parents, \
    def_clear_question_message, def_question_change_photo, def_question_history
from keyboards.inline_together_use import get_empty_btns

load_dotenv(find_dotenv())

from database.orm_query import *

from keyboards.inline_admin import *

from utils.paginator import Paginator


async def get_admin_menu_content(
        message: types.Message,
        session: AsyncSession,
        bot: Bot,
        state: FSMContext,
        level: int,
        menu_name: str,
        product_id: int,
        category: int | None = None,
        page: int | None = None,
        telegram_id: int | None = None):
    if level == 0:
        return await def_main_menu_admin(session, state, level)
    elif level == 1:
        return await def_catalog(session, state, level)
    elif level == 2:
        return await def_type_catalog(session, state, menu_name)
    elif level == 3:
        return await def_products(session, state, level, category, page)
    elif level == 4:
        return await def_delete_product(session, state, product_id, category, page)

    elif level == 10:
        return await def_information(session, state, level)
    elif level == 11:
        return await def_themes(session, state, level, page)
    elif level == 12:
        return await def_theme_edit_name(session, state, menu_name)
    elif level == 13:
        return await def_theme_edit_photo(session, state, menu_name)

    elif level == 15:
        return await def_general(session, state, level, page)

    elif level == 20:
        return await def_questions_byers(session, state, level)
    elif level == 21:
        return await def_question_history(
            message, state, session, level, 20, telegram_id, True, True)
    elif level == 22:
        return await def_question_change_photo(
            session, state, level, 21, menu_name, category, product_id, True, page)
    elif level == 23:
        return await def_list_out_one_question_parents(
            message, session, state, menu_name, level, 21, 10, product_id, True)

    elif level == 25:
        return await def_question_history(
            message, state, session, level, 20, telegram_id, True, False)
    elif level == 26:
        return await def_question_change_photo(
            session, state, level, 20, menu_name, category, product_id, True, page)
    elif level == 27:
        return await def_list_out_one_question_parents(
            message, session, state, menu_name, level, 25, 10, product_id, True)

    elif level == 30:
        return await def_delete_photo_product(session, state, level, page)
    elif level == 31:
        return await def_copy_product(session, state, level, product_id)
    elif level == 32:
        return await def_edit_product(session, state, level, product_id)
    elif level == 33:
        return await def_choice_product_photo(session, state, level, page)
    elif level == 34:
        return await def_choice_product_price(session, state, level)
    elif level == 35:
        return await def_choice_product_color(session, state, level)
    elif level == 36:
        return await def_choice_product_size(session, state, level, menu_name)
    elif level == 37:
        return await def_choice_product_gender(session, state, level, menu_name)
    elif level == 38:
        return await def_choice_product_composition(session, state, level, menu_name)
    elif level == 39:
        return await def_choice_product_description(state, level, menu_name)
    elif level == 40:
        return await def_choice_product_link(state, level)
    elif level == 41:
        return await def_choice_product_end(session, state)

    else:
        return await def_main_menu_admin(session, state, level)


async def def_empty_return(session: AsyncSession, id_name: str, caption: str, level_back: int):
    result = await orm_get_general(session, id_name)
    image = InputMediaPhoto(media=result.picture, caption=caption)
    reply_markup = get_empty_btns(level_back=level_back)
    return image, reply_markup


# level=0
async def def_main_menu_admin(session: AsyncSession, state: FSMContext, level: int):
    await def_clear_question_message(state)
    await state.update_data({'get_message': ''})
    result = await orm_get_general(session, 'main')
    image = InputMediaPhoto(media=result.picture, caption='Основное меню администратора')
    reply_markup = get_admin_main_btns(level=level)
    return image, reply_markup


# ****************************************************************************************
# level=1
async def def_catalog(session: AsyncSession, state: FSMContext, level: int):
    await state.update_data({'get_message': f'catalog'})

    categories = await orm_get_prod_cats(session)
    if len(categories) == 0:
        caption = "Категории отсутствуют.\n\n*Введите новую.*"
    else:
        caption = "Выберите категорию. \n\n*При необходимости введите новую.*"

    result = await orm_get_general(session, 'catalog')
    image = InputMediaPhoto(media=result.picture, caption=caption, parse_mode='Markdown')
    reply_markup = get_admin_catalog_btns(level=level, categories=categories)
    return image, reply_markup


# level=2
async def def_type_catalog(session: AsyncSession, state: FSMContext, cat_name: str):
    await state.update_data({'get_message': f'type_catalog'})
    await state.update_data({'cat_name': cat_name})

    types = await orm_get_prod_cat_types(session, cat_name)
    await state.update_data({'id_cat_type': types[0].id})

    if types[0].type_name == '':
        products = await orm_get_products(session, cat_id=types[0].id, frozen=False)
        if len(products) != 0:
            return await def_products(session, state, 3, types[0].id, 1)

    result = await orm_get_general(session, 'catalog')
    image = InputMediaPhoto(media=result.picture, caption='Выберите тип. \n\n*При необходимости введите новый тип*', parse_mode='Markdown')
    reply_markup = get_admin_catalog_type_btns(level=2, menu_name=cat_name, categories=types)
    return image, reply_markup


# level=3
async def def_products(session: AsyncSession, state: FSMContext, level: int, id_cat_type: int, page: int):
    categories = await orm_get_prod_cat_types_id(session, id_cat_type)
    cat_name = categories.cat_name
    type_name = categories.type_name
    if type_name != '':
        cat_name = f'{cat_name} {type_name}'

    await state.update_data({'get_message': f'product_name'})
    await state.update_data({'id_cat_type': id_cat_type})
    await state.update_data({'cat_name': cat_name})
    await state.update_data({'product_id': 0})
    await state.update_data({'product_id_current': 0})

    products = await orm_get_products(session, cat_id=id_cat_type, frozen=False)
    if len(products) == 0:
        caption = f"Нет товаров в категории {cat_name}.\n\n*Введите наименование товара.*"
        result = await orm_get_general(session, 'catalog')
        image = InputMediaPhoto(media=result.picture, caption=caption, parse_mode='Markdown')
        reply_markup = get_admin_products_btns(level=level, menu_name=cat_name, category=0, product_id=0)

    else:
        if page == -1:
            page = len(products)
        paginator = Paginator(products, page=page)
        product = paginator.get_page()[0]
        pagination_btns = def_pages(paginator)

        pictures = await orm_get_product_pictures(session, product.id)

        caption = (f"*{cat_name} {product.name}\n*"
                   f"*Стоимость:* _{product.price} руб._\n"
                   f"*Цвет:* _{product.color}_\n"
                   f"*Размер:* _{product.size}_\n"
                   f"*Пол:* _{product.gender}_\n"
                   f"*Состав:* _{product.composition}_\n"
                   f"*Описание:* \n_{product.description}_\n\n"
                   f"Товар {paginator.page} из {paginator.pages}\n\n"
                   f"*Для создания нового товара. Введите его наименование.*")

        image = InputMediaPhoto(media=pictures[0].picture, caption=caption, parse_mode='Markdown')
        reply_markup = get_admin_products_btns(level=level,
                                               category=id_cat_type,
                                               menu_name=cat_name,
                                               page=page,
                                               pagination_btns=pagination_btns,
                                               product_id=product.id,
                                               link=product.link)
    return image, reply_markup


# level=4
async def def_delete_product(session: AsyncSession, state: FSMContext, product_id: int, category: int, page: int):
    # делаю предыдущий продукт не активным
    await orm_product_frozen(session, product_id)
    if page == 0:
        page = 1
    return await def_products(session, state, 3, category, page)


# *******************************************************************************************
# level=10
async def def_information(session: AsyncSession, state: FSMContext, level: int):
    result = await orm_get_general(session, 'information')
    image = InputMediaPhoto(media=result.picture, caption='Основные настройки')
    reply_markup = get_admin_information_btns(level=level)
    return image, reply_markup


# level=11
async def def_themes(session: AsyncSession, state: FSMContext, level: int, page: int):
    themes = await orm_get_category_questions(session)
    if len(themes) == 0:
        await state.update_data({'page': 0})
        await state.update_data({'get_message': 'new_theme'})
        return await def_empty_return(session, 'question', 'Темы отсутствуют.\n\nВведите наименование темы.', 10)

    if len(themes) < page:
        page = len(themes)
    paginator = Paginator(themes, page=page)
    theme = paginator.get_page()[0]
    pagination_btns = def_pages(paginator)

    await state.update_data({'page': page})
    await state.update_data({'get_message': f'new_theme'})

    caption = (f"Тема: {theme.name}\n"
               f"Описание: {theme.description}\n\n"
               f"Для создания темы, введите наименование темы")
    image = InputMediaPhoto(media=theme.picture, caption=caption)
    reply_markup = get_admin_themes_btns(level=level,
                                         product_id=theme.id,
                                         page=page,
                                         pagination_btns=pagination_btns,
                                         menu_name=theme.name)
    return image, reply_markup


# level=12
async def def_theme_edit_name(session: AsyncSession, state: FSMContext, menu_name: str, repeat: bool = False):
    # корректирую тему
    theme = await orm_get_name_category_question(session, menu_name)

    await state.update_data({'get_message': f'theme_{menu_name}'})

    if repeat:
        caption = f"Введенная тема уже существует.\n\nВведите новое наименование темы вопросов"
    else:
        caption = f"Текущая тема: {menu_name}.\n\nВведите новое наименование темы вопросов"
    image = InputMediaPhoto(media=theme.picture, caption=caption)

    reply_markup = get_edit_name_theme_btns(level=12, menu_name=menu_name)
    return image, reply_markup


# level=13
async def def_theme_edit_photo(session: AsyncSession, state: FSMContext, menu_name: str):
    # корректирую тему
    await state.update_data({'get_message': f'editthemephoto_{menu_name}'})

    theme = await orm_get_name_category_question(session, menu_name)

    caption = (f"Тема: {menu_name}\n"
               f"Описание: {theme.description}\n\n"
               f"Вставьте фото c описанием темы вопросов")
    image = InputMediaPhoto(media=theme.picture, caption=caption)

    reply_markup = get_empty_btns(level_back=12)
    return image, reply_markup


# level=15
async def def_general(session: AsyncSession, state: FSMContext, level: int, page: int):
    general_parametrs = await orm_get_generals(session)
    if len(general_parametrs) < page:
        page = len(general_parametrs)
    paginator = Paginator(general_parametrs, page=page)
    pagination_btns = def_pages(paginator)
    general_parametr = paginator.get_page()[0]

    await state.update_data({'get_message': f'general_{general_parametr.id}'})
    await state.update_data({'page': page})

    if general_parametr.description == '':
        caption = (f"{general_parametr.name}\n\n"
                   f"Вставьте фото раздела")
    else:
        caption = (f"{general_parametr.name}\n\n"
                   f"Описание:\n{general_parametr.description}\n\n"
                   f"Вставьте фото c описанием раздела")
    await state.update_data({'description': general_parametr.description})

    image = InputMediaPhoto(media=general_parametr.picture, caption=caption)
    reply_markup = get_admin_general_btns(level=level,
                                          product_id=general_parametr.id,
                                          page=page,
                                          pagination_btns=pagination_btns,
                                          menu_name=general_parametr.id_name)
    return image, reply_markup


# level=20
# ********************************************************************************************
async def def_questions_byers(session: AsyncSession, state: FSMContext, level: int):
    await def_clear_question_message(state)
    result = await orm_get_general(session, 'question')
    image = InputMediaPhoto(media=result.picture, caption='Работа с вопросами покупателей')
    reply_markup = get_admin_questions_byers_btns(level=level)
    return image, reply_markup


# ***********************************************************************************************
# level=30
async def def_delete_photo_product(session: AsyncSession, state: FSMContext, level: int, page: int):
    # удаление фото
    data_state = await state.get_data()
    product_pictures = data_state['product_pictures']
    product_pictures.pop(page)
    await state.update_data({'product_pictures': product_pictures})

    if page == 0:
        page = 1
    return await def_choice_product_photo(session, state, 33, page)

# level=31
async def def_copy_product(session: AsyncSession, state: FSMContext, level: int, product_id: int):
    # копирование товара
    return await def_edit_product(session, state, 32, product_id, True)


# level=32
async def def_edit_product(session: AsyncSession, state: FSMContext, level: int, product_id: int, copy: bool = False):
    await state.update_data({'get_message': f'product_name'})

    product = await orm_get_product_id(session, product_id)
    await state.update_data({'product_name': product.name})
    await state.update_data({'product_price': product.price})
    await state.update_data({'product_color': product.color})
    await state.update_data({'product_size': product.size})
    await state.update_data({'product_gender': product.gender})
    await state.update_data({'product_composition': product.composition})
    await state.update_data({'product_description': product.description})
    await state.update_data({'product_link': product.link})

    product_pictures = []
    pictures = await orm_get_product_pictures(session, product_id)
    for picture in pictures:
        product_pictures.append(picture.picture)
    await state.update_data({'product_pictures': product_pictures})

    await state.update_data({'product_id_current': product_id})
    if copy:
        await state.update_data({'product_id': 0})
    else:
        await state.update_data({'product_id': product_id})

    data_state = await state.get_data()
    cat_name = data_state['cat_name']

    caption = (f"Категория: *{cat_name}.*\n\n"
               f"Текущее наименование: *{product.name}*.\n\n*Напишите новое наименование продукта.*")
    result = await orm_get_general(session, 'catalog')
    image = InputMediaPhoto(media=result.picture, caption=caption, parse_mode='Markdown')
    reply_markup = get_start_edit_product_btns(level=33, id_cat_type=data_state['id_cat_type'])
    return image, reply_markup


# level=33
async def def_choice_product_photo(session: AsyncSession, state: FSMContext, level: int, page: int):
    # запрос фото
    await state.update_data({'get_message': f'product_photo'})

    data_state = await state.get_data()

    product_pictures = data_state['product_pictures']
    if product_pictures == []:
        result = await orm_get_general(session, 'catalog')
        picture = result.picture
        pagination_btns = {}
        caption = (f"Категория: *{data_state['cat_name']}.*\n"
                   f"Наименование: *{data_state['product_name']}*.\n\n*Фото отсутствуют!\nВставьте фото товара.*")
    else:
        paginator = Paginator(product_pictures, page=page)
        picture = paginator.get_page()[0]
        pagination_btns = def_pages(paginator)
        caption = (f"Категория: *{data_state['cat_name']}.*\n"
                   f"Наименование: *{data_state['product_name']}*.\n\n*Вставьте дополнительные фото товара.*")

    # запоминаю для возврата в предыдущее окно
    data_state = await state.get_data()
    product_id = data_state['product_id_current']

    image = InputMediaPhoto(media=picture, caption=caption, parse_mode='Markdown')
    reply_markup = get_admin_product_photos_btns(level=level, pagination_btns=pagination_btns, page=page, product_id=product_id)
    return image, reply_markup


# level=34
async def def_choice_product_price(session: AsyncSession, state: FSMContext, level: int):
    # запрос цены
    data_state = await state.get_data()
    product_pictures = data_state['product_pictures']
    if len(product_pictures) == 0:
        # фото не были загружены
        return await def_choice_product_photo(session, state, level, 1)

    await state.update_data({'get_message': f'product_price'})

    data_state = await state.get_data()
    product_price = data_state['product_price']
    if product_price == 0:
        caption = (f"Категория: *{data_state['cat_name']}.*\n"
                   f"Наименование: *{data_state['product_name']}*.\n\n"
                   f"*Напишите цену.*")
        flag_edit = False
    else:
        caption = (f"Категория: *{data_state['cat_name']}.*\n"
                   f"Наименование: *{data_state['product_name']}*.\n"
                   f"Текущая цена: *{product_price}*\n\n"
                   f"*Напишите новую цену.*")
        flag_edit = True

    image = InputMediaPhoto(media=product_pictures[0], caption=caption, parse_mode='Markdown')
    reply_markup = get_edit_product_btns(level=level,
                                         categories=[],
                                         back_menu='',
                                         pass_menu='',
                                         flag_edit=flag_edit)
    return image, reply_markup


# level=35
async def def_choice_product_color(session: AsyncSession, state: FSMContext, level: int):
    # формирую вывод вариантов цветов
    await state.update_data({'get_message': f'product_color'})
    data_state = await state.get_data()

    colors = await orm_get_product_colors(session)
    if len(colors) == 0:
        caption = (f"Категория: *{data_state['cat_name']}.*\n"
                   f"Наименование: *{data_state['product_name']}*.\n\n"
                   f"*Цвета отсутствуют, введите новый.*")
        flag_edit = False
    else:
        product_color = data_state['product_color']
        if product_color == '':
            caption = (f"Категория: *{data_state['cat_name']}.*\n"
                       f"Наименование: *{data_state['product_name']}*.\n\n"
                       f"*Выберите цвет или введите новый.*")
            flag_edit = False
        else:
            caption = (f"Категория: *{data_state['cat_name']}.*\n"
                       f"Наименование: *{data_state['product_name']}*.\n"
                       f"Текущий цвет: *{product_color}*\n\n"
                       f"*Выберите цвет или введите новый.*")
            flag_edit = True

    product_pictures = data_state['product_pictures']
    image = InputMediaPhoto(media=product_pictures[0], caption=caption, parse_mode='Markdown')
    reply_markup = get_edit_product_btns(level=level,
                                         categories=colors,
                                         back_menu='',
                                         pass_menu=data_state['product_color'],
                                         flag_edit=flag_edit)
    return image, reply_markup


# level=36
async def def_choice_product_size(session: AsyncSession, state: FSMContext, level: int, menu_name: str):
    # формирую вывод вариантов размеров
    await state.update_data({'product_color': menu_name})
    await state.update_data({'get_message': f'product_size'})

    data_state = await state.get_data()

    sizes = await orm_get_product_sizes(session)
    if len(sizes) == 0:
        caption = (f"Категория: *{data_state['cat_name']}.*\n"
                   f"Наименование: *{data_state['product_name']}*.\n\n"
                   f"*Размеры отсутствуют, введите новый.*")
        flag_edit = False
    else:
        product_size = data_state['product_size']
        if product_size == '':
            caption = (f"Категория: *{data_state['cat_name']}.*\n"
                       f"Наименование: *{data_state['product_name']}*.\n\n"
                       f"*Выберите размер или введите новый.*")
            flag_edit = False
        else:
            caption = (f"Категория: *{data_state['cat_name']}.*\n"
                       f"Наименование: *{data_state['product_name']}*.\n"
                       f"Текущий размер: *{product_size}*\n\n"
                       f"*Выберите размер или введите новый.*")
            flag_edit = True

    product_pictures = data_state['product_pictures']
    image = InputMediaPhoto(media=product_pictures[0], caption=caption, parse_mode='Markdown')
    reply_markup = get_edit_product_btns(level=level,
                                         categories=sizes,
                                         back_menu='',
                                         pass_menu=data_state['product_size'],
                                         flag_edit=flag_edit)
    return image, reply_markup


# level=37
async def def_choice_product_gender(session: AsyncSession, state: FSMContext, level: int, menu_name: str):
    # формирую вывод вариантов гендера
    await state.update_data({'product_size': menu_name})
    await state.update_data({'get_message': f'product_gender'})

    data_state = await state.get_data()

    genders = await orm_get_product_genders(session)
    if len(genders) == 0:
        caption = (f"Категория: *{data_state['cat_name']}.*\n"
                   f"Наименование: *{data_state['product_name']}*.\n\n"
                   f"*Выбор пола отсутствует, введите новый.*")
        flag_edit = False
    else:
        product_gender = data_state['product_gender']
        if product_gender == '':
            caption = (f"Категория: *{data_state['cat_name']}.*\n"
                       f"Наименование: *{data_state['product_name']}*.\n\n"
                       f"*Выберите пол или введите новый.*")
            flag_edit = False
        else:
            caption = (f"Категория: *{data_state['cat_name']}.*\n"
                       f"Наименование: *{data_state['product_name']}*.\n"
                       f"Текущий пол: *{product_gender}*\n\n"
                       f"*Выберите пол или введите новый.*")
            flag_edit = True

    product_pictures = data_state['product_pictures']
    image = InputMediaPhoto(media=product_pictures[0], caption=caption, parse_mode='Markdown')
    reply_markup = get_edit_product_btns(level=level,
                                         categories=genders,
                                         back_menu=data_state['product_color'],
                                         pass_menu=data_state['product_gender'],
                                         flag_edit=flag_edit)
    return image, reply_markup


# level=38
async def def_choice_product_composition(session: AsyncSession, state: FSMContext, level: int, menu_name: str):
    # формирую вывод вариантов составов
    await state.update_data({'product_gender': menu_name})
    await state.update_data({'get_message': f'product_composition'})

    data_state = await state.get_data()

    compositions = await orm_get_product_compositions(session)
    if len(compositions) == 0:
        caption = (f"Категория: *{data_state['cat_name']}.*\n"
                   f"Наименование: *{data_state['product_name']}*.\n\n"
                   f"*Выбор состава отсутствует, введите новый.*")
        flag_edit = False
    else:
        product_composition = data_state['product_composition']
        if product_composition == '':
            caption = (f"Категория: *{data_state['cat_name']}.*\n"
                       f"Наименование: *{data_state['product_name']}*.\n\n"
                       f"*Выберите состав или введите новый.*")
            flag_edit = False
        else:
            caption = (f"Категория: *{data_state['cat_name']}.*\n"
                       f"Наименование: *{data_state['product_name']}*.\n"
                       f"Текущий состав: *{product_composition}*\n\n"
                       f"*Выберите состав или введите новый.*")
            flag_edit = True

    product_pictures = data_state['product_pictures']
    image = InputMediaPhoto(media=product_pictures[0], caption=caption, parse_mode='Markdown')
    reply_markup = get_edit_product_btns(level=level,
                                         categories=compositions,
                                         back_menu=data_state['product_size'],
                                         pass_menu=data_state['product_composition'],
                                         flag_edit=flag_edit)
    return image, reply_markup


# level=39
async def def_choice_product_description(state: FSMContext, level: int, menu_name: str):
    # формирую запрос описания
    await state.update_data({'product_composition': menu_name})
    await state.update_data({'get_message': f'product_description'})

    data_state = await state.get_data()

    product_description = data_state['product_description']
    if product_description == '':
        caption = (f"Категория: *{data_state['cat_name']}.*\n"
                   f"Наименование: *{data_state['product_name']}*.\n\n"
                   f"*Введите описание.*")
        flag_edit = False
    else:
        caption = (f"Категория: *{data_state['cat_name']}.*\n"
                   f"Наименование: *{data_state['product_name']}*.\n"
                   f"Текущее описание: *{product_description}*\n\n"
                   f"*Введите новое описание.*")
        flag_edit = True

    product_pictures = data_state['product_pictures']
    image = InputMediaPhoto(media=product_pictures[0], caption=caption, parse_mode='Markdown')
    reply_markup = get_edit_product_btns(level=level,
                                         categories=[],
                                         back_menu=data_state['product_gender'],
                                         pass_menu='',
                                         flag_edit=flag_edit)
    return image, reply_markup


# level=40
async def def_choice_product_link(state: FSMContext, level: int):
    # формирую запрос ссылки
    await state.update_data({'get_message': f'product_link'})

    data_state = await state.get_data()

    product_link = data_state['product_link']
    if product_link == '':
        caption = (f"Категория: *{data_state['cat_name']}.*\n"
                   f"Наименование: *{data_state['product_name']}*.\n\n"
                   f"*Введите ссылку.*")
        flag_edit = False
    else:
        caption = (f"Категория: *{data_state['cat_name']}.*\n"
                   f"Наименование: *{data_state['product_name']}*.\n"
                   f"Текущая ссылка: *{product_link}*\n\n"
                   f"*Введите новую ссылку.*")
        flag_edit = True

    product_pictures = data_state['product_pictures']
    image = InputMediaPhoto(media=product_pictures[0], caption=caption, parse_mode='Markdown')
    reply_markup = get_edit_product_btns(level=level,
                                         categories=[],
                                         back_menu='',
                                         pass_menu='catalog',
                                         flag_edit=flag_edit)
    return image, reply_markup


# level=41
async def def_choice_product_end(session: AsyncSession, state: FSMContext):
    # сохраняю весь товар
    await state.update_data({'get_message': f''})

    data_state = await state.get_data()
    product_pictures = data_state['product_pictures']

    product_id = data_state['product_id']
    parents_id = 0
    if product_id != 0:
        # измененный продукт
        # делаю предыдущий продукт не активным
        await orm_product_frozen(session, product_id)

        # проверка прародителя
        current_product = await orm_get_product_id(session, product_id)
        if current_product.parents_id == 0:
            parents_id = product_id
        else:
            parents_id = current_product.parents_id

    # сохраняю товар
    product_id = await orm_add_product(session=session,
                                       parents_id=parents_id,
                                       name=data_state['product_name'],
                                       cat_id=data_state['id_cat_type'],
                                       price=data_state['product_price'],
                                       color=data_state['product_color'],
                                       size=data_state['product_size'],
                                       gender=data_state['product_gender'],
                                       composition=data_state['product_composition'],
                                       description=data_state['product_description'],
                                       link=data_state['product_link'])
    # проверяю фото к товару
    pictures = await orm_get_product_pictures(session, product_id)
    for picture in pictures:
        # смотрим в БД
        if picture in product_pictures:
            # введенные картинки совпали с БД, убираю из списка добавления
            product_pictures.remove(picture)
        else:
            # В списке добавления этой картинке нет, замораживаю ее в БД
            await orm_product_picture_frozen(session, picture.id)

    # сохраняю измененные фото к товару
    for picture in product_pictures:
        await orm_add_product_picture(session, product_id, picture)
    return await def_products(session, state, 3, int(data_state['id_cat_type']), -1)



