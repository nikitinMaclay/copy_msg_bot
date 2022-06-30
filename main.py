import asyncio
import datetime
import random
import time
import traceback
from colorama import Fore
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN
from aiogram.types.callback_query import CallbackQuery
from mark_ups import menu_markup_for_reg, markup_continue_after_id, markup_continue_after_hash, markup_receive_code,\
    markup_continue_after_id_reload, markup_continue_after_hash_reload, markup_continue_after_phone, \
    markup_continue_after_phone_reload, markup_receive_code_reload, markup_continue_after_group, \
    markup_accept_message, markup_menu
from telegram_parser_api import API
from sql_commands import *

ADMIN = 508537898
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class Moder:
    def __init__(self, api: API = API(), user_id: int = random.randrange(-123123, 0), active=False):
        self.api = api
        self.moder_id = user_id
        self.active = active
        self.last_message = ''
        self.users = []
        self.username = ''
        self.all_messages_base = {}
        self.counter = 0
        self.flag = True

    async def main_sender(self, timer=25):
        while True:
            if self.moder_id == ADMIN:
                offset = datetime.timezone(datetime.timedelta(hours=3))
                t = datetime.datetime.now(offset)
                if t.hour == 23 and t.minute == 0:
                    final_message = ''
                    for moder in moders:
                        final_message += f"Отчёт за день:\nМенеджер: @{moder.username}:\n" \
                                         f"Количество пользователей, которым написал модератор: {len(moder.users)}\n" \
                                         f"Пользователи: "
                        for u in moder.users:
                            final_message += f"@{u} "
                        final_message += '\n'
                    await bot.send_message(ADMIN, final_message)
                    await asyncio.sleep(60)
            if self.active:
                print(self.username, f"{datetime.datetime.now().hour}:{datetime.datetime.now().minute}")
                if datetime.datetime.now().minute == 59:
                    self.flag = True
                if datetime.datetime.now().minute == 0 and self.flag:
                    await bot.send_message(self.moder_id, f'Принято сообщений сегодня: {self.counter}')
                    await self.api.client.disconnect()
                    await asyncio.sleep(5)
                    await self.api.client.connect()
                    self.flag = False
                try:
                    for chat in self.api.target_group:
                        result = await self.api.parse(chat, limit=15)
                        if result == 0:
                            res_msg = f'Чат {chat.title} недоступен. Он удален из очереди.\n\n' \
                                      f'Попробуйте добавить его еще раз'
                            my_message = await bot.send_message(self.moder_id, res_msg)
                            self.api.target_group.remove(chat)
                            print(self.moder_id, my_message.text)
                        else:
                            await asyncio.sleep(5)
                            for msg in result:
                                res_msg = f'Чат: <a href="https://t.me/{chat.username}">{chat.title}</a>\n' \
                                          f'Сообщение:\n' \
                                          f'{msg.message}'
                                my_message = await bot.send_message(self.moder_id, res_msg,
                                                                    reply_markup=markup_accept_message,
                                                                    parse_mode=types.ParseMode.HTML,
                                                                    disable_web_page_preview=True)
                                self.all_messages_base[my_message.message_id] = {
                                    "from_id": msg.from_id,
                                    "message": msg.message
                                }
                                print([int(self.moder_id),
                                       int(my_message.message_id),
                                       int(msg.from_id.user_id),
                                       str(msg.message)])
                                add_all_messages([int(self.moder_id),
                                                  int(my_message.message_id),
                                                  int(msg.from_id.user_id),
                                                  str(msg.message)
                                                  ])
                                await asyncio.sleep(1)
                            await asyncio.sleep(timer)
                    await asyncio.sleep(60)
                except:
                    print(traceback.format_exc())
                    print(Fore.RED + f'API модера {self.moder_id}. Бот упал во время работы')
            else:
                await asyncio.sleep(timer)


moders = {
    0: Moder()
}


