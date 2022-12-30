import fitz  # https://pymupdf.readthedocs.io/en/latest/tutorial.html
import os
from pathlib import Path
import pytesseract
import xml.etree.ElementTree as ET
import elementpath
from PIL import Image, ImageDraw, ImageFont
import glob
# from lxml import etree
import io

# Hier wird Tesseract definiert
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Mert's Ordner
#ordner = r'C:\\Users\\mertc\\Desktop\\HTL - Fächer\\Diplomarbeit\\Test-tesseract\\'

# Leo's Ordner
# ordner = r'D:\Diplomarbeit\test_tesseract\\'

# Melih's Ordner
ordner = r'C:\Users\Anwender\Documents\SCHULE\Diplomarbeit\test_tesseract\\'


# hier wird von alle xml Files der Text ausgelesen und die Bilder mit einem Rahmen gekennzeichnet
def highlight_images(dir):
    for f in glob.glob("%s/*.png" % dir):  # Jedes einzelne png File im Ordner läuft hier durch
        ff = os.path.join(dir, f)  # Hier wird der Pfad den png Files gepseichert
        if '-thumb' in ff:  # Wenn der Pfad ff enthält
            continue  # soll er zur nächsten Iteration springen
        print(ff)

        highlight_image(ff, '%s_alto_neu.xml' % ff)  # Die Higlight_image Methode wird durchgeführt
        get_Text(ff, '%s_alto_neu.xml' % ff)  # Die get_Text Methode wird druchgeführt
        # output = aw.Document()
        # input = aw.Document(ff + "_text.txt")
        # Append the source document to the end of the destination document.
        # output.append_document(input, aw.ImportFormatMode.KEEP_SOURCE_FORMATTING)
        # output.save(ff+"Output.docx")


# Hier werden die Dartstellungen mittels einer Umrandung gekennzeichnet
# und die Methode zum Ausschneiden der Subbilder wird ausgeführt
def highlight_image(img, xml):
    print(xml)
    #Als Erstes wird das XML - File und die PNG - Datei geöffnet
    root = ET.parse(xml)
    image = Image.open(img)

    # Zum Zeichnen auf der PNG - Datei wird dafür
    # extra eine Instanz erzeugt
    draw = ImageDraw.Draw(image)
    anz = 1  # Dient für die Anzahl der erkannten SubBilder

    # Hier wird ein neuer Ordner für die Subbilder erstellt,
    # wo diese dann später nach dem Ausschneiden abgespeichert werden
    ff = os.path.splitext(img)[0]
    dir = ff + "_bilder"
    Path(dir).mkdir(exist_ok=True)


    # Jedes erkannte Darstellung läuft hier durch
    for p in elementpath.select(
            root, '//Illustration',
            {'': 'http://www.loc.gov/standards/alto/ns-v3#'}):

        # Die ID, Position und die Größe werden abgespeichert,
        # danach werden diese in einem Array gespeichert
        gid = p.attrib["ID"]
        x0 = int(p.attrib["HPOS"])
        y0 = int(p.attrib["VPOS"])
        x1 = int(x0 + int(p.attrib["WIDTH"]))
        y1 = int(y0 + int(p.attrib["HEIGHT"]))
        shape = [x0, y0, x1, y1]

        #Die crop_img - Methode wird ausgeführt
        crop_img(img, shape, anz, dir)
        anz += 1  # die Anzahl der erkannten Subbilder wird um 1 erhöhrt

        # Auf der jeweiligen PNG - Seite, werden die ganzen erkannten
        # Subbilder mit einer grünen Umrandung gekennzeichnet.
        draw.text((x1, y1), gid, align="right",
                  font=ImageFont.load_default(), fill="green")
        draw.rectangle(shape, fill=None, outline="green")

    # Die Seite mit den gekennzeichneten subbilder wird
    # in einer neuer PNG - Datei abgespeichert
    image.save(img + "_col.jpg")


