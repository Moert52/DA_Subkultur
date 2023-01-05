import os
import json
import shutil

from flask import Flask, render_template, flash, request, url_for, send_from_directory
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
import elementpath
import datetime
import glob
import hashlib
import json
import os
import pathlib
import re
from flask_restful import Api
from werkzeug.utils import secure_filename, redirect
import requests
import Tesseract
from Solr import Processor, addAll
from conf import DOCUMENTS_PATH, OCR_PATH
from models.User import User

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
#ordner = r'C:\Users\Anwender\Documents\SCHULE\Diplomarbeit\test_tesseract'

# Leo's Pfad
# ordner = r'D:\Diplomarbeit\test_tesseract'
app.config['OCR_PATH'] = OCR_PATH
app.config['DOCUMENTS_PATH'] = DOCUMENTS_PATH

host = "http://127.0.0.1:5000/artikel"


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
        insert(user)
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

# Hier wird mittels dem keyword nach den jeweiligen Bilder gesucht
@app.route('/suche/<keyword>', methods=('GET', 'POST'))
@app.route('/suche', methods=('GET', 'POST'))
def getSearch(keyword=""):
    print("search")
    resultArr = []  # ein Array für die Ergebnisse

    # Wenn ein Schlüsselwort submitted wurde, wird dieser
    # abgespeichert und der search - Methode mitgegeben, wo
    # man dann die jeweiligen Einträge von der Suche erhält
    if request.method == 'POST':
        keyword = request.form['keyword']
        if keyword == '':
            keyword = 'StringIsNull'
        resultArr = json.loads(requests.get('%s/%s' % (host, keyword)).json())

        if keyword == 'StringIsNull':
            keyword = ''
        print(resultArr)
    # Wenn das Array aber leer ist, wird ein leeres String
    # der search - Methode mitgegeben, welche daraufhin
    # alle Einträge zurückgibt
    if not resultArr:
        if keyword == '':
            keyword = 'StringIsNull'
        resultArr = json.loads(requests.get('%s/%s' % (host, keyword)).json())

        if keyword == 'StringIsNull':
            keyword =''

    # Die jeweiligen Werte werden der Webseite weitergegeben und diese
    # werden dann mit den Ergebnissen gemeinsam auf der Webseite angezeigt
    return render_template("Suche.html", len=len(resultArr), arr=resultArr,
                           name=str(keyword) or 'StringIsNull',
                           keyword=keyword or "Keyword")

#Hier wird das enstsprechende Bild mit den jeweiligen Keyword gehighlightet angezeigt
@app.route('/getImage/<path:url>/<string>')
def getImage(url, string):
    clearFolder()
    print(url)
    print(string)
    getstring = ''
    if string != "StringIsNull":
        strr = string.lower()

        strr = strr.title()  # Jeder Buchstabe bei jedem Wort wird groß geschrieben
        strr = strr.split()

        getstring = ''
        for s in strr:
            getstring = '%s %s %s %s' % (s, s.upper(), s.lower(),
                                         getstring)  # +  string + ' %s ' % string.upper() + '%s ' % string.lower()  # Das Schlüsselwort wird in 3 Arten gespeichert normal, alles groß, alles klein
        print(getstring)
    highlight_image(url, '%s_alto_neu.xml' % url, getstring)
    name = pathlib.Path(url).stem
    path = (app.config['DOCUMENTS_PATH'] + '\suche\\') + name + '_suche.jpg'
    print(path)
    return render_template("getImage.html", url=path, name=string)  # , titlearr= sorted(searchArr))

