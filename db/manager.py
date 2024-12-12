import json
from db.db import *
from difflib import SequenceMatcher

class Item:
    def __init__(self, item_name, item_price):
        self.__name = item_name
        self.__price = item_price

    def get_name(self):
        return self.__name

    def get_price(self):
        return self.__price

def create_customer_table():
    create_table("tblCustomer",
                 customerId=DataType.PRIMARY_KEY,
                 customerName=DataType.TEXT,
                 customerAddress=DataType.TEXT,
                 customerPostcode=DataType.TEXT,
                 customerEmail=DataType.TEXT
                 )

def add_customer(customer_name, customer_address, customer_postcode, customer_email):
    insert_table("tblCustomer",
                 customerName=customer_name,
                 customerAddress=customer_address,
                 customerPostcode=customer_postcode,
                 customerEmail=customer_email
                 )

def create_inventory_table():
    create_table("tblInventory",
                 itemId=DataType.PRIMARY_KEY,
                 itemName=DataType.TEXT,
                 itemPrice=DataType.INTEGER,
                 itemsInStock=DataType.INTEGER
                 )

def add_item(item_name, item_price, items_in_stock):
    insert_table("tblInventory",
                 itemName=item_name,
                 itemPrice=item_price,
                 itemsInStock=items_in_stock
                 )

def create_order_table():
    create_table("tblOrder",
                 orderId=DataType.PRIMARY_KEY,
                 customerId=(DataType.FOREIGN_KEY, "Customer"),
                 orderDate=DataType.TEXT,
                 orderTotalCost=DataType.INTEGER
                 )

def add_order(customer_id, order_date, order_total_cost):
    insert_table("tblOrder",
                 customerId=customer_id,
                 orderDate=order_date,
                 orderTotalCost=order_total_cost
                 )

def create_order_line_table():
    create_table("tblOrderLine",
                 orderId=(DataType.FOREIGN_KEY, "tblOrder"),
                 itemId=(DataType.FOREIGN_KEY, "tblInventory"),
                 quantity=DataType.INTEGER,
                 costWhenPurchased=DataType.INTEGER
                 )

def add_order_line(order_id, item_id, quantity, cost_when_purchased):
    insert_table("tblOrderLine",
                 orderId=order_id,
                 itemId=item_id,
                 quantity=quantity,
                 costWhenPurchased=cost_when_purchased
                 )

def init_tables():
    create_customer_table()
    create_inventory_table()
    create_order_table()
    create_order_line_table()

def init_sample(filepath, add_func):
    with open(filepath) as file:
        json_file = json.load(file)
    for item in json_file:
        add_func(**item)

def init_sample_customers():
    init_sample("db/customers.json", add_customer)

def init_sample_inventory():
    init_sample("db/inventory.json", add_item)

def get_similarity(word_a, word_b):
    return SequenceMatcher(None, word_a, word_b).ratio()

def search_inventory(search_item):
    sqlstring = """
    SELECT itemName, itemPrice FROM tblInventory;
    """
    items_sql = run_sql(sqlstring)
    items_ranked = list()
    for item_name, item_price in items_sql:
        items_ranked.append((item_name, item_price, get_similarity(search_item, item_name)))
    items_ranked.sort(key=lambda x: x[2], reverse=True)
    items = [Item(item_name, item_price) for item_name, item_price, _ in items_ranked]
    return items