class AddGroup(StatesGroup):
    waiting_for_group = State()


async def group_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Отмена')
    await bot.send_message(text="Введите ссылку на группу:", chat_id=message.chat.id, reply_markup=keyboard)
    await AddGroup.waiting_for_group.set()


async def group_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await state.finish()
        await message.answer("Действие отменено", reply_markup=markup_menu)
        return
    if "http" not in message.text.lower():
        await bot.send_message(message.from_user.id, "Формат введеных данных не верен\nВведите"
                                                     " ссылку на группу повторно")
        await bot.delete_message(chat_id=message.from_user.id,
                                 message_id=message.message_id)
        return
    else:
        # if len(chats) < 10:
        adding = add_group_to_base(username=message.from_user.username, url=message.text)
        print(adding)
        if adding:
            get_chat_res = await moders[message.from_user.id].api.get_chat(message.text)
            if get_chat_res:
                await bot.send_message(message.from_user.id, "Группа принята", reply_markup=markup_menu)
                await state.finish()
                print(get_groups(message.from_user.username))
                await moders[message.from_user.id].main_sender()
            else:
                await bot.send_message(message.from_user.id, "Чат не найден."
                                                             " Проверьте, что вы находитесь в этой группе!\n"
                                                             "И что группа существует!")
                return
        else:
            await bot.send_message(message.from_user.id, "Вы не можете добавить эту группу,"
                                                         " так как она уже отслеживается")
            return
        # else:
        #    await message.answer("Вы достигли лимита по количеству групп.\n"
        #                         "Удалите ненужные вам группы, чтобы добавить новые.", reply_markup=markup_menu)


def register_handlers_add_group(dp: Dispatcher):
    dp.register_message_handler(group_start, Text(equals="Добавить группу", ignore_case=True), state="*")
    dp.register_message_handler(group_start, commands="add_group", state="*")
    dp.register_message_handler(group_chosen, state=AddGroup.waiting_for_group)


class DeleteGroup(StatesGroup):
    waiting_for_delete_group = State()


async def delete_group_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup()
    buttons = []
    if moders[message.from_user.id].api.target_group:
        for chat in moders[message.from_user.id].api.target_group:
            buttons.append(chat.title)
        keyboard.row(*buttons).add('Отмена')
        await bot.send_message(text="Нажмите на группу, которую хотите удалить:",
                               chat_id=message.chat.id, reply_markup=keyboard)
        await DeleteGroup.waiting_for_delete_group.set()
    else:
        msg = "Вы пока что не отслеживаете сообщества, исправьте это нажав кнопку \"Добавить группу\" в меню!"
        await bot.send_message(chat_id=message.chat.id, text=msg, reply_markup=markup_menu)


async def delete_group_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await state.finish()
        await message.answer("Действие отменено", reply_markup=markup_menu)
        return
    try:
        chat_to_delete = message.text
        url = ''
        for chat in moders[message.from_user.id].api.target_group:
            if chat.title.lower() == chat_to_delete.lower():
                url = 'https://t.me/' + chat.username
                chat_to_delete = chat
                break
        delete = delete_group_from_base(url)
        if delete:
            await bot.send_message(message.from_user.id, "Группа удалена", reply_markup=markup_menu)
            moders[message.from_user.id].api.target_group.remove(chat_to_delete)
            await state.finish()
            await moders[message.from_user.id].main_sender()
    except:
        print(traceback.format_exc())
        await bot.send_message(message.from_user.id, "Пожалуйста, выберите одну из кнопок")
        await bot.delete_message(chat_id=message.from_user.id,
                                 message_id=message.message_id)
        return


def register_handlers_delete_group(dp: Dispatcher):
    dp.register_message_handler(delete_group_start, Text(equals="Удалить группу", ignore_case=True), state="*")
    dp.register_message_handler(delete_group_start, commands="delete_group", state="*")
    dp.register_message_handler(delete_group_chosen, state=DeleteGroup.waiting_for_delete_group)


