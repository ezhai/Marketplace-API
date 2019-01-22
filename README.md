# Marketplace-API
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>
<body>
    <h2>
        My submission for the Summer 2019 Shopify Backend Developer Challenge
    </h2>
    <h3>
        Classes and Methods:
    </h3>
    <p>
        Item(title, price, inventory_count) - stores the data of an product <br> <br>
        ItemSchema(title, price, inventory_count) - format for printing out Item data <br> <br>
        Cart(items, total_cost) - stores the data of a user's cart
        <ul>
            <li>
                update_cost() - updates the total_cost of Items in the car
            </li>
            <li>
                empty_cart() - resets the Cart; empties out the contents of items and resets total_cost to 0
            </li>
            <li>
                num_in_cart(Item item) - returns the number of the queried Item currently in the cart
            </li>
        </ul>
        CartSchema(items, total_cost) - format for printing out Cart data <br>
    </p>
    <h3>
        RESTFUL Commands:
    </h3>
    <h4>
        "GET /inventory[?available]"
    </h4>
    <p>
        Returns a list of all Items in the inventory in a JSON format. <br>
        Has an optional parameter to display only Items currently in stock.
    </p>
    <h4>
        "POST /inventory"
    </h4>
    <p>
        Adds a new Item to the inventory. Item must be in JSON format and posted in the body section of the request. <br>
        Format: {"title": (title), "price": (price), "inventory_count": (inventory_count)}
    </p>
    <h4>
        "GET /inventory/(item_title)"
    </h4>
    <p>
        Returns the Item in JSON format in the inventory with the specified title if it exists.
    </p>
    <h4>
        "PUT /inventory/(item_title)"
    </h4>
    <p>
        Updates an Item's data. Updated data must be in JSON format and posted in the body section of the request. <br>
        Format: {"title": (title), "price": (price), "inventory_count": (inventory_count)}
    </p>
    <h4>
        "DELETE /inventory/(item_title)"
    </h4>
    <p>
        Deletes the Item in the inventory with the specified title if it exists.
    </p>
    <h4>
        "PUT /inventory/(item_title)/(cart_user)/purchase"
    </h4>
    <p>
        Adds the Item with the specified title to the specified user's Cart if it is currently in stock.
    </p>
    <h4>
        "GET /carts/(cart_user)>"
    </h4>
    <p>
        Returns the specified user's Cart in JSON format.
    </p>
    <h4>
        "PUT /carts/(cart_user)>"
    </h4>
    <p>
        Creates a new Cart with the specified name if it doesn't already exist.
    </p>
    <h4>
        "PUT /carts/(cart_user)/complete>"
    </h4>
    <p>
        "Completes" a specified user's Cart by resetting it and returning the Items that were successfully purchased
        and items that could not be purchased in JSON format. The amount of Items purchased is deducted from their
        inventory_counts.
    </p>
</body>
</html>
