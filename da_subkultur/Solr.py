# -*- coding: utf-8 -*-
import datetime
import glob
import hashlib
import json
import os
import pathlib
import re
import shutil
import xml.etree.ElementTree as ET

import elementpath
from PIL import Image, ImageDraw
from flask import Flask, render_template, request, send_from_directory, jsonify
from flask_restful import Api, Resource, reqparse, abort
from pysolr import Solr

from conf import DOCUMENTS_PATH

DOCUMENT_SITE = 'Artikel'  # Zentrale Document Site für die Add_All Methode
# DOCUMENT_URL = r'C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract\Cultblech_1'
app = Flask(__name__, template_folder='static/templates')  # Die Flask-Anwendung
api = Api(app)
app.config['SECRET_KEY'] = 'you-will-never-guess'

# Mert's Ordner
#ordner = r'C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract'

# Leo's Ordner
# ordner = r'D:\Diplomarbeit\test_tesseract'

# Melih's Ordner
#ordner = r'C:\Users\Anwender\Documents\SCHULE\Diplomarbeit\test_tesseract'

ordner = DOCUMENTS_PATH



class Processor(object):  # Klasse Processor - beinhaltet die Solr - Methoden

    # Initialisierung des Solr - Servers
    def __init__(self, solr_server_url):
        self.server = Solr(solr_server_url)

    # Hier wird die "put / patch" - Methode in Solr durchgeführt
    # def process(self, fname, title):
    def process(self, fname, title, DOCUMENT_URL, DOCUMENT_SITE_ID):
        #Hier wird der Pfad und der Name der Datei enstprechend bearbeitet
        base, _ = os.path.splitext(os.path.basename(fname))  # Dateiname ohne der Dateiendung
        url = DOCUMENT_URL + r"\%s" % (base) + '.txt'  # Der Pfad der txt - Datei (ohne den Dateinamen)
        fPath = os.path.join(DOCUMENT_URL, fname)  # Der Pfad der txt - Datei mit dem Dateinamen

        # Die txt - Datei wird geöffnet
        txt_file = open(fPath, encoding="utf-8")

        # Teil der Methode wo der ganze Text von der txt - Datei
        # in die content - Variable für Solr gespeichert wird
        content = ''
        for line in txt_file: #Jede Zeile in der Datei läuft hier durch
            s = line.strip() #Die Zeile wird entsprechend bearbeitet
            # Dann wird kontrolliert, ob die Zeile überhaupt irgendeinen
            # Text enthält und nicht mit undgültigen Zeichen anfängt
            if s and not s.startswith(('*', '=', '-')):
                content = content + " " + s  #str(s.encode(encoding='utf-8', errors='strict'))
        txt_file.close() #Die Datei wird geschlossen
        print(content)

        # Die ID wird anhand dem Title und der Site erstellt und es wird ein
        # Zeitstempel, wann die Datei das letze mal geändert wurde erzeugt
        document_id = u"%s-%s" % (DOCUMENT_SITE_ID, title)  # Hier ensteht eine ID mittels dem Titel und der Site
        #print("new document: %s" % (document_id,))
        t = os.path.getmtime(fPath)  # Hier wird die Zeit gespeichert

        # Hier ensteht ein Dictionary vom Artikel mit Title, site,
        # content, id, url and date, welches auf Solr hochgeladen wird
        doc = {
            # Die erzeugte ID wird gehasht
            'id': hashlib.sha1(document_id.encode('utf-8')).hexdigest(),
            'site': DOCUMENT_SITE_ID,
            'url': url,
            'title': title,
            'content': content,
            'last_modified': str(datetime.datetime.fromtimestamp(t))
        }

        # docStr = json.dumps(doc)
        try:
            # Der Eintrag wird auf Solr hochgeladen und commited
            self.server.add([doc])
            self.server.commit()
        except (IOError, Exception) as e:
            # Sonst kommt eine Fehlermeldung wenn es nicht geklappt hat
            print("Failed to add documents to Solr: %s", e)

    # Hier wird ein Eintrag auf Solr gelöscht
    def delete(self, title, DOCUMENT_SITE_ID):
        # Hier ensteht ein Dictionary vom Artikel mit Title, site,
        # content, id, url and date, welches auf Solr hochgeladen wird
        document_id = u"%s-%s" % (DOCUMENT_SITE_ID, title)
        #logging.info("new document: %s" % (document_id,))
        #print(hashlib.sha1(document_id.encode('utf-8')).hexdigest())

        # Hier wird die generierte id gehasht und anhand der gehashten ID
        # wird der entsprechende Eintrag gelöscht
        self.server.delete(id=str(hashlib.sha1(
            document_id.encode('utf-8')).hexdigest()))  # Hier wird der Eintrag mittels der ID gelöscht
        self.server.commit()


    # Hier wird nach einem Eintrag gesucht
    def search(self, keyword):
        # Hier werden die entsprechenden Einträge auf Solr gesucht und
        # ausgegeben bzw. alle Einträge werden ausgegeben
        #
        # Wenn kein Schlüsselwort eingegeben wurde, werden alle Einträge angezeigt
        if keyword == '':
            results = self.server.search('*:*', sort='order_i asc', rows=500, )

        # Sonst wird im content, title und site nach dem schlüsselwort
        # gesucht und in max. 500 Zeilen gespeichert
        else:
            results = self.server.search('content:*%s* title:*%s* site:*%s*' %
                                         (keyword, keyword, keyword),
                                         sort='order_i asc',
                                         rows=500, )
        self.server.commit()

        z = 0
        pathArr = [None] * len(results)
        titleArr = [None] * len(results)

        try:
            # Jedes einzelne Ergebnis läuft hier durch
            for result in results:
                # print('URL: %s' % result['url'])
                # Die URL wird gespeichert und es wird daraus der
                # entsprechende Pfad zum jeweiligen Bild erstellt
                url = str(result['url'][0])
                path = os.path.dirname(url) # Der Pfad wird herausgefiltert
                p = pathlib.Path(url).stem  # Der Dateiname wird gespeichert

                # Danach wird der Dateiname bearbeitet und anhand dem
                # und den gepsicherten Pfad wird der Pfad zum jeweiligen
                # Bild wird erstellt
                path = os.path.join(path, p.removesuffix('png_text') + 'png')

                #Der Titel und der Pfad wird ins jeweilige Array gespeichert
                pathArr[z] = path  # Hier wird der Pfad des Ergebnissen gespeichert
                titleArr[z] = result['title'] # Hier wird der Titel des Ergebnisses gespeichert
                z += 1  # Hier wird mitgezählt wie viele Ergebnisse gefunden wurden
            print(pathArr)

        # Hier wird Fehlermeldung ausgegeben, wenn etwas nicht funktioniert hat
        except Exception as e:
            error = self.log.error("Bei der Suche ist ein Fehler aufgetreten"
                                   " \nError: %s", e)
            print(error)
            return 404
            # Die Anzahl der Ergebnisse werden zur Kontrolle in der Konsole ausgegeben
        print('Es wurden %s Eintraege gefunden' % z)

        # Der Title - Array und der Path - Array werden ausgegeben
        return titleArr, pathArr

    # Methode zum Löschen aller Einträge auf Solr
    def delAll(self):
        self.server.delete(q='*:*')
        print("Alles gelöscht")

