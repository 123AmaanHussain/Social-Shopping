from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB configuration
app.config['MONGO_URI'] = 'mongodb://localhost:27017/your_database_name'
mongo = PyMongo(app)

# User model routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        user = {
            'username': username,
            'email': email,
            'password': hashed_password
        }

        existing_user = mongo.db.users.find_one({'email': email})
        if not existing_user:
            mongo.db.users.insert_one(user)
            return redirect(url_for('login'))
        else:
            return 'Email already exists.'

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = mongo.db.users.find_one({'email': email})

        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            return redirect(url_for('index'))

        return 'Login failed. Check your credentials.'

    return render_template('login.html')

@app.route('/index')
def index():
    if 'username' in session:
        return render_template('index.html')  # Display homepage
    return redirect(url_for('login'))

# Product management routes
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        image_url = request.form['image_url']

        product = {
            'name': name,
            'description': description,
            'price': price,
            'image_url': image_url
        }

        mongo.db.products.insert_one(product)
        return redirect(url_for('view_products'))

    return render_template('add_product.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/view_products')
def view_products():
    products = mongo.db.products.find()
    return render_template('view_products.html', products=products)

# Function to simulate mood-based recommendations (placeholder)
def get_recommendations(mood):
    # This should be replaced with actual mood detection logic
    ommendations = mongo.db.products.find()  # Get all products for now
    return recommendations

@app.route('/recommendations')
def recommendations():
    mood = request.args.get('mood', None)  # Get mood from request or default to 'happy'
    products = get_recommendations(mood)
    return render_template('recommendations.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)

def add_to_cart(product_id):
    # Assuming you have a products collection to fetch product details
    product = mongo.db['products'].find_one({'_id': product_id})
    
    if product:
        user_id = session.get('user_id')
        if user_id:
            cart_collection.update_one(
                {'user_id': user_id},
                {'$addToSet': {'products': product}},
                upsert=True
            )
            return redirect(url_for('recommendations'))
        else:
            return redirect(url_for('login'))  # Redirect to login if not authenticated
    else:
        return "Product not found", 404


# CART RELATED DATA
cart_collection = db['cart']
products_collection = db['products']
def cart():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    cart_items = cart_collection.find_one({'user_id': user_id})
    cart = cart_items.get('products', []) if cart_items else []
    return render_template('cart.html', cart=cart)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    cart_items = cart_collection.find_one({'user_id': user_id})
    cart = cart_items.get('products', []) if cart_items else []

    for item in cart:
        product_id = str(item['id'])
        quantity = int(request.form.get(f'quantity_{product_id}', 1))
        item['quantity'] = quantity

    cart_collection.update_one(
        {'user_id': user_id},
        {'$set': {'products': cart}},
        upsert=True
    )

    return redirect(url_for('cart'))

@app.route('/share_cart', methods=['POST'])
def share_cart():
    # Placeholder for sharing functionality
    return "Cart shared with friends."

@app.route('/place_order', methods=['POST'])
def place_order():
    # Placeholder for order placement functionality
    return "You have successfully ordered the products."

if __name__ == '__main__':
    app.run(debug=True)

#CHECKOUT PAGE
def logout():
    if request.method == 'POST':
        session.pop('user_id', None)
        session.pop('username', None)
        return render_template('checkout.html', message="You have successfully logged out.")

    return redirect(url_for('login'))

#FRIENDS
@app.route('/add_friend', methods=['POST'])
def add_friend():
    user_id = session.get('user_id')
    friend_email = request.form['friend_email']
    
    if not user_id:
        return redirect(url_for('login'))

    friend = mongo.db.users.find_one({'email': friend_email})
    if friend:
        mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$addToSet': {'friends': friend_email}}
        )
        return redirect(url_for('friends_list'))
    else:
        return "Friend not found."

@app.route('/friends_list')
def friends_list():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    friends = user.get('friends', []) if user else []
    return render_template('friends_list.html', friends=friends)
