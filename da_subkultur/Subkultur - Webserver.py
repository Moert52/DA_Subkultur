from flask_restful import Resource, Api
from flask import Flask, render_template, session, jsonify, flash, request, redirect

#Hallo
app=Flask(__name__,template_folder='static/templates')  # Die Flask-Anwendung
api = Api(app)  # Die Flask API
app.secret_key = '_5#y2L"F4Q8z/n/xec] /'
app.config['UPLOAD_FOLDER'] = r'C:\Users\mertc\Desktop\HTL - Fächer\Diplomarbeit\Test-tesseract'

@app.route('/')
def Start():
    return render_template("Start.html")

@app.route('/admin/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        site = request.form['site']
        file = request.form['file']

        if not title:
            flash('Title is required!')
        elif not site:
            flash('Site is required!')
        elif not file:
            flash('File is required!')
        else:
            print(title)
            print(file)
            file.save(secure_filename(f.filename))

    return render_template("create.html")

if __name__ == '__main__':
    app.run(debug=True)
