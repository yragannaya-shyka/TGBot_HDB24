import json

def read_load_json_data(file_name: str, data: dict):
    """records a user's request into json file and return request ID

    Args:
        file_name (str): a file of json format where you want to record requests
        data (dict): data which you want to record

    Return nothing
    """

    with open(file_name, "r", encoding="utf-8") as f_o:
        data_from_json = json.load(f_o)

    request_id = len(data_from_json) + 1
    data_from_json[request_id] = data

    with open(file_name, "w", encoding="utf-8") as f_o:
        json.dump(data_from_json, f_o, indent=4, ensure_ascii=False)

    return request_id

def bitrix_id_by_name(file_name: str, user_name: str):
    """Returns bitrix ID of the user by the name of the user

    Args:
        file_name (str): a file of users storage in json format
        user_name (str): a name of the user

    Returns:
        _type_: _description_
    """
    with open(file_name, "r", encoding="utf-8") as f_o:
        data_from_json = json.load(f_o)

    for user in data_from_json.values():
        if user_name in user["name"]:
            return user["b24_user_id"]


def bitrix_id_by_chat_id(chat_id: int, file_name='users.json'):
    with open(file_name, "r", encoding="utf-8") as f_o:
        data_from_json = json.load(f_o)
    return data_from_json[str(chat_id)]["b24_user_id"]
