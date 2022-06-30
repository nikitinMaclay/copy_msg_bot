from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup, KeyboardButton
menu_markup_for_reg = InlineKeyboardMarkup(row_width=1, one_time_keyboard=True)
buttons_for_reg = [InlineKeyboardButton(text="Продолжить", callback_data='continue')]

menu_markup_for_reg.add(*buttons_for_reg)


markup_continue_after_id = InlineKeyboardMarkup(row_width=1)
buttons_continue_after_id = [InlineKeyboardButton(text="Отправить", callback_data='continue_id')]

markup_continue_after_id.add(*buttons_continue_after_id)


markup_continue_after_id_reload = InlineKeyboardMarkup(row_width=1)
buttons_continue_after_id_reload = [InlineKeyboardButton(text="Отправить снова", callback_data='continue_id')]

markup_continue_after_id_reload.add(*buttons_continue_after_id_reload)


markup_continue_after_hash = InlineKeyboardMarkup(row_width=1)
buttons_continue_after_hash = [InlineKeyboardButton(text="Отправить", callback_data='continue_hash')]

markup_continue_after_hash.add(*buttons_continue_after_hash)


markup_continue_after_hash_reload = InlineKeyboardMarkup(row_width=1)
buttons_continue_after_hash_reload = [InlineKeyboardButton(text="Отправить снова", callback_data='continue_hash')]

markup_continue_after_hash_reload.add(*buttons_continue_after_hash_reload)


markup_continue_after_phone = InlineKeyboardMarkup(row_width=1)
buttons_continue_after_phone = [InlineKeyboardButton(text="Отправить", callback_data='continue_phone')]

markup_continue_after_phone.add(*buttons_continue_after_phone)


markup_continue_after_phone_reload = InlineKeyboardMarkup(row_width=1)
buttons_continue_after_phone_reload = [InlineKeyboardButton(text="Отправить снова", callback_data='continue_phone')]

markup_continue_after_phone_reload.add(*buttons_continue_after_phone_reload)

markup_receive_code = InlineKeyboardMarkup(row_width=1)
buttons_receive_code = [InlineKeyboardButton(text="Отправить код", callback_data='receive_code')]

markup_receive_code.add(*buttons_receive_code)


markup_receive_code_reload = InlineKeyboardMarkup(row_width=1)
buttons_receive_code_reload = [InlineKeyboardButton(text="Отправить код снова", callback_data='receive_code')]

markup_receive_code_reload.add(*buttons_receive_code_reload)


markup_continue_after_group = InlineKeyboardMarkup(row_width=1)
buttons_continue_after_group = [InlineKeyboardButton(text="Отправить", callback_data='continue_group')]

markup_continue_after_group.add(*buttons_continue_after_group)

markup_continue_after_group_reload = InlineKeyboardMarkup(row_width=1)
buttons_continue_after_group_reload = [InlineKeyboardButton(text="Отправить снова", callback_data='continue_group')]

markup_continue_after_group_reload.add(*buttons_continue_after_group_reload)


markup_accept_message = InlineKeyboardMarkup(row_width=2)
buttons_accept_message = [
    InlineKeyboardButton(text="Принять", callback_data='accept_message'),
    InlineKeyboardButton(text="Отклонить", callback_data='decline_message')
]

markup_menu = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
markup_menu.row(*[
    KeyboardButton(text='Добавить группу'),
    KeyboardButton(text='Удалить группу')
                  ]).row(*[KeyboardButton(text='Список групп'),
                           KeyboardButton(text='Отчет')]).add(KeyboardButton(text='Включить/Выключить бота'))
markup_menu.add(KeyboardButton(text='Скрыть меню'))


markup_accept_message.add(*buttons_accept_message)