# Hier wird der erkannte Text vom XML - File ausgelesen
# und in einem txt - Dokument abgespeichert
# (Mit Berücksichtigung der Zeilenumbrüche)
def get_Text(img, xml):
    # Hier werden die notwendigen Instanzen erstellt
    # und das XML - Dokument wird geöffnet
    print(xml)
    root = ET.parse(xml)
    txtArr = []  # Array umd en ganzen Content abzuspeichern
    rowArr = []  # Array um dei ganzen Wörter in einer Zeile abzuspeichern
    done = False
    althoe = 0  # hier wird die alte Hoehe vom vorigen Element gespeichert
    # for l in elementpath.select(root, '//TextLine', {'': 'http://www.loc.gov/standards/alto/ns-v3#'}):
    # an = 0
    # print(str(l.attrib["CONTENT"]))

    # Jedes String Element läuft hier durch
    for t in elementpath.select(
            root, '//String',
            {'': 'http://www.loc.gov/standards/alto/ns-v3#'}):
        # Der Inhalt und die y - Position vom
        # jeweiligen String Element werden gespeichert
        st = str(t.attrib["CONTENT"])  # Der Content
        print(st)
        height = int(t.attrib["VPOS"])  # die y - Position wird gespeichert

        # Die done Abfrage, ist dafür zuständig das diese
        # Abfrage als erstes bei jederm ersten Durchlauf einer
        # for - Schleife durchgeführt, dort wird der Inhalt und
        # die y - Position vom String Element abgespeichert
        if not done:  # Solange done False ist...
            rowArr.append(st)
            done = True  # ... Done wird auf True gesetzt
            althoe = height

        # Hier wird abgeprüft ob die Anfangspoisiton der Höhe
        # vom vorigen Element, sich mit der Anfangspotion
        # vom jetzigen Element starkt unterscheidet, dann...
        elif (height > (althoe - 20)) and (height < (althoe + 20)) \
                and (done == True):
            rowArr.append(st)  # ... speichert es den Inhalt ins array
            # ...althoehe bekommt den Wert der
            # y - Position des jetzigen Elements
            althoe = height

        # Ansonsten soll er den Array, wo der ganze Inhalt drinnen ist
        # in ein anderes Array abspeichern, damit sozusagen ein
        # Zeilenumbruch steht
        else:
            txtArr.append(rowArr)
            rowArr = []  # rowArr steeht wieder leer
            rowArr.append(st)  # das content wird ins leere rowArr gespeichert
            # ...althoehe bekommt den Wert der
            # y - Position des jetzigen Elements
            althoe = height

    txtArr.append(rowArr)  # ein Zeilenumbruch wird erzeugt

    # Hier wird der ganze Text in den Arrays mit den
    # entspechenden Zeilenumbrüchen in einer txt - Datei gespeichert
    te = ''
    for i in txtArr:  # Jede Zeile im txtArr läuft hier durch
        for j in i:  # Jedes Wort in der Zeile läuft hier durch
            te = te + str(j) + " "  #und wird hier gespeichert
        te = te + " \n"  # Ein Zeilenumbruch wird in der Variable erstellt

    # Der ganze Text wird in der einer txt - Datei gespeichert
    open(img + "_text.txt", "w", encoding="iso-8859-1").write(te)


# Hier werden die Darstellungen von den jeweiligen Seiten
# ausgeschnitten und dann abgespeichert
def crop_img(img, shape, anz, dir):
    # die enstsprechende Suffix wird vom Dateinamen gelöscht
    # danach wird dieser Dateiname extra abgespeichert
    ff = dir.removesuffix("_bilder")
    name = os.path.basename(ff)

    # Hier wird die die jeweilige Seite
    # mittels Image geöffnet
    #
    # Danach wird anhand der Position und Größe
    # des Subbildes, dieser ausgeschnitten
    im = Image.open(img)
    im1 = im.crop(shape)

    #Es erfolgt eine Überprüfung, ob die Darstellung überhaupt existiert
    if im1.width == 0 or im1.height == 0:
        # Wenn die Darstellung nicht existiert kommt eine Fehlermeldung
        print("Fehler beim Bildausschnitt erstellen")
    else:
        # Wenn alles geklappt hat, wie erwartet, wird das jeweilige
        # ausgeschnittene Subbild mit den formatierten Dateinamen
        # im entsprechenden Ordner abgespeichert
        im1.save(dir + "\\\\" + name + "_pic_" +
                 str(anz) + ".jpg")


