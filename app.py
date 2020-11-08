import os
from astropy.table import QTable, Table, Column
from flask import Flask #(Render_tempate, redirect, request, session, url_For)
from flask import render_template
from flask import jsonify
from flask_pymongo import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

if os.path.exists("env.py"):
    import env

app = Flask(__name__)

# Set Variables
databaseConnection = os.environ.get("MONGO_URI")
dbName = os.environ.get("MONGO_DBNAME")

@app.route('/')
@app.route('/get-heroes/')
def getHeroes():
    # Connect Database
    connection = MongoClient(databaseConnection)
    database = connection.marvelHeroes
    collection = database.Heroes
    heroes = collection.find({})
    allData = []
    for hero in heroes:
        name = str(hero.get("Name"))
        alias = str(hero.get("Alias"))
        #appearances = str(hero.get("First Comic Appearance"))
        #cinematicAppearances = str(hero.get("Marvel Cinematic Appearance"))
        #playedBy = str(hero.get("Played by"))
        #createdBy = str(hero.get("Created by"))
        data = name + "," + alias
        allData.append(data)
    headers = ["Name", "Alias"]
    print(allData)
    return render_template('index.html', headers=headers, values=allData)


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
