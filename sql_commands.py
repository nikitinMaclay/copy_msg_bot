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
        print(traceback.format_exc())
        return False


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
