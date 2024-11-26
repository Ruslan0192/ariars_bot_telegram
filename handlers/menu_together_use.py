from aiogram import Bot, types
from aiogram.types import InputMediaPhoto
from aiogram.fsm.context import FSMContext


from sqlalchemy.ext.asyncio import AsyncSession

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
# from apscheduler_di import ContextSchedulerDecorator



from database.models import Questions
from database.orm_query import (orm_get_question_pictures,
                                orm_get_category_question,
                                orm_get_user, orm_get_question_id,
                                orm_get_questions_telegram,
                                orm_get_general,
                                orm_get_new_questions,
                                orm_get_active_questions,
                                orm_get_active_telegram_questions, orm_get_prod_cats)
# from database.redis_jobstore import RedisJobStore

from keyboards.inline_admin import get_admin_questions_byers_btns

from keyboards.inline_together_use import get_history_questions_btns, get_empty_btns
from keyboards.inline_user import get_user_question_main_btns, get_user_catalog_btns

from utils.paginator import Paginator


job_stores = {
    'redis': RedisJobStore()}
scheduler = AsyncIOScheduler(jobstores=job_stores)

# scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone="Europe/Moscow", jobstores=jobstores))



# 23 часа до сброса сообщений message_show
TIME_CLEAR_MESSAGE = 23


def def_pages(paginator: Paginator):
    btns = dict()
    if paginator.has_previous():
        btns["◀ Пред."] = "previous"

    if paginator.has_next():
        btns["След. ▶"] = "next"
    return btns


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
                await state.update_data({'telegram_id_answer': question.telegram_id})
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


async def def_clear_question_message(bot: Bot, state: FSMContext):
    data_state = await state.get_data()
    scheduler_job_id = data_state['scheduler_job_id']
    get_message = data_state['get_message']
    edit_message = data_state['edit_message']
    telegram_id = data_state['telegram_id']

    if scheduler_job_id != '':
        telegram_id = data_state['telegram_id']
        message_show = data_state['message_show']
        messages_delete = list(message_show.values())
        await bot.delete_messages(telegram_id, messages_delete)

        if scheduler.get_job(scheduler_job_id) != None:
            scheduler.remove_job(scheduler_job_id)

    await state.clear()
    await state.update_data({'telegram_id': telegram_id})
    await state.update_data({'scheduler_job_id': ''})
    await state.update_data({'get_message': get_message})
    await state.update_data({'edit_message': edit_message})


async def def_start_timer_clear_messages(
        session: AsyncSession, bot: Bot, state: FSMContext, message_show: dict,
        admin: bool, question: bool = True):

    data_state = await state.get_data()
    telegram_id = data_state['telegram_id']

    if message_show != {}:
        # есть дополнительные сообщения, запускаю таймер для автоудаления через 23 часа
        await state.update_data({'message_show': message_show})

        scheduler_job = scheduler.add_job(func=def_timer_clear_messages,
                                          # jobstore='redis',
                                          trigger='interval',
                                          hours=TIME_CLEAR_MESSAGE,
                                          # seconds=TIME_CLEAR_MESSAGE,
                                          args=(session, bot, state, admin, telegram_id, question))
        await state.update_data({'scheduler_job_id': scheduler_job.id})


async def def_timer_clear_messages(
        session: AsyncSession, bot: Bot, state: FSMContext, admin: bool, telegram_id: int, question: bool):

    await def_clear_question_message(bot, state)
    await state.update_data({'get_message': f''})

    data_state = await state.get_data()
    edit_message = data_state['edit_message']

    if admin:
        image, reply_markup = await def_questions_byers_admin(session, bot, state, 20)
    else:
        image, reply_markup = await def_question_main_user(session, bot, state, question)

    await bot.edit_message_media(media=image,
                                 chat_id=telegram_id,
                                 message_id=edit_message,
                                 reply_markup=reply_markup)


