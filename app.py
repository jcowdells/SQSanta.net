from flask import Flask, render_template, session, request
from log.log import *
from sqsanta.navbar import Navbar
from db.manager import search_inventory

app = Flask(__name__)

navbar = Navbar(
    Home="/",
    Search="/search/",
    Register="/register/"
)

def render_base(template, **kwargs):
    return render_template(template, navbar=navbar, title="SQSanta.net", **kwargs)

@app.route("/")
@app.route("/index/")
def index():
    return render_base("index.html")

@app.route("/search/", methods=["GET", "POST"])
def search():
    results = list()
    if request.method == "POST":
        results = search_inventory(request.form["search"])
    return render_base("search.html", results=results)

if __name__ == '__main__':
    app.run()
