from json_work import *
users = db_open("db/users.json")
print(f"Количество пользователей: {len(users.keys())}")
while 1:
    for user in users.keys():
        print(f'''
ID: {user}
Имя: {users[user]["name"]}
Класс: {users[user]["class"]}
Баллы: {users[user]["score"]}
        ''')
    input()