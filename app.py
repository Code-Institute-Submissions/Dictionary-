import os
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import flash
from flask import session
from flask import url_for
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


# Replace function
def replace(data):
    data = data.replace(",", "@")
    return data


# userName check
def authCheck(string, dataType):
    # Min 5
    if len(string) < 5:
        flash("Ensure " + dataType + " has a minumim of 5 characters")
        return(bool(False))

    # Max 15
    if len(string) > 15:
        flash("Ensure " + dataType + " username has a maximum of 15 characters")
        return(bool(False))

    # No spaces
    if " " in string:
        flash("Spaces not allowed in " + dataType)
        return(bool(False))

    return(bool(True))


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
        appearance = str(d.get("First Comic Appearance"))
        cinematicAppearances = str(d.get("Marvel Cinematic Appearance"))
        playedBy = str(d.get("Played by"))
        createdBy = str(d.get("Created by"))

        # Replace , with #
        name = replace(name)
        alias = replace(alias)
        appearance = replace(appearance)
        cinematicAppearances = replace(cinematicAppearances)
        playedBy = replace(playedBy)
        createdBy = replace(createdBy)

        # Initialise into a single string
        data = name + "," + alias + "," + appearance + "," + cinematicAppearances + "," + playedBy + "," + createdBy

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
        "Marvel Cinematic Appearance",
        "Played By",
        "Created By"
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
        "Marvel Cinematic Appearance",
        "Played By",
        "Created By"
    ]
    # Return villains page
    return render_template(
        'villains.html',
        headers=headers,
        values=villainData
    )


# Register page
@app.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Set variables
        username = request.form['username']
        password = request.form['password']

        # Run auth checks
        userCheck = authCheck(username, "username")
        passCheck = authCheck(password, "password")

        if userCheck is not True or passCheck is not True:
            return redirect(url_for('register'))
        else:
            # Checks if username already exists in db
            connection = MongoClient(databaseConnection)
            db = connection.marvelHeroes
            # Set Collection we should use
            collection = db["users"]
            # Get ALL the data
            existing_user = collection.find_one(
                {"username": username}
            )

            if existing_user:
                flash("Username already exists")
                return redirect(url_for('register'))

            register = {
                "username": username,
                "password": generate_password_hash(password)
            }
            collection.insert_one(register)

            # Put the new user into 'session' cookie
            session["user"] = username
            flash("Registration Successfull")
            return redirect(url_for('register'))
    else:
        return render_template('register.html')


# Log-in page
@app.route("/login/", methods=["GET", "POST"])
def login():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
