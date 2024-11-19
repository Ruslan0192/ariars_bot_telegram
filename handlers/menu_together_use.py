from aiogram.fsm.context import FSMContext
from aiogram import Bot, types
from aiogram.types import InputMediaPhoto

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Questions
from database.orm_query import (orm_get_question_pictures,
                                orm_get_category_question,
                                orm_get_user, orm_get_question_id,
                                orm_get_questions_telegram,
                                orm_get_general,
                                orm_get_archive_questions,
                                orm_get_new_questions,
                                orm_get_parents_questions, orm_get_active_questions, orm_get_active_telegram_questions)
from keyboards.inline_together_use import get_history_questions_btns, get_empty_btns

from utils.paginator import Paginator


def def_pages(paginator: Paginator):
    btns = dict()
    if paginator.has_previous():
        btns["◀ Пред."] = "previous"

    if paginator.has_next():
        btns["След. ▶"] = "next"
    return btns


async def def_clear_question_message(state: FSMContext):
    data_state = await state.get_data()
    try:
        message_show = data_state['message_show']
        for key, message_product in message_show.items():
            await message_product.delete()
    except:
        pass
    await state.update_data({'message_show': {}})
    # await state.update_data({'get_message': ''})


async def def_out_pictures_in_question(session: AsyncSession,
                                       state: FSMContext,
                                       question: Questions,
                                       level: int,
                                       type_message: int,
                                       admin: bool,
                                       level_back: int,
                                       theme_name: str,
                                       page: int = 1):
    """" type_message = category в callback_data
    в разделе "новые сообщения", "архив сообщений"
        0 - кнопка "выбрать", из списка message_show (для удаления без панели управления)
        1 - кнопка "выбрать", переменная edit_message (для изменения, с панелью управления)
    в разделе "новые сообщения ->выбрать (введите ответ (прием сообщения))", "архив сообщений ->выбрать (просмотр переписки)"
        10 - нет кнопки "выбрать", из списка message_show (для удаления без панели управления)
        11 - нет кнопки "выбрать", переменная edit_message (для изменения, с панелью управления)
    """
    pictures = await orm_get_question_pictures(session, question.id)

    time_ask = question.created.strftime("%d-%m-%Y")
    time_answer = question.updated.strftime("%d-%m-%Y")

    under_type_message = int(type_message / 10)

    if admin:
        # сообщения для интерфейса админа
        telegram_id = question.telegram_id
        user = await orm_get_user(session, telegram_id)
        name = user.name

        if under_type_message == 0:
            caption = (f'*{name} (id:{telegram_id})*\n\n'
                       f'Переписка по теме *"{theme_name}"*\n'
                       f"*Вопрос* от {time_ask}:\n"
                       f"_{question.question_text}_")
            if question.answer_text != '':
                caption += f"\n*Ответ* от {time_answer}:\n_{question.answer_text}_\n\n"
        else:
            caption = (f'*{name} (id:{telegram_id})*\n\n'
                       f'Вопрос от {time_ask} по теме *"{theme_name}"*:\n'
                       f"_{question.question_text}_")
            if question.answer_text == '':
                # ответа не было
                caption += f"\n\n*Напишите ответ*"
                await state.update_data({'get_message': f'textanswerquestion_{question.id}'})
                await state.update_data({'telegram_id': question.telegram_id})
            else:
                caption += f"\n*Ответ* от {time_answer}:\n_{question.answer_text}_"

    else:
        # сообщения для интерфейса покупателя
        if under_type_message == 2:
            # в разделе "новые сообщения = "выбрать"
            if type_message % 2 == 1:
                caption = (f'Вопрос по теме *"{theme_name}"*:\n'
                           f"_{question.question_text}_\n\n"
                           f"Сообщение отправлено {time_ask}.\n"
                           f"*При необходимости добавьте фотографию*")
            else:
                caption = (f'Переписка по теме *"{theme_name}"*:\n'
                           f"*Вопрос* от {time_ask}:\n_{question.question_text}_\n"
                           f"*Ответ* от {time_answer}:\n_{question.answer_text}_")
        else:
            if question.answer_text == '':
                # ответа не было
                caption = (f'Переписка по теме *"{theme_name}"*:\n'
                           f"*Вопрос* от {time_ask}:\n_{question.question_text}_\n"
                           f"*Ответа еще не было*")
            else:
                caption = (f'Переписка по теме *"{theme_name}"*:\n'
                           f"*Вопрос* от {time_ask}:\n_{question.question_text}_\n"
                           f"*Ответ* от {time_answer}:\n_{question.answer_text}_")
                if type_message % 2 == 1:
                    caption += f"\n\n*Для продолжения переписки, напишите сообщение*"
                    await state.update_data({'get_message': f'textanswerquestion_{question.id}'})
                    await state.update_data({'theme': question.category_question_id})
                    await state.update_data({'parents_id': question.parents_id})

    if len(pictures) == 0:
        media = ''
        pagination_btns = {}
    else:
        paginator = Paginator(pictures, page=page)
        picture = paginator.get_page()[0]
        pagination_btns = def_pages(paginator)
        media = picture.picture
        caption = f"Фото {paginator.page} из {paginator.pages}\n\n" + caption

    reply_markup = get_history_questions_btns(level=level,
                                              page=page,
                                              pagination_btns=pagination_btns,
                                              product_id=question.id,
                                              type_message=type_message,
                                              theme_name=theme_name,
                                              level_back=level_back)
    return media, caption, reply_markup


