
import sys
import json
from settings import *
from app_components import GraphCalculator, GraphApp


func_file = sys.argv[2]
with open(func_file, "w") as file:
    file.write('[]')

if sys.argv[1] == 'GraphCalculator':
    func_texts = []
    
    def send_function(text: str, color: ColorType, index: int):
        info = text, color
        if index < len(func_texts):
            func_texts[index] = info
        else:
            func_texts.append(info)
        with open(func_file, "w") as func_files:
            func_files.write(json.dumps(func_texts))
    
    def remove_function(index: int):
        if index < len(func_texts):
            func_texts.pop(index)
            with open(func_file, "w") as func_files:
                func_files.write(json.dumps(func_texts))
    
    GraphCalculator(func_file, send_function, remove_function).run()
elif sys.argv[1] == 'GraphApp':
    GraphApp(func_file).run()

