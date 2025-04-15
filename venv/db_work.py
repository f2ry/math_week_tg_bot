import sqlite3 as sq
import json
db_path = "db/db.db"

def add_user(uid, name, user_class):
    global db_path
    connection = sq.connect(db_path)
    cursor = connection.cursor()
    new_user = (uid, name, user_class, 0)
    request_user_add = '''
    INSERT INTO USERS (ID, NAME, CLASS, SCORE) VALUES (?, ?, ?, ?)'''
    cursor.execute(request_user_add, new_user)
    connection.commit()
    cursor.close()
    connection.close()

def select_user(uid):
    global db_path
    connection = sq.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(f'SELECT * FROM USERS WHERE ID="{uid}"')
    user = cursor.fetchall()
    cursor.close()
    connection.close()
    if user:
        return user[0]
    return False

def remove_user(uid):
    global db_path
    connection = sq.connect(db_path)
    cursor = connection.cursor()
    if not select_user(uid):
        return 0
    cursor.execute(f'DELETE FROM USERS WHERE ID = "{uid}"')
    cursor.execute(f'DELETE FROM SOLUTIONS WHERE ID = "{uid}"')
    connection.commit()
    cursor.close()
    connection.close()

def add_answer(uid, task_id, answer):
    global db_path
    connection = sq.connect(db_path)
    cursor = connection.cursor()
    new_answer = (uid, task_id, answer)
    insert_request = "INSERT INTO SOLUTIONS (ID, TASK_ID, ANSWER) VALUES (?, ?, ?);"
    cursor.execute(insert_request, new_answer)
    connection.commit()
    cursor.close()
    connection.close()

def add_score(uid):
    global db_path
    connection = sq.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(f"UPDATE USERS SET SCORE = SCORE + 1 WHERE ID = {uid}")
    connection.commit()
    cursor.close()
    connection.close()

def count_solutions(uid):
    global db_path
    connection = sq.connect(db_path)
    cursor = connection.cursor()
    request_uid_solutions = f"SELECT * FROM SOLUTIONS WHERE ID = {uid}"
    cursor.execute(request_uid_solutions)
    uid_solutions = cursor.fetchall()
    cursor.close()
    connection.close()
    return len(uid_solutions)
    

def is_solved(uid, task_id):
    global db_path
    connection = sq.connect(db_path)
    cursor = connection.cursor()
    request_uid_solutions = f"SELECT * FROM SOLUTIONS WHERE ID = {uid}"
    cursor.execute(request_uid_solutions)
    uid_solutions = cursor.fetchall()
    cursor.close()
    connection.close()
    for elem in uid_solutions:
        if task_id == elem[1]:
            return True
    return False

def count_users():
    global db_path
    connection = sq.connect(db_path)
    cursor = connection.cursor()
    all_users_request = "SELECT * FROM USERS"
    cursor.execute(all_users_request)
    all_users = cursor.fetchall()
    cursor.close()
    connection.close()
    return len(all_users)

def get_top_users():
    global db_path
    connection = sq.connect(db_path)
    cursor = connection.cursor()
    top_users_request = "SELECT * FROM USERS ORDER BY SCORE DESC LIMIT 5;"
    cursor.execute(top_users_request)
    top_users = cursor.fetchall()
    cursor.close()
    connection.close()
    return top_users

def json_to_sql(json_path, sql_path):
    connection = sq.connect(sql_path)
    cursor = connection.cursor()
    with open(json_path) as f:
        json_data = json.load(f)
    for user in json_data.keys():
        if select_user(user):
            continue
        add_user(user, json_data[user]["name"], json_data[user]["class"])
        user_solutions = json_data[user]["solved"]
        for task in user_solutions.keys():
            add_answer(user, task, user_solutions[task])
    cursor.close()
    connection.close()

json_to_sql("db/users.json", "db/db.db")
print(get_top_users())
