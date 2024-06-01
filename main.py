
import subprocess
import sys
import threading
from secrets import choice
from string import digits
# from classes import GraphCalculator, GraphApp

# def initialize_calc(ga: GraphApp):
#     gc = GraphCalculator(lambda func: ga.graph.add_y_func(func, 'red'))
#     gc.run()

# def main():
#     ga = GraphApp()
    
#     gc_thread = threading.Thread(target=lambda: initialize_calc(ga))
#     gc_thread.daemon = True
#     gc_thread.start()
    
#     try:
#         ga.run()
#     except Exception as e:
#         print(e)
#         return

def main():
    random_file_name = ''.join([choice(digits) for _ in range(20)]) + '.json'
    
    gc_thread = threading.Thread(target=lambda: subprocess.run(['py', 'run_app_components.py', 'GraphCalculator', str(random_file_name)]))
    gc_thread.daemon = True
    gc_thread.start()
    subprocess.run(['py', 'run_app_components.py', 'GraphApp', str(random_file_name)])

if __name__ == '__main__':
    main()
    sys.exit()