# Der Ordner, wo alle Subordner, die durch die Ocr enstellt wurde, wird durchgelaufen und ladet die jeweiligen
# Einträge auf Solr hoch
def directoryToAddAll(directory, processor, title, site):  #
    dirArr = []  # Array wo der Pfad aller Subordner hinzugefügt wird
    rootdir = directory  # rootdir ist des Hauptordner, wo sich die Subordner befinden
    for dir in os.listdir(rootdir):  # Hier wird jeder einzelner Ordner
        d = os.path.join(rootdir, dir)  # Mit dem richtigen Pfad
        if os.path.isdir(d):  # Und mit der Überprüfung, ob es ein Ordner ist
            dirArr.append(d)  # i in die dirArr gespeichert
    # Dann wird geprüft ob der Ordner PDF & Suche im Array ist
    if (ordner + "\PDF") in dirArr:
        # Und jenachdem werden diese vom Array entfernt
        dirArr.remove((ordner + "\PDF"))
    if (ordner + "\suche") in dirArr:
        dirArr.remove((ordner + "\suche"))

    # print(dirArr)

    for i in dirArr:  # dirArr wird in einer for Schleife durchgelaufen
        DOCUMENT_URL = i  # der Pfad wird gespeichert
        # addAll(i, processor, 'Titel')
        # Und dann wird die addAll Methode ausgeführt, wobei jeder Eintrag die gleiche Site und den gleichen Titel bekommt
        addAll(i, processor, title, site)


