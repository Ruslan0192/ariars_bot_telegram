from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger

class MenuCallBack(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    category: int | None = None
    page: int = 1
    product_id: int | None = None
    category_control_type: bool = True

def get_callback_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()

def get_user_main_btns(*, level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Меню 🍕": "catalog",
        "Мои заказы 🛒": "carts",
        "Сведения ℹ️": "information",
    }
    for text, menu_name in btns.items():
        if menu_name == 'catalog':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=level + 1, menu_name=menu_name).pack()))
        elif menu_name == 'carts':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=10, menu_name=menu_name).pack()))
        elif menu_name == 'information':
            logger.info("information",
                        telegram_id=1,
                        name=menu_name)
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=20, menu_name=menu_name).pack()))

    return keyboard.adjust(*sizes).as_markup()

def get_user_catalog_btns(*, level: int, categories: list):
    keyboard = InlineKeyboardBuilder()
    if len(categories) % 2 == 0:
        sizes = (2,)
    else:
        sizes = (1,2,)
    for c in categories:
        keyboard.add(InlineKeyboardButton(text=c.name,
                                          callback_data=MenuCallBack(level=level + 1,
                                                                     menu_name=c.name,
                                                                     category=c.id,
                                                                     category_control_type=True
                                                                     ).pack()))

    keyboard.add(InlineKeyboardButton(text='Корзина 🛒',
                                      callback_data=MenuCallBack(level=3, menu_name='order').pack()))
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
                                                                     menu_name=c.type_name,
                                                                     category=c.id,
                                                                     category_control_type=False
                                                                     ).pack()))

    keyboard.add(InlineKeyboardButton(text='Корзина 🛒',
                                      callback_data=MenuCallBack(level=4, menu_name='order').pack()))
    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=level - 1,
                                                                 menu_name='catalog',
                                                                 ).pack()))
    # keyboard.add(InlineKeyboardButton(text='На главную 🏠',
    #                                   callback_data=MenuCallBack(level=0, menu_name='main').pack()))



    return keyboard.adjust(*sizes).as_markup()

def get_products_btns(
        *,
        level: int,
        category: int,
        page: int,
        pagination_btns: dict,
        product_id: int,
        sizes: tuple[int] = (1, 2)
):

    row = []
    for text, menu_name in pagination_btns.items():
        if menu_name == "next":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MenuCallBack(
                                                level=level,
                                                menu_name=menu_name,
                                                category=category,
                                                page=page + 1,
                                                category_control_type=False
                                            ).pack()))

        elif menu_name == "previous":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MenuCallBack(
                                                level=level,
                                                menu_name=menu_name,
                                                category=category,
                                                page=page - 1,
                                                category_control_type=False
                                            ).pack()))



    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Купить 💵',
                                      callback_data=MenuCallBack(level=level,
                                                                 menu_name='add_to_order',
                                                                 category=category,
                                                                 product_id=product_id,
                                                                 category_control_type=False).pack()))
    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=level - 1,
                                                                 menu_name='catalog',
                                                                 category_control_type=False).pack()))
    keyboard.add(InlineKeyboardButton(text='Корзина 🛒',
                                      callback_data=MenuCallBack(level=3,
                                                                 menu_name='order',
                                                                 category_control_type=False).pack()))

    # keyboard.add(InlineKeyboardButton(text='На главную 🏠',
    #                                   callback_data=MenuCallBack(level=0, menu_name='main').pack()))
    keyboard.adjust(*sizes)
    return keyboard.row(*row).as_markup()

def get_user_order_btns(
        *,
        level: int,
        page: int | None,
        pagination_btns: dict | None,
        product_id: int | None,
        sizes: tuple[int] = (3,)
):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Меню 🍕',
                             callback_data=MenuCallBack(level=1, menu_name='catalog').pack()))
    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0, menu_name='main').pack()))

    return keyboard.adjust(*sizes).as_markup()