@dp.message_handler(commands=['menu'])
async def menu(message: types.Message):
    await bot.send_message(message.from_user.id, "Меню открыто", reply_markup=markup_menu)


@dp.message_handler(commands=['start'])
async def reg(message: types.Message):
    print(message)
    user = message.from_user
    moder = get_user(user.username)
    if moder:
        await bot.send_message(message.from_user.id, "Подождите, идет подключение...")
        moders[user.id] = Moder(API(moder[2], moder[3], moder[4]), user.id)
        moders[user.id].moder_id = user.id
        moders[user.id].username = user.username
        msgs = get_all_messages(user.id)
        if msgs:
            for msg in msgs:
                moders[user.id].all_messages_base[int(msg[1])] = {
                    "from_id": int(msg[2]),
                    "message": str(msg[3])
                }
        print(moders[user.id].all_messages_base)
        start_res = await moders[user.id].api.start()
        for chat in get_groups(user.username):
            await moders[user.id].api.get_chat(chat)
        print(moders[user.id].api.target_group)
        if start_res:
            await bot.send_message(message.from_user.id, "Введите полученный код в формате code_xxxxx",
                                   reply_markup=markup_receive_code)
        else:
            await bot.send_message(message.from_user.id, "Вы уже авторизованы по коду", reply_markup=markup_menu)
            moders[user.id].active = True
            await moders[user.id].main_sender()
        time.sleep(0.5)
    else:
        moders[user.id] = Moder()
        moders[user.id].moder_id = user.id
        moders[user.id].username = user.username
        message_for_reg = "Разработчики проекта: @Mikhai_Maclay и @crazysadboi\n" \
                          "Пройдите регистрацию по ссылке: \nhttps://my.telegram.org\n" \
                          "Вот гайд, если не разберетесь: \n" \
                          "https://tlgrm.ru/docs/api/obtaining_api_id\n\n" \
                          "Если прошли регистрацию, нажмите кнопку  ⬇  "
        await bot.send_message(message.from_user.id, f"Привет!\n {message_for_reg}", reply_markup=menu_markup_for_reg)


@dp.message_handler(content_types=["text"])
async def receive_message(message: types.Message):
    try:
        moders[message.from_user.id].last_message = message
    except KeyError:
        await bot.send_message(chat_id=message.chat.id, text='Вы не в системе, пожалуйста нажмите на команду:\n'
                                                             '/start')
    if message.from_user.id in moders.keys():
        if message.text == 'Скрыть меню':
            await bot.send_message(chat_id=message.chat.id, text='Меню скрыто, чтобы открыть меню нажмите на команду:\n'
                                                                 '/menu', reply_markup=types.ReplyKeyboardRemove())
        if message.text == 'Добавить группу':
            await group_start(message)
        if message.text == 'Список групп':
            chats = moders[message.from_user.id].api.target_group
            if chats:
                msg = "Сообщества отслеживаемые вами:\n\n"
                i = 1
                for chat in chats:
                    msg += str(i) + '. ' + f'<a href="https://t.me/{chat.username}">{chat.title}</a>\n'
                    i += 1
                await bot.send_message(chat_id=message.chat.id, text=msg, parse_mode=types.ParseMode.HTML,
                                       disable_web_page_preview=True)
            else:
                msg = "Вы пока что не отслеживаете сообщества, исправьте это нажав кнопку \"Добавить группу\" в меню!"
                await bot.send_message(chat_id=message.chat.id, text=msg)
        if message.text == 'Удалить группу':
            await delete_group_start(message)
        if message.text == 'Включить/Выключить бота':
            if moders[message.from_user.id].active:
                msg = "Бот выключен!"
                await bot.send_message(chat_id=message.chat.id, text=msg)
                moders[message.from_user.id].active = False
            else:
                msg = "Бот включен!"
                await bot.send_message(chat_id=message.chat.id, text=msg)
                moders[message.from_user.id].active = True
        if message.text == 'Отчет':
            await bot.send_message(message.from_user.id,
                                   f'Принято сообщений сегодня: '
                                   f'{moders[message.from_user.id].counter}\n')
            if moders[message.from_user.id].counter >= 38:
                await bot.send_message(message.from_user.id,
                                       f'Норма выполнена! Бот выключен')
                moders[message.from_user.id].active = False
                moders[message.from_user.id].counter = 0