# Hier wird jede txt Datei in einem Ordner auf Solr hochgeladen
# def addAll(dir, processor, title):
def addAll(DOCUMENT_URL, processor, title, DOCUMENT_SITE):
    id = 0  # Hier bekommt jeder Eintrag eine ID mit dem Filenamen
    for f in glob.glob("%s/*.txt" % DOCUMENT_URL):  # Hier läuft jede einzelner txt Datei + ihren Pfad im Ordner durch
        file = f.removeprefix(DOCUMENT_URL + '\\')  # Danach bekommt man den Dateinamen + Extension
        print(file)
        name = os.path.basename(DOCUMENT_URL)  # Hier bekommt man nur den Dateinamen ohne Extension

        # processor.process(file, name + '_%s' % str(id))
        # Dann wird die txt Datei auf Solr hochgeladen
        #processor.process(file, name + '_%s' % str(id), DOCUMENT_URL, DOCUMENT_SITE)
        processor.process(file, title, DOCUMENT_URL, DOCUMENT_SITE)
        id = id + 1  # Die ID erhöht sich dann um 1


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
        resultArr = search(keyword)

    # Wenn das Array aber leer ist, wird ein leeres String
    # der search - Methode mitgegeben, welche daraufhin
    # alle Einträge zurückgibt
    if not resultArr:
        resultArr = search(keyword)

    # Die jeweiligen Werte werden der Webseite weitergegeben und diese
    # werden dann mit den Ergebnissen gemeinsam auf der Webseite angezeigt
    return render_template("Suche.html", len=len(resultArr), arr=resultArr,
                           name=str(keyword) or 'StringIsNull',
                           keyword=keyword or "Keyword")

# Die search - Methode, welche die Eintrgäe such und
# demenstrpechend für die Anzeige bearbeitet
def search(keyword):
    # Die array für die Ergebnisse und
    # für die bearbeiteten Titel werden definiert
    resultArr = []
    titlearr = []
    # Gibt ein Array von den Titel und Pfade der Ergebnisse zurück
    searchArr, patharr = p.search(str(keyword))

    # Durchlauf von jedem Titel, es wird die capitalize Methode bei jedem
    # Titel ausgeführt und dann wird diese ins titlearr abgespeichert
    for title in searchArr:
        titlearr.append(str(title[0]).capitalize())

    # Alle Pfade zu den  Files laufen hier durch
    for f in range(len(patharr)):
        # Der Pfad zum richtigen png File wird erstellt
        thumbFile = patharr[f].removesuffix('.png') + '-thumb.png'
        # Mit den jeweiligen Werten wird ein Dictionary erstellt
        doc = {
            'title': titlearr[f],   # Der Titel
            'url': patharr[f],  # Der Pfad vom normalen Bild
            'thumb': thumbFile  # Der Pfad vom verkleinerten Bild
        }
        # Dieses Dictionary wird in ein Array abgespeichert
        resultArr.append(doc)
    return resultArr

