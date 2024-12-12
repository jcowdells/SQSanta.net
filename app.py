from flask import Flask, render_template, session
from log.log import *
from sqsanta.navbar import Navbar

app = Flask(__name__)

navbar = Navbar(
    Home="/",
    Search="/search/",
    Register="/register/"
)

def render_base(template, **kwargs):
    return render_template(template, navbar=navbar, **kwargs)

@app.route("/")
@app.route("/index/")
def index():
    return render_base("index.html")

@app.route("/search/")
def search():
    return render_base("search.html")

if __name__ == '__main__':
    app.run()
