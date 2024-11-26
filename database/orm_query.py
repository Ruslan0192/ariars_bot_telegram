# import datetime

from sqlalchemy import select, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import joinedload

from database.models import *


# **************************************************************************************************************
# __tablename__ = 'General'
async def orm_get_general(session: AsyncSession, id_name: str):
    query = select(General).where(General.id_name == id_name)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_generals(session: AsyncSession):
    query = select(General).where(General.id_name != 'for_devoloper').order_by(General.id.asc())
    result = await session.execute(query)
    return result.scalars().all()


async def orm_add_general(session: AsyncSession,
                          id_name: str,
                          name: str,
                          description: str,
                          value: float,
                          picture: str,
                          ):
    obj = General(
        id_name=id_name,
        name=name,
        description=description,
        value=value,
        picture=picture
    )
    session.add(obj)
    await session.commit()


async def orm_change_general(session: AsyncSession, id: int, picture: str, description: str):
    if description == None:
        query = (update(General).
                 where(General.id == id).values(picture=picture))
    else:
        query = (update(General).
                 where(General.id == id).values(picture=picture,
                                                description=description))
    await session.execute(query)
    await session.commit()


async def orm_change_photo_general(session: AsyncSession, id, picture):
    query = (update(General).
            where(General.id == id).values(picture=picture))
    await session.execute(query)
    await session.commit()


async def orm_change_text_general(session: AsyncSession, id, description):
    query = (update(General).
            where(General.id == id).values(description=description))
    await session.execute(query)
    await session.commit()


# **************************************************************************************************************
# __tablename__ = 'Category_question'
async def orm_add_category_question(session: AsyncSession, name: str, description: str, picture: str):
    obj = Category_question(
        name=name,
        description=description,
        picture=picture
    )
    session.add(obj)
    await session.commit()


async def orm_get_category_questions(session: AsyncSession):
    query = select(Category_question)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_category_question(session: AsyncSession, id: int):
    query = select(Category_question).where(Category_question.id == id)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_name_category_question(session: AsyncSession, name: str):
    query = select(Category_question).where(Category_question.name == name)
    result = await session.execute(query)
    return result.scalar()


async def orm_change_category_question(session: AsyncSession, name: str, description: str, picture: str):
    query = (update(Category_question).
             where(Category_question.name == name).values(description=description, picture=picture))
    await session.execute(query)
    await session.commit()


async def orm_change_name_category_question(session: AsyncSession, id: int, name: str):
    query = (update(Category_question).
             where(Category_question.id == id).values(name=name))
    await session.execute(query)
    await session.commit()


async def orm_delete_category_question(session: AsyncSession, name: str):
    query = (delete(Category_question).where(Category_question.name == name))
    await session.execute(query)
    await session.commit()


# **************************************************************************************************************
# __tablename__ = 'Questions'
async def orm_add_question(session: AsyncSession, telegram_id: int, category_question_id: int,
                           parents_id: int, question_text: str,answer_text: str):
    obj = insert(Questions).values(telegram_id=telegram_id,
                                   category_question_id=category_question_id,
                                   parents_id=parents_id,
                                   question_text=question_text,
                                   answer_text=answer_text)
    result = await session.execute(obj)
    id = result.inserted_primary_key[0]
    await session.commit()
    return id


async def orm_get_question_id(session: AsyncSession, id: int):
    query = select(Questions).where(Questions.id == id)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_new_questions(session: AsyncSession):
    query = select(Questions).where(Questions.answer_text == '')
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_active_questions(session: AsyncSession):
    query = select(Questions).where(Questions.frozen == False)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_active_telegram_questions(session: AsyncSession, telegram_id: int):
    query = select(Questions).where(Questions.frozen == False, Questions.telegram_id == telegram_id)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_question_frozen(session: AsyncSession, id: int):
    query = (update(Questions).
             where(Questions.id == id).values(frozen=True))
    await session.execute(query)
    await session.commit()


