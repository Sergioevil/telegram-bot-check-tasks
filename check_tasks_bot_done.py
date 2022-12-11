from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, Dispatcher, executor, types
import re
from admins import auth_list
import sqlite3 as sq
import config

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

menu_button1 = InlineKeyboardButton('Далее', callback_data='check_task')
inline_kb1 = InlineKeyboardMarkup().add(menu_button1)

menu_button3 = InlineKeyboardButton('🔁 Обновить', callback_data='check_task')
inline_kb3 = InlineKeyboardMarkup().add(menu_button3)


def get_data():
    base = sq.connect('./cool.db')
    cur = base.cursor()
    cur.execute("SELECT * FROM main WHERE checked = ?", (0,))
    data = cur.fetchone()
    base.commit()
    base.close()
    if data:
        return data
    return None


@dp.message_handler(commands=['start'])
async def create_offer_start(message: types.Message):
    if str(message.chat.id) not in auth_list:
        await message.answer('Нет доступа 🚫')
        return
    global msg1
    msg1 = await message.answer(text="""Добрый день!\nЧтобы приступить к модерации задач, нажмите далее""", reply_markup=inline_kb1)


@dp.callback_query_handler(lambda call:call.data == 'ok')
async def all_ok(callback_query: types.CallbackQuery):
    # Check admin rights
    if str(callback_query.message.chat.id) not in auth_list:
        await bot.send_message(callback_query.message.chat.id, 'Нет доступа 🚫')
        return

    global update_msg, task_msk
    data_from_getting = get_data()
    if data_from_getting:
        n, name, description, tg_id, tag, checked, to_1, to_2, link, message_id, message_id_pro = data_from_getting
        text_error = ''
        if not tag:
            text_error+="Укажите тематику задачи!"
        if to_1 == 0 and to_2 == 0:
            if text_error:
                text_error+="\n\nТакже необходимо указать тип канала!"
            else:
                text_error+="Укажите тип канала!"
        if text_error:
            await bot.answer_callback_query(callback_query.id, show_alert=True, text=text_error)
            return
        base = sq.connect('./cool.db')
        cur = base.cursor()
        try:
            cur.execute("UPDATE main SET checked = 1 WHERE id = ?;", (n,))
        except:
            await bot.send_message(callback_query.message.chat.id, 'Обновили сервера, перезапустите сервис с помощью команды /start')
            return
        base.commit()
        base.close()

        # Данные для нового сообщения

        data_from_getting = get_data()
        if data_from_getting:
            n, name, description, tg_id, tag, checked, to_1, to_2, link, message_id, message_id_pro = data_from_getting
            buttons_tags = [
                InlineKeyboardButton(f'В общий канал{" ✓" if to_1 == 1 else ""}', callback_data='to_1'),
                InlineKeyboardButton(f'В премиум канал{" ✓" if to_2 == 1 else ""}', callback_data='to_2'),
                ]

            inline_kb2 = InlineKeyboardMarkup()
            inline_kb2.add(InlineKeyboardButton(f'Разработка{" ✓" if tag == "разработка" else ""}', callback_data='разработка'))
            inline_kb2.row(InlineKeyboardButton(f'Cайты{" ✓" if tag == "сайты" else ""}', callback_data='сайты'),
                InlineKeyboardButton(f'Дизайн{" ✓" if tag == "дизайн" else ""}', callback_data='дизайн')).row(
                    InlineKeyboardButton(f'Копирайтинг{" ✓" if tag == "копирайтинг" else ""}', callback_data='копирайтинг'),
                InlineKeyboardButton(f'Маркетинг{" ✓" if tag == "маркетинг" else ""}', callback_data='маркетинг'))

            for i in buttons_tags:
                inline_kb2.add(i)
            inline_kb2.row(
                InlineKeyboardButton('Отклонить ❌', callback_data='not_ok'),
                InlineKeyboardButton('Готово ✅', callback_data='ok'))
            if link:
                await task_msk.edit_text(f"""<b>{name}</b>\n\n{description}\n\n<a href='{link}'>Связаться с заказчиком</a>""", parse_mode='HTML', reply_markup=inline_kb2)
            elif tg_id:
                task_msk = await bot.send_message(callback_query.message.chat.id,f"""<b>{name}</b>\n\n{description}\n\n<a href='https://telegram.me/#{id}'>Связаться с заказчиком</a>""", parse_mode='HTML', reply_markup=inline_kb2)
        else:
            try:
                await task_msk.delete()
            except:
                pass
            update_msg = await bot.send_message(callback_query.message.chat.id, 'Все задачи проверены', reply_markup=inline_kb3)
    else:
        try:
            await task_msk.delete()
        except:
            pass
        update_msg = await bot.send_message(callback_query.message.chat.id, 'Все задачи проверены', reply_markup=inline_kb3)



