from flask import Flask, render_template,request, redirect, url_for
from gevent.pywsgi import WSGIServer


app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():

    if request.method =='POST':
        question1 = request.form['searchBox1']
        question2 = request.form['searchBox2']
    else:
        question1 = request.args.get('searchBox1')
        question2 = request.args.get('searchBox2')
    return render_template('home.html')



if __name__ == "__main__":
    app.run(debug=True)