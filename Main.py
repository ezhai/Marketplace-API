from flask import Flask, request, jsonify, render_template
from flask_restful import Api, Resource, reqparse
from marshmallow import Schema, fields, post_load


app = Flask(__name__, template_folder="templates")
api = Api(app)


# The basic Item class for storing product details
# Attributes: title, price, inventory_count
class Item:
    def __init__(self, title, price, inventory_count):
        self.title = title
        self.price = price
        self.inventory_count = inventory_count

    # Custom format for representing Items
    def __repr__(self):
        return '<Item(title={self.title!r})>'.format(self=self)


# A schema which makes it easier to display an Item in JSON format
class ItemSchema(Schema):
    title = fields.Str()
    price = fields.Number()
    inventory_count = fields.Integer()

    @post_load
    def make_item(self, data):
        return Item(**data)


# A Cart class for storing items in a cart and calculating their cost
# Attributes: items, total_cost
# You can set items and total_cost yourself when initializing the cart, but be careful if you do
class Cart:
    def __init__(self, items=[], total_cost=0):
        self.items = items
        self.total_cost = total_cost

    # Updates the total_cost of the Items in the Cart
    def update_cost(self):
        self.total_cost = 0
        for item in self.items:
            self.total_cost += item.price

    # Resets/empties out the Cart
    def empty_cart(self):
        self.items = []
        self.total_cost = 0

    # Finds the number of the specified item in the Cart
    # num_in_cart: Item -> Nat
    def num_in_cart(self, query_item):
        i = 0
        for item in self.items:
            if item.title == query_item.title:
                i += 1
        return i


# A schema which makes it easier to display an Cart in JSON format
class CartSchema(Schema):
    items = fields.List(fields.Nested(ItemSchema))
    total_cost = fields.Number()

    @post_load
    def make_cart(self, data):
        return Cart(**data)


# The global inventory and cart systems filled with testing data
inventory = [
    Item("Pencil", 42.00, 9001),
    Item("Apple", 2000.50, 200000),
    Item("Eraser", 3.00, 13),
    Item("Supreme Hoodie", 500.50, 0)
]

carts = {"my_cart": Cart(inventory),
         "cart_1": Cart()}


# Displays the html for the home page
# Usage: "/"
@app.route("/")
def home_screen():
    return render_template('home.html')


# Retrieves and displays the items in the inventory
# An optional parameter "available" returns all items with available inventory
# Usage: GET "/inventory[?available]"
@app.route("/inventory", methods=['GET'])
def get_inventory():
    schema = ItemSchema(many=True)
    items = schema.dump(inventory)
    # If the available parameter is passed in, filters out all the out-of-stock items
    if 'available' in request.args:
        items = schema.dump(filter(lambda t: t.inventory_count > 0, inventory))
    return jsonify(items.data), 200


# Adds a new Item to the inventory
# Consumes a JSON-ified Item of the format "{"title": <title>, "price": <price>, "inventory_count": <inventory_count>}"
# Usage: POST "/inventory"
# Body: {"title": <title>, "price": <price>, "inventory_count": <inventory_count>}
@app.route("/inventory", methods=['POST'])
def add_item():
    new_item = ItemSchema().load(request.json)
    inventory.append(new_item.data)
    schema = ItemSchema(many=True)
    items = schema.dump(inventory)
    return jsonify(items.data), 201


# Retrieves and displays a single Item from the inventory
# Usage: "/inventory/<string:name>"
# <string:name> is the title of the desired Item
@app.route("/inventory/<string:name>", methods=['GET'])
def get_item(name):
    for item in inventory:
        if name.lower() == item.title.lower():
            schema = ItemSchema()
            desired_item = schema.dump(item)[0]
            return jsonify(desired_item), 200

    return "Error 404: Item {} not found in inventory".format(name), 404


