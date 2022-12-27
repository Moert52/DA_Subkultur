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
# ordner = r'C:\\Users\\mertc\\Desktop\\HTL - Fächer\\Diplomarbeit\\Test-tesseract\\'

# Leo's Ordner
ordner = r'D:\Diplomarbeit\test_tesseract'


# hier werden alle xml Files der Text ausgelesen und die Bilder mit einem Rahmen gekennzeichnet
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


# hier erfolgt die Kennzeichnung der Bilder mittels einem Rahmen
def highlight_image(img, xml):
    print(xml)
    root = ET.parse(xml)  # Das xml File wird geöffnet
    image = Image.open(img)  # das png wird geöffnet
    draw = ImageDraw.Draw(image)  # es wird eien Instanz erzeugt um Zeichnen / malen des Bildes
    anz = 1  # Dient für die Anzahl der ausgeschittenen SubBilder
    ff = os.path.splitext(img)[0]  # der Pfad zum Ordner der Datei wird gespeichert
    dir = ff + "_bilder"  # Die entsprechende suffix wird erstellt
    Path(dir).mkdir(exist_ok=True)  # Es wird ein neuer Ordner mit dem neuen Pfad erzeugt
    # os.mkdir(ff + "_bilder")

    # Jedes Illustration Element im xml FIle läuft hier durch
    for p in elementpath.select(root, '//Illustration', {'': 'http://www.loc.gov/standards/alto/ns-v3#'}):
        gid = p.attrib["ID"]  # Die id vom Element wird abgespeichert
        x0 = int(p.attrib["HPOS"])  # die x - Position wird gespeichert
        y0 = int(p.attrib["VPOS"])  # die y - Position wird  gespeichert
        x1 = int(x0 + int(p.attrib["WIDTH"]))  # Die Breite wird gespeichert
        y1 = int(y0 + int(p.attrib["HEIGHT"]))  # Die Höhe wird gespeichert
        shape = [x0, y0, x1, y1]  # Die ganzen Werte wird in einem array gespeichert

        crop_img(img, shape, anz, dir)  # Die crop_img Methode wird durchgeführt
        anz += 1  # die Anzahl wird um 1 erhöhrt
        print(gid, shape)

        # Die ganzen gefunden Bilder auf den einzelnen Seiten der Artikel wird mit einer grünen Umrandung gekenzeichnet
        draw.text((x1, y1), gid, align="right", font=ImageFont.load_default(), fill="green")
        draw.rectangle(shape, fill=None, outline="green")

    image.save(
        img + "_col.jpg")  # Die einzelne Seite vom Artikel mit den gekennzeichneten Bilder wird lokal abgespeichert


# Hier wird der Text vom xml File ausgelesen und in einem Text dokument abgespeichert
# (die Zeilenumbrüche werden berücksichtigt)
def get_Text(img, xml):
    print(xml)
    root = ET.parse(xml)  # Das xml - File wird geöffnet
    txtArr = []  # Array umd en ganzen Content abzuspeichern
    rowArr = []  # Array um dei ganzen Wörter in einer Zeile abzuspeichern
    done = False
    althoe = 0  # hier wird die alte Hoehe vom vorigen Element gespeichert
    # for l in elementpath.select(root, '//TextLine', {'': 'http://www.loc.gov/standards/alto/ns-v3#'}):
    # an = 0
    # print(str(l.attrib["CONTENT"]))

    # Jedes String Element läuft hier durch
    for t in elementpath.select(root, '//String', {'': 'http://www.loc.gov/standards/alto/ns-v3#'}):
        st = str(t.attrib["CONTENT"])  # Der Content
        print(st)
        height = int(t.attrib["VPOS"])  # die y - Position wird gespeichert
        if not done:  # Solange done False ist
            rowArr.append(st)  # der content wird ins array gepseichert
            done = True  # done wird auf True gesetzt
            althoe = height  # althoehe bekommt den Wert von der y Position

        # Solange die Höhe nicht größer oder kleiner als 20 ist und done true ist soll es...
        elif (height > (althoe - 20)) and (height < (althoe + 20)) and (done == True):
            rowArr.append(st)  # speichert es den content ins array
            althoe = height  # althoehe bekommt den Wert von der y Position
        else:  # sonst
            txtArr.append(rowArr)  # rowArray wird ins txtArr gespeichet (also ensteht ein Zeilenumbruch
            rowArr = []  # rowArr steeht wieder leer
            rowArr.append(st)  # das content wird ins leere rowArr gespeichert
            althoe = height  # althoehe bekommt den Wert von der y Position
    txtArr.append(rowArr)  # rowArray wird ins txtArr gespeichet (also ensteht ein Zeilenumbruch
    print(txtArr)
    te = ''  # Hier wird der ganze Text mit den enstsprechenden Zeilenumbruchen gespeichert
    for i in txtArr:  # Jede Zeile im txtArr läuft hier durch
        for j in i:  # Jedes Wort in der Zeile läuft hier durch
            te = te + str(j) + " "  # jedes Wort in die Variable gespeichert
        te = te + " \n"  # und dementsprechend wird ein Zeilenumbruch in der ariable erstellt
    print(te)

    # Der ganze Text wird in die Entsprechende Datei gespeichert
    open(img + "_text.txt", "w", encoding="iso-8859-1").write(te)


