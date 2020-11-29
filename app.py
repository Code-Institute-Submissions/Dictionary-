import os
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import flash
from flask import session
from flask import url_for
from flask_wtf import FlaskForm
from flask_login import LoginManager
from flask_login import current_user, login_user, logout_user
from wtforms import StringField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient

if os.path.exists("env.py"):
    import env

# Set Variables
app = Flask(__name__)
login = LoginManager(app)

# Set Secret key (required by forms) - randmoly generated
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# Set variables out of env.py
databaseConnection = os.environ.get("MONGO_URI")
dbName = os.environ.get("MONGO_DBNAME")
connection = MongoClient(databaseConnection)
db = connection.marvelHeroes


class User:
    def __init__(self, username):
        self.username = username

    def is_authenticated():
        return True

    def is_active():
        return True

    def is_anonymous():
        return False

    def get_id(self):
        return self.username

    def check_password(password_hash, password):
        return check_password_hash(password_hash, password)


# MyForm Class
class MyForm(FlaskForm):
    # Initilize a form
    name = StringField('name', validators=[DataRequired()])


@login.user_loader
def load_user(username):
    u = db['users'].find_one({"username": username})
    if not u:
        return None
    return User(username=u['username'])


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
        flash(
            "Ensure " +
            dataType +
            " username has a maximum of 15 characters"
        )
        return(bool(False))

    # No spaces
    if " " in string:
        flash("Spaces not allowed in " + dataType)
        return(bool(False))

    return(bool(True))


# Get Data function and process
def getData(database):
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
        data = (
            name + "," +
            alias + "," +
            appearance + "," +
            cinematicAppearances + "," +
            playedBy + "," +
            createdBy
        )

        # Add to global array
        allData.append(data)
    # return
    if allData:
        return allData
    else:
        return ""


def getSearchData(database, searchInput):
    # Set global Array
    allData = []
    # Connect Database
    connection = MongoClient(databaseConnection)
    db = connection.marvelHeroes

    # Connect correct table
    collection = db[database]

    # Get All Keys
    keys = collection.find_one({})
    # Loop through each key and search data
    for key in keys:
        # Get cursor
        cursor = collection.find({key: {
            "$regex": searchInput, "$options": 'i'}}
            )
        # cursor = collection.find({key: searchInput})
        if cursor:
            # Get the data from cursor
            for data in cursor:
                # If not null
                if data:
                    # Get Values out of data
                    name = str(data.get("Name"))
                    alias = str(data.get("Alias"))
                    appearance = str(data.get("First Comic Appearance"))
                    cinematicAppearances = str(
                        data.get("Marvel Cinematic Appearance")
                        )
                    playedBy = str(data.get("Played by"))
                    createdBy = str(data.get("Created by"))

                    # Replace , with #
                    name = replace(name)
                    alias = replace(alias)
                    appearance = replace(appearance)
                    cinematicAppearances = replace(cinematicAppearances)
                    playedBy = replace(playedBy)
                    createdBy = replace(createdBy)

                    # Initialise into a single string
                    data = (
                        name + "," +
                        alias + "," +
                        appearance + "," +
                        cinematicAppearances + "," +
                        playedBy + "," +
                        createdBy
                    )

                    # Add to global array
                    allData.append(data)
    if allData:
        return allData
    else:
        return "Nothing"


def searchData(searchInput):
    # Global searchData
    searchData = ""
    # Seach Heroes
    heroData = getSearchData("Heroes", searchInput)

    # Now Villains
    villainData = getSearchData("Villians", searchInput)

    if heroData == "Nothing" and villainData != "Nothing":
        searchData = villainData
    elif heroData != "Nothing" and villainData == "Nothing":
        searchData = heroData
    elif heroData != "Nothing" and villainData != "Nothing":
        searchData = heroData + villainData
    else:
        # No data found
        searchData = "Nothing"
    return searchData


def checkVariable(input):
    if input:
        return input
    else:
        return "None"


def checkDatabase(name, alias, database):
    collection = db[database]
    nameCheck = collection.find({"Name": name})
    aliasCheck = collection.find({"Alias": alias})

    if nameCheck or aliasCheck:
        return "Exists"
    else:
        return "None"


def databaseAdd(
    name,
    alias,
    firstComiCappearance,
    MarvelCinematicAppearance,
    playedBy,
    createdBy,
    database
):
    collection = db[database]
    data = {
        "Name": name,
        "Alias": alias,
        "First Comic Appearance": firstComiCappearance,
        "Marvel Cinematic Appearance": MarvelCinematicAppearance,
        "Played by": playedBy,
        "Created by": createdBy
    }
    collection.insert_one(data)


# Set Index page
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Initialize MyForm class
        form = MyForm()
        #  If there is a submit button pressed (button)
        if form.validate_on_submit():
            # If it means hero's
            if 'Heroes' in request.form:
                # return hero page
                render_template('heroes.html')
            elif 'Villains' in request.form:
                # return villain page
                render_template('villains.html')
            elif 'Register' in request.form:
                # return register page
                render_template('register.html')
        else:
            # POST without submit
            if 'search' in request.form:
                userInput = request.form['search']
                headers = [
                    "Name",
                    "Alias",
                    "First Comic Appearance",
                    "Marvel Cinematic Appearance",
                    "Played By",
                    "Created By"
                ]
                results = searchData(userInput)
                if results != "Nothing":
                    return render_template(
                        "searchResults.html",
                        headers=headers,
                        values=results
                    )
                else:
                    flash("Not found")
                    return redirect(url_for('heroes'))
    return render_template("index.html")


