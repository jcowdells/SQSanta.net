import json
from db.db import *
from difflib import SequenceMatcher

class Item:
    def __init__(self, item_id, item_name, item_price):
        super().__init__()
        self.__id = item_id
        self.__name = item_name
        self.__price = item_price

    def get_name(self):
        return self.__name

    def get_price(self):
        price = self.__price / 100
        return f"£{price:.2f}"

    def get_price_int(self):
        return self.__price

    def get_link(self):
        return f"/items/{self.__id}/"

class Customer:
    def __init__(self, customer_name, customer_address, customer_postcode, customer_email):
        self.__name = customer_name
        self.__address = customer_address
        self.__postcode = customer_postcode
        self.__email = customer_email

    def get_name(self):
        return self.__name

    def get_address(self):
        return self.__address

    def get_postcode(self):
        return self.__postcode

    def get_email(self):
        return self.__email


class Order:
    def __init__(self):
        super().__init__()
        self.__id = 0
        self.__total_price = 0
        self.__items = list()

    def add_item(self, item_name, item_price, item_quantity):
        self.__items.append((item_name, item_price, item_quantity))

    def get_name(self, index):
        return self.__items[index][0]

    def get_price(self, index):
        price = self.__items[index][1] / 100
        return f"£{price:.2f}"

    def get_quantity(self, index):
        return self.__items[index][2]

    def get_num_items(self):
        return len(self.__items)

    def set_total_price(self, total_price):
        self.__total_price = total_price

    def get_total_price(self):
        price = self.__total_price / 100
        return f"£{price:.2f}"

    def set_id(self, order_id):
        self.__id = order_id

    def get_handler(self):
        return f"/handler/{self.__id}/"

class PastOrders:
    def __init__(self):
        self.__orders = list()

    def add_order(self, order_id, order_date, order_price, order_quantity):
        self.__orders.append((order_id, order_date, order_price, order_quantity))

    def get_link(self, index):
        order_id = self.__orders[index][0]
        return f"/orders/{order_id}/"

    def get_date(self, index):
        return self.__orders[index][1]

    def get_price(self, index):
        price = self.__orders[index][2] / 100
        return f"£{price:.2f}"

    def get_quantity(self, index):
        return self.__orders[index][3]

    def get_num_orders(self):
        return len(self.__orders)

def create_customer_table():
    create_table("tblCustomer",
                 customerId=DataType.PRIMARY_KEY,
                 customerName=DataType.TEXT,
                 customerAddress=DataType.TEXT,
                 customerPostcode=DataType.TEXT,
                 customerEmail=DataType.TEXT
                 )

def customer_exists(customer_email):
    sqlstring = """
    SELECT customerId FROM tblCustomer
    WHERE customerEmail = ?
    """
    values = (customer_email,)
    matches = run_sql(sqlstring, values)
    return len(matches) > 0

def get_customer_id(customer_email):
    sqlstring = """
    SELECT customerId FROM tblCustomer
    where customerEmail = ?
    """
    values = (customer_email,)
    matches = run_sql(sqlstring, values)
    if len(matches) > 0:
        return matches[0][0]

def get_customer(customer_id):
    sqlstring = """
    SELECT customerName, customerAddress, customerPostcode, customerEmail FROM tblCustomer
    WHERE customerId = ?
    """
    values = (customer_id,)
    matches = run_sql(sqlstring, values)
    if len(matches) > 0:
        return Customer(*matches[0])

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

def item_exists(item_id):
    sqlstring = """
    SELECT itemId FROM tblInventory
    WHERE itemId = ?
    """
    values = (item_id,)
    matches = run_sql(sqlstring, values)
    return len(matches) > 0

def get_item(item_id):
    sqlstring = """
    SELECT itemName, itemPrice FROM tblInventory
    WHERE itemId = ?
    """
    values = (item_id,)
    matches = run_sql(sqlstring, values)
    if len(matches) > 0:
        return Item(item_id, matches[0][0], matches[0][1])

