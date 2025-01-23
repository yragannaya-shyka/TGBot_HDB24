from telebot import types, TeleBot
import requests
import os
from dotenv import load_dotenv
from sup_funcs import read_load_json_data, bitrix_id_by_name, bitrix_id_by_chat_id
import urllib.parse
from texts import  welcome_message, info_message, help_message, rights_list_message

load_dotenv()


b24_wh = os.getenv("B24_WH")
b24_admin_id = os.getenv("B24_ADMIN_ID")


def hello_handler(message: types.Message, bot: TeleBot):
    bot.send_message(message.chat.id, "Hello test")


def start_handle(message: types.Message, bot: TeleBot):
    keybourd = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    create_request_button = types.KeyboardButton("Создать запрос")
    keybourd.add(create_request_button)
    bot.send_message(message.chat.id, welcome_message, parse_mode="Markdown", reply_markup=keybourd)


def help_handle(message: types.Message, bot: TeleBot):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    question_button = types.KeyboardButton("Задать вопрос разработчику бота")
    keyboard.add(question_button)
    bot.send_message(message.chat.id, help_message, reply_markup=keyboard)


def info_handle(message: types.Message, bot: TeleBot):
    bot.send_message(message.chat.id, info_message)


def request_handle(message: types.Message, bot: TeleBot):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    invite_new_user_button = types.KeyboardButton("Подключение нового сотрудника")
    access_rights_button = types.KeyboardButton("Предоставление прав доступа")
    send_message_button_b24 = types.KeyboardButton("Отправить уведомление")
    keyboard.add(invite_new_user_button, access_rights_button, send_message_button_b24)
    bot.send_message(message.chat.id, 'Выберите интересующий вас запрос из меню ниже.', reply_markup=keyboard)


def handle_message(message: types.Message, bot:TeleBot):
    """Handle ReplyKeybord with "requset" command.

    Args:
        message (types.Message): await message from telegram.
        bot (TeleBot): Telebot class object of the current bot.

    """

    if message.text == "Подключение нового сотрудника":
        msg = bot.reply_to(message, "Введите ФИО нового сотрудника")
        bot.register_next_step_handler(message, invite_new_user_step_name, bot=bot)
    elif message.text == "Предоставление прав доступа":
        msg = bot.reply_to(message, "Введите ФИО сотрудника, кому необходимо предоставить права доступа.")
        bot.register_next_step_handler(msg, procces_access_rights_step_name, bot=bot)
    elif message.text == "Отправить уведомление":
        msg = bot.reply_to(message, "Добавте текст уведомления")
        bot.register_next_step_handler(msg, procces_notify_step, bot=bot)
    else:
        bot.reply_to(message, f"You tuped: {message.text}")


def procces_notify_step(message: types.Message, bot: TeleBot):
    """Sends notify to B24 user in case of "Отправить уведомление" message from handele_message func.

    Args:
        message (types.Message): _description_
        bot (TeleBot): _description_
    """
    try:
        description = message.text
        requests.get(f"{b24_wh}im.notify.personal.add.json?USER_ID={b24_admin_id}&MESSAGE={description}")
        bot.reply_to(message, f"Уведомление '{description}' отправлено!")
    except Exception as e:
        bot.reply_to(message, "Что-то пошло не так!")


#access_rights procces steps
def procces_access_rights_step_name(message: types.Message, bot: TeleBot):
    try:
        data = {
            "type": "Запрос прав доступа",
            "initiator": ["ufCRM_12_1732527565", None],
            "name": ["ufCrm_12_1737536925", None],
            "rights": ["ufCrm_12_1737537025432", None],
            "link": ["ufCrm_12_1737537083844", None]
        }

        initiator = bitrix_id_by_chat_id(message.chat.id)
        data["initiator"][1] = initiator
        name = message.text
        data["name"][1] = bitrix_id_by_name("users.json", name)

        bot.reply_to(message, rights_list_message)
        bot.register_next_step_handler(message, procces_access_rights_step_rights, bot=bot, data=data)
    except Exception as e:
        bot.send_message(message.chat.id, "Не удалось обработать ФИО")


def procces_access_rights_step_rights(message: types.Message, bot: TeleBot, data: dict):
    try:
        rights = message.text
        data["rights"][1] = rights
        msg = bot.reply_to(message, "Вставьте ссылку на объект (папка/файл) предоставления прав доступа.")
        bot.register_next_step_handler(msg, procces_access_rights_step_link, bot=bot, data=data)
    except Exception as e:
        bot.reply_to(message, "Не удалось обработать запрашиваемые права")



