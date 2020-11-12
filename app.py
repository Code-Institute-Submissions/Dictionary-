import os
from flask import Flask
from flask import render_template
from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from flask_pymongo import pymongo
from pymongo import MongoClient


# MyForm Class
class MyForm(FlaskForm):
    # Initilize a form
    name = StringField('name', validators=[DataRequired()])


if os.path.exists("env.py"):
    import env

# Set Variables
app = Flask(__name__)

# Set Secret key (required by forms) - randmoly generated
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# Set variables out of env.py
databaseConnection = os.environ.get("MONGO_URI")
dbName = os.environ.get("MONGO_DBNAME")


# Get Data function and process
def getData(database):
    # Connect Database
    connection = MongoClient(databaseConnection)
    db = connection.marvelHeroes
    # Set Collection we should use
    collection = db[database]
    # Get ALL the data
    data = collection.find({})
    # Set return Array
    allData = []
    # Loop through all data to parse
    for d in data:
        # Get5 Values out of data
        name = str(d.get("Name"))
        alias = str(d.get("Alias"))
        """
        appearance = str(d.get("First Comic Appearance"))
        cinematicAppearances = str(d.get("Marvel Cinematic Appearance"))
        playedBy = str(d.get("Played by"))
        createdBy = str(d.get("Created by"))
        """
        # Initialise into a single string
        data = name + "," + alias
        # Add to global array
        allData.append(data)
    # return Data
    return allData


# Set Index page
@app.route('/')
def index():
    # Initialize MyForm class
    form = MyForm()
    # If there is a submit button pressed (button)
    if form.validate_on_submit():
        # If it means hero's
        if 'Heroes' in request.form:
            # return hero page
            render_template('heroes.html')
        elif 'Villains' in request.form:
            # return villain page
            render_template('villains.html')
            'Register' in request.form
            # return register page
            render_template('register.html')
    # No button pressed, return home page
    return render_template('index.html')


# Set Hero Page
@app.route('/heroes/')
def heroes():
    # Connecto to database and get hero data
    heroData = getData("Heroes")
    # Set Headers
    headers = [
        "Name",
        "Alias",
        "First Comic Appearance",
        "Marvel Cinematic Appearance"
    ]
    # return Hers page
    return render_template(
        'heroes.html',
        headers=headers,
        values=heroData
    )


# Set Villain Page
@app.route('/villains/')
def villains():
    # Connect to database with Villains and process data
    villainData = getData("Villians")
    # Set Headers
    headers = [
        "Name",
        "Alias",
        "First Comic Appearance",
        "Marvel Cinematic Appearance"
    ]
    # Return villains page
    return render_template(
        'villains.html',
        headers=headers,
        values=villainData
    )


@app.route("/register/", methods=["GET", "POST"])
def register():
    return render_template("register.html")


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