def update_item_quantity(item_id, item_quantity):
    update_table("tblInventory",
                 "itemId", item_id,
                 itemsInStock=item_quantity
                 )

def get_item_quantity(item_id):
    sqlstring = """
    SELECT itemsInStock FROM tblInventory
    WHERE itemId = ?
    """
    values = (item_id,)
    matches = run_sql(sqlstring, values)
    if len(matches) > 0:
        return matches[0][0]

def create_order_table():
    create_table("tblOrder",
                 orderId=DataType.PRIMARY_KEY,
                 customerId=(DataType.FOREIGN_KEY, "tblCustomer"),
                 orderDate=DataType.TEXT,
                 orderTotalCost=DataType.INTEGER
                 )

def add_order(customer_id, order_date, order_total_cost):
    return insert_table("tblOrder",
                 customerId=customer_id,
                 orderDate=order_date,
                 orderTotalCost=order_total_cost
                 )

def get_order_cost(order_id):
    sqlstring = """
    SELECT orderTotalCost FROM tblOrder
    WHERE orderId = ?
    """
    values = (order_id,)
    matches = run_sql(sqlstring, values)
    if len(matches) > 0:
        return matches[0][0]

def update_order_cost(order_id, order_total_cost):
    update_table("tblOrder",
                 "orderId", order_id,
                 orderTotalCost=order_total_cost)

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

def get_order(order_id):
    sqlstring = """
    SELECT tblInventory.itemName, tblInventory.itemPrice, tblOrderLine.quantity FROM tblOrderLine
    INNER JOIN tblInventory ON tblOrderLine.itemId = tblInventory.itemId
    WHERE tblOrderLine.orderId = ?
    """
    values = (order_id,)
    matches = run_sql(sqlstring, values)
    order = Order()
    for match in matches:
        order.add_item(*match)
    order.set_id(order_id)
    order.set_total_price(get_order_cost(order_id))
    return order

def has_order(order_id):
    sqlstring = """
    SELECT orderId FROM tblOrder
    WHERE orderId = ?
    """
    values = (order_id,)
    return len(values) > 0

def get_orders(customer_id):
    sqlstring = """
    SELECT tblOrder.orderId, tblOrder.orderDate, tblOrder.orderTotalCost, SUM(tblOrderLine.quantity) FROM tblOrder
    INNER JOIN tblOrderLine ON tblOrder.orderId = tblOrderLine.orderId
    WHERE tblOrder.customerId = ?
    GROUP BY tblOrder.orderId
    """
    values = (customer_id,)
    matches = run_sql(sqlstring, values)
    orders = PastOrders()
    for match in matches:
        orders.add_order(*match)
    return orders

def customer_has_order(customer_id, order_id):
    sqlstring = """
    SELECT orderId FROM tblOrder
    WHERE customerId = ?
    AND orderId = ?
    """
    values = (customer_id, order_id)
    matches = run_sql(sqlstring, values)
    return len(matches) > 0

def replace_order_stock(order_id):
    sqlstring = """
    SELECT tblInventory.itemId, tblOrderLine.quantity FROM tblOrderLine
    INNER JOIN tblInventory on tblOrderLine.itemId = tblInventory.itemId
    WHERE tblOrderLine.orderId = orderId
    """
    matches = run_sql(sqlstring)
    for item_id, quantity in matches:
        prev_quantity = get_item_quantity(item_id)
        update_item_quantity(item_id, prev_quantity + quantity)

def delete_order(order_id):
    delete_from_table("tblOrderLine",
                      orderId=order_id)
    delete_from_table("tblOrder",
                      orderId=order_id)

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
    SELECT itemId, itemName, itemPrice FROM tblInventory;
    """
    items_sql = run_sql(sqlstring)
    items_ranked = list()
    for item_id, item_name, item_price in items_sql:
        items_ranked.append((item_id, item_name, item_price, get_similarity(search_item, item_name)))
    items_ranked.sort(key=lambda x: x[3], reverse=True)
    items = [Item(item_id, item_name, item_price) for item_id, item_name, item_price, _ in items_ranked]
    return items
