from telebot.types import KeyboardButton, ReplyKeyboardMarkup

main_button = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

main_button.add("📊 Ma'lumot olish", "📝 Ma'lumot qo'shish")


cencel = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('❌ Bekor qilish'))

get_back = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('⬅️ ortga'))


ask_phone = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(KeyboardButton(
    '☎️ Raqam jo\'natish', request_contact=True), KeyboardButton('❌ Bekor qilish'))
