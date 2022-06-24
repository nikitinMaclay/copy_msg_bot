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


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

moderator_access = {
    "api_id": 0,
    "api_hash": "",
    "phone_number": "",
    "code": "",
    "group": ""
}

moderator_api = None
last_message = ""
moderator_id = 0
all_messages_base = {
    0: types.Message
}


@dp.message_handler(commands=['start'])
async def reg(message: types.Message):
    message_for_reg = "Пройдите регистрацию по ссылке: \nhttps://my.telegram.org\n" \
                      "Вот гайд, если не разберетесь: \n" \
                      "https://tlgrm.ru/docs/api/obtaining_api_id\n\n" \
                      "Если прошли регистрацию, нажмите кнопку  ⬇  "
    await bot.send_message(message.from_user.id, f"Привет! {message_for_reg}", reply_markup=menu_markup_for_reg)


@dp.message_handler(content_types=["text"])
async def receive_message(message: types.Message):
    global last_message
    last_message = message


@dp.callback_query_handler(text="continue")
async def login(query: CallbackQuery):
    global last_message
    await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                        message_id=query.message.message_id,
                                        reply_markup=None)
    await bot.send_message(query.from_user.id, "Введите api_id", reply_markup=markup_continue_after_id)


@dp.callback_query_handler(text="continue_id")
async def login(query: CallbackQuery):
    global last_message
    if last_message["text"].isdigit() and len(last_message["text"]) in range(7, 9):
        moderator_access["api_id"] = int(last_message["text"])
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
    global last_message
    if last_message["text"].isalnum() and len(last_message["text"]) == 32:
        moderator_access["api_hash"] = last_message["text"]
        await bot.send_message(query.from_user.id, "api_hash принят")
        time.sleep(0.5)
        await bot.send_message(query.from_user.id, "Введите номер телефона", reply_markup=markup_continue_after_phone)
    else:
        await bot.send_message(query.from_user.id, "Формат введеных данных не верен\nВведите api_hash повторно",
                               reply_markup=markup_continue_after_hash_reload)
    await bot.delete_message(chat_id=query.from_user.id,
                             message_id=query.message.message_id)


@dp.callback_query_handler(text="continue_phone")
async def login(query: CallbackQuery):
    global last_message, moderator_api
    if last_message["text"][1:].isdigit() and len(last_message["text"]) == 12 and "+" in last_message["text"]:
        moderator_access["phone_number"] = last_message["text"]
        moderator_api = API(moderator_access["api_id"], moderator_access["api_hash"], moderator_access["phone_number"])
        start_res = await moderator_api.start()
        if start_res:
            await bot.send_message(query.from_user.id, "Номер телефона принят. Введите полученный код",
                                   reply_markup=markup_receive_code)
        else:
            await bot.send_message(query.from_user.id, "Номер телефона принят. Вы уже авторизованы по коду")
        time.sleep(0.5)
    else:
        await bot.send_message(query.from_user.id, "Формат введеных данных не верен\nВведите номер телефона повторно",
                               reply_markup=markup_continue_after_phone_reload)
    await bot.delete_message(chat_id=query.from_user.id,
                             message_id=query.message.message_id)


@dp.callback_query_handler(text="receive_code")
async def login(query: CallbackQuery):
    global last_message, moderator_api, moderator_id
    if last_message["text"].isdigit() and len(last_message["text"]) == 5:
        moderator_access["code"] = last_message["text"]
        await bot.send_message(query.from_user.id, "Код подтверждения принят!")
        login_res = await moderator_api.login(moderator_access["code"])
        if login_res:
            await bot.send_message(query.from_user.id, "Авторизация успешна! Введите ссылку на группу",
                                   reply_markup=markup_continue_after_group)
            moderator_id = query.from_user.id
        else:
            await bot.send_message(query.from_user.id, "Не тот код!\nВведите"
                                                       " код подтверждения повторно",
                                   reply_markup=markup_receive_code_reload)
            await moderator_api.code_again()
    else:
        await bot.send_message(query.from_user.id, "Формат введеных данных не верен\nВведите"
                                                   " код подтверждения повторно",
                               reply_markup=markup_receive_code_reload)
    await bot.delete_message(chat_id=query.from_user.id,
                             message_id=query.message.message_id)


@dp.callback_query_handler(text="continue_group")
async def login(query: CallbackQuery):
    global last_message, moderator_api
    if "http" in last_message["text"]:
        moderator_access["group"] = last_message["text"]
        get_chat_res = await moderator_api.get_chat(moderator_access["group"])
        await bot.send_message(query.from_user.id, "Ссылка принята!")
        if get_chat_res:
            await bot.send_message(query.from_user.id, "Бот начал работу!")
            await moderator_api.parse(limit=20)
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
    global moderator_api
    # Жесть, я решение забыл. Я сидел уже придумал и просто забыл. Завтра вспомню наверное
    await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                        message_id=query.message.message_id,
                                        reply_markup=None)


@dp.callback_query_handler(text="decline_message")
async def decline(query: CallbackQuery):
    global last_message, moderator_api
    await bot.delete_message(chat_id=query.from_user.id,
                             message_id=query.message.message_id)


async def main_sender(moder_id, timer=120):
    global moderator_api
    while True:
        try:
            result = await moderator_api.parse()
            time.sleep(10)
            for msg in result:
                all_messages_base[msg.from_id.user_id] = msg
                res_msg = f"Сообщение:\n" \
                          f"{msg.message}"
                # Берем id этого сообщения и засовываем как ключ в all_msgs_base или user_id, мозг не работает уже
                await bot.send_message(moder_id, res_msg, reply_markup=markup_accept_message)
                time.sleep(10)

            time.sleep(timer + 60)
        except:
            traceback.format_exc()
            print(Fore.RED + f'API модера {moder_id}. Бот упал во время работы')

if __name__ == "__main__":
    executor.start_polling(dp)