# Hier werden alle Seiten von dem PDF-Dokument
# in einzelne PNG - Bilder abgespeichert
def extract_pdf(fname):
    pdffile = fname
    doc = fitz.open(pdffile)  # Das PDF - File wird geöffnet

    #Durchlauf jeder einzlnen PDF - Seite
    for i in range(doc.page_count):
        page = doc.load_page(i)  # Die Nummer von der Seite
        mat = fitz.Matrix(5, 5)  # Für eine höhere Bildqualität
        pix = page.get_pixmap(matrix=mat)  # Umwandlung in einer PixMap
        dir, extension = os.path.splitext(pdffile)  # Pfad der Datei
        filename = Path(dir).stem  # der Dateiname
        # Pfad zum Ordner wohin es gespeichert werden soll
        dirr = ordner + filename
        Path(dirr).mkdir(exist_ok=True)  # Erstellung eines neuen Ordners

        # Die einzelne Seiten der PDF werden als png File abgespeichert
        pix.save("%s/%d.png" % (dirr, i))
        image = Image.open(("%s/%d.png" % (dirr, i)))
        w = int(image.width / 10)
        h = int(image.height / 10)
        image = image.resize((w, h), Image.ANTIALIAS)
        image.save("%s/%d-thumb.png" % (dirr, i), quality=10, dpi=(72, 72))


# Hier erfolgt die Texterkennung der einzelnen PNG - Seiten,
# anschließend wird der Inhalt in einem XML - File abgespeichert
def do_ocr(f):
    # Der Inhalt der Seite wird mittels Tesseract ausgelesen
    res = pytesseract.image_to_alto_xml(f, lang='deu')
    # Danach wird ein XML - File erzeugt, wo dann der
    # ganze Inhalt hineingeschrieben wird
    fp = open("%s_alto.xml" % f, "wb")
    fp.write(res)
    fp.close()

    # Es wir ein neues XML - File erzeugt mit dem richtigen encoding,
    # wo dann der ganze Inhalt erneut hinein geschrieben wird
    fp = io.open("%s_alto.xml" % f, mode="r", encoding="iso-8859-1")
    s = fp.read()
    print(s)
    open("%s_alto_neu.xml" % f, 'w', encoding="utf-8").write(s)


# Hier wird bei seiten im Ordner die Ocr - Methode durchgeführt
def do_ocr_dir(dir):
    for f in glob.glob("%s/*.png" % dir):  # Jedes einezlne png File im Ordner läuft hier durch
        ff = os.path.join(dir, f)  # Der Pfad der png Files wird gespeichert
        if '-thumb' in ff:  # Wenn der Pfad (ff) -thumb enthält...
            continue  #... soll er zur nächsten Iteration springen
        do_ocr(ff)  # Die do_ocr Methode wird durchgeführt


# Hier werden alle Methoden zusammengefasst, welches dann bei allen pdf Files im Ordner durchgeführt wird
def process_dir(dir):
    for f in glob.glob("%s/*.pdf" % dir):  # Jedes pdf File im Ordner läuft hier durch
        ff = os.path.join(dir, f)  # Der Pfad der PDF Files
        # print (ff)
        dir, extension = os.path.splitext(ff)
        # print('Ordner' + dir)
        filename = Path(ff).stem  # Hier bekommt man nur den Namen der pdf Datei
        # Der PFad wo sich die PDFS befindne wo di eOrdner mit den Inhalten erzeugt werden soll
        di = ordner
        # Hier wird ein Pfad zu einem neuen Ordner erzeugt
        dir = os.path.join(di,
                           filename)  # r'C:\\Users\\mertc\\Desktop\\HTL - Fächer\\Diplomarbeit\\Test-tesseract\\' + filename
        print(dir)
        extract_pdf(ff)  # Die MEthode extract_pdf wird durchgeführt
        do_ocr_dir(dir)  # DIe do_ocr_dir Methode wird durchgeführt
        highlight_images(dir)  # Die highlight_images Methode wird durchgeführt


# Hier wird in jedem Unterordner nach dem png - File gesucht und ein thumb png bzüglich dem png File erzeugt
def searchDir(path):
    r = glob.glob('%s/**/*.png' % path, recursive=True)

    for file in r:
        # print(file)
        image = Image.open(file)
        w = int(image.width / 10)
        h = int(image.height / 10)
        image = image.resize((w, h), Image.ANTIALIAS)
        file = file.removesuffix('.png')
        image.save("%s-thumb.png" % file, quality=10, dpi=(72, 72))
    # print(r)


if __name__ == '__main__':
    #process_dir(r'C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract') #Merts Tesseract
    process_dir(ordner)
    #searchDir(r'C:\Users\mertc\Desktop\HTL++ - Fächer\Diplomarbeit\Test-tesseract')
    # process_dir(r'D:\Diplomarbeit\Tesseract') #Leos Tesseract
