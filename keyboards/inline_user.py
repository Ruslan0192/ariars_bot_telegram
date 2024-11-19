from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.inline_together_use import MenuCallBack


def get_user_query_name_btns(*, level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Да',
                                      callback_data=MenuCallBack(level=level+1, menu_name='query_name').pack()))
    return keyboard.adjust(*sizes).as_markup()


def get_user_main_btns(*, level: int, sizes: tuple[int] = (1,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Каталог": "catalog",
        "Задать вопрос ❗": "question",
        "Сведения ℹ️": "information",
    }
    for text, menu_name in btns.items():
        if menu_name == 'catalog':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=level + 1, menu_name=menu_name).pack()))
        elif menu_name == 'question':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=20, menu_name=menu_name).pack()))
        elif menu_name == 'information':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=10, menu_name=menu_name).pack()))

    return keyboard.adjust(*sizes).as_markup()

def get_user_catalog_btns(*, level: int, categories: list, sizes: tuple[int] = (1,)):
    keyboard = InlineKeyboardBuilder()
    # if len(categories) % 2 == 0:
    #     sizes = (2,)
    # else:
    #     sizes = (1,2,)
    for c in categories:
        keyboard.add(InlineKeyboardButton(text=c.name,
                                          callback_data=MenuCallBack(level=level + 1,
                                                                     menu_name=c.name,
                                                                     category=c.id).pack()))


    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0, menu_name='main').pack()))

    return keyboard.adjust(*sizes).as_markup()

def get_user_catalog_type_btns(*, level: int, categories: list, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    if len(categories) % 2 == 0:
        sizes = (2,)
    else:
        sizes = (1,2,)

    for c in categories:
        keyboard.add(InlineKeyboardButton(text=c.type_name,
                                          callback_data=MenuCallBack(level=level,
                                                                     menu_name=f'{c.cat_name} {c.type_name}',
                                                                     category=c.id).pack()))

    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=level - 1,
                                                                 menu_name='catalog',
                                                                 ).pack()))
    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0, menu_name='main').pack()))
    return keyboard.adjust(*sizes).as_markup()


def get_user_products_btns(
        *,
        cat_name: str,
        page: int | None = None,
        pagination_btns: dict | None = None,
        product_id: int,
        link: str | None = None,
        first: int,
        read_description: bool
):

    keyboard = InlineKeyboardBuilder()
    if len(pagination_btns.items()) != 0:
        if len(pagination_btns.items()) % 2 == 0:
            sizes = (2, )
        else:
            sizes = (1, 2,)

        for text, menu_control in pagination_btns.items():
            if menu_control == "next":
                keyboard.add(InlineKeyboardButton(text=text,
                                                  callback_data=MenuCallBack(
                                                                            level=4,
                                                                            menu_name=cat_name,
                                                                            category=first,
                                                                            product_id=product_id,
                                                                            read_description=False,
                                                                            page=page + 1).pack()))
            elif menu_control == "previous":
                keyboard.add(InlineKeyboardButton(text=text,
                                                  callback_data=MenuCallBack(
                                                                            level=4,
                                                                            menu_name=cat_name,
                                                                            category=first,
                                                                            product_id=product_id,
                                                                            read_description=False,
                                                                            page=page - 1).pack()))
    else:
        sizes = (2,)
    keyboard.add(InlineKeyboardButton(text='Ссылка на WB', url=link))

    if read_description:
        keyboard.add(InlineKeyboardButton(text='Описание 🔼',
                                          callback_data=MenuCallBack(level=4,
                                                                     menu_name=cat_name,
                                                                     category=first,
                                                                     product_id=product_id,
                                                                     page=page,
                                                                     read_description=False).pack()))
    else:
        keyboard.add(InlineKeyboardButton(text='Описание 🔽',
                                          callback_data=MenuCallBack(level=4,
                                                                     menu_name=cat_name,
                                                                     category=first,
                                                                     product_id=product_id,
                                                                     page=page,
                                                                     read_description=True).pack()))

    if first == 1:
        keyboard.add(InlineKeyboardButton(text='Каталог',
                                          callback_data=MenuCallBack(level=1,
                                                                     menu_name='catalog').pack()))
        keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                          callback_data=MenuCallBack(level=0, menu_name='main').pack()))

    return keyboard.adjust(*sizes).as_markup()


# *************************************************************************
def get_user_question_main_btns(*, level: int, sizes: tuple[int] = (1,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Новый вопрос',
                                      callback_data=MenuCallBack(level=21, menu_name='main').pack()))
    keyboard.add(InlineKeyboardButton(text='Архив',
                                      callback_data=MenuCallBack(level=25, menu_name='main').pack()))
    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0, menu_name='main').pack()))
    return keyboard.adjust(*sizes).as_markup()


def get_user_question_theme_choice_btns(*, level: int, categories: list, sizes: tuple[int] = (1,)):
    keyboard = InlineKeyboardBuilder()
    # if len(categories) % 2 == 0:
    #     sizes = (2,)
    # else:
    #     sizes = (1, 2,)
    for c in categories:
        keyboard.add(InlineKeyboardButton(text=c.name,
                                          callback_data=MenuCallBack(level=level + 1,
                                                                     menu_name=c.name,
                                                                     category=c.id).pack()))
    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=20, menu_name='main').pack()))
    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0, menu_name='main').pack()))

    return keyboard.adjust(*sizes).as_markup()


# *************************************************************************
def get_user_information_btns(*, level: int, sizes: tuple[int] = (1,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "О нас ℹ️": "about",
        "Написать разработчику": "for_devolep",
        'На главную 🏠': "main",
    }
    for text, menu_name in btns.items():
        if menu_name == 'about':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=level+1, menu_name=menu_name).pack()))
        elif menu_name == 'for_devolep':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=level+2, menu_name=menu_name).pack()))
        elif menu_name == 'main':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=0, menu_name=menu_name).pack()))

    return keyboard.adjust(*sizes).as_markup()


def get_user_about_btns(*, level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=10, menu_name='information', cart_id=0).pack()))
    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0, menu_name='main', cart_id=0).pack()))
    return keyboard.adjust(*sizes).as_markup()


# ***********************************************************************************
def get_user_answer_from_admin_btns(*, answer_id: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Посмотреть',
                                      callback_data=MenuCallBack(level=24, menu_name='answeradmin', product_id=answer_id).pack()))
    return keyboard.adjust(*sizes).as_markup()

