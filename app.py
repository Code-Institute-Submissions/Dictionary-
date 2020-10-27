import os
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("/index.html")


@app.route('/villians')
def villians():
    return render_template("/villians.html")

@app.route('/heroes')
def heroes():
    return render_template("/heroes.html")

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)

