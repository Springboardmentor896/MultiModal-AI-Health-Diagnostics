import json

def read_json_file(path):
    with open(path, "r") as file:
        data = json.load(file)
    return data
