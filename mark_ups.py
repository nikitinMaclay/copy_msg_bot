from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton

menu_markup_for_reg = InlineKeyboardMarkup(row_width=1, one_time_keyboard=True)
buttons_for_reg = [InlineKeyboardButton(text="Продолжить", callback_data='continue')]

menu_markup_for_reg.add(*buttons_for_reg)


markup_continue_after_id = InlineKeyboardMarkup(row_width=1)
buttons_continue_after_id = [InlineKeyboardButton(text="Продолжить", callback_data='continue_id')]

markup_continue_after_id.add(*buttons_continue_after_id)


markup_continue_after_hash = InlineKeyboardMarkup(row_width=1)
buttons_continue_after_hash = [InlineKeyboardButton(text="Продолжить", callback_data='continue_hash')]

markup_continue_after_hash.add(*buttons_continue_after_hash)


markup_receive_code = InlineKeyboardMarkup(row_width=1)
buttons_receive_code = [InlineKeyboardButton(text="Получить код", callback_data='receive_code')]

markup_receive_code.add(*buttons_receive_code)
