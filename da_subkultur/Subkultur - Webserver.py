import os

from flask import Flask, render_template, flash, request, url_for
from flask_restful import Api
from werkzeug.utils import secure_filename, redirect

import Tesseract
from Solr import Processor, addAll
from conf import DOCUMENTS_PATH, OCR_PATH
from models import User
from models.userDB import getAllUser, insert

# Für Solr
p = Processor('http://localhost:8983/solr/test')

# Für Flask
app = Flask(__name__, template_folder='static/templates')  # Die Flask-Anwendung
api = Api(app)  # Die Flask API
app.secret_key = '_5#y2L"F4Q8z/n/xec] /'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
# Variablen für wichtige Pfäde

# Mert's Pfad
#ordner = r'C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract'

# Melih's Pfad
ordner = r'C:\Users\Anwender\Documents\SCHULE\Diplomarbeit\test_tesseract'

# Leo's Pfad
# ordner = r'D:\Diplomarbeit\test_tesseract'
app.config['OCR_PATH'] = OCR_PATH
app.config['DOCUMENTS_PATH'] = DOCUMENTS_PATH

base = "http://127.0.0.1:5000/"


# Hier wird die Startseite aufgerufen
@app.route('/')
def Start():
    return render_template("Start.html")


# Login-Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = str(request.form["firstname"])
        lastname = str(request.form["lastname"])
        email = str(request.form["email"])
        password = str(request.form["password"])
        birthdate = str(request.form["birthdate"])
        user = User(firstname, lastname, birthdate, email, password, 'user')

        print(user)
        userDB.insert(user)
        return redirect(url_for('login'))  # , email=email, password=password, message="Efolgreich registriert!"

        # return render_template("register.html")  # , error=insertDB
    else:
        return render_template("register.html")


@app.route('/login', methods=('GET', 'POST'))
def login():
    return render_template("login.html")


@app.route('/subArchiv')
def subArchiv():
    return render_template("subArchiv.html")


@app.route('/admin')
def admin():
    return render_template("admin.html")

@app.route('/allUsers')
def getUsers():
    users = getAllUser()
    print(users)
    return render_template("allUsers.html", usr=users)


# Hier ist die Methode und das Formular um Artikel hochzuladen (OCR + Solr)
@app.route('/admin/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':  # Wenn etwas verschickt wird
        title = request.form['title']  # wird der eingegebene Titel
        site = request.form['site']  # Docuement_Site als Variablen gespeichert
        filenameArr = []
        # Überprüfung ob Titel, Site eingegeben wurden und eine Datei hochgeladen wurde
        if not title:
            flash('Title is required!')
        elif not site:
            flash('Site is required!')
        for uploaded_file in request.files.getlist('file'):
            if uploaded_file.filename == '':
                flash('File is required!')
            else:
                file = secure_filename(uploaded_file.filename)  # Dateiname mit Extension
                path = os.path.join(app.config['OCR_PATH'], file)  # Pfad der Datei
                uploaded_file.save(
                    path)  # PDFs werden in einen bestimmen Ordner gespeichert, wo dann die OCR durchläuft

                filename = os.path.basename(path).split('.')[0]  # Dateiname ohne Extension
                if filename not in filenameArr:
                    filenameArr.append(filename)
                # print(title)
                # print(site)
            # print(app.config['OCR_PATH'])
        if len(os.listdir(app.config['OCR_PATH'])) != 0:  # Überprüfung ob sich überhaupt Dateien im Ordner befinden
            Tesseract.process_dir(app.config[
                                      'OCR_PATH'])  # OCR läuft die PDFS druch und speichert alles in einen eigenen Ordner für die Dateien
            for file in filenameArr:
                filepath = os.path.join(app.config['DOCUMENTS_PATH'],
                                        file)  # Pfad vom Ordner, wohin die OCR die Dateien hingespeichert hat    #
                # for f in glob.glob("%s/*.txt" % filepath):  # Läuft den Ordner durch um alle txt - Dateien...
                addAll(filepath, p, title, site)
                # p.process(f, title, filepath, site)  # ... auf Solr hochzuladen
                p.server.commit()
            clear_folder_to_OCR()
    return render_template("create.html")


# Hier wird die Menüseite aufgerufen
@app.route('/Menu')
def menu():
    return render_template("Start.html")


def clear_folder_to_OCR():
    dir = app.config['OCR_PATH']
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))


if __name__ == '__main__':
    app.run(debug=True)
