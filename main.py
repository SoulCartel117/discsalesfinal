from flask import Flask, render_template, request, redirect, url_for
from jinja2 import Environment
from sqlalchemy import create_engine, text
from werkzeug.security import check_password_hash, generate_password_hash
jinja_env = Environment(extensions=['jinja2.ext.loopcontrols'])

app = Flask(__name__)
conn_str = "mysql://root:Fcfisveryfun117@localhost/disc_retail"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()

salt = "kld@djaa%jkh3ljkk&d83038459"
global no_user
no_user = "Not logged in."
current_user = ""
global total_price
total_price = 0


@app.route('/', methods=['GET'])
def landing():
    results = conn.execute(text(f'SELECT * FROM products WHERE discount != price LIMIT 3')).all()
    return render_template('landing.html', results=results, no_user=no_user)


@app.route('/login', methods=['GET'])
def login_get():
    return render_template('login.html', no_user=no_user)


@app.route('/logout', methods=['GET'])
def logout_get():
    global current_user
    current_user = ''
    no_user = "You have been logged out."
    results = conn.execute(text(f'SELECT * FROM products WHERE discount != price LIMIT 3')).all()
    return render_template('landing.html', no_user=no_user, results=results)


@app.route('/login', methods=['POST'])
def login_post():
    username_login = request.form.get("username")
    password_login = request.form.get("password")
    result = conn.execute(text(f"SELECT * FROM user WHERE username = (:username)"), request.form).all()
    if username_login == result[0][1]:
        password = result[0][2]
        if check_password_hash(password, password_login + salt):
            global current_user
            current_user = conn.execute(text(f"SELECT * FROM user where username = (:username)"), request.form).all()
            current_user = current_user[0][0]
            result2 = conn.execute(text(f"SELECT * FROM user WHERE username = (:username)"), request.form).all()
            global no_user
            no_user = result2[0][1]
            acc_type = result2[0][6]
            if acc_type == "A":
                return redirect(url_for('admin_home'))
            elif acc_type == "V":
                return redirect(url_for('vendor_home'))
            else:
                return redirect(url_for('user_home'))
        else:
            login_error = "Login information does not match system information."
            return render_template('Login.html', login_error=login_error)
    else:
        login_error = "Login information does not match system information."
        return render_template('Login.html', login_error=login_error)


@app.route('/register', methods=['POST'])
def register():
    entered_pass1 = request.form.get("password1")
    entered_pass2 = request.form.get("password2")
    entered_username = request.form.get("username_reg")
    entered_email = request.form.get("email")
    hash_pass = generate_password_hash(entered_pass1 + salt)
    saved_username = conn.execute(text(f"SELECT * FROM user WHERE username = \"{entered_username}\""), request.form).all()
    saved_email = conn.execute(text(f"SELECT * FROM user WHERE email = \"{entered_email}\""), request.form).all()
    if not saved_username:
        if not saved_email:
            if entered_pass2 != entered_pass1:
                reg_error = "Entered passwords are not the same."
                return render_template('Login.html', reg_error=reg_error)
            else:
                conn.execute(text(f"INSERT INTO user (username, password, fname, lname, email, type) "
                                  f"VALUES (:username_reg, \"{hash_pass}\", :fname, :lname,\":email\", :type);"), request.form)
                result = conn.execute(text(f"SELECT * from user where username = \"{entered_username}\""), request.form).all()
                acc_type = result[0][6]
                global current_user
                current_user = conn.execute(text(f"SELECT * FROM user where username = (:username_reg)"), request.form).all()[0][0]
                if acc_type == "A":
                    return redirect(url_for('admin_home'))
                elif acc_type == "V":
                    return redirect(url_for('vendor_home'))
                else:
                    return redirect(url_for('user_home'))
        else:
            email_error = "Email already in use, please enter a different Email."
            return render_template('Login.html', email_error=email_error)
    else:
        username_error = "Username already in use, please enter a different username."
        return render_template('Login.html', username_error=username_error)


@app.route('/user_home', methods=['GET'])
def user_home():
    results = conn.execute(text(f'SELECT * FROM user where ID = {current_user};')).all()
    return render_template('user_home.html', results=results, no_user=no_user)


@app.route('/admin_home', methods=['GET'])
def admin_home():
    results = conn.execute(text(f'SELECT * FROM user where ID = {current_user};')).all()
    return render_template('admin_home.html', results=results, no_user=no_user)