@dp.callback_query_handler(text="continue")
async def login(query: CallbackQuery):
    await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                        message_id=query.message.message_id,
                                        reply_markup=None)
    await bot.send_message(query.from_user.id, "Введите api_id", reply_markup=markup_continue_after_id)


@dp.callback_query_handler(text="continue_id")
async def login(query: CallbackQuery):
    if moders[query.from_user.id].last_message.text.isdigit() and\
            len(moders[query.from_user.id].last_message.text) in range(7, 9):
        moders[query.from_user.id].api.api_id = int(moders[query.from_user.id].last_message.text)
        await bot.send_message(query.from_user.id, "api_id принят")
        time.sleep(0.5)
        await bot.send_message(query.from_user.id, "Введите api_hash", reply_markup=markup_continue_after_hash)
    else:
        await bot.send_message(query.from_user.id, "Формат введеных данных не верен\nВведите api_id повторно",
                               reply_markup=markup_continue_after_id_reload)
    await bot.delete_message(chat_id=query.from_user.id,
                             message_id=query.message.message_id)


@dp.callback_query_handler(text="continue_hash")
async def login(query: CallbackQuery):
    if moders[query.from_user.id].last_message.text.isalnum() and\
            len(moders[query.from_user.id].last_message.text) == 32:
        moders[query.from_user.id].api.api_hash = moders[query.from_user.id].last_message.text
        await bot.send_message(query.from_user.id, "api_hash принят")
        time.sleep(0.5)
        await bot.send_message(query.from_user.id, "Введите номер телефона в формате +xxxxxxxxxxx",
                               reply_markup=markup_continue_after_phone)
    else:
        await bot.send_message(query.from_user.id, "Формат введеных данных не верен\nВведите api_hash повторно",
                               reply_markup=markup_continue_after_hash_reload)
    await bot.delete_message(chat_id=query.from_user.id,
                             message_id=query.message.message_id)


@dp.callback_query_handler(text="continue_phone")
async def login(query: CallbackQuery):
    last_message = moders[query.from_user.id].last_message.text
    if last_message[1:].isdigit() and\
            "+" in last_message:
        moders[query.from_user.id].api.phone = last_message
        start_res = await moders[query.from_user.id].api.start()
        if start_res:
            await bot.send_message(query.from_user.id, "Номер телефона принят. Введите полученный "
                                                       "код в формате code_xxxxx",
                                   reply_markup=markup_receive_code)
        else:
            await bot.send_message(query.from_user.id, "Номер телефона принят. Вы уже авторизованы по коду\n"
                                                       "Введите ссылку на группу",
                                   reply_markup=markup_continue_after_group)
            moder = moders[query.from_user.id]
            add_user_to_base([query.from_user.username, moder.api.api_id, moder.api.api_hash, moder.api.phone])
        time.sleep(0.5)
    else:
        await bot.send_message(query.from_user.id, "Формат введеных данных не верен\nВведите номер телефона повторно",
                               reply_markup=markup_continue_after_phone_reload)
    await bot.delete_message(chat_id=query.from_user.id,
                             message_id=query.message.message_id)