@dp.callback_query_handler(lambda call:call.data in ['to_1', 'to_2'])
async def to_2(callback_query: types.CallbackQuery):
    # Check admin rights
    if str(callback_query.message.chat.id) not in auth_list:
        await bot.send_message(callback_query.message.chat.id, 'Нет доступа 🚫')
        return

    global n, update_msg, task_msk
    n, name, description, tg_id, tag, checked, to_1, to_2, link, message_id, message_id_pro = get_data()
    base = sq.connect("./cool.db")
    cur = base.cursor()
    if callback_query.data == 'to_1':
        if to_1 == 1:
            cur.execute("UPDATE main SET to_1 = 0 WHERE id = ?;", (n,))
            to_1 = 0
        else:
            cur.execute("UPDATE main SET to_1 = 1 WHERE id = ?;", (n,))
            to_1 = 1
    if callback_query.data == 'to_2':
        if to_2 == 1:
            cur.execute("UPDATE main SET to_2 = 0 WHERE id = ?;", (n,))
            to_2 = 0
        else:
            cur.execute("UPDATE main SET to_2 = 1 WHERE id = ?;", (n,))
            to_2 = 1
    base.commit()
    base.close()
    buttons_tags = [
        InlineKeyboardButton(f'В общий канал{" ✓" if to_1 == 1 else ""}', callback_data='to_1'),
        InlineKeyboardButton(f'В премиум канал{" ✓" if to_2 == 1 else ""}', callback_data='to_2'),
        ]

    inline_kb2 = InlineKeyboardMarkup()
    inline_kb2.add(InlineKeyboardButton(f'Разработка{" ✓" if tag == "разработка" else ""}', callback_data='разработка'))
    inline_kb2.row(InlineKeyboardButton(f'Cайты{" ✓" if tag == "сайты" else ""}', callback_data='сайты'),
        InlineKeyboardButton(f'Дизайн{" ✓" if tag == "дизайн" else ""}', callback_data='дизайн')).row(
            InlineKeyboardButton(f'Копирайтинг{" ✓" if tag == "копирайтинг" else ""}', callback_data='копирайтинг'),
        InlineKeyboardButton(f'Маркетинг{" ✓" if tag == "маркетинг" else ""}', callback_data='маркетинг'))

    for i in buttons_tags:
        inline_kb2.add(i)
    inline_kb2.row(
        InlineKeyboardButton('Отклонить ❌', callback_data='not_ok'),
        InlineKeyboardButton('Готово ✅', callback_data='ok'))
    await task_msk.edit_reply_markup(reply_markup=inline_kb2)
    