@app.route('/vendor_home', methods=['GET'])
def vendor_home():
    results = conn.execute(text(f'SELECT * FROM user where ID = {current_user};')).all()
    return render_template('vendor_home.html', results=results, no_user=no_user)


@app.route('/sort')
def sort():
    if current_user != "":
        results = conn.execute(text(f'SELECT * FROM user where ID = {current_user};')).all()
        results = results[0][6]
        if results:
            if results == "A":
                return redirect(url_for("admin_home"))
            elif results == "V":
                return redirect(url_for("vendor_home"))
            elif results == "C":
                return redirect(url_for('user_home'))
            else:
                login_error = 'You are not logged in, please login to go to your homepage.'
                return render_template('login.html', login_error=login_error)
        else:
            login_error = 'You are not logged in, please login to go to your homepage.'
            return render_template('login.html', login_error=login_error)
    else:
        login_error = 'You are not logged in, please login to go to your homepage.'
        return render_template('login.html', login_error=login_error)


@app.route('/products', methods=['GET'])
def products_get():
    reviews = conn.execute(text(f'SELECT * FROM reviews')).all()
    results = conn.execute(text(f'SELECT * FROM products')).all()
    return render_template('products.html', results=results, no_user=no_user, reviews=reviews)


@app.route('/products', methods=['POST'])
def products_post():
    type = request.form.get('type')
    color = request.form.get('color')
    plastic = request.form.get('plastic')
    if color != "all" and type != "all" and plastic != "all":
        # all three selection
        results = conn.execute(text(f"SELECT * FROM products WHERE color = \"{color}\" and type = \"{type}\" and plastic = '{plastic}';")).all()
        product_filter = f"Displaying {color} {plastic} {type}s."
        return render_template('products.html', results=results, product_filter=product_filter, no_user=no_user)
    elif type != "all" and color == "all" and plastic == "all":
        # only type selection
        results = conn.execute(text(f'SELECT * FROM products WHERE type = \"{type}\";')).all()
        product_filter = f"Displaying All color and all plastic {type}s."
        return render_template('products.html', results=results, product_filter=product_filter, no_user=no_user)
    elif type == "all" and color != "all" and plastic == "all":
        # only color selection
        results = conn.execute(text(f'SELECT * FROM products WHERE color = \"{color}\";')).all()
        product_filter = f"Displaying {color} color discs."
        return render_template('products.html', results=results, product_filter=product_filter, no_user=no_user)
    elif type == "all" and color == "all" and plastic != "all":
        # only plastic selection
        results = conn.execute(text(f'SELECT * FROM products WHERE plastic = \"{plastic}\";')).all()
        product_filter = f"Displaying all color {plastic} discs."
        return render_template('products.html', results=results, product_filter=product_filter, no_user=no_user)
    elif type != "all" and color != "all" and plastic == "all":
        # type and color selection
        results = conn.execute(text(f'SELECT * FROM products WHERE type = \"{type}\" and color = \'{color}\';')).all()
        product_filter = f"Displaying {color} {type}s, of any plastic type."
        return render_template('products.html', results=results, product_filter=product_filter, no_user=no_user)
    elif type != "all" and color == "all" and plastic != "all":
        # type and plastic selection
        results = conn.execute(text(f'SELECT * FROM products WHERE type = \"{type}\" and plastic = \'{plastic}\';')).all()
        product_filter = f"Displaying all color {plastic} {type}s."
        return render_template('products.html', results=results, product_filter=product_filter, no_user=no_user)
    elif type == "all" and color != "all" and plastic != "all":
        # color and plastic selection
        results = conn.execute(text(f'SELECT * FROM products WHERE color = \"{color}\" and plastic = \'{plastic}\';')).all()
        product_filter = f"Displaying {color} {plastic} discs."
        return render_template('products.html', results=results, product_filter=product_filter, no_user=no_user)
    else:
        # no filter selection
        results = conn.execute(text(f'SELECT * FROM products;')).all()
        product_filter = f"Displaying All discs."
        return render_template('products.html', results=results, product_filter=product_filter, no_user=no_user)


@app.route('/products_filter_driver')
def products_filter_driver():
    results = conn.execute(text(f"SELECT * FROM products WHERE type = 'Driver';")).all()
    return render_template('products.html', results=results, no_user=no_user)


