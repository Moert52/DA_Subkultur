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
        print("An error occurred while inserting a user", error)
    finally:
        conn.close()


def getUser(id):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=?", id)
        user = c.fetchone()
        return user
    except sqlite3.Error as error:
        print("An error occurred while getting a user", error)
    finally:
        conn.close()
    return -1


def deleteUser(id):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE id=?", id)
        conn.commit()
    except sqlite3.Error as error:
        print("An error occurred while deleting a user", error)
    finally:
        conn.close()


def login(email, password):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? and password=?", (email, password))
        return 1
    except sqlite3.Error as error:
        print("An error occurred while login", error)
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    print("Enter EMail: ")
    email = input()
    print("Enter Password: ")
    password = input()

    if login(email, password) == 1:
        print("logged in")
    else:
        print("login failed")
