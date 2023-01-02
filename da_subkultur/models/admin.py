from django.contrib.sites import requests
import userDB
import admin
from User import User


s = requests.Session()

def checkAdmin(role):
    if s.get("role") != 2 or s.get("loggedIn") != "false":
        print("Keine Userdaten vorhanden")

def admin(role):
    if (s.get("role") == 1):
        print("Dieser User ist ein admin")



