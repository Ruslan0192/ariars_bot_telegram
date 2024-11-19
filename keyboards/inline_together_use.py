
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class MenuCallBack(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    category: int | None = None
    page: int = 1
    product_id: int | None = None
    read_description: bool = True


def get_callback_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


def get_empty_btns(*, level_back: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=level_back,
                                                                 menu_name='information').pack()))
    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0,
                                                                 menu_name='main').pack()))
    return keyboard.adjust(*sizes).as_markup()


def get_history_questions_btns(
        *,
        level: int,
        page: int | None = None,
        pagination_btns: dict | None = None,
        product_id: int,
        type_message: int,
        theme_name: str,
        level_back: int):
    keyboard = InlineKeyboardBuilder()

    if pagination_btns != {}:
        if len(pagination_btns.items()) % 2 == 0:
            row_1 = 2
        else:
            row_1 = 1

        for text, menu_control in pagination_btns.items():
            if menu_control == "next":
                keyboard.add(InlineKeyboardButton(text=text,
                                                  callback_data=MenuCallBack(
                                                      level=level,
                                                      menu_name=theme_name,
                                                      category=type_message,
                                                      product_id=product_id,
                                                      page=page + 1).pack()))
            elif menu_control == "previous":
                keyboard.add(InlineKeyboardButton(text=text,
                                                  callback_data=MenuCallBack(
                                                      level=level,
                                                      menu_name=theme_name,
                                                      category=type_message,
                                                      product_id=product_id,
                                                      page=page - 1).pack()))

    else:
        row_1 = 0

    row_2 = 0
    under_type_message = int(type_message / 10)
    if under_type_message == 0:
        keyboard.add(InlineKeyboardButton(text='Выбрать',
                                          callback_data=MenuCallBack(level=level + 1,
                                                                     menu_name=theme_name,
                                                                     category=type_message,
                                                                     product_id=product_id,
                                                                     page=1).pack()))
        row_2 = 1

    if type_message % 2 == 1:
        keyboard.add(InlineKeyboardButton(text='Назад',
                                          callback_data=MenuCallBack(level=level_back,
                                                                     menu_name='catalog').pack()))
        keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                          callback_data=MenuCallBack(level=0, menu_name='main').pack()))
    # заполняю кол-во кнопок в ряду
    if row_1 == 0:
        if row_2 == 0:
            sizes = (2,)
        else:
            sizes = (1, 2)
    elif row_1 == 1:
        if row_2 == 0:
            sizes = (1, 2,)
        else:
            sizes = (1, 1, 2)
    else:
        if row_2 == 0:
            sizes = (2, 2,)
        else:
            sizes = (2, 1, 2)

    return keyboard.adjust(*sizes).as_markup()
