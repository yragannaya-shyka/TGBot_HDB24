from telebot import types, TeleBot
import requests
from utils.utils import read_load_json_data, bitrix_id_by_name, bitrix_id_by_chat_id
from utils.bitrix import BitrixRequest
import urllib.parse
from messages import  welcome_message, info_message, help_message, rights_list_message
from keyboards import create_keyboard, get_cancel_keyboard
from decorators import handle_errors , handle_action_cancel
from config import B24_WH, B24_ADMIN_ID


def hello_handler(message: types.Message, bot: TeleBot):
    bot.send_message(message.chat.id, "Hello test")


def start_handle(message: types.Message, bot: TeleBot):
    keyboard = create_keyboard([types.KeyboardButton("Создать запрос")])
    bot.send_message(message.chat.id, welcome_message, parse_mode="Markdown", reply_markup=keyboard)


def help_handle(message: types.Message, bot: TeleBot):
    keyboard = create_keyboard([types.KeyboardButton("Задать вопрос разработчику бота")])
    bot.send_message(message.chat.id, help_message, reply_markup=keyboard)


def info_handle(message: types.Message, bot: TeleBot):
    bot.send_message(message.chat.id, info_message)


def request_handle(message: types.Message, bot: TeleBot):
    keyboard = create_keyboard([types.KeyboardButton("Подключение нового сотрудника"),
                                types.KeyboardButton("Предоставление прав доступа"),
                                types.KeyboardButton("Отправить уведомление")])
    bot.send_message(message.chat.id, 'Выберите интересующий вас запрос из меню ниже.', reply_markup=keyboard)


def handle_message(message: types.Message, bot:TeleBot):

    chat_id = message.chat.id

    if message.text == "Подключение нового сотрудника":
        msg = bot.send_message(message.chat.id, "Введите ФИО нового сотрудника", reply_markup=get_cancel_keyboard())
        bot.register_next_step_handler(message, invite_new_user_step_name, bot=bot)
    elif message.text == "Предоставление прав доступа":
        msg = bot.send_message(chat_id, "Введите ФИО сотрудника, кому необходимо предоставить права доступа.", reply_markup=get_cancel_keyboard())
        bot.register_next_step_handler(msg, procces_access_rights_step_name, bot=bot)
    elif message.text == "Отправить уведомление":
        msg = bot.reply_to(message, "Добавте текст уведомления")
        bot.register_next_step_handler(msg, procces_notify_step, bot=bot)
    else:
        bot.reply_to(message, f"You tuped: {message.text}")


def procces_notify_step(message: types.Message, bot: TeleBot):

    try:
        description = message.text
        requests.get(f"{B24_WH}im.notify.personal.add.json?USER_ID={B24_ADMIN_ID}&MESSAGE={description}")
        bot.reply_to(message, f"Уведомление '{description}' отправлено!")
    except Exception as e:
        bot.reply_to(message, "Что-то пошло не так!")


#access_rights procces steps
@handle_errors
@handle_action_cancel
def procces_access_rights_step_name(message: types.Message, bot: TeleBot):
    br = BitrixRequest()

    initiator_tg_id = message.chat.id
    initiator = bitrix_id_by_chat_id(initiator_tg_id)
    br.params["initiator"].value = initiator
    br.params["initiator_tg_id"].value = initiator_tg_id
    name = message.text
    br.params["acces_rights_user"].value = bitrix_id_by_name("users.json", name)
    bot.send_message(message.chat.id, rights_list_message, reply_markup=get_cancel_keyboard())
    bot.register_next_step_handler(message, procces_access_rights_step_rights, bot=bot, br=br)


@handle_errors
@handle_action_cancel
def procces_access_rights_step_rights(message: types.Message, bot: TeleBot, br: BitrixRequest):
    rights = message.text
    br.params["acces_rights_type"].value = rights
    bot.send_message(message.chat.id, "Вставьте ссылку на объект (папка/файл) предоставления прав доступа.", reply_markup=get_cancel_keyboard())
    bot.register_next_step_handler(message, procces_access_rights_step_link, bot=bot, br=br)


