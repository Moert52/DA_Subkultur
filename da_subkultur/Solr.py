# -*- coding: iso-8859-1 -*-
import shutil
from flask_restful import Api, Resource, reqparse, abort
from pysolr import Solr
import os
import logging
import hashlib
import datetime
import xml.etree.ElementTree as ET
import elementpath
from PIL import Image, ImageDraw, ImageFont
import glob
from lxml import etree
import io
import json
import glob
import re
from flask import Flask, render_template, request, url_for, flash, redirect, send_from_directory, jsonify
import pathlib
import datetime
from urllib.parse import urlparse, unquote
from pathlib import Path

DOCUMENT_SITE = 'Artikel'  # Zentrale Document Site f�r die Add_All Methode
# DOCUMENT_URL = r'C:\Users\mertc\Desktop\HTL - F�cher\Diplomarbeit\Test-tesseract\Cultblech_1'
app = Flask(__name__, template_folder='static/templates')  # Die Flask-Anwendung
api = Api(app)
app.config['SECRET_KEY'] = 'you-will-never-guess'

# Mert's Ordner
ordner = r'C:\Users\mertc\Desktop\HTL - F�cher\Diplomarbeit\Test-tesseract'

# Leo's Ordner
# ordner = r'D:\Diplomarbeit\test_tesseract'

# Melih's Ordner
#ordner = r'C:\Users\Anwender\Documents\SCHULE\Diplomarbeit\test_tesseract'



