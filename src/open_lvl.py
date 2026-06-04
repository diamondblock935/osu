import json
from os import path

def load_level(file_path):
    with open(path.dirname(__file__) + "/levels/" + file_path, 'r') as file:
        level_data = json.load(file)
    return level_data
    
