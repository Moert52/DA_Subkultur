import sqlite3

from models import Validation


def tryConnection():
    try:
        conn = sqlite3.connect(r'/models/users.db')
        print("A SQLite connection has been established")
    except sqlite3.Error as error:
        raise Exception("An error occurred while connecting to SQLite", error)
    finally:
        conn.close()
        print("The SQLite connection has been closed")


def insert(user):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        # userList = list(user)
        Validation.check_user(user)
        # Wenn es einen User mit der selben E-Mail gibt, wird eine Fehlermeldung geworfen
        if getUser(user.email) == -1:
            raise Exception("E-Mail is already in use!")

        c.execute("INSERT INTO users (firstname, lastname, birthdate, email, password) "
                  "VALUES (?, ?, ?, ?, ?)",
                  (user.firstname, user.lastname, user.birthdate, user.email, user.password))
        conn.commit()
    except sqlite3.Error as error:
        raise Exception("An error occurred while inserting a user", error)
    finally:
        conn.close()


def getUser(email):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        user = c.fetchone()
        return user
    except sqlite3.Error as error:
        raise Exception("An error occurred while getting a user", error)
    finally:
        conn.close()
    return -1


def getAllUser():
    try:
        c.execute("SELECT * FROM users WHERE email=?", [email])
        conn = sqlite3.connect('users.db')
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
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE id=?", [id])
        conn.commit()
    except sqlite3.Error as error:
        raise Exception("An error occurred while deleting a user", error)
    finally:
        conn.close()
    return 204


def login(email, password):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? and password=?", (email, password))
        if c.fetchone() is None:
            raise Exception("Please use an existing E-Mail or Password")
    except sqlite3.Error as error:
        raise Exception("An error occurred while login", error)
    finally:
        conn.close()
    return 200


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

    else:
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
        user = (firstname, lastname, birthdate, email, password)
        insert(user)


if __name__ == "__main__":
    #logreg()
    print(getAllUser())
    #deleteUser(2)