import json


with open("users.json", "r", encoding="utf-8") as f_o:
    data_from_json = json.load(f_o)
for v in data_from_json.values():
    if "Шинкаренко" in v["name"]:
        print(v["b24_user_id"])
    else:
        print('error')