@app.route('/products_filter_mid')
def products_filter_mid():
    results = conn.execute(text(f"SELECT * FROM products WHERE type = 'Mid';")).all()
    return render_template('products.html', results=results, no_user=no_user)


@app.route('/products_filter_putter')
def products_filter_putter():
    results = conn.execute(text(f"SELECT * FROM products WHERE type = 'Putter';")).all()
    return render_template('products.html', results=results, no_user=no_user)


@app.route('/products_search', methods=['POST'])
def products_search():
    search = request.form.get('search')
    results = conn.execute(text(f"SELECT * FROM products WHERE title like '%{search}%';"), request.form).all()
    return render_template('products.html', results=results, no_user=no_user)


@app.route('/add_cart', methods=['POST'])
def add_cart():
    product_id = request.form.get('product_id')
    order_amount = request.form.get('order_amount')
    product = conn.execute(text(f"SELECT * FROM products WHERE ID = {product_id};")).all()
    title = product[0][1]
    price = product[0][10]
    color = product[0][6]
    plastic = product[0][8]
    og_price = product[0][4]
    conn.execute(text(f"INSERT INTO cart (user_id, title, product_id, price, color, plastic, quantity, og_price) "
                      f"VALUES ({current_user}, '{title}',{product_id}, {price}, '{color}', '{plastic}', {order_amount},{og_price} );"))
    item_added = f"{title} added to cart."
    return redirect(url_for('products_get', no_user=no_user, item_added=item_added))


@app.route('/add_products', methods=['GET'])
def add_products_get():
    return render_template('vendor_home.html', no_user=no_user)


@app.route('/add_products', methods=['POST'])
def add_products_post():
    title = request.form.get('title')
    price = request.form.get('price')
    desc = request.form.get('desc')
    image = request.form.get('image')
    color = request.form.get('color')
    type = request.form.get('type')
    plastic = request.form.get('plastic')
    quantity =  request.form.get('quantity')
    discount = request.form.get('discount')
    if discount != 1:
        discount = int(price) * float(discount)
        conn.execute(text(f"INSERT INTO products (title, description, image, price, type, color, vendorID, plastic, quantity, discount)"
                          f"VALUES (\"{title}\", \"{desc}\", \"{image}\", \"{price}\", \"{type}\", \"{color}\", {current_user}, '{plastic}', {quantity}, {discount});"), request.form)
        new_product = f'You added a {title} for the price of {price}.'
        return render_template('vendor_home.html', new_product=new_product, no_user=no_user)
    else:
        conn.execute(text(
            f"INSERT INTO products (title, description, image, price, type, color, vendorID, plastic, quantity, discount)"
            f"VALUES (\"{title}\", \"{desc}\", \"{image}\", \"{price}\", \"{type}\", \"{color}\", {current_user}, '{plastic}', {quantity}, {price});"),
                     request.form)
        new_product = f'You added a {title} for the price of {price}.'
        return render_template('vendor_home.html', new_product=new_product, no_user=no_user)


@app.route('/add_products_admin', methods=['POST'])
def add_products_admin_post():
    vendor_id = request.form.get('vendor_id')
    title = request.form.get('title')
    price = request.form.get('price')
    desc = request.form.get('desc')
    image = request.form.get('image')
    color = request.form.get('color')
    type = request.form.get('type')
    plastic = request.form.get('plastic')
    quantity =  request.form.get('quantity')
    discount = request.form.get('discount')
    conn.execute(text(f"INSERT INTO products (title, description, image, price, type, color, vendorID, plastic, quantity, discount)"
                      f"VALUES (\"{title}\", \"{desc}\", \"{image}\", \"{price}\", \"{type}\", \"{color}\", {vendor_id}, '{plastic}, {quantity}, {discount}');"), request.form)
    new_product = f'You added a {title} for the price of {price}.'
    return render_template('admin_home.html', new_product=new_product, no_user=no_user)


@app.route('/delete_products', methods=['GET'])
def delete_products_get():
    return render_template('vendor_home.html', no_user=no_user)


