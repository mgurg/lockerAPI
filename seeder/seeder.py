import json


def load_data_from_json(json_file):
    with open(json_file) as file:
        return json.load(file)
