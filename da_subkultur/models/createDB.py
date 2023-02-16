import sqlite3

conn = sqlite3.connect('admins.db')
c = conn.cursor()


c.execute("""CREATE TABLE admins (
        email string PRIMARY KEY UNIQUE NOT NULL
)""")


#c.execute("""CREATE TABLE users(
#        id integer PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
#        firstname text NOT NULL,
#        lastname text NOT NULL,
#        birthdate DATETIME NOT NULL,
#        email text UNIQUE NOT NULL,
#        password text NOT NULL,
#        role text default 'user' NOT NULL
#)""")


conn.commit()
conn.close()