def highlight_image(img, xml, string):
    dic = os.path.basename(img)
    # print('JA:' +dic)
    dic = dic.removesuffix('.png')
    file = dic + '_suche.jpg'  # die entsprechende suffix wird hinzugefügt
    file = file.replace("\\", "-")  # Die enstprechenden Zeichen werden ersetzt

    # Die XML - Datei wird im entsprechenden encoding geöffnet
    root = ET.parse(xml)  # Die xml wird geöffnet
    image = Image.open(img)  # Die jpg Datei wird geöffnet

    # Abfrage ob der String StringIsNull enthält, dann soll er das normale Bild,
    # ohne es zu higlighten, abspeichern und sonst wird das jeweilige keyword gehighlightet
    if string != 'StringIsNull':
        # Der String wird gesplitet, je nachdem ob das keyword mehrere
        # Wörter lang ist und wird dann als array gespeichert
        stri = string.split()
        print(stri)
        # Jedes String Element im XML - Dokument läuft hier durch
        for p in elementpath.select(root, '//String', {'': 'http://www.loc.gov/standards/alto/ns-v3#'}):

            # Der Content vom String - Element wird abgespeichert und
            # danach wird das Encoding enstsprechend umgeändert

            st = p.attrib["CONTENT"]
            st = st.encode('ISO-8859-1')
            st = st.decode('utf-8')
            #print(st)

            for e in stri:  # Dann läuft jedes einzelne wort vom keyword hier durch
                print(e)

                # Es wird geprüft ob das keyword mit
                # dem String - Element überreinstimmt
                if re.search(e, st):
                    # Die Position und die Größe wird abgespeichert,
                    # danach werden diese in einem Array gespeichert
                    x0 = int(p.attrib["HPOS"])
                    y0 = int(p.attrib["VPOS"])
                    x1 = int(x0 + int(p.attrib["WIDTH"]))
                    y1 = int(y0 + int(p.attrib["HEIGHT"]))

                    # Hier werden die entsprechenden Größen mit den enstsprechenden
                    # Abweichungen in einem Array abgespeichert
                    shape = [x0 - 7, y0 - 10, x1 + 8, y1 + 14]

                    # Die Schiftfarbe wird auf schwarz eingestellt
                    TINT_COLOR = (0, 0, 0)

                    # Das JPG - File wird in RGBA-Format konvertiert, danach wird
                    # mit den jeweiligen Werten ein Filter erstellt, welches man dann
                    # zum Malen dem Bild malen verwendet, danach wird ein Rechteck mit
                    # den Positionen und der eingestellten Farbe gemalt
                    image = image.convert("RGBA")
                    overlay = Image.new('RGBA', image.size, TINT_COLOR + (0,))
                    draw = ImageDraw.Draw( overlay)
                    draw.rectangle(shape, fill=(255, 255, 80, 130), outline="black")


                    # Die beiden Bilder werden Alpha-Composited zu einem Bild.
                    # Alpha composite these two images together to obtain the desired result.
                    # Danach wird der Filter auf das gemalte Bild angewendet
                    # und dann wird dieses Bild ins RGB-Format zurückkonvertiert
                    image = Image.alpha_composite(image, overlay)
                    image = image.convert("RGB")

                    # Danach wird das Bild in den jeweilige Ordner gespeichert
    image.save((app.config['DOCUMENTS_PATH'] + '\suche\\') + file, quality=10, dpi=(72, 72))

# Hier kann man die entsprechenden Bilder der Ergebnisse
# downloaden oder auf der Webseite anzeigen
@app.route('/uploads/<path:path>')
def get_file(path):
    # Der entsprechende Pfad zum Ordner wird
    # mittels dem gegegeben Pfad erstellt
    folder = os.path.dirname(path)

    # Der Dateiname wird vom mitgegebenen Pfad rausgeholt.
    name = os.path.basename(path)

    # Mittels der send_from_directory - Methodem, welches mit dem Pfad
    # und dem Dateinamen, das jeweilige Bild anzeigt bzw. herunterladet
    return send_from_directory(folder, name, as_attachment=True)


# Hier wird der gesamte Inhalt vom Suchordner gelöscht
def clearFolder():
    # Hier ist die Variable vom Pfad zum Suchordner
    folder = (app.config['DOCUMENTS_PATH'] + '\suche')
    for filename in os.listdir(folder):  # Jeder einzelne Datei im Ordner läuft hier durch
        file_path = os.path.join(folder, filename)  # Hier bekommt man den Pfad zu der Datei
        try:
            # Dann wird wird geprüft ob es sich um Eine Datei oder einen Link haltet
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Wird dementsprechend gelöscht
            elif os.path.isdir(file_path):  # Sonst wird geprüft ob es sich um einen Subordner handelt
                shutil.rmtree(file_path)  # Dann wird der Subordner gelöscht
        except Exception as e:  # Sonst gibt es demenstprechend eine Exception
            print('Failed to delete %s. Reason: %s' % (file_path, e))


if __name__ == '__main__':
    app.run(debug=True, port='5252')
