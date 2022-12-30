import datetime
import re

from datetime import date


regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


def check_name(name):
    try:
        if name.replace(" ", "").isalpha() is False:
            raise ValueError("Name is not Valid!")
        return 1
    except:
        raise


def check_birthdate(birthdate):
    try:
        datetime.datetime.strptime(birthdate, '%Y-%m-%d')
        if birthdate == str(date.today()):
            raise ValueError("Please use a valid date!")
        return 1
    except:
        raise


def check_email(email):
    try:
        if re.fullmatch(regex, email) is None:
            raise ValueError("Please use a valid E-Mail format!")
        return 1
    except:
        raise


def check_password(password):
    try:
        if len(password) < 8:
            raise ValueError("Your password needs to be 8 characters or longer!")
        if not re.search("[a-z]", password):
            raise ValueError("There has to be at least one lowercase letter in the password!")
        if not re.search("[A-Z]", password):
            raise ValueError("There has to be at least one uppercase letter in the password!")
        if not re.search("[0-9]", password):
            raise ValueError("There has to be at least one number in the password!")
        if not re.search("[_@$#!?=+-.]" , password):
            raise ValueError("There has to be at least one special character in the password!")
        return 1
    except:
        raise


def check_user(user):
    check_name(user.firstname)
    check_name(user.lastname)
    check_birthdate(user.birthdate)
    check_email(user.email)
    check_password(user.password)
    return 1
