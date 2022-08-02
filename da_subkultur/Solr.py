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
from flask import Flask, render_template, send_from_directory

DOCUMENT_SITE_ID = 'Artikel'
#DOCUMENT_URL = r'C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract\Cultblech_1'
app=Flask(__name__, template_folder='static/templates')  # Die Flask-Anwendung

class Processor(object):

    def __init__(self, solr_server_url):
        self.server = Solr(solr_server_url)

    #def process(self, fname, title):
    def process(self, fname, title, DOCUMENT_URL):
        base, _ = os.path.splitext(os.path.basename(fname))
        url = DOCUMENT_URL + r"\%s" % (base) + '.pdf'
        fPath = os.path.join(DOCUMENT_URL,fname)
        fp = open(fPath, encoding="iso-8859-1")
        content = ''
        for line in fp:
            s = line.strip()
            print(s)
            if s and not s.startswith(('**', '==', '--')):
                content += s #str(s.encode(encoding='utf-8', errors='strict'))
        fp.close()
        document_id = u"%s-%s" % (DOCUMENT_SITE_ID, title)
        logging.info("new document: %s" % (document_id,))
        t = os.path.getmtime(fPath)
        doc = {
            'id': hashlib.sha1(document_id.encode('utf-8')).hexdigest(),
            'site': DOCUMENT_SITE_ID,
            'url': url,
            'title': title,
            'content': content,
            'last_modified': str(datetime.datetime.fromtimestamp(t))
        }

        docStr = json.dumps(doc)
        print(docStr)
        try:
            self.server.add([doc])
            self.server.commit()
        except (IOError, Exception) as e:
            if not self.silently_fail:
                raise

            self.log.error("Failed to add documents to Solr: %s", e)

    def delete(self, title):
        document_id = u"%s-%s" % (DOCUMENT_SITE_ID, title)
        logging.info("new document: %s" % (document_id,))
        print(hashlib.sha1(document_id.encode('utf-8')).hexdigest())
        self.server.delete(id=str(hashlib.sha1(document_id.encode('utf-8')).hexdigest()))
        self.server.commit()

    def search(self, title):
        results = self.server.search('content:*%s* title:*%s* site:*%s*' % (title, title, title), sort='order_i asc', rows=500,)
        self.server.commit()
        z = 0
        arr = []
        title.split()
        for t in title:
            t.capitalize()

        title = title + ' %s ' % title.upper() + '%s ' % title.lower()
        print(title)
        try:
            for result in results:
                z += 1
                #print('URL: %s' % result['url'])
                arr.append(result['url'])
            print(arr)
            getPictures(arr)
            highlight(title, arr)
        except Exception as e:
            self.log.error("Kein Content vorhanden bei %s \nError: %s", result['title'], e)

        print('Es wurden %s Eintraege gefunden' % z)


    def delAll(self):
        self.server.delete(q='*:*')
        print("Alles gelöscht")


def dire(dir, p):
    arr = []
    rootdir = dir
    for file in os.listdir(rootdir):
        d = os.path.join(rootdir, file)
        if os.path.isdir(d):
            arr.append(d)
    if r"C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract\PDF" in arr or r"C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract\PDF" in arr:
        arr.remove(r"C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract\PDF")
        arr.remove(r"C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract\suche")

    #print(arr)
    for i in arr:
        DOCUMENT_URL = i
        #addAll(i, p, 'Titel')
        addAll(i, p, 'Titel', DOCUMENT_URL)


#def addAll(dir, p, title):
def addAll(dir, p, title, DOCUMENT_URL):
    z = 0
    for f in glob.glob("%s/*.txt" % dir):
        ff = os.path.join(dir, f)
        file = ff.removeprefix(dir+'\\')
        print(file)
        name = os.path.basename(dir)

        #p.process(file, name + '_%s' % str(z))
        p.process(file, name+'_%s' % str(z), DOCUMENT_URL)
        z=z+1

def extract_pdf(fname):
    pdffile = fname
    doc = fitz.open(pdffile)#

    for i in range(doc.page_count):
        page = doc.load_page(i)  # number of page
        mat = fitz.Matrix(5,5) # To get higher resolution
        pix = page.get_pixmap(matrix=mat)
        dir, extension = os.path.splitext(pdffile)
        Path(dir).mkdir(exist_ok=True)
        pix.save("%s/%d.png" % (dir,i))



@app.route('/suche/<name>')
def homepage(name):
    # returning index.html and list
    # and length of list to html page

    p.search(str(name))
    arr = []
    dirr = r"C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract\suche"
    for f in glob.glob("%s/*.jpg" % dirr):
        ff = os.path.join(dirr, f)
        print(os.path.basename(ff))
        arr.append(os.path.basename(ff))
    print(arr)

    return render_template("test.html", len=len(arr), arr=arr)

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
                shape = [x0, y0,x1,y1 ]


                TINT_COLOR = (0, 0, 0)  # Black
                TRANSPARENCY = .50  # Degree of transparency, 0-100%
                OPACITY = int(255 * TRANSPARENCY)


                anz+=1
                #print (gid, shape)
                image = image.convert("RGBA")
                overlay = Image.new('RGBA', image.size, TINT_COLOR + (0,))
                draw = ImageDraw.Draw(overlay)  # Create a context for drawing things on it.
                #draw.text((x1, y1), gid, align="right", font=ImageFont.load_default(), fill="green")
                draw.rectangle(shape, fill=(255, 127, 127, 127), outline="black")

                # Alpha composite these two images together to obtain the desired result.
                image = Image.alpha_composite(image, overlay)
                image = image.convert("RGB")  # Remove alpha for saving in jpg format.
                dic = img.removeprefix(r'C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract')
                #print('JA:' +dic)
                file = dic + '_suche.jpg'
                file = file.replace("\\", "-")
                #print(file)
                image.save(r'C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract\suche\\' + file)
                image.save(img+"_suche.jpg")
                print(img+"_suche.jpg")


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
    dire(r'C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract', p)
    #p.delAll()
    #addAll(DOCUMENT_URL, p, )
    #p.process('0.png_text.txt', 'Cultblech_Logo_0')
    #p.delete('Cutblech_Logo_0')
    p.search('Innsbruck')

    app.run(use_reloader=True, debug=True)
    #p.server.commit()