@app.route('/delete_products', methods=['POST'])
def delete_products_post():
    delete_id = request.form.get('delete_id')
    item_name = conn.execute(text(f"SELECT * FROM products WHERE ID = {delete_id};")).all()[0][1]
    vendor_check = conn.execute(text(f"SELECT * FROM products WHERE ID = {delete_id};")).all()[0][7]
    admin_check = conn.execute(text(f"SELECT * FROM user WHERE ID = {current_user};")).all()[0][6]
    if vendor_check == current_user:
        conn.execute(text(f"DELETE FROM products WHERE ID = {delete_id};"), request.form)
        item_delete = f'Item deleted, ID: {delete_id}, Product name: {item_name}.'
        return render_template('vendor_home.html', item_delete=item_delete, no_user=no_user)
    elif admin_check == "A":
        conn.execute(text(f"DELETE FROM products WHERE ID = {delete_id};"), request.form)
        item_delete = f'Item deleted, ID: {delete_id}, Product name: {item_name}.'
        return render_template('vendor_home.html', item_delete=item_delete, no_user=no_user)
    else:
        item_delete = f"You are not the vendor for item ID: {delete_id}."
        return render_template('vendor_home.html', item_delete=item_delete, no_user=no_user)


@app.route('/edit_products', methods=['POST'])
def edit_products_post():
    e_id = request.form.get('e_id')
    e_title = request.form.get('e_title')
    e_desc = request.form.get('e_desc')
    e_price = request.form.get('e_price')
    e_image = request.form.get('e_image')
    e_type = request.form.get('e_type')
    e_color = request.form.get('e_color')
    e_quantity =  request.form.get('e_quantity')
    e_discount = request.form.get('e_discount')
    vendor_id = conn.execute(text(f"SELECT * FROM products where ID = {e_id};")).all()[0][7]
    admin_check = conn.execute(text(f"SELECT * FROM user WHERE ID = {current_user};")).all()[0][6]
    if admin_check != "A":
        if vendor_id != current_user:
            valid_vendor = f'You are not the vendor of that product.'
            return render_template('vendor_home.html', valid_vendor=valid_vendor, no_user=no_user)
    if e_title == "":
        e_title = conn.execute(text(f"SELECT * FROM products WHERE ID = {e_id};")).all()[0][1]
        e_title = f"'{e_title}'"
    else:
        e_title = f"'{e_title}'"
    if e_desc == "":
        e_desc = conn.execute(text(f"SELECT * FROM products WHERE ID = {e_id};")).all()[0][2]
        e_desc = f"\"{e_desc}\""
    else:
        e_desc = f"\"{e_desc}\""
    if e_price == "":
        e_price = conn.execute(text(f"SELECT * FROM products WHERE ID = {e_id};")).all()[0][4]
        e_price = f"'{e_price}'"
    else:
        e_price = f"'{e_price}'"
    if e_image == "":
        e_image = conn.execute(text(f"SELECT * FROM products WHERE ID = {e_id};")).all()[0][3]
        e_image = f"'{e_image}'"
    else:
        e_image = f"'{e_image}'"
    if e_type == "no_change":
        e_type = conn.execute(text(f"SELECT * FROM products WHERE ID = {e_id};")).all()[0][5]
        e_type = f"'{e_type}'"
    else:
        e_type = f"'{e_type}'"
    if e_color == "no_change":
        e_color = conn.execute(text(f"SELECT * FROM products WHERE ID = {e_id};")).all()[0][6]
        e_color = f"'{e_color}'"
    else:
        e_color = f"'{e_color}'"
    if e_quantity == "":
        e_quantity = conn.execute(text(f"SELECT * FROM products WHERE ID = {e_id};")).all()[0][9]
        e_quantity = f"'{e_quantity}'"
    else:
        e_quantity = f"'{e_quantity}'"
    if e_discount == "no_change":
        e_discount = conn.execute(text(f"SELECT * FROM products WHERE ID = {e_id};")).all()[0][10]
        e_discount = f"{e_discount}"
        conn.execute(text(
            f"UPDATE products SET title = {e_title}, description = {e_desc}, price = {e_price}, image = {e_image}, type = {e_type}, color = {e_color}, quantity = {e_quantity}, discount = {e_discount} WHERE ID = {e_id};"))
        updated = f"Product ID: {e_id} has been updated."
        return render_template('vendor_home.html', updated=updated, no_user=no_user)
    else:
        if e_discount != 1:
            e_price = e_price.rstrip("'")
            e_price = e_price.lstrip("'")
            e_price = e_price.rstrip("0")
            e_price = e_price.rstrip(".")
            print(e_price)
            e_discount = int(float(e_price)) * float(e_discount)
            conn.execute(text(
                f"UPDATE products SET title = {e_title}, description = {e_desc}, price = {e_price}, image = {e_image}, type = {e_type}, color = {e_color}, quantity = {e_quantity}, discount = {e_discount} WHERE ID = {e_id};"))
            updated = f"Product ID: {e_id} has been updated."
            return render_template('vendor_home.html', updated=updated, no_user=no_user)
        else:
            conn.execute(text(
                f"UPDATE products SET title = {e_title}, description = {e_desc}, price = {e_price}, image = {e_image}, type = {e_type}, color = {e_color}, quantity = {e_quantity}, discount = {e_discount} WHERE ID = {e_id};"))
            updated = f"Product ID: {e_id} has been updated."
            return render_template('vendor_home.html', updated=updated, no_user=no_user)


