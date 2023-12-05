#!/usr/bin/python3
from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Ops someone forgot to implement the webpage!</p>", 404


if __name__ == '__main__':
    app.run(debug=True, port=443)