# Set Hero Page
@app.route('/heroes/', methods=["GET", "POST"])
def heroes():
    if request.method == "POST":
        userInput = request.form['search']
        headers = [
            "Name",
            "Alias",
            "First Comic Appearance",
            "Marvel Cinematic Appearance",
            "Played By",
            "Created By"
        ]
        results = searchData(userInput)

        if results != "Nothing":
            return render_template(
                "searchResults.html",
                headers=headers,
                values=results
            )
        else:
            flash("Not found")
            return redirect(url_for('heroes'))
    else:
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
        # return Hero page
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
            return render_template("profile.html", username=username)
    else:
        return render_template('register.html')


# Log-in page
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile', username=User))
    else:
        if request.method == "POST":
            username = request.form['username']
            password = request.form['password']
            connection = MongoClient(databaseConnection)
            db = connection.marvelHeroes
            # Set Collection we should use
            collection = db["users"]
            # Get ALL the data
            existing_user = collection.find_one(
                {"username": username}
            )
            if existing_user:
                # ensure hashed password matches user input
                if check_password_hash(existing_user["password"], password):
                    session["user"] = username
                    flash("Welcome, {}".format(username))
                    user_obj = User(username=username)
                    login_user(user_obj)
                    return redirect(url_for("profile"))
                else:
                    # invalid password match
                    flash("Incorrect Username and/or Password")
                    return redirect(url_for("login"))
            else:
                # username doesn't exist
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/searchResults", methods=["GET", "POST"])
def searchResults(headers, results):
    if results != "Nothing":
        return render_template(
            "searchResults.html",
            headers=headers,
            values=results
        )
    else:
        # No data found
        flash("No results found, check spelling or sign in and add your own")
        return redirect(url_for("heroes"))


@app.route("/profile", methods=["GET", "POST"])
def profile():
    username = current_user.get_id()
    return render_template("profile.html", username=username)


@app.route("/add_hero", methods=["GET", "POST"])
def add_hero():
    if request.method == "POST":
        name = request.form['name']
        alias = request.form['alias']
        firstComiCappearance = request.form['FirstComicAppearance']
        MarvelCinematicAppearance = request.form['MarvelCinematicAppearance']
        playedBy = request.form['playedBy']
        createdBy = request.form['createdBy']
        # ensure variables pass checks
        name = checkVariable(name)
        alias = checkVariable(alias)
        firstComiCappearance = checkVariable(firstComiCappearance)
        MarvelCinematicAppearance = checkVariable(MarvelCinematicAppearance)
        playedBy = checkVariable(playedBy)
        createdBy = checkVariable(createdBy)
        if name == "None" and alias == "None":
            flash("Name or alias must be set")
            return redirect(url_for("add_hero"))
        # Now ensure Name and alias does not already appear in database
        databaseCheck = checkDatabase(name, alias, "Heroes")
        if databaseCheck == "Exists":
            flash("Name or alias already exists in database")
            return redirect(url_for("add_hero"))
        # Okay now add to database
        databaseAdd(
            name,
            alias,
            firstComiCappearance,
            MarvelCinematicAppearance,
            playedBy,
            createdBy,
            "Heroes"
        )

        flash("Hero Added")
        return redirect(url_for("heroes"))
    else:
        return render_template("add_hero.html")


@app.route("/add_villain", methods=["GET", "POST"])
def add_villain():
    if request.method == "POST":
        name = request.form['name']
        alias = request.form['alias']
        firstComiCappearance = request.form['FirstComicAppearance']
        MarvelCinematicAppearance = request.form['MarvelCinematicAppearance']
        playedBy = request.form['playedBy']
        createdBy = request.form['createdBy']
        # ensure variables pass checks
        name = checkVariable(name)
        alias = checkVariable(alias)
        firstComiCappearance = checkVariable(firstComiCappearance)
        MarvelCinematicAppearance = checkVariable(MarvelCinematicAppearance)
        playedBy = checkVariable(playedBy)
        createdBy = checkVariable(createdBy)
        if name == "None" and alias == "None":
            flash("Name or alias must be set")
            return redirect(url_for("add_villain"))
        # Now ensure Name and alias does not already appear in database
        databaseCheck = checkDatabase(name, alias, "Heroes")
        if databaseCheck == "Exists":
            flash("Name or alias already exists in database")
            return redirect(url_for("add_hero"))
        # Okay now add to database
        databaseAdd(
            name,
            alias,
            firstComiCappearance,
            MarvelCinematicAppearance,
            playedBy,
            createdBy,
            "Villians"
        )
        flash("villain Added")
        return redirect(url_for("villains"))
    else:
        return render_template("add_hero.html")


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)