@app.route('/cart', methods=['GET'])
def cart_get():
    global total_price
    total_price = 0
    total_discount = 0
    results = conn.execute(text(f"SELECT * FROM cart WHERE user_id = {current_user};")).all()
    address = conn.execute(text(f"SELECT * FROM address WHERE user_id = {current_user};")).all()
    if not results:
        no_items = "There are no items in your cart."
        return render_template('cart.html', results=results, no_user=no_user, address=address, no_items=no_items)
    else:
        order_items = conn.execute(text(f"SELECT * FROM cart WHERE user_id = {current_user};")).all()
        for items in order_items:
            price = float(items[4])
            quantity = float(items[7])
            if quantity > 1:
                item_total = price * quantity
                total_price = total_price + item_total
            else:
                total_price = total_price + price
        for items in order_items:
            price = int(items[4])
            og_price = int(items[8])
            quantity = int(items[7])
            if price != og_price:
                og_price = og_price * quantity
                price = price * quantity
                item_discount = og_price - price
                total_discount = item_discount + total_discount
        return render_template('cart.html', results=results, no_user=no_user, address=address, total_price=total_price, total_discount=total_discount)


@app.route('/checkout', methods=['POST'])
def checkout():
    save_for_later = request.form.get('save_for_later')
    if save_for_later:
        conn.execute(text(f"INSERT INTO address (user_id, credit, cc_date, ssn, address, city, zip, phone)"
                          f"VALUES ({current_user}, :cc_number, :date, :s_number, :address, :city, :zip, :phone);"), request.form)
        ordered = f"Order successful and information saved"
        order_items = conn.execute(text(f"SELECT * FROM cart WHERE user_id = {current_user};")).all()
        order_id = conn.execute(text(f"SELECT count(ID) FROM orders WHERE user_id = {current_user};")).all()
        order_id = str(order_id[0][0])
        order_id = int(order_id) + 1
        for items in order_items:
            title = items[2]
            product_id = items[3]
            price = items[4]
            color = items[5]
            plastic = items[6]
            quantity = items[7]
            conn.execute(text(f"INSERT INTO orders (user_id, item_id, item_title, item_color, item_plastic, quantity, item_price, total_price, order_id) "
                          f"VALUES ({current_user}, {product_id}, '{title}', '{color}', '{plastic}', {quantity}, {price}, {total_price}, {order_id}); "))
        conn.execute(text(f"DELETE FROM cart WHERE user_id = {current_user};"))
        return render_template('order.html', no_user=no_user, ordered=ordered)
    else:
        order_items = conn.execute(text(f"SELECT * FROM cart WHERE user_id = {current_user};")).all()
        order_id = conn.execute(text(f"SELECT count(ID) FROM orders WHERE user_id = {current_user};")).all()
        order_id = str(order_id[0][0])
        order_id = int(order_id) + 1
        for items in order_items:
            title = items[2]
            product_id = items[3]
            price = items[4]
            color = items[5]
            plastic = items[6]
            quantity = items[7]
            conn.execute(text(
            f"INSERT INTO orders (user_id, item_id, item_title, item_color, item_plastic, quantity, item_price, total_price, order_id) "
            f"VALUES ({current_user}, {product_id}, '{title}', '{color}', '{plastic}', {quantity}, {price}, {total_price}, {order_id}); "))
        conn.execute(text(f"DELETE FROM cart WHERE user_id = {current_user};"))
        ordered = f"Order successful and information not saved"
        return redirect(url_for('order_get', no_user=no_user, ordered=ordered))