# level = 21 и 25
async def def_question_history(message: types.Message,
                               bot: Bot,
                               state: FSMContext,
                               session: AsyncSession,
                               level: int,
                               level_back: int,
                               admin: bool,
                               new: bool):
    type_message = 0
    if admin:
        if new:
            archive_questions = await orm_get_new_questions(session)
        else:
            archive_questions = await orm_get_active_questions(session)
    else:
        data_state = await state.get_data()
        telegram_id = data_state['telegram_id']
        archive_questions = await orm_get_active_telegram_questions(session, telegram_id)

    if len(archive_questions) == 0:
        result = await orm_get_general(session, 'question')
        image = InputMediaPhoto(media=result.picture, caption='Нет новых вопросов!')
        reply_markup = get_empty_btns(level_back=level_back)
        return image, reply_markup

    return await def_list_out_questions(message=message,
                                        session=session,
                                        bot=bot,
                                        state=state,
                                        level=level+1,
                                        questions=archive_questions,
                                        type_message=type_message,
                                        level_back=level_back,
                                        admin=admin)


async def def_list_out_questions(message: types.Message,
                                 session: AsyncSession,
                                 bot: Bot,
                                 state: FSMContext,
                                 level: int,
                                 questions: list,
                                 type_message: int,
                                 level_back: int,
                                 admin: bool):
    """ выдает список всех вопросов находящихся в question. Последнее сообщение с меню"""
    # убрать все вопросы, вывести все заново
    await def_clear_question_message(bot, state)

    data_state = await state.get_data()
    telegram_id = data_state['telegram_id']
    edit_message = data_state['edit_message']
    await bot.delete_message(telegram_id, edit_message)

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
            message_product = await message.answer_photo(
                photo=photo, caption=caption, reply_markup=reply_markup, parse_mode='Markdown')
        message_show.update({question.id: message_product.message_id})

    await def_start_timer_clear_messages(session, bot, state, message_show, admin)

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
    edit_message = await message.answer_photo(
        photo=photo, caption=caption, reply_markup=reply_markup, parse_mode='Markdown')
    await state.update_data({'edit_message': edit_message.message_id})

    return None, None


# level=20 admin
async def def_questions_byers_admin(session: AsyncSession, bot: Bot, state: FSMContext, level: int):
    await def_clear_question_message(bot, state)
    result = await orm_get_general(session, 'question')
    image = InputMediaPhoto(media=result.picture, caption='Работа с вопросами покупателей')
    reply_markup = get_admin_questions_byers_btns(level=level)
    return image, reply_markup


# level=1 and 20 user
async def def_question_main_user(
        session: AsyncSession, bot: Bot, state: FSMContext, question: bool):
    await def_clear_question_message(bot, state)
    await state.update_data({'get_message': ''})

    # themes = await orm_get_category_questions(session)
    if question:
        result = await orm_get_general(session, 'question')
        caption = 'Задайте новый вопрос или посмотрите истории запросов:'
        reply_markup = get_user_question_main_btns(level=20)
    else:
        categories = await orm_get_prod_cats(session)
        result = await orm_get_general(session, 'catalog')
        caption = "Категории:"
        reply_markup = get_user_catalog_btns(level=1, categories=categories)

    image = InputMediaPhoto(media=result.picture, caption=caption)
    return image, reply_markup


# level = 23 и 26
async def def_question_change_photo(session: AsyncSession,
                                    bot: Bot,
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
    telegram_id = data_state['telegram_id']
    if category % 10 == 1:
        #  сообщение с меню
        edit_message = data_state['edit_message']
    else:
        message_show = data_state['message_show']
        edit_message = message_show[str(question.id)]

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
                                              args=(session, bot, state, admin, telegram_id, question))
            await state.update_data({'scheduler_job_id': scheduler_job.id})

    return None, None


# level = 24 и 27
async def def_list_out_one_question_parents(message: types.Message,
                                            bot: Bot,
                                            session: AsyncSession,
                                            state: FSMContext,
                                            menu_name: str,
                                            level: int,
                                            level_back: int,
                                            type_message: int,
                                            id_question: int,
                                            admin: bool,
                                            ):
    """ выдает список вопросов для одной ветки переписки: первый прародитель, затем все дочки.
    Последнее сообщение с меню"""
    if admin == False and menu_name == 'answeradmin':
        # пришел ответ от администратора
        await message.delete()
    if admin and menu_name == 'questionuser':
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
                                        bot=bot,
                                        state=state,
                                        level=level-1,
                                        questions=out_question,
                                        type_message=type_message,
                                        level_back=level_back,
                                        admin=admin)
