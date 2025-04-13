import telebot

from json_work import *

db_path = "db/users.json"
tasks_path = "db/tasks.json"
config_path = "db/config.json"
config = db_open(config_path)
TOKEN = config["token"]
day = config["day"]
bot = telebot.TeleBot(token=TOKEN, parse_mode="HTML")


@bot.message_handler(commands=["start"])
def start(message):
    parsed_start = message.text.split(" ", maxsplit=1)
    chat_id = message.chat.id
    db = db_open(db_path)
    if str(chat_id) not in db.keys():
        bot.send_message(chat_id, "Привет! Кажется, мы с тобой раньше не виделись.\nДавай знакомиться! Как тебя зовут?\n<i>Введи свои ФИ</i>:")
        bot.register_next_step_handler(message, registration, db)
        return 0
    else:
        if len(parsed_start) > 1:
            solve(message)
            return 0
        user = db[str(chat_id)]
        bot.send_message(chat_id, f"""
Привет, {message.from_user.username}!

<b>Имя:</b> {user["name"]}
<b>Класс:</b> {user["class"]}
<b>Решенные задания:</b> {len(user["solved"].keys())} из {day}0

<b>Доступные команды:</b>
/start - показывает это сообщение.
/start * - отправляет задание, где * - номер задания. 
/solve * - делает то же самое, что и start *. 
/remove - команда для удаления себя из базы. Нужна, если при регистрации что-то пошло не так.
/top - выводит топ-5 людей по количеству набранных очков.

А вообще, просто сканируй QR-код с заданием и давай решать!
📷📷📷
                         """)
    

def registration(message, db):
    chat_id = message.chat.id
    name = message.text
    bot.send_message(chat_id, "В каком ты классе?\n<i>Введи номер и букву:</i>")
    bot.register_next_step_handler(message, next_step, db, name)

def next_step(message, db, name):
    chat_id = message.chat.id
    class_numero = message.text
    db.update(
        {str(chat_id): {
            "name": name,
            "class": class_numero,
            "score": 0,
        "solved": {
                }
   }})
    db_rewrite(db_path, db)
    bot.send_message(chat_id, "Вот мы и познакомились!\nОтправляю тебя в главное меню...")
    print(f"\nnew user: {chat_id}!\nname: {name}\ncurrent users' counter: {len(db.keys())}")
    message.text = "/start"
    start(message)

@bot.message_handler(commands=["remove"])
def remove(message):
    chat_id = message.chat.id
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Да, я уверен", "Нет, я передумал")
    bot.send_message(chat_id, "Ты уверен, что хочешь это сделать?\n⚠<i>Это действие необратимо.\nВесь прогресс будет утерян!</i>⚠", reply_markup=kb)
    bot.register_next_step_handler(message, remove_confirmation, chat_id)

def remove_confirmation(message, chat_id):
    db = db_open(db_path)
    if message.text == "Да, я уверен":
        db.pop(str(chat_id))
        db_rewrite(db_path, db)
        bot.send_message(chat_id, "Приятно было познакомиться... Надеюсь, мы еще увидимся!", reply_markup=telebot.types.ReplyKeyboardRemove())
        return 0
    if message.text == "Нет, я передумал":
        bot.send_message(chat_id, "Хорошо, что ты решил остаться...\nТелепортирую тебя в главное меню!", reply_markup=telebot.types.ReplyKeyboardRemove())
        message.text = "/start"
        start(message)
    else:
        bot.send_message(chat_id, "Не понял, что ты имеешь ввиду...\nСделаем вид, что ничего не было!", reply_markup=telebot.types.ReplyKeyboardRemove())
        message.text = "/start"
        start(message)

@bot.message_handler(commands=["solve"])
def solve(message):
    global day
    tasks = db_open(tasks_path)
    chat_id = message.chat.id
    parsed = message.text.split(" ", maxsplit=1)
    if len(parsed) == 1:
        bot.send_message(chat_id, "Не хватает номера задания. Попробуй ещё раз!")
        message.text = "/start"
        start(message)
        return 0

    task_id = parsed[1]
    user = db_open(db_path)[str(chat_id)]
    if task_id in tasks.keys():
        if task_id in user["solved"].keys():
            bot.send_message(chat_id, "Вы уже решали это задание!")
            message.text = "/start"
            start(message)
            return 0
        if int(task_id) not in range(int(str(day-1)+"1"), int(str(day)+"1")):
            bot.send_message(chat_id, "Кажется, это задание не относится к сегодняшним...")
            message.text = "/start"
            start(message)
            return 0
        kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("Я пока не хочу это решать...")
        bot.send_photo(chat_id, telebot.types.InputFile(f"db/tasks/pics/day_{day}/{task_id}.png"), caption='''
<i>Введите ответ ниже.</i>
                       
<b>Пожалуйста, вводите ответ внимательно и не торопитесь!</b>
Примеры ответов:
- десятичные дроби: 1,23 (вводятся с запятой)
- выражения: 2+2=4 (вводятся без пробелов)
- целые числа: -5 
<b>Нажмите кнопку ниже, чтобы отказаться от решения.</b>''',
                       reply_markup=kb)
        bot.register_next_step_handler(message, answer_validation, chat_id, user, tasks, task_id)
    else:
        bot.send_message(chat_id, "Задания в базе нет.")

def answer_validation(message, chat_id, user, tasks, task_id):
    answer = message.text
    if answer == "Я пока не хочу это решать...":
        bot.send_message(chat_id, "Как скажешь! Телепортирую тебя в главное меню...", reply_markup=telebot.types.ReplyKeyboardRemove())
        message.text = "/start"
        start(message)
        return 0 
    if answer.lower() == tasks[task_id].lower():
        user["score"] = int(user["score"]) + 1
    user["solved"].update({task_id: answer})
    db = db_open(db_path)
    db[str(chat_id)].update(user)
    db_rewrite(db_path, db)
    bot.send_message(chat_id, "<i>Ваш ответ записан. Надеюсь, он не был случайным...</i>", reply_markup=telebot.types.ReplyKeyboardRemove())
    message.text = "/start"
    start(message)

@bot.message_handler(commands=["day"])
def day_change(message):
    global day
    chat_id = message.chat.id
    if str(chat_id) not in config["admins"]:
        bot.send_message(chat_id, "is not accessed")
        return 0
    text = message.text.split(" ", maxsplit=1)
    if len(text) == 2:
        new_day = text[1]
        bot.send_message(chat_id, f"Был день: {day}\nНовый день: {new_day}")
        day = int(new_day)
        config.update({"day": day})
        db_rewrite(config_path, config)
        return 0
    else:
        bot.send_message(chat_id, f"Сейчас установлен день: {day}")
        return 0
    
@bot.message_handler(commands=["top"])
def top(message):
    chat_id = message.chat.id
    db = db_open(db_path)
    users_score = {}
    for user in db:
        users_score.update({user: int(db[user]["score"])})
    sorted_score = dict(sorted(users_score.items(), key=lambda item: item[1], reverse=True))
    result = ''
    right_range = len(sorted_score.keys()) if len(sorted_score.keys()) < 5 else 5
    for user in list(sorted_score.keys())[0:right_range]:
        result += f'''
UID: {user}
Имя: {db[user]["name"]}
Количество очков: {sorted_score[user]}
'''
    bot.send_message(chat_id, result)
    
print("succ3ss")
bot.infinity_polling()