@app.route('/order', methods=['GET'])
def order_get():
    order_count = conn.execute(text(f"SELECT distinct order_id, date, status, total_price FROM orders WHERE user_id = {current_user};")).all()
    print(order_count)
    results = conn.execute(text(f"SELECT * FROM orders WHERE user_id = {current_user};")).all()
    return render_template('order.html', results=results, no_user=no_user, order_count=order_count)


@app.route('/review_link', methods=['POST'])
def review_get():
    product_id = request.form.get('product_id_review')
    print(f"Review get {product_id}")
    return render_template('reviews.html', no_user=no_user, product_id=product_id)


@app.route('/review', methods=['POST'])
def review_post():
    rating = request.form.get('rating')
    item_id = request.form.get('id')
    print(f"Review post {item_id}")
    title = conn.execute(text(f"SELECT * FROM products WHERE id = {item_id};")).all()[0][1]
    name = conn.execute(text(f"SELECT * FROM user WHERE id = {current_user};")).all()[0][3]
    conn.execute(text(f"INSERT INTO reviews (user_id, name, description, rating, product_id)"
                      f"VALUES ({current_user},\"{name}\", \":description\", :rating, :id);"), request.form)
    review = f"You have left a {rating} star rating for {title} with product ID {item_id}."
    return render_template('reviews.html', no_user=no_user, review=review)


@app.route('/approve', methods=['GET'])
def approve_get():
    results = conn.execute(text(f"SELECT * FROM orders")).all()
    count = conn.execute(text(f"SELECT count(distinct user_id) FROM orders;")).all()[0]
    return render_template('approve.html', no_user=no_user, results=results, count=count)


@app.route('/approve', methods=['POST'])
def approve_post():
    status = request.form.get('approval')
    order_id = request.form.get('order_id')
    user = request.form.get('user_id')
    conn.execute(text(f"UPDATE orders SET status = \'{status}\' WHERE order_id = \'{order_id}\';"))
    if status == "Approve":
        print("past approve")
        items = conn.execute(text(f"SELECT * from orders WHERE order_id = \"{order_id}\";")).all()
        for x in items:
            item_id = x[3]
            print(f"Item id {item_id}")
            item_quantity = x[7]
            print(f"item quantity {item_quantity}")
            inventory = conn.execute(text(f"SELECT * FROM products where ID = {item_id}")).all()[0][9]
            if inventory >= item_quantity:
                print(f"TEST TEST TEST enough inventory")
                inventory = int(inventory) - int(item_quantity)
                conn.execute(text(f"UPDATE products SET quantity = {inventory} WHERE ID = {item_id};"))
                updated = f"The order ID {order_id} ordered by user {user} as been updated to {status}."
                return render_template('approve.html', no_user=no_user, updated=updated)
            else:
                print(f"TEST TEST no enough inventory")
                inventory = int(inventory) - int(item_quantity)
                updated = f"Item ID {item_id} does not have sufficient quantity. Over ordered by {inventory}."
                return render_template('approve.html', no_user=no_user, updated=updated)
    else:
        updated = f"The order ID {order_id} ordered by user {user} as been updated to {status}."
        return render_template('approve.html', no_user=no_user, updated=updated)


@app.route('/quantity_change', methods=['POST'])
def quantity_change():
    product_id = request.form.get('product_id')
    print(product_id)
    quantity = request.form.get('quantity')
    print(quantity)
    conn.execute(text(f"UPDATE cart SET quantity = {quantity} WHERE user_id = {current_user} and product_id = {product_id};"))
    quantity_change = f"Product ID {product_id} has been updated to a quantity of {quantity}."
    return redirect(url_for('cart_get', no_user=no_user, quantity_change=quantity_change))


@app.route('/cart_delete', methods=['POST'])
def cart_delete():
    product_id = request.form.get('product_id')
    print(product_id)
    conn.execute(text(f"DELETE FROM cart WHERE user_id = {current_user} and product_id = {product_id};"))
    quantity_change = f"Removed product {product_id} from cart."
    return redirect(url_for('cart_get', no_user=no_user, quantity_change=quantity_change))


if __name__ == '__main__':
    app.run(debug=True)