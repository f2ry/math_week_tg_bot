from json_work import *
users = db_open("db/users.json")
while 1:
    for user in users.keys():
        print(f'''
ID: {user}
Имя: {users[user]["name"]}
Класс: {users[user]["class"]}
Баллы: {users[user]["score"]}
        ''')
    input()