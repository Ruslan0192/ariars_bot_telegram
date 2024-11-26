from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.inline_together_use import MenuCallBack


def get_admin_main_btns(*, level: int, sizes: tuple[int] = (1,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Вопросы покупателей": "questions",
        "Каталог": "catalog",
        "Настройки": "information",
    }
    for text, menu_name in btns.items():
        if menu_name == 'questions':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=20, menu_name=menu_name).pack()))
        if menu_name == 'catalog':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=level + 1,
                                                                         menu_name=menu_name).pack()))
        elif menu_name == 'information':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=10, menu_name=menu_name).pack()))
    return keyboard.adjust(*sizes).as_markup()


def get_admin_catalog_btns(*, level: int, categories: list, sizes: tuple[int] = (1,)):
    keyboard = InlineKeyboardBuilder()
    for c in categories:
        keyboard.add(InlineKeyboardButton(text=c.name,
                                          callback_data=MenuCallBack(level=level + 1,
                                                                     menu_name=c.name,
                                                                     category=c.id).pack()))

    # keyboard.add(InlineKeyboardButton(text='Добавить 🛒',
    #                                   callback_data=MenuCallBack(level=level+1, menu_name='catalog').pack()))
    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0, menu_name='main').pack()))

    return keyboard.adjust(*sizes).as_markup()


def get_admin_catalog_type_btns(*, level: int, menu_name: str, categories: list, sizes: tuple[int] = (1,)):
    keyboard = InlineKeyboardBuilder()
    if categories[0].type_name != '':
        for c in categories:
            keyboard.add(InlineKeyboardButton(text=c.type_name,
                                              callback_data=MenuCallBack(level=level + 1,
                                                                         menu_name=c.cat_name,
                                                                         category=c.id,
                                                                         ).pack()))
    else:
        sizes = (1, 2)
        keyboard.add(InlineKeyboardButton(text='Тип не нужен',
                                          callback_data=MenuCallBack(level=level+1,
                                                                     category=categories[0].id,
                                                                     menu_name=categories[0].cat_name
                                                                     ).pack()))
    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=level - 1,
                                                                 menu_name='catalog').pack()))
    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0, menu_name='main').pack()))

    return keyboard.adjust(*sizes).as_markup()


def get_start_edit_product_btns(*, level: int, id_cat_type: int, sizes: tuple[int] = (1, 2)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Пропустить',
                                      callback_data=MenuCallBack(level=level,
                                                                 menu_name='information').pack()))
    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=3,
                                                                 menu_name='information',
                                                                 category=id_cat_type).pack()))
    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0,
                                                                 menu_name='main').pack()))
    return keyboard.adjust(*sizes).as_markup()


def get_edit_product_btns(*, level: int, categories: list, pass_menu: str, back_menu: str, flag_edit: bool = False, sizes: tuple[int] = (1,)):
    keyboard = InlineKeyboardBuilder()
    for c in categories:
        keyboard.add(InlineKeyboardButton(text=c.name,
                                          callback_data=MenuCallBack(level=level+1,
                                                                     menu_name=c.name).pack()))
    if flag_edit:
        keyboard.add(InlineKeyboardButton(text='Пропустить',
                                          callback_data=MenuCallBack(level=level+1,
                                                                     menu_name=pass_menu).pack()))
    row = []
    row.append(InlineKeyboardButton(text='Назад',
                                    callback_data=MenuCallBack(level=level-1,
                                                               menu_name=back_menu).pack()))
    row.append(InlineKeyboardButton(text='На главную 🏠',
                                    callback_data=MenuCallBack(level=0,
                                                               menu_name='main').pack()))
    keyboard.adjust(*sizes)
    return keyboard.row(*row).as_markup()