# Adds a given Item to a given user's Cart if the Item's inventory_count is not 0
# Usage: "/inventory/<string:name>/<string:user>/purchase"
# <string:name> is the title of the desired Item
# <string:user> is the string corresponding to the desired user's Cart
@app.route("/inventory/<string:name>/<string:user>/purchase", methods=['PUT'])
def purchase_item(name, user):
    for item in inventory:
        # Finds the specified item in the inventory
        if name.lower() == item.title.lower():
            if user in carts:
                pass
            # If a user's cart doesnt already exist, creates a new one
            else:
                new_cart = Cart()
                carts[user] = new_cart

            # Adds an item to cart only if they cannot buy any more product than currently in stock
            if item.inventory_count - carts[user].num_in_cart(item) > 0:
                carts[user].items.append(item)
                carts[user].update_cost
                return "{} added to cart".format(item.title), 200
            else:
                return "Error 400: You cannot purchase any more {} :(".format(item.title), 400

    return "Error 404: Item {} not found in inventory".format(name), 404


# Updates the information of a given Item
# Consumes a JSON-ified Item of the format {"title": <title>, "price": <price>, "inventory_count": <inventory_count>}
# Usage: PUT "/inventory/<string:name>"
# <string:name> is the title of the desired Item
# Body: {"title": <title>, "price": <price>, "inventory_count": <inventory_count>}
@app.route("/inventory/<string:name>", methods=['PUT'])
def update_item(name):
    for item in inventory:
        if name.lower() == item.title.lower():
            # Updates the Item in an inventory
            item.title = request.json["title"]
            item.price = request.json["price"]
            item.inventory_count = request.json["inventory_count"]

            # Returns the updated Item in JSON format
            schema = ItemSchema()
            updated_item = schema.dump(item)[0]
            return jsonify(updated_item), 200

    return add_item()


# Deletes a given item from the inventory
# Usage: DELETE "/inventory/<string:name>"
# <string:name> is the title of the unwanted Item
@app.route("/inventory/<string:name>", methods=['DELETE'])
def delete_item(name):
    global inventory

    for item in inventory:
        if name.lower() == item.title.lower():
            deleted_item = item
            break
    else:
        return "Error 404: Item {} not found in inventory".format(name), 404

    inventory = [item for item in inventory if item.title.lower() != name.lower()]
    return "Item {} has been removed from the inventory".format(deleted_item.title), 200


# Displays the information of a given Cart
# Usage: GET "/carts/<string:user>"
# <string:user> is the string corresponding to the desired user's Cart
@app.route("/carts/<string:user>", methods=['GET'])
def get_cart(user):
    if user in carts:
        carts[user].update_cost()
        schema = CartSchema()
        cart = schema.dump(carts[user])[0]
        return jsonify(cart), 200
    else:
        return "Error 404: Cart not found.", 404


# Creates a new Cart and adds it to the carts system if one with the specified name doesn't already exist
# Usage: POST "/carts/<string:user>"
@app.route("/carts/<string:user>", methods=['POST'])
def add_cart(user):
    if user in carts:
        get_cart(user)
    else:
        carts[user] = Cart()
        schema = CartSchema()
        cart = schema.dump(carts[user])[0]
    return jsonify(cart), 201


# Completes a purchase of all the items in a given Cart
# Returns the successful purchases and unsuccessful purchases (ie. denied over-purchases)
# Usage: PUT "/carts/<string:user>/complete"
@app.route("/carts/<string:user>/complete", methods=['PUT'])
def complete_cart(user):
    cart = carts[user]
    cart.update_cost()
    success = []
    failed = []

    for item in cart.items:
        item_in_inventory = inventory[inventory.index(item)]

        # Adds valid purchases to a list of accepted purchases
        if item_in_inventory.inventory_count > 0:
            item_in_inventory.inventory_count -= 1
            success.append(item)
        # Blocks accidental over-purchases from going through and adds the items to a list of denied purchases
        else:
            failed.append(item)
    # Empties the cart
    cart.empty_cart()

    # Prints out the successful and unsuccessful purchases
    schema = ItemSchema(many=True)
    success_items = schema.dump(success)
    failed_items = schema.dump(failed)
    return jsonify({"purchased": success_items,
                    "unable_to_purchase": failed_items})


# Runs the api. Note that the default port is 5000
# It can be accessed by calling http://localhost:5000
if __name__ == '__main__':
    app.run(debug=True)



