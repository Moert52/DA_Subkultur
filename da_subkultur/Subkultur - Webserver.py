import glob
import os

from flask import Flask, render_template, flash, request, url_for
from flask_restful import Api
from werkzeug.utils import secure_filename, redirect



import Tesseract
from Solr import Processor

#Für Solr
p = Processor('http://localhost:8983/solr/test')

#Für Flask
app=Flask(__name__,template_folder='static/templates')  # Die Flask-Anwendung
api = Api(app)  # Die Flask API
app.secret_key = '_5#y2L"F4Q8z/n/xec] /'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
#Variablen für wichtige Pfäde
app.config['UPLOAD_PATH'] = r'C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract\ToOCR'
app.config['DOCUMENTS_PATH'] = r'C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract'




#Hier wird die Startseite aufgerufen
@app.route('/')
def Start():
    return render_template("Start.html")

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/login')
def login():
    return render_template("login.html")





#Hier ist die Methode und das Formular um Artikel hochzuladen (OCR + Solr)
@app.route('/admin/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':    #Wenn etwas verschickt wird
        title = request.form['title']   #wird der eingegebene Titel
        site = request.form['site']     #Docuement_Site als Variablen gespeichert

        #Überprüfung ob Titel, Site eingegeben wurden und eine Datei hochgeladen wurde
        if not title:
            flash('Title is required!')
        elif not site:
            flash('Site is required!')
        for uploaded_file in request.files.getlist('file'):
            if uploaded_file.filename == '':
                flash('File is required!')
            else:
                file = secure_filename(uploaded_file.filename)      #Dateiname mit Extension
                path = os.path.join(app.config['UPLOAD_PATH'], file)    #Pfad der Datei
                uploaded_file.save(path)       #PDFs werden in einen bestimmen Ordner gespeichert, wo dann die OCR durchöäuft

                filename = os.path.basename(path).split('.')[0]     #Dateiname ohne Extension
                #print(title)
                #print(site)
                #print(app.config['UPLOAD_PATH'])
        if len(os.listdir(app.config['UPLOAD_PATH']) ) != 0:    #Überprüfung ob sich überhaupt Dateien im Ordner befinden
            Tesseract.process_dir(app.config['UPLOAD_PATH'])    #OCR läuft die PDFS druch und speichert alles in einen eigenen Ordner für die Dateien
            filepath = os.path.join(app.config['DOCUMENTS_PATH'], filename)     #Pfad vom Ordner, wohin die OCR die Dateien hingespeichert hat    #
            for f in glob.glob("%s/*.txt" % filepath):      #Läuft den Ordner durch um alle txt - Dateien...
                p.process(f, title, filepath, site)         #... auf Solr hochzuladen

    return render_template("create.html")

#Hier wird die Menüseite aufgerufen@app.route('/Menu')
def Menu():
    return render_template("Start.html")

if __name__ == '__main__':
    app.run(debug=True)