# level = 21 и 25
async def def_question_history(message: types.Message,
                               state: FSMContext,
                               session: AsyncSession,
                               level: int,
                               level_back: int,
                               telegram_id: int,
                               admin: bool,
                               new: bool):
    type_message = 0
    if admin:
        if new:
            archive_questions = await orm_get_new_questions(session)
        else:
            archive_questions = await orm_get_active_questions(session)
    else:
        archive_questions = await orm_get_active_telegram_questions(session, telegram_id)

    if len(archive_questions) == 0:
        result = await orm_get_general(session, 'question')
        image = InputMediaPhoto(media=result.picture, caption='Переписки не было!')
        reply_markup = get_empty_btns(level_back=level_back)
        return image, reply_markup

    return await def_list_out_questions(message=message,
                                        session=session,
                                        state=state,
                                        level=level+1,
                                        questions=archive_questions,
                                        type_message=type_message,
                                        level_back=level_back,
                                        admin=admin)


async def def_list_out_questions(message: types.Message,
                                 session: AsyncSession,
                                 state: FSMContext,
                                 level: int,
                                 questions: list,
                                 type_message: int,
                                 level_back: int,
                                 admin: bool):
    """ выдает список всех вопросов находящихся в question. Последнее сообщение с меню"""
    # убрать все вопросы, вывести все заново
    await def_clear_question_message(state)

    data_state = await state.get_data()
    try:
        edit_message = data_state['edit_message']
        await edit_message.delete()
    except:
        pass


    if int(type_message/10) == 0:
        # для вывода истории по всем темам
        flag_theme = True
    else:
        # просмотр истории одного вопроса
        flag_theme = False
        theme = await orm_get_category_question(session, questions[0].category_question_id)

    count = 0
    message_show = {}
    max_index_questions = len(questions)-1
    while count <= max_index_questions-1:
        question = questions[count]
        count += 1
        if flag_theme:
            theme = await orm_get_category_question(session, question.category_question_id)
        photo, caption, reply_markup = await def_out_pictures_in_question(session=session,
                                                                          state=state,
                                                                          question=question,
                                                                          level=level,
                                                                          type_message=type_message,
                                                                          admin=admin,
                                                                          theme_name=theme.name,
                                                                          level_back=level_back)
        if photo == '':
            message_product = await message.answer(text=caption, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            message_product = await message.answer_photo(photo=photo, caption=caption, reply_markup=reply_markup, parse_mode='Markdown')
        message_show.update({question.id: message_product})
    await state.update_data({'message_show': message_show})

    # последнее сообщение с меню
    question = questions[max_index_questions]
    if flag_theme:
        theme = await orm_get_category_question(session, question.category_question_id)
    photo, caption, reply_markup = await def_out_pictures_in_question(session=session,
                                                                      state=state,
                                                                      question=question,
                                                                      level=level,
                                                                      type_message=type_message+1,
                                                                      admin=admin,
                                                                      theme_name=theme.name,
                                                                      level_back=level_back)
    if photo == '':
        result = await orm_get_general(session, 'question')
        photo = result.picture
    edit_message = await message.answer_photo(photo=photo, caption=caption, reply_markup=reply_markup, parse_mode='Markdown')
    await state.update_data({'edit_message': edit_message})

    return None, None


# level = 23 и 26
async def def_question_change_photo(session: AsyncSession,
                                    state: FSMContext,
                                    level: int,
                                    level_back: int,
                                    menu_name: str,
                                    category: int,
                                    product_id: int,
                                    admin: bool,
                                    page: int):
    # меняю фото в сообщении
    question = await orm_get_question_id(session, id=product_id)

    data_state = await state.get_data()
    if category % 10 == 1:
        #  сообщение с меню
        edit_message = data_state['edit_message']
    else:
        message_show = data_state['message_show']
        edit_message = message_show[question.id]

    media, caption, reply_markup = await def_out_pictures_in_question(session=session,
                                                                      state=state,
                                                                      question=question,
                                                                      level=level,
                                                                      type_message=category,
                                                                      admin=admin,
                                                                      level_back=level_back,
                                                                      theme_name=menu_name,
                                                                      page=page)
    image = InputMediaPhoto(media=media, caption=caption, parse_mode='Markdown')
    await edit_message.edit_media(media=image, reply_markup=reply_markup)
    return None, None


# level = 24 и 27
async def def_list_out_one_question_parents(message: types.Message,
                                            session: AsyncSession,
                                            state: FSMContext,
                                            menu_name: str,
                                            level: int,
                                            level_back: int,
                                            type_message: int,
                                            id_question: int,
                                            admin: bool,
                                            ):
    """ выдает список вопросов для одной ветки переписки: первый прародитель, затем все дочки. Последнее сообщение с меню"""
    if admin == False and menu_name == 'answeradmin':
        # пришел ответ от администратора
        await message.delete()
    if admin == True and menu_name == 'questionuser':
        # пришел вопрос от покупателя
        await message.delete()

    question = await orm_get_question_id(session, id_question)
    out_question = []
    if question.parents_id == 0:
        # только один вопрос, без переписки
        out_question.append(question)
    else:
        # поиск всех сообщений по переписке
        father_question = await orm_get_question_id(session, question.parents_id)
        # первое прародитель
        out_question.append(father_question)
        questions = await orm_get_questions_telegram(session, father_question.telegram_id, father_question.id)
        out_question += questions
    return await def_list_out_questions(message=message,
                                        session=session,
                                        state=state,
                                        level=level-1,
                                        questions=out_question,
                                        type_message=type_message,
                                        level_back=level_back,
                                        admin=admin)