def get_admin_products_btns(
        *,
        level: int,
        category: int,
        menu_name: str,
        page: int | None = None,
        pagination_btns: dict | None = None,
        product_id: int,
        link: str | None = None,
        sizes: tuple[int] = (2, )
):
    keyboard = InlineKeyboardBuilder()
    if product_id != 0:
        sizes = (1, 3, 2)
        keyboard.add(InlineKeyboardButton(text='Ссылка на WB', url=link,
                                          callback_data=MenuCallBack(level=level,
                                                                     menu_name='product',
                                                                     category=category,
                                                                     product_id=product_id).pack()))
        if pagination_btns != {}:
            if len(pagination_btns.items()) % 2 == 0:
                sizes = (1, 2, 3, 2)
            else:
                sizes = (1, 1, 3, 2)
            for text, control in pagination_btns.items():
                if control == "next":
                    keyboard.add(InlineKeyboardButton(text=text,
                                                      callback_data=MenuCallBack(
                                                          level=level,
                                                          menu_name=control,
                                                          category=category,
                                                          page=page + 1).pack()))

                elif control == "previous":
                    keyboard.add(InlineKeyboardButton(text=text,
                                                      callback_data=MenuCallBack(
                                                          level=level,
                                                          menu_name=control,
                                                          category=category,
                                                          page=page - 1).pack()))

        keyboard.add(InlineKeyboardButton(text='Копировать',
                                          callback_data=MenuCallBack(level=31,
                                                                     menu_name=menu_name,
                                                                     category=category,
                                                                     product_id=product_id).pack()))
        keyboard.add(InlineKeyboardButton(text='Изменить',
                                          callback_data=MenuCallBack(level=32,
                                                                     menu_name=menu_name,
                                                                     category=category,
                                                                     product_id=product_id).pack()))
        keyboard.add(InlineKeyboardButton(text='Удалить',
                                          callback_data=MenuCallBack(level=4,
                                                                     menu_name=menu_name,
                                                                     category=category,
                                                                     product_id=product_id,
                                                                     page=page-1).pack()))

    keyboard.add(InlineKeyboardButton(text='Каталог',
                                      callback_data=MenuCallBack(level=1,
                                                                 menu_name='catalog').pack()))
    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0, menu_name='main').pack()))

    return keyboard.adjust(*sizes).as_markup()


def get_admin_product_photos_btns(
        *,
        level: int,
        page: int | None = None,
        pagination_btns: dict | None = None,
        product_id: int,
        btn_delete: bool,
        sizes: tuple[int] = (2, )
):
    keyboard = InlineKeyboardBuilder()
    if btn_delete:
        if pagination_btns != {}:
            if len(pagination_btns.items()) % 2 == 0:
                sizes = (2, 1, 1, 2)
            else:
                sizes = (1, 1, 1, 2)

            for text, control in pagination_btns.items():
                if control == "next":
                    keyboard.add(InlineKeyboardButton(text=text,
                                                      callback_data=MenuCallBack(
                                                          level=level,
                                                          menu_name=control,
                                                          page=page + 1).pack()))

                elif control == "previous":
                    keyboard.add(InlineKeyboardButton(text=text,
                                                      callback_data=MenuCallBack(
                                                          level=level,
                                                          menu_name=control,
                                                          page=page - 1).pack()))
        else:
            sizes = (1, 1, 2,)
        keyboard.add(InlineKeyboardButton(text='Удалить',
                                          callback_data=MenuCallBack(level=30,
                                                                     menu_name='Delete',
                                                                     page=page-1).pack()))
        keyboard.add(InlineKeyboardButton(text='Дальше',
                                          callback_data=MenuCallBack(level=level+1,
                                                                     menu_name='catalog').pack()))

    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=32,
                                                                 menu_name='catalog', product_id=product_id).pack()))
    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0, menu_name='main').pack()))

    return keyboard.adjust(*sizes).as_markup()


def get_admin_product_type_btns(*, level: int, categories: list, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    for c in categories:
        keyboard.add(InlineKeyboardButton(text=c.name,
                                          callback_data=MenuCallBack(level=level + 1,
                                                                     menu_name=c.name,
                                                                     category=c.id).pack()))
    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=level-1, menu_name='catalog').pack()))
    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0, menu_name='main').pack()))

    return keyboard.adjust(*sizes).as_markup()


def get_admin_information_btns(*, level: int, sizes: tuple[int] = (1,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Темы вопросов": "question",
        "Основные настройки": "general",
        "На главную 🏠": "main",
    }
    for text, menu_name in btns.items():
        if menu_name == 'question':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=11, menu_name=menu_name).pack()))
        elif menu_name == 'general':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=15, menu_name=menu_name).pack()))
        elif menu_name == 'main':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=0, menu_name='main').pack()))
    return keyboard.adjust(*sizes).as_markup()

