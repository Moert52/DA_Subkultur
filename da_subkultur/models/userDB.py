import sqlite3
from models import Validation
from User import User


def tryConnection():
    try:
        conn = sqlite3.connect('users.db')
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
        print(user)
        # userList = list(user)
        Validation.check_user(user)
        # Wenn es einen User mit der selben E-Mail gibt, wird eine Fehlermeldung geworfen
        if getUser(user.email) == -1:
            raise Exception("E-Mail is already in use!")
        if (
            user.email == "ldjurdjevic@tsn.at" or user.email == "mertcet@tsn.at" or
                user.email == "meesen@tsn.at"):
            user.role = 1
        else:
            user.role = 0


        c.execute("INSERT INTO users (firstname, lastname, birthdate, email, password, role) "
                  "VALUES (?, ?, ?, ?, ?)",
                  (user.firstname, user.lastname, user.birthdate, user.email, user.password, user.role))
        conn.commit()
    except sqlite3.Error as error:
        raise Exception("An error occurred while inserting a user", error)
    finally:
        conn.close()


def getUser(email):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", [email])
        user = c.fetchone()
        return user
    except sqlite3.Error as error:
        raise Exception("An error occurred while getting a user", error)
    finally:
        conn.close()
    return -1


def getAllUser():
    try:
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


def changeUser(id,user):
    try:
        conn = sqlite3.connect ('user.db')
        c = conn.cursor()
        c.execute("update users set firstname, lastname, birthdate, email, password, role" +
                  " where id =?", [id])
        conn.commit()
    except sqlite3.Error as error:
        raise Exception("An error occurred changing a user", error)
    finally:
        conn.close()


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
    return 1


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
        user = User(firstname, lastname, birthdate, email, password)
        print(user.role)
        print(user.firstname)
        insert(user)


if __name__ == "__main__":
    logreg()
    print(getAllUser())
    print(getUser('mcetinkaya@tsn.at'))
    #deleteUser(1)