@dp.callback_query_handler(lambda call:call.data == 'not_ok')
async def not_ok(callback_query: types.CallbackQuery):
    # Check admin rights
    if str(callback_query.message.chat.id) not in auth_list:
        await bot.send_message(callback_query.message.chat.id, 'Нет доступа 🚫')
        return

    global n, update_msg, task_msk
    base = sq.connect('./cool.db')
    cur = base.cursor()
    cur.execute("DELETE FROM main WHERE id = ?;", (n,))
    base.commit()
    base.close()
    data_from_getting = get_data()
    try:
        await update_msg.delete()
    except:
        pass
    try:
        await task_msk.delete()
    except:
        pass
    if data_from_getting:
        n, name, description, tg_id, tag, checked, to_1, to_2, link, message_id, message_id_pro = get_data()
        buttons_tags = [
        InlineKeyboardButton(f'В общий канал{" ✓" if to_1 == 1 else ""}', callback_data='to_1'),
        InlineKeyboardButton(f'В премиум канал{" ✓" if to_2 == 1 else ""}', callback_data='to_2'),
            ]

        inline_kb2 = InlineKeyboardMarkup()
        inline_kb2.add(InlineKeyboardButton(f'Разработка{" ✓" if tag == "разработка" else ""}', callback_data='разработка'))
        inline_kb2.row(InlineKeyboardButton(f'Cайты{" ✓" if tag == "сайты" else ""}', callback_data='сайты'),
            InlineKeyboardButton(f'Дизайн{" ✓" if tag == "дизайн" else ""}', callback_data='дизайн')).row(
                InlineKeyboardButton(f'Копирайтинг{" ✓" if tag == "копирайтинг" else ""}', callback_data='копирайтинг'),
            InlineKeyboardButton(f'Маркетинг{" ✓" if tag == "маркетинг" else ""}', callback_data='маркетинг'))

        for i in buttons_tags:
            inline_kb2.add(i)
        inline_kb2.row(
            InlineKeyboardButton('Отклонить ❌', callback_data='not_ok'),
            InlineKeyboardButton('Готово ✅', callback_data='ok'))
        if link:
            task_msk = await bot.send_message(callback_query.message.chat.id,f"""<b>{name}</b>\n\n{description}\n\n<a href='{link}'>Связаться с заказчиком</a>""", parse_mode='HTML', reply_markup=inline_kb2)
        elif tg_id:
            task_msk = await bot.send_message(callback_query.message.chat.id,f"""<b>{name}</b>\n\n{description}\n\n<a href='tg://user?id={tg_id}'>Связаться с заказчиком</a>""", parse_mode='HTML', reply_markup=inline_kb2)
    else:
        update_msg = await bot.send_message(callback_query.message.chat.id, 'Все задачи проверены', reply_markup=inline_kb3)


@dp.callback_query_handler(lambda call:call.data == 'check_task')
async def process_callback_button_verif(callback_query: types.CallbackQuery):
    # Check admin rights
    if str(callback_query.message.chat.id) not in auth_list:
        await bot.send_message(callback_query.message.chat.id, 'Нет доступа 🚫')
        return

    global n, update_msg, task_msk, msg1
    try:
        await update_msg.delete()
    except:
        pass
    data_from_getting = get_data()
    if data_from_getting:
        n, name, description, tg_id, tag, checked, to_1, to_2, link, message_id, message_id_pro = data_from_getting
        try:
            await msg1.delete()
        except:
            pass
        try:
            await task_msk.delete()
        except:
            pass
        
        n, name, description, tg_id, tag, checked, to_1, to_2, link, message_id, message_id_pro = data_from_getting
        buttons_tags = [
            InlineKeyboardButton(f'В общий канал{" ✓" if to_1 == 1 else ""}', callback_data='to_1'),
            InlineKeyboardButton(f'В премиум канал{" ✓" if to_2 == 1 else ""}', callback_data='to_2'),
            ]

        inline_kb2 = InlineKeyboardMarkup()
        inline_kb2.add(InlineKeyboardButton(f'Разработка{" ✓" if tag == "разработка" else ""}', callback_data='разработка'))
        inline_kb2.row(InlineKeyboardButton(f'Cайты{" ✓" if tag == "сайты" else ""}', callback_data='сайты'),
            InlineKeyboardButton(f'Дизайн{" ✓" if tag == "дизайн" else ""}', callback_data='дизайн')).row(
                InlineKeyboardButton(f'Копирайтинг{" ✓" if tag == "копирайтинг" else ""}', callback_data='копирайтинг'),
            InlineKeyboardButton(f'Маркетинг{" ✓" if tag == "маркетинг" else ""}', callback_data='маркетинг'))

        for i in buttons_tags:
            inline_kb2.add(i)
        inline_kb2.row(
            InlineKeyboardButton('Отклонить ❌', callback_data='not_ok'),
            InlineKeyboardButton('Готово ✅', callback_data='ok'))
        if link:
            task_msk = await bot.send_message(callback_query.message.chat.id,f"""<b>{name}</b>\n\n{description}\n\n<a href='{link}'>Связаться с заказчиком</a>""", parse_mode='HTML', reply_markup=inline_kb2)
        elif tg_id:
            task_msk = await bot.send_message(callback_query.message.chat.id,f"""<b>{name}</b>\n\n{description}\n\n<a href='tg://user?id={tg_id}'>Связаться с заказчиком</a>""", parse_mode='HTML', reply_markup=inline_kb2)

    else:
        await bot.answer_callback_query(callback_query.id, show_alert=False)
        update_msg = await bot.send_message(callback_query.message.chat.id, 'Все задачи проверены', reply_markup=inline_kb3)





