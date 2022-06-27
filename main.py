import asyncio
import random
import time
import traceback
from colorama import Fore
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from config import TOKEN
from aiogram.types.callback_query import CallbackQuery
from mark_ups import menu_markup_for_reg, markup_continue_after_id, markup_continue_after_hash, markup_receive_code,\
    markup_continue_after_id_reload, markup_continue_after_hash_reload, markup_continue_after_phone, \
    markup_continue_after_phone_reload, markup_receive_code_reload, markup_continue_after_group, \
    markup_continue_after_group_reload, markup_accept_message
from telegram_parser_api import API
from sql_commands import *


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


class Moder:
    def __init__(self, api: API = API(), user_id: int = random.randrange(-123123, 0), active=False):
        self.api = api
        self.moder_id = user_id
        self.active = active
        self.last_message = ''
        self.all_messages_base = {}

    async def main_sender(self, timer=25):
        while True:
            if self.active:
                overall_time = 0
                try:
                    for chat in self.api.target_group:
                        result = await self.api.parse(chat, limit=15)
                        await asyncio.sleep(5)
                        for msg in result:
                            res_msg = f"Сообщение:\n" \
                                      f"{msg.message}"
                            my_message = await bot.send_message(self.moder_id, res_msg,
                                                                reply_markup=markup_accept_message)
                            self.all_messages_base[my_message.message_id] = msg
                            await asyncio.sleep(1)
                        overall_time += timer
                        print(overall_time)
                        await asyncio.sleep(timer)
                    await asyncio.sleep(60)
                except:
                    print(traceback.format_exc())
                    print(Fore.RED + f'API модера {self.moder_id}. Бот упал во время работы')


moders = {
    0: Moder()
}


@dp.message_handler(commands=['add_group'])
async def reg(message: types.Message):
    print(message)
    message_for_reg = "Введите ссылку на группу"
    await bot.send_message(message.from_user.id, f"{message_for_reg}", reply_markup=markup_continue_after_group)


@dp.message_handler(commands=['start'])
async def reg(message: types.Message):
    print(message)
    user = message.from_user
    moder = get_user(user.username)
    if moder:
        moders[user.id] = Moder(API(moder[2], moder[3], moder[4]), user.id)
        moders[user.id].moder_id = user.id
        Moder()
        start_res = await moders[user.id].api.start()
        if start_res:
            await bot.send_message(message.from_user.id, "Введите полученный код в формате code_xxxxx",
                                   reply_markup=markup_receive_code)
        else:
            await bot.send_message(message.from_user.id, "Вы уже авторизованы по коду\nЧтобы добавить группу введите\n"
                                                         "/add_group",
                                   reply_markup=markup_continue_after_group)
            moders[user.id].active = True
        time.sleep(0.5)
    else:
        moders[user.id] = Moder()
        moders[user.id].moder_id = user.id
        message_for_reg = "Разработчики проекта: @Mikhai_Maclay и @crazysadboi\n" \
                          "Пройдите регистрацию по ссылке: \nhttps://my.telegram.org\n" \
                          "Вот гайд, если не разберетесь: \n" \
                          "https://tlgrm.ru/docs/api/obtaining_api_id\n\n" \
                          "Если прошли регистрацию, нажмите кнопку  ⬇  "
        await bot.send_message(message.from_user.id, f"Привет!\n {message_for_reg}", reply_markup=menu_markup_for_reg)


@dp.message_handler(content_types=["text"])
async def receive_message(message: types.Message):
    moders[message.from_user.id].last_message = message


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
            len(last_message) == 12 and\
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


@dp.callback_query_handler(text="continue_group")
async def login(query: CallbackQuery):
    last_message = moders[query.from_user.id].last_message.text
    if "http" in last_message:
        get_chat_res = await moders[query.from_user.id].api.get_chat(last_message)
        await bot.send_message(query.from_user.id, "Ссылка принята!")
        if get_chat_res:
            await bot.send_message(query.from_user.id, "Бот начал работу!")
            await bot.send_message(query.from_user.id, "Чтобы отправить больше ссылок на группы, "
                                                       "вызовите команду /add_group")
            if moders[query.from_user.id].api.target_group:
                moders[query.from_user.id].active = True
            await moders[query.from_user.id].main_sender()
        else:
            await bot.send_message(query.from_user.id, "Чат не найден. Проверьте, что вы находитесь в этой группе!\n"
                                                       "И что группа существует!",
                                   reply_markup=markup_continue_after_group_reload)
    else:
        await bot.send_message(query.from_user.id, "Формат введеных данных не верен\nВведите"
                                                   " ссылку на группу повторно",
                               reply_markup=markup_continue_after_group_reload)
    await bot.delete_message(chat_id=query.from_user.id,
                             message_id=query.message.message_id)


@dp.callback_query_handler(text="accept_message")
async def accept(query: CallbackQuery):
    msg = moders[query.from_user.id].all_messages_base[query.message.message_id]
    username = await moders[query.from_user.id].api.client.get_entity(msg.from_id)
    await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                        message_id=query.message.message_id,
                                        reply_markup=None)
    if username.username is not None:
        await bot.edit_message_text(f"@{username.username}\n"
                                    f"Сообщение:\n"
                                    f"{msg.message}", message_id=query.message.message_id, chat_id=query.from_user.id)
    else:
        await bot.edit_message_text(f"Пользователь пользуется закрытым аккаунтом\n"
                                    f"Сообщение:\n"
                                    f"{msg.message}", message_id=query.message.message_id, chat_id=query.from_user.id)


@dp.callback_query_handler(text="decline_message")
async def decline(query: CallbackQuery):
    await bot.delete_message(chat_id=query.from_user.id,
                             message_id=query.message.message_id)


if __name__ == "__main__":
    executor.start_polling(dp)
