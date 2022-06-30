import sqlite3
from cryptography.fernet import Fernet

conn = sqlite3.connect('users.db')
c = conn.cursor()

#c.execute("""CREATE TABLE journals (
#        id integer PRIMARY KEY NOT NULL,
#        title text,
#        name text,
#        url text,
#        date text
#)""")


# c.execute("""CREATE TABLE users(
#        id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
#        firstname text,
#        lastname text,
#        birthdate text,
#        email text,
#        password text,
#        role text
# )""")


conn.commit()
conn.close()