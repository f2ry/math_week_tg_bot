import qrcode
from json_work import *
path = "db/tasks/qrs"
link = "https://t.me/f2ryt3st_bot?start="

tasks = db_open("db/tasks.json")
tasks_ids = [*tasks.keys()]
for id in range(31, 51):
    qr = qrcode.make(f"{link}{id}")
    qr.save(f"{path}/{id}.png")