class Processor(object):  # Klasse Processor - beinhaltet die Solr - Methoden

    # Initialisierung vom Processor Objekt
    def __init__(self, solr_server_url):
        self.server = Solr(solr_server_url)

    # Hier wird die "put / patch" - Methode in Solr durchgef�hrt
    # def process(self, fname, title):
    def process(self, fname, title, DOCUMENT_URL, DOCUMENT_SITE_ID):
        #Hier wird der Pfad und der Name der Datei enstprechend bearbeitet
        base, _ = os.path.splitext(os.path.basename(fname))  # Dateiname ohne der Dateiendung
        url = DOCUMENT_URL + r"\%s" % (base) + '.txt'  # Der Pfad der txt - Datei (ohne den Dateinamen)
        fPath = os.path.join(DOCUMENT_URL, fname)  # Der Pfad der txt - Datei mit dem Dateinamen

        # Die Datei wird ge�ffnet
        txt_file = open(fPath, encoding="iso-8859-1")

        # Teil der Methode wo der ganze Text von der txt - Datei
        # in die content - Variable f�r Solr gespeichert wird
        content = ''
        for line in txt_file: #Jede Zeile in der Datei l�uft hier durch
            s = line.strip() #Die Zeile wird entsprechend bearbeitet
            # Dann wird kontrolliert, ob die Zeile �berhaupt irgendeinen
            # Text enth�lt und nicht mit undg�ltigen Zeichen anf�ngt
            if s and not s.startswith(('*', '=', '-')):
                s = s.decode('iso-8859-1', 'ignore')
                print(s)
                content = content + " " + s  #str(s.encode(encoding='utf-8', errors='strict'))
        txt_file.close() #Die Datei wird geschlossen
        print(content)

        # Die ID wird anhand dem Title und der Site erstellt
        document_id = u"%s-%s" % (DOCUMENT_SITE_ID, title)  # Hier ensteht eine ID mittels dem Titel und der Site
        logging.info("new document: %s" % (document_id,))
        t = os.path.getmtime(fPath)  # Hier wird die Zeit gespeichert

        # Hier ensteht ein Dictionary vom Artikel mit Title, site,
        # content, id, url and date, welches auf Solr hochgeladen wird
        doc = {
            'id': hashlib.sha1(document_id.encode('utf-8')).hexdigest(),  # die id wird gehasht
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
            self.log.error("Failed to add documents to Solr: %s", e)

    # Hier wird ein Eintrag gel�scht auf Solr
    def delete(self, title, DOCUMENT_SITE_ID):
        document_id = u"%s-%s" % (DOCUMENT_SITE_ID, title)  # Mittels title und site bekommt man die gehashte ID
        logging.info("new document: %s" % (document_id,))
        print(hashlib.sha1(document_id.encode('utf-8')).hexdigest())
        self.server.delete(id=str(
            hashlib.sha1(document_id.encode('utf-8')).hexdigest()))  # Hier wird der Eintrag mittels der ID gel�scht
        self.server.commit()

    # Hier wird nach einem Eintrag gesucht
    def search(self, title):
        # Hier wird im content, title und site nach dem schl�sselwort gesucht und in max. 500 Zeilen gespeichert
        if title == '':
            results = self.server.search('*:*', sort='order_i asc', rows=500, )
        else:
            results = self.server.search('content:*%s* title:*%s* site:*%s*' % (title, title, title),
                                         sort='order_i asc',
                                         rows=500, )
        self.server.commit()
        z = 0
        pathArr = []
        titlearr = []

        try:
            for result in results:  # Man l�uft jetzt jedes einzelne Ergebnis durch
                z += 1  # Hier wird mitgez�hlt wie viele Ergebnisse gefunden wurden
                # print('URL: %s' % result['url'])
                url = str(result['url'][0])
                path = os.path.dirname(url)
                p = pathlib.Path(url).stem
                path = os.path.join(path, p.removesuffix('png_text') + 'png')

                pathArr.append(path)  # Hier wird der Pfad des Ergebnissen gespeichert
                titlearr.append(result['title'])  # Hier wird der Titel des Ergebnisses gespeichert
            print(pathArr)
            # getPictures(pathArr)    #Dann wird die getPictures Methode durchgef�hrt
            # highlight(title, pathArr)   #Und die gesuchten Schl�sselw�rter werden in den Bildern gespeichert

        # Hier kommt die entsprechende Fehlermedlung wenn es eine gibt
        except Exception as e:
            error = self.log.error("Kein Content vorhanden bei %s \nError: %s", result['title'], e)
            return 404

        print('Es wurden %s Eintraege gefunden' % z)

        # Der Titel Array wird zur�ckgegeben
        return titlearr, pathArr

    # Methode zum L�schen aller Eintr�ge auf Solr
    def delAll(self):
        self.server.delete(q='*:*')
        print("Alles gel�scht")


# Der Ordner, wo alle Subordner, die durch die Ocr enstellt wurde, wird durchgelaufen und ladet die jeweiligen
# Eintr�ge auf Solr hoch
def directoryToAddAll(directory, processor, title, site):  #
    dirArr = []  # Array wo der Pfad aller Subordner hinzugef�gt wird
    rootdir = directory  # rootdir ist des Hauptordner, wo sich die Subordner befinden
    for dir in os.listdir(rootdir):  # Hier wird jeder einzelner Ordner
        d = os.path.join(rootdir, dir)  # Mit dem richtigen Pfad
        if os.path.isdir(d):  # Und mit der �berpr�fung, ob es ein Ordner ist
            dirArr.append(d)  # i in die dirArr gespeichert
    # Dann wird gepr�ft ob der Ordner PDF & Suche im Array ist
    if (ordner + "\PDF") in dirArr:
        # Und jenachdem werden diese vom Array entfernt
        dirArr.remove((ordner + "\PDF"))
    if (ordner + "\suche") in dirArr:
        dirArr.remove((ordner + "\suche"))

    # print(dirArr)

    for i in dirArr:  # dirArr wird in einer for Schleife durchgelaufen
        DOCUMENT_URL = i  # der Pfad wird gespeichert
        # addAll(i, processor, 'Titel')
        # Und dann wird die addAll Methode ausgef�hrt, wobei jeder Eintrag die gleiche Site und den gleichen Titel bekommt
        addAll(i, processor, title, site)


# Hier wird jede txt Datei in einem Ordner auf Solr hochgeladen
# def addAll(dir, processor, title):
def addAll(DOCUMENT_URL, processor, title, site):
    id = 0  # Hier bekommt jeder Eintrag eine ID mit dem Filenamen
    for f in glob.glob("%s/*.txt" % DOCUMENT_URL):  # Hier l�uft jede einzelner txt Datei + ihren Pfad im Ordner durch
        file = f.removeprefix(DOCUMENT_URL + '\\')  # Danach bekommt man den Dateinamen + Extension
        print(file)
        name = os.path.basename(DOCUMENT_URL)  # Hier bekommt man nur den Dateinamen ohne Extension

        # processor.process(file, name + '_%s' % str(id))
        # Dann wird die txt Datei auf Solr hochgeladen
        processor.process(file, name + '_%s' % str(id), DOCUMENT_URL, DOCUMENT_SITE)
        id = id + 1  # Die ID erh�ht sich dann um 1


# Hier wird mittels dem keyword nach die jeweiligen Bilder gesucht
@app.route('/suche/<key>', methods=('GET', 'POST'))
@app.route('/suche', methods=('GET', 'POST'))
def getSearch(key=''):
    print(key)
    print("search")
    keyword = ""
    if key != '':
        keyword = key

    resultArr = []  # ein Array f�r die Ergebnisse, nachdem Sie angepasst wurden
    if request.method == 'POST':  # Wenn das keyword submitted wird
        keyword = request.form['keyword']  # wird das eingegebene keyword in eine Variable gespeichert
        resultArr = search(keyword)
    if not resultArr:
        resultArr = search(keyword)
    # Die entsprechenden Werte werden weitergegeben und die Ergebnise werden dann auf der Webseite angezeigt
    return render_template("Suche.html", len=len(resultArr), arr=resultArr,
                           name=str(keyword) or 'StringIsNull',
                           keyword=keyword or "Keyword")  # , titlearr= sorted(searchArr))


def search(keyword):
    resultArr = []  # ein Array f�r die Ergebnisse, nachdem Sie angepasst wurden
    titlearr = []  # Wieder eine Titelarray, aber f�r die Titel nachdem capitalize
    searchArr, patharr = p.search(str(keyword))  # Gibt einen Array von den Titeln der Ergebnissen bei der Suche
    print("asas" + str(patharr))
    # print(searchArr)
    # Jeder einzelner title l�uft hier durch, bei der die capitalize Methode durchgef�hrt wird
    for title in searchArr:
        titlearr.append(str(title[0]).capitalize())
    titlearr.sort()  # Danach wird das titleArr nach dem Alphabet sortiert
    # print(titlearr)
    # Variable zum Suchordner
    resultDirectory = (ordner + "\suche")
    for f in patharr:  # Alle jpg Files im Suchordner werden durchgelaufen
        # ff = os.path.join(resultDirectory, f)   #der Pfad zum jpg File
        # Dann wird ein Dictionary erstellt mit den entsprechen Weten
        thumbFile = f.removesuffix('.png') + '-thumb.png'
        print(thumbFile)
        doc = {
            'title': pathlib.Path(str(f)).stem,
            'url': f,  # str(f.removeprefix("['"))
            'thumb': thumbFile
        }
        # print(os.path.basename(ff))
        resultArr.append(doc)  # Das Dictionary wird dann ins result - Array gepseichert
    print(resultArr)
    return resultArr

#Hier wird das enstsprechende Bild mit den jeweiligen Keyword gehighlightet angezeigt
@app.route('/getImage/<path:url>/<string>')
def getImage(url, string):
    ts = datetime.datetime.now().timestamp()
    clearFolder()
    print(url)
    print(string)
    if string != "StringIsNull":
        strr = string.lower()

        strr = strr.title()  # Jeder Buchstabe bei jedem Wort wird gro� geschrieben
        strr = strr.split()

        getstring = ''
        for s in strr:
            getstring = '%s %s %s %s' % (s, s.upper(), s.lower(),
                                         getstring)  # +  string + ' %s ' % string.upper() + '%s ' % string.lower()  # Das Schl�sselwort wird in 3 Arten gespeichert normal, alles gro�, alles klein
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


# Hier kann man die entsprechenden Bilder downloaden bzw auf der Flask anzeigen
@app.route('/uploads/<path:filename>')
def download_file(filename):
    folder = os.path.dirname(filename)
    print(folder)
    name = os.path.basename(filename)
    print(name)
    return send_from_directory(folder, name, as_attachment=True)
    # return send_from_directory(r"C:\Users\mertc\Desktop\HTL - F�cher\Diplomarbeit\Test-tesseract\suche", filename, as_attachment=True)


# Dort bekommt man die ganzen Bilder von einem Ordner / PDF File
###################
# noch nicht fertig#
###################
def getPictures(dir):
    picArr = []  # Array f�r die Bilder
    for f in dir:
        ff = f[0].removesuffix('.png_text.pdf')  # Die enstprechende Suffix wird entfernt
        ff = ff + '_bilder'  # und durch Bilder ersetzt
        for file in os.listdir(ff):  # jede Datei / jedes Bild im Ordner l�uft hier durch
            folder = os.path.join(ff, file)  # Pfad der Datei
            print(folder)
            picArr.append(folder)  # Das Pfad der Datei wird in picArr gespeichert
            # img = Image.open(folder)
            # img.show()
        print('URL: ' + picArr[0])


# Hier wird der ganze Inhalt vom Suchordner gel�scht und wieder neue Ergebnisse draufgespeichert
def highlight(string, pathArr):
    clearFolder()  # die clearFolder Methode wird durchgef�hrt
    for f in pathArr:  # Jeder einzelner Pfad im mitgegebnen Array l�uft hier durch
        ff = f[0].removesuffix('_text.pdf')  # Die entsprechende Suffix wird entfernt
        ff = ff.replace("\\\\", "\\")
        highlight_image(ff, '%s_alto_neu.xml' % ff, string)  # Dann wird die highlight_image Methode durchgef�hrt


def highlight_image(img, xml, string):
    dic = os.path.basename(img)
    # print('JA:' +dic)
    dic = dic.removesuffix('.png')
    file = dic + '_suche.jpg'  # die entsprechende suffix wird hinzugef�gt
    file = file.replace("\\", "-")  # Die enstprechenden Zeichen werden ersetzt
    # print(file)
    # print(xml)

    # print(stri)
    root = ET.parse(xml)  # Die xml wird ge�ffnet
    image = Image.open(img)  # Die jpg Datei wird ge�ffnet
    ts = datetime.datetime.now().timestamp()
    if string != 'StringIsNull':  # Wenn der String null ist soll er das normale Bild ohne es zu higlighten abspeichern
        stri = string.split()  # Der String wird gesplitet (je nachdem, ob das keyword mehrere W�rter lang ist) & als array gespeichert
        print(stri)
        # Jedes String element in dem xml File l�uft hier durch
        for p in elementpath.select(root, '//String', {'': 'http://www.loc.gov/standards/alto/ns-v3#'}):
            st = str(p.attrib["CONTENT"])  # den Content vom String Element wird abgespeichert
            for e in stri:  # Dann l�uft jedes einzelne wort vom keyword hier durch
                if re.search(e, st):  # Dann wird gepr�ft ob das keyword im content vom String vorhanden ist
                    th = datetime.datetime.now().timestamp()
                    print("x")
                    # gid = p.attrib["ID"]
                    x0 = int(p.attrib["HPOS"])  # Die x - Position wird gepseichert
                    y0 = int(p.attrib["VPOS"])  # Die y - Position wird gepseichert
                    x1 = int(x0 + int(p.attrib["WIDTH"]))  # Hier wird die Breite gepseichert
                    y1 = int(y0 + int(p.attrib["HEIGHT"]))  # Hier wird die H�he gespeichert
                    shape = [x0 - 7, y0 - 10, x1 + 8,
                             y1 + 14]  # Hier werden die entsprechenden Gr��en in einem Array gespeichert

                    TINT_COLOR = (0, 0, 0)  # Black     #Die Schriftfarbe ist schwarz
                    TRANSPARENCY = .50  # Degree of transparency, 0-100%    #Die Transparenz bei 50%
                    OPACITY = int(255 * TRANSPARENCY)

                    # print (gid, shape)
                    image = image.convert("RGBA")  # Das jpg File wird ins RGBA Format konvertiert
                    overlay = Image.new('RGBA', image.size, TINT_COLOR + (
                        0,))  # und mit den entsprechenden Werten bekommt sozusagen einen Filter
                    draw = ImageDraw.Draw(
                        overlay)  # EIen Variable wird erstellt umd auf dem Bild etwas zu zeichnen / malen.
                    # draw.text((x1, y1), gid, align="right", font=ImageFont.load_default(), fill="green")
                    draw.rectangle(shape, fill=(255, 255, 80, 130),
                                   outline="black")  # Es wird ein Rechteck gemalt auf dem content
                    # vom String, ist dann sozusagen ein Highlight auf das keyword im jpg File gemalt

                    # Alpha composite these two images together to obtain the desired result.
                    image = Image.alpha_composite(image, overlay)  # Hier wird das ganze format
                    image = image.convert("RGB")  # und Filter zur�ckgesetut

                    # Die gesuchte Artikelseite wird im entsprechenden Ordner gespeichert
                    delta1 = th - ts
                    print("Timestamp 1: %d s" % delta1)
    ts = datetime.datetime.now().timestamp()
    image.save((ordner + '\suche\\') + file, quality=10,
               dpi=(72, 72))
    th = datetime.datetime.now().timestamp()
    delta1 = th - ts
    print("Timestamp 3 %d s" % delta1)  # Laufzeit liegt beim Speichern
    # image.save(img+"_suche.jpg")
    # print(img+"_suche.jpg")


# Hier wird der gesamte Inhalt vom Suchordner gel�scht
def clearFolder():
    # Hier ist die Variable vom Pfad zum Suchordner
    folder = (ordner + '\suche')
    for filename in os.listdir(folder):  # Jeder einzelne Datei im Ordner l�uft hier durch
        file_path = os.path.join(folder, filename)  # Hier bekommt man den Pfad zu der Datei
        try:
            # Dann wird wird gepr�ft ob es sich um Eine Datei oder einen Link haltet
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Wird dementsprechend gel�scht
            elif os.path.isdir(file_path):  # Sonst wird gepr�ft ob es sich um einen Subordner handelt
                shutil.rmtree(file_path)  # Dann wird der Subordner gel�scht
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
        data_get = Processor.search(title)
        # Wenn die keine Daten gefunden werden, wird eine Fehlermeldung ausgegeben
        if data_get == 404:
            abort(404, message=f"Eintrag {title} nicht gefunden!")
        # Dann wird der gefundene Eintrag zur�ckgegeben
        return jsonify(data_get), 200

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

    # directoryToAddAll(r'C:\Users\mertc\Desktop\HTL - F�cher\Diplomarbeit\Test-tesseract', p, 'Titel', 'Artikel - Site')
    # p.delAll()
    # addAll(DOCUMENT_URL, p, )
    # p.process('0.png_text.txt', 'Cultblech_Logo_0')
    # p.delete('Cutblech_Logo_0')
    # p.search('Innsbruck')
    app.run(use_reloader=True, debug=True)  # Hier l�uft die Flask Anwendung
    # p.server.commit()


# Die Main
if __name__ == '__main__':
    main()
