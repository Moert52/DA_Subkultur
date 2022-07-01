import sqlite3
from datetime import date

from models import User


def tryConnection():
    try:
        conn = sqlite3.connect(r'C:\Users\mertc\PycharmProjects\da_subkultur\users.db')
        print("A SQLite connection has been established")
    except sqlite3.Error as error:
        print("An error occurred while connecting to SQLite", error)
    finally:
        conn.close()
        print("The SQLite connection has been closed")


def insert(user):
    try:
        userList = list(user)
        conn = sqlite3.connect(r'C:\Users\mertc\PycharmProjects\da_subkultur\users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (firstname, lastname, birthdate, email, password) "
                  "VALUES (?, ?, ?, ?, ?)",
                  (userList[0], userList[1], userList[2], userList[3], userList[4]))
        conn.commit()
    except sqlite3.Error as error:
        print("An error occurred while inserting a user", error)
    finally:
        conn.close()


def getUser(id):
    try:
        conn = sqlite3.connect(r'C:\Users\mertc\PycharmProjects\da_subkultur\users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=?", id)
        user = c.fetchone()
        return user
    except sqlite3.Error as error:
        print("An error occurred while getting a user", error)
    finally:
        conn.close()
    return -1

def getAllUser():
    try:
        conn = sqlite3.connect(r'C:\Users\mertc\PycharmProjects\da_subkultur\users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        user = c.fetchone()
        return user
    except sqlite3.Error as error:
        print("An error occurred while getting a user", error)
    finally:
        conn.close()
    return -1

def deleteUser(id):
    try:
        conn = sqlite3.connect(r'C:\Users\mertc\PycharmProjects\da_subkultur\users.db')
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE id=?", id)
        conn.commit()
    except sqlite3.Error as error:
        print("An error occurred while deleting a user", error)
    finally:
        conn.close()


def login(email, password):
    try:
        conn = sqlite3.connect(r'C:\Users\mertc\PycharmProjects\da_subkultur\users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? and password=?", (email, password))
        if (c.fetchone() != None):
            return 1
        else:
            return 0
    except sqlite3.Error as error:
        print("An error occurred while login", error)
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    getUser(0)
    print("Login oder Register (login/register):")

    if input() == "login":

        print("Enter EMail: ")
        email = input()
        print("Enter Password: ")
        password = input()

        if login(email, password) == 1:
            print("logged in")
        else:
            print("login failed")

    else:
        print("Firstname: ")
        firstname = str(input())
        print("Lastname: ")
        lastname = str(input())
        print("Birthdate(YYYY:MM:DD): ")
        b = input().split(":")
        birthdate = date(int(b[0]), int(b[1]), int(b[2]))
        print("EMail: ")
        email = str(input())
        print("Password: ")
        password = str(input())
        user = (firstname, lastname, birthdate, email, password)
        insert(user)
