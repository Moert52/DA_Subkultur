import fitz #https://pymupdf.readthedocs.io/en/latest/tutorial.html
import os
from pathlib import Path
import pytesseract
import xml.etree.ElementTree as ET
import elementpath
from PIL import Image, ImageDraw, ImageFont
import glob
from lxml import etree
import io



#Hier wird Tesseract definiert
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

#hier werden alle xml Files der Text ausgelesen und die Bilder mit einem Rahmen gekennzeichnet
def highlight_images(dir):
    for f in glob.glob("%s/*.png" % dir):
        ff = os.path.join(dir, f)
        print(ff)


        highlight_image(ff, '%s_alto_neu.xml' % ff)
        get_Text(ff, '%s_alto_neu.xml' % ff)
        #output = aw.Document()
        #input = aw.Document(ff + "_text.txt")
        # Append the source document to the end of the destination document.
        #output.append_document(input, aw.ImportFormatMode.KEEP_SOURCE_FORMATTING)
        #output.save(ff+"Output.docx")



#hier erfolgt die Gekennzeichnung der Bilder mittels einem Rahmen
def highlight_image(img, xml):
    print(xml)
    root = ET.parse(xml)
    image = Image.open(img)
    draw = ImageDraw.Draw(image)
    anz = 1
    ff = os.path.splitext(img)[0]
    dir = ff + "_bilder"
    Path(dir).mkdir(exist_ok=True)
    #os.mkdir(ff + "_bilder")

    for p in elementpath.select(root, '//Illustration', {'' : 'http://www.loc.gov/standards/alto/ns-v3#'}):
        gid = p.attrib["ID"]
        x0 = int(p.attrib["HPOS"])
        y0 = int(p.attrib["VPOS"])
        x1 = int(x0 + int(p.attrib["WIDTH"]))
        y1 = int(y0 + int(p.attrib["HEIGHT"]))
        shape = [x0, y0,x1,y1 ]

        crop_img(img, shape, anz, dir)
        anz+=1
        print (gid, shape)
        draw.text((x1, y1), gid, align="right", font=ImageFont.load_default(), fill="green")
        draw.rectangle(shape, fill=None, outline ="green")
    image.save(img + "_col.jpg")

#Hier wird der Text vom xml File ausgelesen und in einem Text dokument abgespeichert
#(die Zeilenumbrüche werden berücksichtigt)
def get_Text(img, xml):
    print(xml)
    root = ET.parse(xml)
    anz = 0
    txt = []
    arr = []
    done = False
    althoe=0
    #for l in elementpath.select(root, '//TextLine', {'': 'http://www.loc.gov/standards/alto/ns-v3#'}):
        #an = 0
        #print(str(l.attrib["CONTENT"]))
    for t in elementpath.select(root, '//String', {'': 'http://www.loc.gov/standards/alto/ns-v3#'}):
        st = str(t.attrib["CONTENT"])
        print(st)
        height = int(t.attrib["VPOS"])
        if done == False:
            arr.append(st)
            done = True
            althoe = height
        elif (height > (althoe-20)) &(height< (althoe+20))&(done ==True):
            arr.append(st)
            althoe = height
        else:
            anz = anz + 1
            txt.append(arr)
            arr = []
            arr.append(st)
            althoe = height
    txt.append(arr)
    print(txt)
    te=''
    for i in txt:
        for j in i:
            te = te + str(j) + " "
        te = te +" \n"
    print(te)

    open(img + "_text.txt", "w",encoding="iso-8859-1").write(te)

#Hier werden die Bilder von den einzelnen Dokumenten ausgeschneidet und dann abgespeichert
def crop_img(img, shape, anz, dir):

    ff = dir.removesuffix("_bilder")

    name = os.path.basename(ff)
    im = Image.open(img)
    im1 = im.crop((shape))
    #im1.show()
    if im1.width == 0 or im1.height == 0:
        print("Fehler beim Bildausschnitt erstellen")
    else:
        im1.save(dir + "\\\\" + name +"_pic_"+str(anz)+".jpg")

#Hier werden alle Seiten des pdfs File in einzelne png - Bilder abgespeichert
def extract_pdf(fname):
    pdffile = fname
    doc = fitz.open(pdffile)
    for i in range(doc.page_count):
        page = doc.load_page(i)  # number of page
        mat = fitz.Matrix(5,5) # To get higher resolution
        pix = page.get_pixmap(matrix=mat)
        dir, extension = os.path.splitext(pdffile)
        Path(dir).mkdir(exist_ok=True)
        pix.save("%s/%d.png" % (dir,i))

#Hier erfolgt die ocr der seite, aschnließend werden die Informationen in einem xml - File abgespeichert
def do_ocr(f):
    print(f)
    res = pytesseract.image_to_alto_xml(f, lang='deu')
    print("Ergebnis")
    print(res)

    #res = replace(res)
    print(res)
    fp = open("%s_alto.xml" % f, "wb")
    fp.write(res)
    fp.close()

    #fp = f
    fp_out = '0.png_alto_utf-8.xml'
    fp = io.open("%s_alto.xml" % f, mode="r", encoding="iso-8859-1")
    s = fp.read()
    print(s)
    open("%s_alto_neu.xml" % f, 'w', encoding="utf-8").write(s)

#Hier wird bei seiten im Ordner die Ocr - Methode durchgeführt
def do_ocr_dir(dir):
    for f in glob.glob("%s/*.png" % dir):
        ff = os.path.join(dir, f)
        do_ocr(ff)

#Hier werden alle Methoden zusammengefasst, welches dann bei allen pdf Files im Ordner durchgeführt wird
def process_dir(dir):
    for f in glob.glob("%s/*.pdf" % dir):
        ff = os.path.join(dir, f)
        print (ff)
        dir, extension = os.path.splitext(ff)
        extract_pdf(ff)
        do_ocr_dir(dir)
        highlight_images(dir)

if __name__ == '__main__':
    process_dir(r'C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract') #Merts Tesseract
    #process_dir(r'D:\Diplomarbeit\Tesseract') #Leos Tesseract
