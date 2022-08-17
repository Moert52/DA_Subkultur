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
from flask import Flask,  render_template, request, url_for, flash, redirect, send_from_directory
from app.forms import SearchForm


DOCUMENT_SITE = 'Artikel' #Zentrale Document Site für die Add_All Methode
#DOCUMENT_URL = r'C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract\Cultblech_1'
app=Flask(__name__, template_folder='static/templates')  # Die Flask-Anwendung
app.config['SECRET_KEY'] = 'you-will-never-guess'

class Processor(object): #Klasse Processur - beinhaltet die Solr - Methoden

    #Initialisierung vom Processor Objekt
    def __init__(self, solr_server_url):
        self.server = Solr(solr_server_url)

    #Hier wird die "put" - Methode in Solr durchgeführt
    #def process(self, fname, title):
    def process(self, fname, title, DOCUMENT_URL, DOCUMENT_SITE_ID):
        base, _ = os.path.splitext(os.path.basename(fname))     #Dateiname ohne Extension
        url = DOCUMENT_URL + r"\%s" % (base) + '.pdf'       #Der Pfad von PDF Datei
        fPath = os.path.join(DOCUMENT_URL,fname)            #Pfad der txt Datei
        fp = open(fPath, encoding="iso-8859-1")     #Die Datei wird geöffnet
        #Hier wird der ganze Text der txt Datei in die content Variable gepseichert
        content = ''
        for line in fp:
            s = line.strip()
            print(s)
            if s and not s.startswith(('**', '==', '--')):
                content += s #str(s.encode(encoding='utf-8', errors='strict'))
        fp.close()
        document_id = u"%s-%s" % (DOCUMENT_SITE_ID, title)  #Hier ensteht eine ID mittels dem Titel und der Site
        logging.info("new document: %s" % (document_id,))
        t = os.path.getmtime(fPath)  #Hier wird die Zeit gespeichert
        #Hier ensteht ein Dictionary vom Artikel mit Title, site, content, id, url and date, welches auf Solr hochgeladen wird
        doc = {
            'id': hashlib.sha1(document_id.encode('utf-8')).hexdigest(), #die id wird gehasht
            'site': DOCUMENT_SITE_ID,
            'url': url,
            'title': title,
            'content': content,
            'last_modified': str(datetime.datetime.fromtimestamp(t))
        }


        #docStr = json.dumps(doc)
        try:
            self.server.add([doc])  #Hier wird das Document in Solr hochgeladen
            self.server.commit()
        except (IOError, Exception) as e:
            self.log.error("Failed to add documents to Solr: %s", e)

    #Hier wird ein Eintrag gelöscht auf Solr
    def delete(self, title, DOCUMENT_SITE_ID):
        document_id = u"%s-%s" % (DOCUMENT_SITE_ID, title)  #Mittels title und site bekommt man die gehashte ID
        logging.info("new document: %s" % (document_id,))
        print(hashlib.sha1(document_id.encode('utf-8')).hexdigest())
        self.server.delete(id=str(hashlib.sha1(document_id.encode('utf-8')).hexdigest())) #Hier wird der Eintrag mittels der ID gelöscht
        self.server.commit()

    #Hier wird nach einem Eintrag gesucht
    def search(self, title):
        #Hier wird im content, title und site nach dem schlüsselwort gesucht und in max. 500 Zeilen gespeichert
        results = self.server.search('content:*%s* title:*%s* site:*%s*' % (title, title, title), sort='order_i asc', rows=500,)
        self.server.commit()
        z = 0
        pathArr = []
        titlearr = []
        title.split()   # Die Wörter werden sozugagen aufgesplittet und array artig gespeichert
        for t in title:
            t.capitalize() #Jeder Buchstabe bei jedem Wort wird groß geschrieben

        title = title + ' %s ' % title.upper() + '%s ' % title.lower() #Das Schlüsselwort wird in 3 Arten gespeichert normal, alles groß, alles klein
        print(title)
        try:
            for result in results:  #Man läuft jetzt jedes einzelne Ergebnis durch
                z += 1  #Hier wird mitgezählt wie viele Ergebnisse gefunden wurden
                #print('URL: %s' % result['url'])
                pathArr.append(result['url'])    #Hier wird die Pfad des Ergebnissen gespeichert
                titlearr.append(result['title'])    #Hier wird der Titel des Ergebnisses gespeichert
            print(pathArr)
            getPictures(pathArr)    #Dann wird die getPictures Methode durchgeführt
            highlight(title, pathArr)   #Und die gesuchten Schlüsselwörter werden in den Bildern gespeichert

        #Hier kommt die entsprechende Fehlermedlung wenn es eine gibt
        except Exception as e:
            self.log.error("Kein Content vorhanden bei %s \nError: %s", result['title'], e)

        print('Es wurden %s Eintraege gefunden' % z)

        #Der Titel Array wird zurückgegeben
        return titlearr

    #Methode zum Löschen aller Einträge auf Solr
    def delAll(self):
        self.server.delete(q='*:*')
        print("Alles gelöscht")

