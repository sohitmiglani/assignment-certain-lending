# importing general extensions of flask here
from flask import Flask, session, render_template, request, flash, url_for, redirect, send_file, Response, make_response
from flask_cors import CORS
import matplotlib.pyplot as plt
import flask
from flask_bootstrap import Bootstrap
import app_functions
import pandas as pd
import os

plt.style.use('ggplot')
plt.switch_backend('Agg')

app = Flask(__name__)
app.config.from_object(__name__)
app.config['DEBUG'] = True
app.config["SECRET_KEY"] = app_functions.random_id(50)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
Bootstrap(app)
CORS(app, resources={r'/*': {'origins': '*'}})

@app.route("/", methods=["GET", "POST"])
def home():
    session.clear()
    cwd = os.getcwd()

    try:
        os.remove(cwd + '/static/images/age.png')
        os.remove(cwd + '/static/images/rooms.png')
    except:
        pass

    if request.method == "POST":
        if request.form['submit_button'] == 'submit_info':
            api_key = "48ed381483aabf5758717c7aa023980f"
            zip_code = request.form["zip_code"]
            add1 = request.form["add1"]
            add2 = request.form["add2"]

            app_functions.search_property(api_key, add1, add2)
            app_functions.search_zip(api_key, zip_code)

            return redirect(url_for('results'))

    return render_template('index.html')


@app.route("/results", methods=["GET", "POST"])
def results():
    if request.method == "POST":
        if request.form['submit_button'] == 'go_back':
            return redirect(url_for('home'))

    return render_template('results.html', session=session)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.errorhandler(404)
def page_not_found(e):
    # the flash utlity flashes a message that can be shown on the main HTML page
    flash('The page that you tried to visit does not exist. You have been redirected to the home page')
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
