from django.contrib.sites import requests
import admin



s = requests.Session()

def checkAdmin(role):
    if s.get("role") != 'user' and s.get("login") != "false":
        print("Änderung nicht möglich")

def admin(role):
    if (s.get("role") == 'admin'):
        print("Dieser User ist ein admin")



