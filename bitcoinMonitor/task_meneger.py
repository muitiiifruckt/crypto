import schedule
import time
import subprocess
from api import start

def run_api_script():
    """Функция для запуска скрипта api.py"""
    try:
        print("sdfsf")
        start()
        print("api.py executed successfully")
    except :
        print(f"Error executing api.py:")

# Планирование задачи
schedule.every(1).minutes.do(run_api_script)

# Основной цикл
while True:
    schedule.run_pending()
    time.sleep(1)