#Hier wird das enstsprechende Bild mit den jeweiligen Keyword gehighlightet angezeigt
@app.route('/getImage/<path:url>/<string>')
def getImage(url, string):
    ts = datetime.datetime.now().timestamp()
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
    th = datetime.datetime.now().timestamp()
    highlight_image(url, '%s_alto_neu.xml' % url, getstring)
    thh = datetime.datetime.now().timestamp()
    name = pathlib.Path(url).stem
    path = (ordner + '\suche\\') + name + '_suche.jpg'
    print(path)
    delta1 = th - ts
    delta2 = thh - ts
    print("Timestamp 1: %d s" % delta1)
    print("Timestamp 2: %d s" % delta2)
    return render_template("getImage.html", url=path, name=string)  # , titlearr= sorted(searchArr))


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
    # return send_from_directory(r"C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract\suche", filename, as_attachment=True)


# Dort bekommt man die ganzen Bilder von einem Ordner / PDF File
###################
# noch nicht fertig#
###################
def getPictures(dir):
    picArr = []  # Array für die Bilder
    for f in dir:
        ff = f[0].removesuffix('.png_text.pdf')  # Die enstprechende Suffix wird entfernt
        ff = ff + '_bilder'  # und durch Bilder ersetzt
        for file in os.listdir(ff):  # jede Datei / jedes Bild im Ordner läuft hier durch
            folder = os.path.join(ff, file)  # Pfad der Datei
            print(folder)
            picArr.append(folder)  # Das Pfad der Datei wird in picArr gespeichert
            # img = Image.open(folder)
            # img.show()
        print('URL: ' + picArr[0])


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
    image.save((ordner + '\suche\\') + file, quality=10, dpi=(72, 72))



    # image.save(img+"_suche.jpg")
    # print(img+"_suche.jpg")


# Hier wird der gesamte Inhalt vom Suchordner gelöscht
def clearFolder():
    # Hier ist die Variable vom Pfad zum Suchordner
    folder = (ordner + '\suche')
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


parser = reqparse.RequestParser()
parser.add_argument("filename", required=True)
parser.add_argument("title", required=True)
parser.add_argument("url", required=True)
parser.add_argument("site_id", required=True)


class Artikel(Resource):
    def get(self, title):
        # Es wird nach dem passenden Eintrag gesucht
        if title == 'StringIsNull':
            title = ''
        data_get = search(title)
        # Wenn die keine Daten gefunden werden, wird eine Fehlermeldung ausgegeben
        if data_get == 404:
            abort(404, message=f"Eintrag {title} nicht gefunden!")
        # Dann wird der gefundene Einxtrag zurückgegeben
        return json.dumps(data_get), 200

    def post(self):
        args = parser.parse_args()
        Processor.process(fname=args["filename"], title=args["title"], DOCUMENT_URL=args["url"], DOCUMENT_SITE_ID=args["site_id"])
        return Processor.search(args["title"]), 201

    def delete(self):
        args = parser.parse_args()
        data_del = Processor.search(title=args["title"])
        if data_del == 404:
            abort(404, message=f"Eintrag {args['title']} nicht gefunden!")
        Processor.delete(title=args["title"], DOCUMENT_SITE_ID=args["site_id"])
        return '', 204


api.add_resource(Artikel, "/artikel/<title>")


def main():
    global p
    p = Processor('http://localhost:8983/solr/test')  # Hier wird ein Processor instanziert

    # directoryToAddAll(r'C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract', p, 'Titel', 'Artikel - Site')
    # p.delAll()
    # addAll(DOCUMENT_URL, p, )
    # p.process('0.png_text.txt', 'Cultblech_Logo_0')
    # p.delete('Cutblech_Logo_0')
    # p.search('Innsbruck')
    app.run(use_reloader=True, debug=True)  # Hier läuft die Flask Anwendung
    # p.server.commit()


# Die Main
if __name__ == '__main__':
    main()
