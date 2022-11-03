import sqlite3
from flask import Flask, render_template, request, make_response
from datetime import date

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
        c.execute("INSERT INTO users (firstname, lastname, birthdate, email, password, role) "
                  "VALUES (?, ?, ?, ?, ?, ?)",
                  (user.firstname, user.lastname, user.birthdate, user.email, user.password, user.role))
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


def getUsers():
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        users = c.fetchall()
        return users
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
        if c.fetchone() is not None:
            return 1
        else:
            return 0
    except sqlite3.Error as error:
        print("An error occurred while login", error)
    finally:
        conn.close()
    return 0


app = Flask(__name__)


#@app.route("/")
#def getUsers():
#    users = getUsers()
#    print(users)
#    return render_template("login.html", usr=users)


if __name__ == "__main__":
    #app.run(debug=True)
    print(getUsers())
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

    if input() == "register":
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
        user = (firstname, lastname, birthdate, email, password, "user")
        insert(user)
