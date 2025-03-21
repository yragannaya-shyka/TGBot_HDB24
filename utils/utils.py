import json
from telebot import types, TeleBot

class ActionCanceled(Exception):
    pass


def read_load_json_data(file_name: str, data: dict):
    with open(file_name, "r", encoding="utf-8") as f_o:
        data_from_json = json.load(f_o)

    request_id = len(data_from_json) + 1
    data_from_json[request_id] = data

    with open(file_name, "w", encoding="utf-8") as f_o:
        json.dump(data_from_json, f_o, indent=4, ensure_ascii=False)

    return request_id

def bitrix_id_by_name(file_name: str, user_name: str):
    with open(file_name, "r", encoding="utf-8") as f_o:
        data_from_json = json.load(f_o)

    for user in data_from_json.values():
        if user_name in user["name"]:
            return user["b24_user_id"]


def bitrix_id_by_chat_id(chat_id: int, file_name='users.json'):
    with open(file_name, "r", encoding="utf-8") as f_o:
        data_from_json = json.load(f_o)
    return data_from_json[str(chat_id)]["b24_user_id"]


def cancelable_step(func):
    def wrapper(message, *args, **kwargs):
        user_id = message.chat.id
        if message.text.lower() == '/cancel' or message.text == "Отмена":
            raise ActionCanceled("Действие отменено.")
        return func(message, *args, **kwargs)
    return wrapper


def process_step(message: types.Message, bot: TeleBot, step_name: str, next_step: callable, data: dict):
    data[step_name] = message.text

def escape_markdown(text):
    reserved_chars = r"_"
    for char in reserved_chars:
        text = text.replace(char, f"\\{char}")
    return text

def get_ur_users():
    with open("urusers.json", "r", encoding="utf-8") as f_o:
        urusers = json.load(f_o)
    return urusers

def user_access_by_id(user_chat_id):
    with open("users.json", "r", encoding="utf-8") as f_o:
        users = json.load(f_o)
    return user_chat_id in users


def registr_new_user(user_chat_id, name, username):
    with open("users.json", "r", encoding="utf-8") as f_o:
        users = json.load(f_o)
    data = {"useraname":username,
            "name": name,
            "b24_user_id":""}
    users[str(user_chat_id)] = data

    with open("users.json", "w", encoding="utf-8") as f_o:
        json.dump(users, f_o, indent=4, ensure_ascii=False)
