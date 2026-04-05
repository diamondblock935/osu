import json
from objects import Circle, slider, Approach_Circle
# from main import Circle, slider, menu_button, Approach_Circle

def load_level(file_path):
    with open(file_path, 'r') as file:
        level_data = json.load(file)
    return level_data
    