@handle_errors
@handle_action_cancel
def procces_access_rights_step_link(message: types.Message, bot: TeleBot, br: BitrixRequest):
    link = message.text
    encoded_description = urllib.parse.unquote(link)
    coded_url = urllib.parse.quote(encoded_description,safe=":/")
    double_coded_url = urllib.parse.quote(coded_url)
    br.params["acces_rights_object_link"].value = double_coded_url
    record_data = br.get_data_for_record()
    request_id = read_load_json_data("users_requests.json", record_data)
    br.params["title"].value = f"ТГ запрос №{request_id} - {br.categoryes["access_rights"].name}"
    requests.get(br.create_bitrix_smart_process_element("access_rights"))
    bot.send_message(message.chat.id, f"Ваш запрос №{request_id} принят в работу. Ожидайте уведомление о выполнении запроса.")



#invite_new_user steps
@handle_errors
@handle_action_cancel
def invite_new_user_step_name(message: types.Message, bot: TeleBot):
    br = BitrixRequest()

    initiator_tg_id = message.chat.id
    initiator = bitrix_id_by_chat_id(initiator_tg_id)
    br.params["initiator"].value = initiator
    br.params["initiator_tg_id"].value = initiator_tg_id


    name = message.text
    br.params["new_user_name"].value = name

    bot.send_message(message.chat.id, "Введите должность нового сотрудника", reply_markup=get_cancel_keyboard())
    bot.register_next_step_handler(message, invite_new_user_step_position, bot=bot, br=br)


@handle_errors
@handle_action_cancel
def invite_new_user_step_position(message: types.Message, bot: TeleBot, br: BitrixRequest):
    position = message.text
    br.params["new_user_position"].value = position
    msg = bot.send_message(message.chat.id, "Введите подразделение нового сотрудника", reply_markup=get_cancel_keyboard())
    bot.register_next_step_handler(msg, invite_new_user_step_division, bot=bot, br=br)



@handle_errors
@handle_action_cancel
def invite_new_user_step_division(message: types.Message, bot: TeleBot, br: BitrixRequest):
    division = message.text
    br.params["new_user_division"].value = division
    msg = bot.send_message(message.chat.id, "Введите ФИО руководителя нового сотрудника", reply_markup=get_cancel_keyboard())
    bot.register_next_step_handler(msg, invite_new_user_step_supervisor, bot=bot, br=br)


@handle_errors
@handle_action_cancel
def invite_new_user_step_supervisor(message: types.Message, bot: TeleBot, br: BitrixRequest):

    supervsor = message.text
    br.params["new_user_supervisor"].value = bitrix_id_by_name("users.json", supervsor)
    record_data = br.get_data_for_record()
    request_id = read_load_json_data("users_requests.json", record_data)
    br.params["title"].value = f"ТГ запрос №{request_id} - {br.categoryes["new_user"].name}"
    requests.get(br.create_bitrix_smart_process_element("new_user"))
    bot.reply_to(message, f"Ваш запрос №{request_id} принят в работу. Ожидайте уведомление о выполнении запроса.")



HANDLERS = [
    (hello_handler, lambda message: message.text == "Hello"),
    (request_handle, lambda message: message.text == "Создать запрос"),
    (request_handle, lambda message: message.text.startswith("/request")),
    (start_handle, lambda message: message.text.startswith("/start")),
    (help_handle, lambda message: message.text.startswith("/help")),
    (info_handle, lambda message: message.text.startswith("/info")),
    (handle_message, lambda message: True)
]

def register_handler(bot: TeleBot):
    for handle, conditition in HANDLERS:
        bot.register_message_handler(handle, func=conditition, pass_bot=True)
