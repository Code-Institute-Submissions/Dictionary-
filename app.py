import os
from flask import Flask, (Render_tempate, redirect, request, session, url_For)
from flask_pymongo import PyMongo 
from bson.objectid import ObjectId
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secure_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route('/')
@app.route("/name")
def name():
    heroes = mongo.db.heroes.find
    return render_template("heroes.html", heroes=heroes)


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)

