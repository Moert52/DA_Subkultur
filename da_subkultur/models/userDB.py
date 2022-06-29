import sqlite3

from da_subkultur.models.User import User


def tryConnection():
    try:
        conn = sqlite3.connect('users.db')
        print("A SQLite connection has been established")
    except sqlite3.Error as error:
        print("An error occurred while connecting to SQLite", error)
    finally:
        conn.close()
        print("The SQLite connection has been closed")


def insert(user):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (id, email, password) VALUES (?, ?, ?)", (user.id, user.email, user.password))
        conn.commit()
    except sqlite3.Error as error:
        print("An error occurred while connecting to SQLite", error)
    finally:
        conn.close()


def getUser(id):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id={}".format(id))
        user = c.fetchone()
        return user
    except sqlite3.Error as error:
        print("An error occurred while connecting to sqlite", error)
    finally:
        conn.close()
    return -1


def deleteUser(id):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE id={}".format(id))
        conn.commit()
    except sqlite3.Error as error:
        print("An error occurred while connecting to SQLite", error)
    finally:
        conn.close()


if __name__ == "__main__":
    print(getUser(1))