async def orm_get_parents_questions(session: AsyncSession, parents_id: int):
    query = select(Questions).where(Questions.parents_id == parents_id)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_archive_questions(session: AsyncSession, parents_id: int):
    query = select(Questions).where(Questions.answer_text != '',
                                    Questions.parents_id == parents_id)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_questions_telegram(session: AsyncSession, telegram_id: int, parents_id: int):
    query = select(Questions).where(Questions.telegram_id == telegram_id,
                                    Questions.parents_id == parents_id)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_questions_archive(session: AsyncSession):
    query = select(Questions).distinct(Questions.telegram_id)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_answer_question(session: AsyncSession, id: int, answer_text: str):
    query = (update(Questions).
             where(Questions.id == id).values(answer_text=answer_text, ))
    await session.execute(query)
    await session.commit()


# **************************************************************************************************************
# __tablename__ = 'Question_pictures'
async def orm_add_questions_pictures(session: AsyncSession, question_id: int, picture: str, caption: str):
    obj = Question_pictures(question_id=question_id,
                            picture=picture,
                            caption=caption)
    session.add(obj)
    await session.commit()


async def orm_get_question_pictures(session: AsyncSession, question_id: int):
    query = select(Question_pictures).where(Question_pictures.question_id == question_id)
    result = await session.execute(query)
    return result.scalars().all()


# **************************************************************************************************************
# __tablename__ = 'User'
async def orm_get_users(session: AsyncSession):
    query = select(User)
    result = await session.execute(query)
    return result.scalars().all()

# поиск пользователя
async def orm_get_user(session: AsyncSession, telegram_id: int):
    query = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(query)
    return result.scalar()

async def orm_add_user(session: AsyncSession,
                       telegram_id: int,
                       name: str):
    obj = User(
        telegram_id=telegram_id,
        name=name
    )
    session.add(obj)
    await session.commit()

async def orm_change_user(session: AsyncSession,
                          telegram_id: int,
                          name: str):
    query = update(User).where(User.telegram_id == telegram_id).values(
        name=name,
    )
    await session.execute(query)
    await session.commit()

async def orm_add_telefon_user(session: AsyncSession,
                          telegram_id: int,
                          telefon: str):
    query = update(User).where(User.telegram_id == telegram_id).values(
        telefon=telefon,
    )
    await session.execute(query)
    await session.commit()


# **************************************************************************************************************
# __tablename__ = 'Admin'
async def orm_add_admin(session: AsyncSession,
                       telegram_id: int,
                       superadmin: bool):
    obj = Admin(
        telegram_id=telegram_id,
        superadmin=superadmin
    )
    session.add(obj)
    await session.commit()


async def orm_get_admins_work(session: AsyncSession):
    query = select(Admin).where(Admin.user == False)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_change_admin_user(session: AsyncSession, telegram_id: int):
    query = update(Admin).where(Admin.telegram_id == telegram_id).values(user=True)
    await session.execute(query)
    await session.commit()


async def orm_get_admins_no_work(session: AsyncSession):
    query = select(Admin).where(Admin.user == True)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_change_user_admin(session: AsyncSession, telegram_id: int):
    query = update(Admin).where(Admin.telegram_id == telegram_id).values(user=False)
    await session.execute(query)
    await session.commit()



# **************************************************************************************************************
#     __tablename__ = 'Products'
async def orm_get_product_name(session: AsyncSession, name: str):
    query = select(Products).where(Products.name == name)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_product_id(session: AsyncSession, id: int):
    query = select(Products).where(Products.id == id)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_products_parent(session: AsyncSession, parents_id: int):
    query = select(Products).where(Products.parents_id == parents_id)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_products(session: AsyncSession, cat_id: int, frozen):
    query = select(Products).where(Products.cat_id == cat_id,
                                   Products.frozen == frozen)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_product_frozen(session: AsyncSession, id: int):
    query = (update(Products).
             where(Products.id == id).values(frozen=True))
    await session.execute(query)
    await session.commit()


async def orm_add_product(session: AsyncSession, parents_id: int, name: str, cat_id: int,
                          composition: str, color: str, size: str, gender: str,
                          description: str, price: float, link: str):
    obj = insert(Products).values(parents_id=parents_id,
                                  name=name,
                                  cat_id=cat_id,
                                  composition=composition,
                                  color=color,
                                  size=size,
                                  gender=gender,
                                  description=description,
                                  price=price,
                                  link=link)
    result = await session.execute(obj)
    id = result.inserted_primary_key[0]
    await session.commit()
    return id


# **************************************************************************************************************
#     __tablename__ = 'Product_cat'
async def orm_get_prod_cats(session: AsyncSession):
    query = select(Product_cat)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_prod_cat(session: AsyncSession, name: str):
    query = select(Product_cat).where(Product_cat.name == name)
    result = await session.execute(query)
    return result.scalar()