def procces_access_rights_step_link(message: types.Message, bot: TeleBot, data: dict):
    try:
        link = message.text
        data["link"][1] = link

        request_id = read_load_json_data("users_requests.json", data)
        encoded_description = urllib.parse.unquote(data["link"][1])
        coded_url = urllib.parse.quote(encoded_description,safe=":/")
        double_coded_url = urllib.parse.quote(coded_url)


        requests.get(f'''{b24_wh}crm.item.add.json?entityTypeId=1034
                     &fields[TITLE]=ТГ запрос №{request_id} - {data["type"]}
                     &fields[ufCrm_12_1723450334376]=158
                     &fields[{data["name"][0]}]={data["name"][1]}
                     &fields[{data["rights"][0]}]={data["rights"][1]}
                     &fields[{data["link"][0]}]={double_coded_url}
                     &fields[{data["initiator"][0]}]={data["initiator"][1]}''')
        bot.reply_to(message, f"Ваш запрос №{request_id} принят в работу. Ожидайте уведомление о выполнении запроса.")
    except Exception as e:
        bot.reply_to(message, "Не удалось создать запрос на предоставление прав досутпа")


#invite_new_user steps
def invite_new_user_step_name(message: types.Message, bot: TeleBot):
    try:

        data = {
            "type": "Добавление нового сотрудника",
            "initiator": ["ufCrm_12_1732527565", None],
            "initiator_tg_id": ["ufCrm_12_1736781758613", None],
            "name": ["ufCrm_12_1736781830742", None],
            "position": ["ufCrm_12_1736781849952", None],
            "division": ["ufCrm_12_1736781881035", None],
            "supervisor": ["ufCrm_12_1736781897", None],

        }

        initiator = bitrix_id_by_chat_id(message.chat.id)
        initiator_tg_id = message.chat.id
        data["initiator"][1] = initiator
        data["initiator_tg_id"][1] = initiator_tg_id
        name = message.text
        data["name"][1] = name

        bot.reply_to(message, "Введите должность нового сотрудника")
        bot.register_next_step_handler(message, invite_new_user_step_position, bot=bot, data=data)
    except Exception as e:
        print(e)
        bot.reply_to(message, "Не удалось создать пользоватея")

def invite_new_user_step_position(message: types.Message, bot: TeleBot, data: dict):
    try:
        position = message.text
        data["position"][1] = position
        msg = bot.reply_to(message, "Введите подразделение нового сотрудника")
        bot.register_next_step_handler(msg, invite_new_user_step_division, bot=bot, data=data)
    except Exception as e:
        bot.reply_to(message, "Не удалось создать пользоватея")


def invite_new_user_step_division(message: types.Message, bot: TeleBot, data: dict):
    try:
        division = message.text
        data["division"][1] = division
        msg = bot.reply_to(message, "Введите ФИО руководителя нового сотрудника")
        bot.register_next_step_handler(msg, invite_new_user_step_supervisor, bot=bot, data=data)
    except Exception as e:
        bot.reply_to(message, "Не удалось создать пользоватея")


def invite_new_user_step_supervisor(message: types.Message, bot: TeleBot, data: dict):
    try:
        supervsor = message.text
        data["supervisor"][1] = bitrix_id_by_name("users.json", supervsor)
        request_id = read_load_json_data("users_requests.json", data)
        requests.get(f'''{b24_wh}crm.item.add.json?entityTypeId=1034
                     &fields[TITLE]=ТГ запрос №{request_id} - {data["type"]}
                     &fields[ufCrm_12_1723450334376]=160
                     &fields[{data["name"][0]}]={data["name"][1]}
                     &fields[{data["position"][0]}]={data["position"][1]}
                     &fields[{data["division"][0]}]={data["division"][1]}
                     &fields[{data["supervisor"][0]}]={data["supervisor"][1]}
                     &fields[{data["initiator"][0]}]={data["initiator"][1]}
                     &fields[{data["initiator_tg_id"][0]}]={data["initiator_tg_id"][1]}''')
        bot.reply_to(message, f"Ваш запрос №{request_id} принят в работу. Ожидайте уведомление о выполнении запроса.")
    except Exception as e:
        bot.reply_to(message, "Не удалось создать пользоватея")




def register_handler(bot: TeleBot):
    bot.register_message_handler(hello_handler, func=lambda message: message.text == "Hello", pass_bot=True)
    bot.register_message_handler(request_handle, func=lambda message: message.text == "Создать запрос", pass_bot=True)
    bot.register_message_handler(request_handle, commands=["request"], pass_bot=True)
    bot.register_message_handler(start_handle, func=lambda message: True, commands=["start"], pass_bot=True)
    bot.register_message_handler(help_handle, func=lambda message: True, commands=["help"], pass_bot=True)
    bot.register_message_handler(info_handle, commands=["info"], pass_bot=True)
    bot.register_message_handler(handle_message, func=lambda message: True, pass_bot=True)
