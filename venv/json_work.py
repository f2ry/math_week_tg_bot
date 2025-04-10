import json


def db_open(path):
    with open(path, "r") as f:
        file = json.load(f)
    return file

def db_rewrite(path, new_data):
    with open(path, "w") as f:
        json.dump(new_data, f, indent=3)


    
