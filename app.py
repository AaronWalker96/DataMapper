# Imports
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route('/success', methods = ['POST'])  
def success():  
    if request.method == 'POST':  
        f = request.files['file']
        content = f.getvalue()
        strvalue = content.decode('utf-8')
        return render_template("success.html", name = f.filename, content=strvalue)  

if __name__ == "__main__":
    app.run()