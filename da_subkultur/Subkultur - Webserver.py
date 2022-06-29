from flask_restful import Resource, Api
from flask import Flask, render_template, session, jsonify

#Hallo
app=Flask(__name__,template_folder='static/templates')  # Die Flask-Anwendung
api = Api(app)  # Die Flask API
app.secret_key = '_5#y2L"F4Q8z/n/xec] /'

@app.route('/')
def Start():
    return render_template("Start.html")


def Test():
    print('Hallo')

def tTest():
    print('LEonardo ist ein stinkender Serbe')


if __name__ == '__main__':
    app.run(debug=True)