@dp.callback_query_handler(lambda call:call.data in ["маркетинг", "копирайтинг", "разработка", "дизайн", "сайты"])
async def to_1(callback_query: types.CallbackQuery):
    # Check admin rights
    if str(callback_query.message.chat.id) not in auth_list:
        await bot.send_message(callback_query.message.chat.id, 'Нет доступа 🚫')
        return

    global n, update_msg, task_msk
    n, name, description, tg_id, tag, checked, to_1, to_2, link, message_id, message_id_pro = get_data()
    if tag == callback_query.data:
        await bot.answer_callback_query(callback_query.id, show_alert=False)
        return
    base = sq.connect('./cool.db')
    cur = base.cursor()
    cur.execute(f'UPDATE main SET tags = ? WHERE id = ?;', (callback_query.data, n))
    base.commit()
    base.close()
    tag = callback_query.data
    buttons_tags = [
        InlineKeyboardButton(f'В общий канал{" ✓" if to_1 == 1 else ""}', callback_data='to_1'),
        InlineKeyboardButton(f'В премиум канал{" ✓" if to_2 == 1 else ""}', callback_data='to_2'),
        ]

    inline_kb2 = InlineKeyboardMarkup()
    inline_kb2.add(InlineKeyboardButton(f'Разработка{" ✓" if tag == "разработка" else ""}', callback_data='разработка'))
    inline_kb2.row(InlineKeyboardButton(f'Cайты{" ✓" if tag == "сайты" else ""}', callback_data='сайты'),
        InlineKeyboardButton(f'Дизайн{" ✓" if tag == "дизайн" else ""}', callback_data='дизайн')).row(
            InlineKeyboardButton(f'Копирайтинг{" ✓" if tag == "копирайтинг" else ""}', callback_data='копирайтинг'),
        InlineKeyboardButton(f'Маркетинг{" ✓" if tag == "маркетинг" else ""}', callback_data='маркетинг'))

    for i in buttons_tags:
        inline_kb2.add(i)
    inline_kb2.row(
        InlineKeyboardButton('Отклонить ❌', callback_data='not_ok'),
        InlineKeyboardButton('Готово ✅', callback_data='ok'))
    await task_msk.edit_reply_markup(reply_markup=inline_kb2)


@dp.errors_handler()
async def message_not_modified_handler(update, error):
    
    try:
        if str(update.callback_query.message.chat.id) not in auth_list:
            await bot.send_message(update.message.chat.id, 'Нет доступа 🚫')
            return
    except:
        pass
    try:
        if str(update.message.chat.id) not in auth_list:
            await bot.send_message(update.message.chat.id, 'Нет доступа 🚫')
            return
    except:
        pass
    try:
        await bot.send_message(update.callback_query.message.chat.id, 'Обновите бота - /start')
    except:
        pass
    try:
        await bot.send_message(update.message.chat.id, 'Обновите бота - /start')
    except:
        pass
    return True


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)




