import sqlite3 as sq

dbn = 'db.db'

with sq.connect(dbn) as con:
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
    """)
    cur.execute('DROP TABLE images')

    cur.execute("""
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        user_id REFERENCES users(id),
        user_name REFERENCES users(username)
    )
    """)

