import sqlite3
import string

import bcrypt

from User import User

from cryptography.fernet import Fernet

databasePath = 'models/users.db'


def tryConnection():
    try:
        conn = sqlite3.connect(databasePath)
        print("A SQLite connection has been established")
    except sqlite3.Error as error:
        raise Exception("An error occurred while connecting to SQLite", error)
    finally:
        conn.close()
        print("The SQLite connection has been closed")


def insert(user):
    try:
        conn = sqlite3.connect(databasePath)
        c = conn.cursor()
        print(user)
        secure_password = get_hashed_password(user.password)
        c.execute("INSERT INTO users (firstname, lastname, birthdate, email, password, role) "
                  "VALUES (?, ?, ?, ?, ?, ?)",
                  (user.firstname, user.lastname, user.birthdate, user.email, secure_password, user.role))
        conn.commit()
    except sqlite3.Error as error:
        raise Exception("An error occurred while inserting a user", error)
    finally:
        conn.close()


def getUser(id):
    try:
        conn = sqlite3.connect(databasePath)
        c = conn.cursor()
        if type(id) is string:
            c.execute("SELECT * FROM users WHERE email=?", [id])
        elif type(id) is int:
            c.execute("SELECT * FROM users WHERE id=?", [id])
        user = c.fetchone()
        return user
    except sqlite3.Error as error:
        raise Exception("An error occurred while getting a user", error)
    finally:
        conn.close()


def getAllUser():
    try:
        conn = sqlite3.connect(databasePath)
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        users = c.fetchall()
        return users
    except sqlite3.Error as error:
        raise Exception("An error occurred while getting a user", error)
    finally:
        conn.close()


def deleteUser(id):
    try:
        conn = sqlite3.connect(databasePath)
        c = conn.cursor()
        if type(id) is string:
            c.execute("DELETE FROM users WHERE email=?", [id])
        elif type(id) is int:
            c.execute("DELETE FROM users WHERE id=?", [id])
        conn.commit()
    except sqlite3.Error as error:
        raise Exception("An error occurred while deleting a user", error)
    finally:
        conn.close()


def login(email, password):
    try:
        conn = sqlite3.connect(databasePath)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? ", email)
        user = c.fetchone()
        if user is None:
            raise Exception("Please use an existing E-Mail or Password")
        else:
            if check_password(password, user.password):
                return 1
            else:
                raise Exception("Wrong Password provided")
    except sqlite3.Error as error:
        raise Exception("An error occurred while login", error)
    finally:
        conn.close()


def logreg():
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

    elif input() == "register":
        print("Firstname: ")
        firstname = str(input())
        print("Lastname: ")
        lastname = str(input())
        print("Birthdate(YYYY-MM-DD): ")
        birthdate = str(input())
        print("E-Mail: ")
        email = str(input())
        print("Password: ")
        password = str(input())

        user = User(firstname, lastname, birthdate, email, password)
        insert(user)


def get_hashed_password(plain_text_password):
    # Passwort wird mit Salt gehashed, bcrypt speichert Salt im Hash
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())


def check_password(plain_text_password, hashed_password):
    # Passwort mittels bcrypt prüfen
    return bcrypt.checkpw(plain_text_password, hashed_password)


if __name__ == "__main__":
    password = "Hallo123".encode('utf-8')
    print(password)
    hash = get_hashed_password(password)
    print(hash)
    falsch = "Hallo".encode('utf-8')
    print(check_password(password, hash))