def get_admin_themes_btns(
        *,
        level: int,
        product_id: int,
        page: int,
        pagination_btns: dict,
        menu_name: str
):
    keyboard = InlineKeyboardBuilder()
    if pagination_btns != {}:
        if len(pagination_btns.items()) % 2 == 0:
            sizes = (2, 1, 2)
        else:
            sizes = (1, 1, 2)

        for text, menu_control in pagination_btns.items():
            if menu_control == "next":
                keyboard.add(InlineKeyboardButton(text=text,
                                                  callback_data=MenuCallBack(
                                                    level=level,
                                                    menu_name='general',
                                                    product_id=product_id,
                                                    page=page + 1,
                                                  ).pack()))

            elif menu_control == "previous":
                keyboard.add(InlineKeyboardButton(text=text,
                                                  callback_data=MenuCallBack(
                                                    level=level,
                                                    menu_name='general',
                                                    product_id=product_id,
                                                    page=page - 1,
                                                  ).pack()))
    else:
        sizes = (1, 2)

    keyboard.add(InlineKeyboardButton(text='Изменить',
                                      callback_data=MenuCallBack(level=level+1,
                                                                 menu_name=menu_name,
                                                                 page=page
                                                                 ).pack()))
    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=10,
                                                                 menu_name='information',
                                                                 page=page
                                                                 ).pack()))
    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0,
                                                                 menu_name='main',
                                                                 page=page
                                                                 ).pack()))
    return keyboard.adjust(*sizes).as_markup()



def get_edit_name_theme_btns(*, level: int, menu_name: str, sizes: tuple[int] = (1, 2)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Пропустить',
                                      callback_data=MenuCallBack(level=level+1,
                                                                 menu_name=menu_name).pack()))
    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=level-1,
                                                                 menu_name=menu_name).pack()))
    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0,
                                                                 menu_name='main').pack()))
    return keyboard.adjust(*sizes).as_markup()


def get_admin_general_btns(
        *,
        level: int,
        product_id: int,
        page: int,
        pagination_btns: dict,
        menu_name: str,
        sizes: tuple[int] = (2,)
):
    keyboard = InlineKeyboardBuilder()
    if pagination_btns != {}:
        if len(pagination_btns.items()) % 2 != 0:
            sizes = (1, 2)

        for text, menu_control in pagination_btns.items():
            if menu_control == "next":
                keyboard.add(InlineKeyboardButton(text=text,
                                                  callback_data=MenuCallBack(
                                                    level=level,
                                                    menu_name='general',
                                                    product_id=product_id,
                                                    page=page + 1,
                                                  ).pack()))

            elif menu_control == "previous":
                keyboard.add(InlineKeyboardButton(text=text,
                                                  callback_data=MenuCallBack(
                                                    level=level,
                                                    menu_name='general',
                                                    product_id=product_id,
                                                    page=page - 1,
                                                  ).pack()))

    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=10,
                                                                 menu_name='information',
                                                                 page=page
                                                                 ).pack()))
    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0,
                                                                 menu_name='main',
                                                                 page=page
                                                                 ).pack()))
    return keyboard.adjust(*sizes).as_markup()


def get_admin_questions_byers_btns(*, level: int, sizes: tuple[int] = (1, )):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Новые вопросы": "new_questions",
        "Архив": "archive_questions",
    }
    for text, menu_name in btns.items():
        if menu_name == 'new_questions':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=level+1,
                                                                         menu_name=menu_name).pack()))
        if menu_name == 'archive_questions':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=25,
                                                                         menu_name=menu_name).pack()))

    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0,
                                                                 menu_name='main',
                                                                 page=1
                                                                 ).pack()))
    return keyboard.adjust(*sizes).as_markup()


def get_admin_question_from_user_btns(*, question_id: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Посмотреть',
                                      callback_data=MenuCallBack(level=23,
                                                                 menu_name='questionuser',
                                                                 product_id=question_id).pack()))
    return keyboard.adjust(*sizes).as_markup()