# Der Ordner, wo alle Subordner, die durch die Ocr enstellt wurde, wird durchgelaufen und ladet die jeweiligen
# Einträge auf Solr hoch
def directoryToAddAll(directory, processor, title, site):  #
    dirArr = []     #Array wo der Pfad aller Subordner hinzugefügt wird
    rootdir = directory    #rootdir ist des Hauptordner, wo sich die Subordner befinden
    for dir in os.listdir(rootdir):    # Hier wird jeder einzelner Ordner
        d = os.path.join(rootdir, dir)     # Mit dem richtigen Pfad
        if os.path.isdir(d):    # Und mit der Überprüfung, ob es ein Ordner ist
            dirArr.append(d)    #i in die dirArr gespeichert
    # Dann wird geprüft ob der Ordner PDF & Suche im Array ist
    if r"C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract\PDF" in dirArr:
        # Und jenachdem werden diese vom Array entfernt
        dirArr.remove(r"C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract\PDF")
    if r"C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract\suche" in dirArr:
        dirArr.remove(r"C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract\suche")

    #print(dirArr)

    for i in dirArr:    # dirArr wird in einer for Schleife durchgelaufen
        DOCUMENT_URL = i    # der Pfad wird gespeichert
        #addAll(i, processor, 'Titel')
        # Und dann wird die addAll Methode ausgeführt, wobei jeder Eintrag die gleiche Site und den gleichen Titel bekommt
        addAll(i, processor, title, site)

#Hier wird jede txt Datei in einem Ordner auf Solr hochgeladen
#def addAll(dir, processor, title):
def addAll(directory, processor, title, DOCUMENT_URL):
    id = 0   # Hier bekommt jeder Eintrag eine ID mit dem Filenamen
    for f in glob.glob("%s/*.txt" % directory):     #Hier läuft jede einzelner txt Datei + ihren Pfad im Ordner durch
        file = f.removeprefix(directory+'\\')  #Danach bekommt man den Dateinamen + Extension
        print(file)
        name = os.path.basename(directory)  # Hier bekommt man nur den Dateinamen ohne Extension

        #processor.process(file, name + '_%s' % str(id))
        #Dann wird die txt Datei auf Solr hochgeladen
        processor.process(file, name+'_%s' % str(id), DOCUMENT_URL, DOCUMENT_SITE)
        id=id+1   # Die ID erhöht sich dann um 1



@app.route('/index')
def index():
    return render_template('Start.html')