# Hier werden die Bilder von den einzelnen Dokumenten ausgeschneidet und dann abgespeichert
def crop_img(img, shape, anz, dir):
    # die enstsprechende Suffix wird gelöscht
    ff = dir.removesuffix("_bilder")

    name = os.path.basename(ff)  # der Filename wird abgespeichert
    im = Image.open(img)  # Das Bild wird geöffnet
    im1 = im.crop(shape)  # Das entsprechende subBild wird ausgeschnitten
    # im1.show()
    if im1.width == 0 or im1.height == 0:  # Dann wird geprüft ob das Bild überhaupt eine Höhe und Breite hat
        print("Fehler beim Bildausschnitt erstellen")  # eine Fehlermeldung
    else:
        im1.save(dir + "\\\\" + name + "_pic_" + str(
            anz) + ".jpg")  # Das asugeschnittene Bilder wird im entsprechenden ordner gespeichert


# Hier werden alle Seiten des pdfs File in einzelne png - Bilder abgespeichert
def extract_pdf(fname):
    pdffile = fname
    # print('PDF:' + pdffile)
    doc = fitz.open(pdffile)  # Das pdfile wird geöffnet
    for i in range(doc.page_count):  # jeder einzelne Seite der PDF läuft hier durch
        page = doc.load_page(i)  # Die Nummer von der Seite
        mat = fitz.Matrix(5, 5)  # Um eine höhe Bildqualität zu bekommen
        pix = page.get_pixmap(matrix=mat)  # wird in eine pixmap umgewandelt
        dir, extension = os.path.splitext(pdffile)  # der Pfad der Datei wird heruasgeholt
        filename = Path(dir).stem  # der Dateiname wird herausgeholt
        # r'C:\\Users\\mertc\\Desktop\\HTL - Fächer\\Diplomarbeit\\Test-tesseract\\'
        dirr = ordner + filename  # Pfad zum Ordner
        # wohin es gespeichert wird
        print(dirr)
        Path(dirr).mkdir(exist_ok=True)  # Hier wird ein Ordner neues Ordner erstellt
        # dirr = 'C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract'
        # Path(dirr).mkdir(exist_ok=True)
        pix.save("%s/%d.png" % (dirr, i))  # Die PDF einzelne Seite wird als png File gespeichert
        image = Image.open(("%s/%d.png" % (dirr, i)))
        w = int(image.width / 10)
        h = int(image.height / 10)
        image = image.resize((w, h), Image.ANTIALIAS)
        image.save("%s/%d-thumb.png" % (dirr, i), quality=10, dpi=(72, 72))


# Hier erfolgt die ocr der seite, aschnließend werden die Informationen in einem xml - File abgespeichert
def do_ocr(f):
    print(f)
    res = pytesseract.image_to_alto_xml(f, lang='deu')  # Das Bild wird zu einem xml FIle umgewandelt
    print("Ergebnis")
    print(res)

    # res = replace(res)
    print(res)
    fp = open("%s_alto.xml" % f, "wb")  # Es wird ein xml FIle erzeugt, wo dann der ganze Inhalt von dem
    # umgewandelten xml File hineingeschrieben wird

    fp.write(res)
    fp.close()

    # fp = f
    fp_out = '0.png_alto_utf-8.xml'
    # Dann wird ein neues xml File erzeugt mit dem richtigen encoding, wo dann der ganze Inhalt erneut hingeschrieben wird
    fp = io.open("%s_alto.xml" % f, mode="r", encoding="iso-8859-1")
    s = fp.read()
    print(s)
    open("%s_alto_neu.xml" % f, 'w', encoding="utf-8").write(s)


# Hier wird bei seiten im Ordner die Ocr - Methode durchgeführt
def do_ocr_dir(dir):
    for f in glob.glob("%s/*.png" % dir):  # Jedes einezlne png File im Ordner läuft hier durch
        ff = os.path.join(dir, f)  # Der Pfad der png Files wird gespeichert
        if '-thumb' in ff:  # Wenn der Pfad ff enthält
            continue  # soll er zur nächsten Iteration springen
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
        di = r'C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract'
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
    process_dir(r'D:\Diplomarbeit\test_tesseract')
    #searchDir(r'C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract')
    # process_dir(r'D:\Diplomarbeit\Tesseract') #Leos Tesseract
