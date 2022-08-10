from flask_restful import Resource, Api
from flask import Flask, render_template, session, jsonify, flash, request, redirect
from werkzeug.utils import secure_filename
import os

#Hallo
import Tesseract

app=Flask(__name__,template_folder='static/templates')  # Die Flask-Anwendung
api = Api(app)  # Die Flask API
app.secret_key = '_5#y2L"F4Q8z/n/xec] /'
app.config['UPLOAD_PATH'] = r'C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract\ToOCR'

@app.route('/')
def Start():
    return render_template("Start.html")

@app.route('/admin/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        site = request.form['site']
        #uploaded_file = request.files['file']
        #filename = secure_filename(uploaded_file.filename)

        if not title:
            flash('Title is required!')
        elif not site:
            flash('Site is required!')
        for uploaded_file in request.files.getlist('file'):
            if uploaded_file.filename == '':
                flash('File is required!')
            else:
                filename = secure_filename(uploaded_file.filename)
                uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
                print(title)
                print(site)
                print(app.config['UPLOAD_PATH'])
        if len(os.listdir(app.config['UPLOAD_PATH']) ) != 0:
            Tesseract.process_dir(app.config['UPLOAD_PATH'])




    return render_template("create.html")

@app.route('/Menu')
def Menu():
    return render_template("Start.html")

if __name__ == '__main__':
    app.run(debug=True)
