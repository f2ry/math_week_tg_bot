@echo off
chcp 65001
echo [1] Активация виртуального окружения...
call .\Scripts\activate.bat
pause
echo [2] Установка зависимостей...
pip install -r requirements.txt
echo [3] Запуск скрипта
python main.py