def get_user_delivery_btns(*, level: int, sizes: tuple[int] = (1,1,2,)):
    keyboard = InlineKeyboardBuilder()



    keyboard.add(InlineKeyboardButton(text='В кафе',
                                      callback_data=MenuCallBack(level=8,
                                                                 menu_name='take_cafe',).pack()))
    keyboard.add(InlineKeyboardButton(text='Доставить',
                                      callback_data=MenuCallBack(level=5,
                                                                 menu_name='payment',).pack()))
    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=level - 1,
                                                                 menu_name='order',
                                                                 category_control_type=False).pack()))
    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0, menu_name='main').pack()))
    return keyboard.adjust(*sizes).as_markup()


def get_user_payment_btns(*, level: int, sizes: tuple[int] = (1,1,2)):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Курьеру, наличными или переводом',
                                      callback_data=MenuCallBack(level=7,
                                                                 menu_name='take_courier',).pack()))
    keyboard.add(InlineKeyboardButton(text='Сейчас, банковской картой',
                                      callback_data=MenuCallBack(level=6,
                                                                 menu_name='payment_card',).pack()))
    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=level - 1,
                                                                 menu_name='delivery').pack()))
    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0, menu_name='main').pack()))
    return keyboard.adjust(*sizes).as_markup()



def get_user_payment_card_btns(*, level: int, sizes: tuple[int] = (1,2)):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Оплатить',
                                      callback_data=MenuCallBack(level=level + 1,
                                                                 menu_name='payment_card',
                                                                 category_control_type=True,).pack()))
    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=level - 1,
                                                                 menu_name='payment').pack()))
    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0,
                                                                 menu_name='main').pack()))

    return keyboard.adjust(*sizes).as_markup()

def get_user_end_order_btns(*, level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0, menu_name='main', cart_id=0).pack()))

    return keyboard.adjust(*sizes).as_markup()


def get_user_carts_btns(*, level: int, categories: list):
    if len(categories) % 2 == 0:
        sizes = (2,)
    else:
        sizes = (1,2,)
    keyboard = InlineKeyboardBuilder()


    for c in categories:

        updated = c.updated.strftime("%d-%m-%Y")
        text = f'{c.number_cart} от {updated}'
        keyboard.add(InlineKeyboardButton(text=text,
                                          callback_data=MenuCallBack(level=level,
                                                                     menu_name='history_cart',
                                                                     category=c.id,
                                                                     ).pack()))

    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0, menu_name='main', cart_id=0).pack()))
    return keyboard.adjust(*sizes).as_markup()



def get_user_adress_btns(*, level: int, categories: list):
    if len(categories) % 2 == 0:
        sizes = (2,)
    else:
        sizes = (1,2,)

    keyboard = InlineKeyboardBuilder()

    for c in categories:
        keyboard.add(InlineKeyboardButton(text=c.adress_user,
                                          callback_data=MenuCallBack(level=level,
                                                                     menu_name='take_courier',
                                                                     category=c.id,
                                                                     category_control_type=False
                                                                     ).pack()))
    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=4, menu_name='delivery').pack()))
    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0, menu_name='main', cart_id=0).pack()))

    return keyboard.adjust(*sizes).as_markup()



def get_information_btns(*, level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        'На главную 🏠': "main",
        "О нас ℹ️": "about",
        "Оплата 💰": "payment",
        "Доставка ⛵": "shipping",
        "Вакансии": "vacancy",
        "Разработчику": "for_devolep",
    }
    for text, menu_name in btns.items():
        if menu_name == 'main':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=0, menu_name=menu_name).pack()))
        elif menu_name == 'payment':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=level+1, menu_name=menu_name).pack()))
        elif menu_name == 'shipping':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=level+2, menu_name=menu_name).pack()))
        elif menu_name == 'vacancy':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=level+3, menu_name=menu_name).pack()))
        elif menu_name == 'about':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=level+4, menu_name=menu_name).pack()))
        elif menu_name == 'for_devolep':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=level+5, menu_name=menu_name).pack()))

    return keyboard.adjust(*sizes).as_markup()


def get_user_about_btns(*, level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=20, menu_name='information', cart_id=0).pack()))
    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0, menu_name='main', cart_id=0).pack()))

    return keyboard.adjust(*sizes).as_markup()

def get_user_telefon_add_btns(*, level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=8, menu_name='take_courier').pack()))
    keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                                      callback_data=MenuCallBack(level=0, menu_name='main').pack()))

    return keyboard.adjust(*sizes).as_markup()
