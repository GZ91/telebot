import telebot
from telebot import types
from SM import StateMenu, binary_search_smenu
import constants

bot = telebot.TeleBot(constants.BOT_KEY)

list_tel_smenu = []

@bot.message_handler(commands=["start"])
def start(m, res=False):

    global list_tel_smenu
    id_tel = m.chat.id
    SMenu = StateMenu(id_tel, m.from_user.username)
    list_tel_smenu.append(SMenu)
    sorted(list_tel_smenu)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    text = SMenu.get_state(m.text, types, markup, m.chat.id)
    bot.send_message(m.chat.id, text, reply_markup=markup)



@bot.message_handler()
def command(m):
    SMenu = None
    tel_id = m.chat.id
    global list_tel_smenu
    if len(list_tel_smenu):
        SMenu = binary_search_smenu(list_tel_smenu, tel_id)

    if SMenu == None:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("/start"))
        bot.send_message(tel_id, constants.TEXT_PRESTART, reply_markup=markup)
        return None
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    text = SMenu.get_state(m.text, types, markup, m.chat.id)
    if text == constants.TEXT_STRING_EXIT:
        list_tel_smenu.remove(SMenu)
    bot.send_message(m.chat.id, text, reply_markup=markup)

bot.polling(none_stop=True, interval=0)