@dp.callback_query_handler(text="receive_code")
async def login(query: CallbackQuery):
    check_msg = moders[query.from_user.id].last_message.text.split("_")[-1]
    if check_msg.isdigit() and len(check_msg) == 5:
        print(check_msg)
        await bot.send_message(query.from_user.id, "Код подтверждения принят!")
        login_res = await moders[query.from_user.id].api.login(check_msg)
        if login_res:
            await bot.send_message(query.from_user.id, "Авторизация успешна! Введите ссылку на группу",
                                   reply_markup=markup_continue_after_group)
            if moders[query.from_user.id].api.target_group:
                moders[query.from_user.id].active = True
            moder = moders[query.from_user.id]
            add_user_to_base([query.from_user.username, moder.api.api_id, moder.api.api_hash, moder.api.phone])
        else:
            await bot.send_message(query.from_user.id, "Не тот код!\nВведите"
                                                       " код подтверждения повторно",
                                   reply_markup=markup_receive_code_reload)
            await moders[query.from_user.id].api.code_again()
    else:
        await moders[query.from_user.id].api.code_again()
        await bot.send_message(query.from_user.id, "Формат введеных данных не верен\nВведите"
                                                   " код подтверждения повторно",
                               reply_markup=markup_receive_code_reload)
    await bot.delete_message(chat_id=query.from_user.id,
                             message_id=query.message.message_id)


@dp.callback_query_handler(text="accept_message")
async def accept(query: CallbackQuery):
    msg = moders[query.from_user.id].all_messages_base[query.message.message_id]
    try:
        username = await moders[query.from_user.id].api.client.get_entity(msg["from_id"])
        await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                            message_id=query.message.message_id,
                                            reply_markup=None)
        print(query.message)
        chats = moders[query.from_user.id].api.target_group
        chat = None
        for c in chats:
            if c.title in query.message.text:
                chat = c
                break

        if username.username is not None:
            moders[query.from_user.id].users.append(username.username)
            moders[query.from_user.id].counter += 1
            if chat:
                res_msg = f'@{username.username}\n'\
                          f'Чат: <a href="https://t.me/{chat.username}">{chat.title}</a>\n' \
                          f'Сообщение:\n' \
                          f'{msg["message"]}'
            else:
                res_msg = f'@{username.username}\n' \
                          f'{query.message.text}'
            await bot.edit_message_text(text=res_msg,
                                        message_id=query.message.message_id, chat_id=query.from_user.id,
                                        parse_mode=types.ParseMode.HTML, disable_web_page_preview=True,
                                        entities=query.message.entities)
            if moders[query.from_user.id].counter == 35:
                await bot.send_message(moders[query.from_user.id].moder_id, f'Достигли лимита по открытию 35 контактов')
            if moders[query.from_user.id].counter >= 38:
                await bot.send_message(moders[query.from_user.id].moder_id,
                                       f'Принято сообщений сегодня: {moders[query.from_user.id].counter}\n'
                                       f'Норма выполнена! Бот выключен')
                moders[query.from_user.id].active = False
        else:
            res_msg = f'Пользователь пользуется закрытым аккаунтом\n' \
                      f'Чат: <a href="https://t.me/{chat.username}">{chat.title}</a>\n' \
                      f'Сообщение:\n' \
                      f'{msg.message}'
            await bot.edit_message_text(text=res_msg,
                                        message_id=query.message.message_id, chat_id=query.from_user.id,
                                        parse_mode=types.ParseMode.HTML, disable_web_page_preview=True,
                                        entities=query.message.entities)
    except:
        await bot.edit_message_text(f"Пользователь пользуется закрытым аккаунтом\n{query.message.text}",
                                    message_id=query.message.message_id, chat_id=query.from_user.id,
                                    parse_mode=types.ParseMode.HTML, disable_web_page_preview=True,
                                    entities=query.message.entities)


@dp.callback_query_handler(text="decline_message")
async def decline(query: CallbackQuery):
    await bot.delete_message(chat_id=query.from_user.id,
                             message_id=query.message.message_id)


if __name__ == "__main__":
    register_handlers_add_group(dp)
    register_handlers_delete_group(dp)
    executor.start_polling(dp)
