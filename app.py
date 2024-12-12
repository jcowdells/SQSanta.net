import datetime

from flask import Flask, render_template, session, request, url_for, redirect
from log.log import *
from sqsanta.navbar import Navbar
from db.manager import search_inventory, add_customer, customer_exists, get_customer_id, get_customer, item_exists, \
    update_item_quantity, get_item, get_item_quantity, Order, add_order, init_tables, add_order_line, get_order

app = Flask(__name__)
app.config["SECRET_KEY"] = "A_SECRET!!!!"
app.config["SERVER_NAME"] = "127.0.0.1:5000"

init_tables()

def render_base(template, **kwargs):
    login_link = "/login/"
    login_title = "Login"
    if "customer" in session:
        login_link = "/account/"
        login_title = "Account"
    return render_template(template, navbar=navbar, title="SQSanta.net", login_link=login_link, login_title=login_title,
                           **kwargs)

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

@app.route("/register/", methods=["GET", "POST"])
def register():
    errors = list()
    if request.method == "POST":
        if customer_exists(request.form["email"]):
            errors.append("Email has been taken!")
        else:
            if request.form["name"] == "":
                errors.append("Name cannot be empty!")
            elif request.form["address"] == "":
                errors.append("Address cannot be empty!")
            elif request.form["postcode"] == "":
                errors.append("Postcode cannot be empty!")
            elif request.form["email"] == "":
                errors.append("Email cannot be empty!")
            else:
                add_customer(request.form["name"], request.form["address"], request.form["postcode"], request.form["email"])
                session["customer"] = get_customer_id(request.form["email"])
                return redirect(url_for("index"))
    return render_base("register.html", errors=errors)

@app.route("/login/", methods=["GET", "POST"])
def login():
    errors = list()
    if "customer" in session:
        return redirect(url_for("account"))
    if request.method == "POST":
        if "password" not in request.form:
            errors.append("Please swear that it's your account!")
        else:
            if customer_exists(request.form["email"]):
                session["customer"] = get_customer_id(request.form["email"])
                return redirect(url_for("account", errors=errors))
            else:
                errors.append("Email is not associated with an account!")
    return render_base("login.html", errors=errors)

@app.route("/account/", methods=["GET", "POST"])
def account():
    if "customer" not in session:
        return redirect(url_for("login"))
    customer = get_customer(session["customer"])
    if request.method == "POST":
        session.pop("customer")
        session.pop("order")
        return redirect(url_for("index"))
    return render_base("account.html", customer=customer)

@app.route("/manage/")
def manage():
    errors = list()
    if "customer" not in session:
        return redirect(url_for("login"))
    customer = get_customer(session["customer"])
    if customer.get_email() != "admin":
        errors.append("Admin access only! Please sign in using 'admin' to access this (only if you really are an admin)!")
        return render_base("base.html", errors=errors)
    return render_base("manage.html", management=management)

@app.route("/basket/")
def basket():
    if "order" in session:
        order = get_order(session["order"])
    else:
        order = Order()
    if request.method == "POST":
        pass
    return render_base("basket.html", order=order)

@app.route("/manage/update_stock/", methods=["GET", "POST"])
def update_stock():
    errors = list()
    successes = list()
    if request.method == "POST":
        item_id = int(request.form["item_id"])
        item_quantity = int(request.form["item_quantity"])
        if not item_exists(item_id):
            errors.append("Item does not exist!")
        elif item_quantity < 0:
            errors.append("Item cannot have a negative quantity!")
        else:
            update_item_quantity(item_id, item_quantity)
            successes.append("Item has been updated!")
    return render_base("update_stock.html", errors=errors, successes=successes)

@app.route("/items/<item_id>/", methods=["GET", "POST"])
def items(item_id):
    errors = list()
    if "customer" not in session:
        return redirect(url_for("login"))
    try:
        item_id = int(item_id)
    except ValueError:
        item_id = None
    if item_id is None or not item_exists(item_id):
        errors.append("Unknown item!")
        return render_base("base.html", errors=errors)
    item = get_item(item_id)
    if request.method == "POST":
        if request.form["item_quantity"] == "":
            errors.append("Quantity cannot be empty!")
        else:
            item_quantity = int(request.form["item_quantity"])
            if item_quantity > get_item_quantity(item_id):
                errors.append("Not enough items in stock!")
            else:
                customer_id = session["customer"]
                if "order" not in session:
                    session["order"] = add_order(customer_id, datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d"), 0)
                order_id = int(session["order"])
                add_order_line(order_id, item_id, item_quantity, item_quantity * item.get_price_int())
                prev_quantity = get_item_quantity(item_id)
                update_item_quantity(item_id, prev_quantity - item_quantity)
                return redirect(url_for("basket"))
    return render_base("item.html", item=item, errors=errors)

with app.app_context():
    navbar = Navbar(
        Home=url_for("index"),
        Search=url_for("search"),
        Basket=url_for("basket"),
        Register=url_for("register"),
        Manage=url_for("manage"),
        )

    management = Navbar(
        Update_Stock=url_for("update_stock"),
        Generate_Report=url_for("index")
    )

if __name__ == '__main__':
    app.run()
