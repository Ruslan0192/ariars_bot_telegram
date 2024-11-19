from aiogram import Bot

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_add_general, orm_get_admins_work, orm_add_category_question


async def load_list_admins(session: AsyncSession, bot: Bot):
    # загрузка из бд адресов админа и владельца
    bot.my_admins_list = []
    result = await orm_get_admins_work(session=session)
    for admin_bd in result:
        bot.my_admins_list.append(admin_bd.telegram_id)

        if admin_bd.superadmin:
            bot.superadmin = admin_bd.telegram_id


async def save_default_question(session: AsyncSession, picture):
    # сохраняю темы вопросов по умолчанию
    await orm_add_category_question(session, name='Прочее',
                                    description='Здесь можете написать любой вопрос',
                                    picture=picture)


async def save_default_in_base(session: AsyncSession, picture):
    # сохраняю картинки по умолчанию
    await orm_add_general(session,
                          id_name='hello_description',
                          name='Приветствие',
                          description='Вас приветствует бот дома брендовой одежды "AriarsHouse"!',
                          value=0,
                          picture=picture,
                          )
    await orm_add_general(session,
                          id_name='main',
                          name='Основное меню',
                          description='',
                          value=0,
                          picture=picture,
                          )
    await orm_add_general(session,
                          id_name='catalog',
                          name='Каталог',
                          description='',
                          value=0,
                          picture=picture,
                          )
    await orm_add_general(session,
                          id_name='order',
                          name='Пустая корзина',
                          description='',
                          value=0,
                          picture=picture,
                          )
    await orm_add_general(session,
                          id_name='question',
                          name='Вопрос',
                          description='',
                          value=0,
                          picture=picture,
                          )
    await orm_add_general(session,
                          id_name='information',
                          name='Подраздел информация',
                          description='',
                          value=0,
                          picture=picture,
                          )
    await orm_add_general(session,
                          id_name='about_description',
                          name='О нас',
                          description='Дом брендовой одежды "AriarsHouse"\n'
                                      'Мы изготавливаем одежду только из премиум материалов,\n'
                                      'контроль и приемку товаров ведут квалифицированные специалисты ОТК.\n\n',
                          value=0,
                          picture=picture,
                          )
