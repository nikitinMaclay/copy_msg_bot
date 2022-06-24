from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from config import TOKEN
from aiogram.types.callback_query import CallbackQuery
from mark_ups import menu_markup_for_reg, markup_continue_after_id, markup_continue_after_hash, markup_receive_code
from telegram_parser_api import API


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

moderator_access = {
    "api_id": 0,
    "api_hash": "",
    "phone_number": "",
    "code": ""
}

moderator_api = None


@dp.message_handler(commands=['start'])
async def reg(message: types.Message):
    message_for_reg = "Пройдите регистрацию по ссылке: \nhttps://my.telegram.org\n" \
                      "Вот гайд, если не разберетесь: \n" \
                      "https://tlgrm.ru/docs/api/obtaining_api_id\n\n" \
                      "Если прошли регистрацию, нажмите кнопку  ⬇  "
    await bot.send_message(message.from_user.id, f"Привет! {message_for_reg}", reply_markup=menu_markup_for_reg)


@dp.message_handler(content_types=["text"])
async def receive_message(message: types.Message):
    msg_for_handling = message["text"]
    if not moderator_access["api_id"]:
        if msg_for_handling.isdigit():
            moderator_access["api_id"] = int(msg_for_handling)
            await bot.send_message(message.from_user.id, "api_id принят", reply_markup=markup_continue_after_id)
        else:
            await bot.send_message(message.from_user.id, "Формат введеных данных не верен")
    elif not moderator_access["api_hash"]:
        if msg_for_handling.isalnum() and len(msg_for_handling) == 32:
            moderator_access["api_hash"] = msg_for_handling
            await bot.send_message(message.from_user.id, "api_hash принят", reply_markup=markup_continue_after_hash)
        else:
            await bot.send_message(message.from_user.id, "Формат введеных данных не верен")
    elif not moderator_access["phone_number"]:
        if msg_for_handling[1:].isdigit() and len(msg_for_handling) == 12 and "+" in msg_for_handling:
            moderator_access["phone_number"] = msg_for_handling
            await bot.send_message(message.from_user.id, "Номер телефона принят",
                                   reply_markup=markup_receive_code)
        else:
            await bot.send_message(message.from_user.id, "Формат введеных данных не верен")
    elif not moderator_access["code"]:
        if msg_for_handling.isdigit() and len(msg_for_handling) == 5:
            moderator_access["code"] = msg_for_handling
            print(moderator_access["code"])
            await bot.send_message(message.from_user.id, "Код принят, пробуем подключиться")
            await moderator_api.login(moderator_access["code"])
            get_chat_res = await moderator_api.get_chat("https://t.me/finrequest")
            if get_chat_res:
                await bot.send_message(message.from_user.id, "Ваш код уже есть в системе! \nБот готов к работе!")
            await moderator_api.parse(limit=20)
        else:
            await bot.send_message(message.from_user.id, "Формат введеных данных не верен")
            print(moderator_access)


@dp.callback_query_handler(text="continue")
async def login(query: CallbackQuery):
    await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                        message_id=query.message.message_id,
                                        reply_markup=None)
    await bot.send_message(query.from_user.id, "Введите api_id")


@dp.callback_query_handler(text="continue_id")
async def login(query: CallbackQuery):
    await bot.delete_message(chat_id=query.from_user.id,
                             message_id=query.message.message_id)
    await bot.send_message(query.from_user.id, "Введите api_hash")


@dp.callback_query_handler(text="continue_hash")
async def login(query: CallbackQuery):
    await bot.delete_message(chat_id=query.from_user.id,
                             message_id=query.message.message_id)
    await bot.send_message(query.from_user.id, "Введите номер телефона")


@dp.callback_query_handler(text="receive_code")
async def login(query: CallbackQuery):
    global moderator_api
    await bot.delete_message(chat_id=query.from_user.id,
                             message_id=query.message.message_id)
    moderator_api = API(moderator_access["api_id"], moderator_access["api_hash"], moderator_access["phone_number"])
    if moderator_api is not None:
        start_res = await moderator_api.start()
        if start_res:
            await bot.send_message(query.from_user.id, "Введите код")


if __name__ == "__main__":
    executor.start_polling(dp)