@app.route('/suche', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        keyword = request.form['keyword']

        if not keyword:
            flash('Keyword is required!')
        else:
            return redirect(url_for('homepage', name=keyword))
    return render_template('test.html')


@app.route('/suche/<name>')
def homepage(name):
    if request.method == 'POST':
        keyword = request.form['keyword']

        if not keyword:
            flash('Keyword is required!')
        else:
            keywords.append(keyword)
            return redirect(url_for('homepage', name=keyword))
    # returning index.html and list
    # and length of list to html page
    titlear = p.search(str(name))
    titlearr = []
    arr = []
    print(titlear)
    for title in titlear:
        titlearr.append(str(title[0]).capitalize())

    titlearr.sort()
    print(titlearr)
    #titlear.sort(key = lambda x: x.lower())
    dirr = r"C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract\suche"
    for f in glob.glob("%s/*.jpg" % dirr):
            ff = os.path.join(dirr, f)
            doc = {
                'title': titlearr[glob.glob("%s/*.jpg" % dirr).index(f)],
                'url': os.path.basename(ff)
            }
            #print(os.path.basename(ff))
            arr.append(doc)
    #print(arr)

    return render_template("test.html", len=len(arr), arr=arr, name=str(name)) #, titlearr= sorted(titlear))

#first create the route
@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(r"C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract\suche", filename, as_attachment=True)

def getPictures(dir):
    arr=[]
    for f in dir:
        ff = f[0].removesuffix('.png_text.pdf')


        ff = ff + '_bilder'
        for file in os.listdir(ff):
            folder = os.path.join(ff, file)
            print(folder)
            arr.append(folder)
            #img = Image.open(folder)
            #img.show()
        print('URL: ' + arr[0])


def highlight(string, dir):
    #print(os.path.basename(dir[0]))
    #dic = dir[0].removesuffix('\\'+ os.path.basename(dir[0]))
    #dic = dic.replace("\\\\", "\\")
    #print(dic)
    #for f in glob.glob("%s/*.png" % dic):
        #ff = os.path.join(dic, f)
        #highlight_image(ff, '%s_alto_neu.xml' % ff, string)
    clearFolder()
    for f in dir:
        ff = f[0].removesuffix('_text.pdf')
        ff = ff.replace("\\\\", "\\")
        highlight_image(ff, '%s_alto_neu.xml' % ff, string)

def highlight_image(img, xml, string):
    #print(xml)
    stri = string.split()
    #print(stri)
    root = ET.parse(xml)
    image = Image.open(img)

    anz = 1
    for p in elementpath.select(root, '//String', {'' : 'http://www.loc.gov/standards/alto/ns-v3#'}):
        st = str(p.attrib["CONTENT"])
        for e in stri:
            if re.search(e, st):
                gid = p.attrib["ID"]
                x0 = int(p.attrib["HPOS"])
                y0 = int(p.attrib["VPOS"])
                x1 = int(x0 + int(p.attrib["WIDTH"]))
                y1 = int(y0 + int(p.attrib["HEIGHT"]))
                shape = [x0-7, y0-10,x1+8,y1+14 ]


                TINT_COLOR = (0, 0, 0)  # Black
                TRANSPARENCY = .50  # Degree of transparency, 0-100%
                OPACITY = int(255 * TRANSPARENCY)


                anz+=1
                #print (gid, shape)
                image = image.convert("RGBA")
                overlay = Image.new('RGBA', image.size, TINT_COLOR + (0,))
                draw = ImageDraw.Draw(overlay)  # Create a context for drawing things on it.
                #draw.text((x1, y1), gid, align="right", font=ImageFont.load_default(), fill="green")
                draw.rectangle(shape, fill=(255, 255, 80, 130), outline="black")

                # Alpha composite these two images together to obtain the desired result.
                image = Image.alpha_composite(image, overlay)
                image = image.convert("RGB")  # Remove alpha for saving in jpg format.
                dic = img.removeprefix(r'C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract')
                #print('JA:' +dic)
                file = dic + '_suche.jpg'
                file = file.replace("\\", "-")
                #print(file)
                image.save(r'C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract\suche\\' + file)
                #image.save(img+"_suche.jpg")
                #print(img+"_suche.jpg")


def clearFolder():
    folder = r'C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract\suche'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))




if __name__ == '__main__':

    p = Processor('http://localhost:8983/solr/test')
    directoryToAddAll(r'C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract', p, 'Titel', 'Artikel - Site')
    #p.delAll()
    #addAll(DOCUMENT_URL, p, )
    #p.process('0.png_text.txt', 'Cultblech_Logo_0')
    #p.delete('Cutblech_Logo_0')
    #p.search('Innsbruck')

    #app.run(use_reloader=True, debug=True)
    #p.server.commit()