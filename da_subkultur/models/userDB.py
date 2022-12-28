import sqlite3
from datetime import date

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from cryptography.fernet import Fernet

from models import Validation
from models.User import User
from models import Validation


key = b'f-_6pyLfUVeDMtCP1BjDcmFv_ninS7WZqxFyQGfF0vs='


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
        userList = list(user)
        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        Validation.check_user(user)
        # Wenn es einen User mit der selben E-Mail gibt, wird eine Fehlermeldung geworfen
        if getUser(userList[3]) == -1:
            raise Exception("E-Mail is already used.")

        c.execute("INSERT INTO users (firstname, lastname, birthdate, email, password) "
                  "VALUES (?, ?, ?, ?, ?)",
                  (userList[0], userList[1], userList[2], userList[3], userList[4]))
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
    return -1


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
        raise Exception("An error occurred while login", error)
    finally:
        conn.close()
    return 0


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


def encrypt(password):
    cipher_suite = Fernet(key)
    ciphered_text = cipher_suite.encrypt(password)
    return ciphered_text


def decrypt():
    return


class LoginForm(FlaskForm):
    email = StringField(validators=[
        InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Email"})

    password = PasswordField(validators=[
        InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    firstname = StringField(validators=[
        InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "First Name"})

    lastname = StringField(validators=[
        InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Last Name"})

    birthdate = StringField(validators=[
        InputRequired(), Length(min=4, max=8)], render_kw={"placeholder": "Birthdate"})

    email = StringField(validators=[
        InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Email"})

    password = PasswordField(validators=[
        InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    role = PasswordField(validators=[
        InputRequired(), Length(min=2, max=10)], render_kw={"placeholder": "Role"})

    submit = SubmitField('Register')

    def validate_email(self, email):
        existing_User_email = User.query.filter_by(email=email.data).first()
        if existing_User_email:
            raise ValidationError(
                "Diese Email wurde bereits verwendet bitte verwenden Sie eine andere Mail-Adresse")


#if __name__ == "__main__":
    #logreg()
    #print(getAllUser())
    #deleteUser(5)
