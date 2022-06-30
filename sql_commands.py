import sqlite3
import traceback


def add_user_to_base(user: list):
    try:
        conn = sqlite3.connect('api.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO api_base(username, api_id, api_hash, phone) VALUES(?, ?, ?, ?);", user)
        conn.commit()
        return True
    except:
        print(user)
        print(traceback.format_exc())
        return False


def add_all_messages(data: list):
    try:
        conn = sqlite3.connect('api.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO messages(user_id, message_id, from_id, message) VALUES(?, ?, ?, ?);", data)
        conn.commit()
        return True
    except:
        print(traceback.format_exc())
        return False


def get_all_messages(user_id: int):
    try:
        conn = sqlite3.connect('api.db')
        cur = conn.cursor()
        messages = cur.execute(f"SELECT * FROM messages WHERE user_id={user_id}").fetchall()
        messages = list(map(lambda x: [x[1], x[2], x[3], x[4]], messages))
        return messages
    except:
        print(traceback.format_exc())
        return None


def add_group_to_base(username: str, url: str):
    try:
        conn = sqlite3.connect('api.db')
        cur = conn.cursor()
        groups = cur.execute(f"SELECT url FROM groups").fetchall()
        if url not in list(map(lambda x: x[0], groups)):
            cur.execute(f"INSERT INTO groups(user, url) VALUES('{username}', '{url}');")
            conn.commit()
        else:
            print(False)
            return False
        return True
    except:
        print(traceback.format_exc())
        return False


def delete_group_from_base(url: str):
    try:
        conn = sqlite3.connect('api.db')
        cur = conn.cursor()
        cur.execute(f"DELETE FROM groups WHERE url='{url}';")
        conn.commit()
        return True
    except:
        print(traceback.format_exc())
        return False


def get_groups(username: str):
    try:
        conn = sqlite3.connect('api.db')
        cur = conn.cursor()
        groups = cur.execute(f"SELECT url FROM groups WHERE user='{username}'").fetchall()
        return list(map(lambda x: x[0], groups))
    except:
        print(traceback.format_exc())
        return None


def get_user(username):
    res = []
    conn = sqlite3.connect('api.db')
    cur = conn.cursor()
    try:
        user = cur.execute(f"SELECT * FROM api_base WHERE username='{username}'").fetchall()[0]
        for i in user:
            res.append(str(i))
        if '+' not in res[-1] and res[-1][:1] != '8':
            res[-1] = '+' + res[-1]
        return res
    except IndexError:
        print(f'username: {username} не в базе')
        return None
