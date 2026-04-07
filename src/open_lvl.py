import json

def load_level(file_path):
    with open(file_path, 'r') as file:
        level_data = json.load(file)
    return level_data
    