async def orm_add_prod_cat(session: AsyncSession, name: str):
    obj = Product_cat(name=name)
    session.add(obj)
    await session.commit()


# **************************************************************************************************************
#     __tablename__ = 'Product_cat_type'
async def orm_get_prod_cat_no_types(session: AsyncSession, cat_name: str):
    query = select(Product_cat_type).where(Product_cat_type.cat_name == cat_name,
                                           Product_cat_type.type_name != '')
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_prod_cat_type(session: AsyncSession, cat_name: str, type_name: str):
    query = select(Product_cat_type).where(Product_cat_type.cat_name == cat_name,
                                           Product_cat_type.type_name == type_name)
    result = await session.execute(query)
    return result.scalar()

async def orm_get_prod_cat_types(session: AsyncSession, cat_name: str):
    query = select(Product_cat_type).where(Product_cat_type.cat_name == cat_name)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_prod_cat_types_id(session: AsyncSession, id: int):
    query = select(Product_cat_type).where(Product_cat_type.id == id)
    result = await session.execute(query)
    return result.scalar()

async def orm_add_prod_cat_type(session: AsyncSession, cat_name: str, type_name: str):
    obj = insert(Product_cat_type).values(cat_name=cat_name, type_name=type_name)
    result = await session.execute(obj)
    id = result.inserted_primary_key[0]
    await session.commit()
    return id

async def orm_change_prod_cat_type_name(session: AsyncSession, id: int, type_name: str):
    query = update(Product_cat_type).where(Product_cat_type.id == id).values(type_name=type_name)
    await session.execute(query)
    await session.commit()


async def orm_change_prod_cat_photo(session: AsyncSession, id: int, picture: str):
    query = update(Product_cat_type).where(Product_cat_type.id == id).values(picture=picture)
    await session.execute(query)
    await session.commit()


# **************************************************************************************************************
# __tablename__ = 'Product_pictures'
async def orm_add_product_picture(session: AsyncSession, product_id: int, picture: str):
    obj = Product_pictures(product_id=product_id,
                           picture=picture)
    session.add(obj)
    await session.commit()

async def orm_get_product_pictures(session: AsyncSession, product_id: int):
    query = select(Product_pictures).where(Product_pictures.product_id == product_id,
                                           Product_pictures.frozen == False)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_product_picture_frozen(session: AsyncSession, id: int):
    query = (update(Product_pictures).
             where(Product_pictures.id == id).values(frozen=True))
    await session.execute(query)
    await session.commit()


# **************************************************************************************************************
# __tablename__ = 'Product_composition'
async def orm_add_product_composition(session: AsyncSession,  name: str):
    obj = Product_composition(name=name)
    session.add(obj)
    await session.commit()


async def orm_get_product_compositions(session: AsyncSession):
    query = select(Product_composition)
    result = await session.execute(query)
    return result.scalars().all()


# **************************************************************************************************************
# __tablename__ = 'Product_color'
async def orm_add_product_color(session: AsyncSession,  name: str):
    obj = Product_color(name=name)
    session.add(obj)
    await session.commit()

async def orm_get_product_colors(session: AsyncSession):
    query = select(Product_color)
    result = await session.execute(query)
    return result.scalars().all()


# **************************************************************************************************************
# __tablename__ = 'Product_size'
async def orm_add_product_size(session: AsyncSession,  name: str):
    obj = Product_size(name=name)
    session.add(obj)
    await session.commit()

async def orm_get_product_sizes(session: AsyncSession):
    query = select(Product_size)
    result = await session.execute(query)
    return result.scalars().all()


# **************************************************************************************************************
# __tablename__ = 'Product_gender'
async def orm_add_product_gender(session: AsyncSession,  name: str):
    obj = Product_gender(name=name)
    session.add(obj)
    await session.commit()

async def orm_get_product_genders(session: AsyncSession):
    query = select(Product_gender)
    result = await session.execute(query)
    return result.scalars().all()


# ********************************************************************************
# __tablename__ = 'Question_for_devoloper'
async def orm_add_question_for_devoloper(session: AsyncSession, text: str):
    obj = Question_for_devoloper(text=text)
    session.add(obj)
    await session.commit()
