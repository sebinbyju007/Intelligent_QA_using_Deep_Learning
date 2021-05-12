  
from __future__ import division, print_function
# coding=utf-8

import pickle

# Keras
from keras.models import load_model

# Flask utils
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer

MODEL_PATH = 'models/sample.h5'




model = load_model(MODEL_PATH)
print('Model loaded. Start serving...')






from flask import Flask, render_template, url_for, jsonify, request
app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')


@app.route('/result', methods=['POST'])
def result():
    text1 = request.form['searchBox']
    return render_template('result.html', result1= 'The query is : > {}' .format(text1))   
    
    

if __name__== '__main__':
    app.run(debug=True)