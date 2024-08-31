from flask import render_template, request, redirect, url_for, session
from app import app, mongo
from werkzeug.security import generate_password_hash, check_password_hash
import cv2
# import numpy as np
from fer import FER
from flask import render_template
import datetime
from bson import ObjectId
from flask_pymongo import PyMongo

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
    #products = get_all_products()
    if 'username' in session:
        products = get_all_products()
        
        return render_template('index.html', products=products)  # Display homepage
    return redirect(url_for('login'))

def get_all_products():
    try:
        print(mongo.db.get_collection)
        products = list(mongo.db.products.find())
        print("Printing the products here ==================", products)
        return products
    except Exception as e:
        print(f"Error fetching products: {e}")
        return []  # Return an empty list if an error occurs

@app.route('/product/<product_id>')
def product_details(product_id):
    product = mongo.db.products.find_one({"_id": product_id})
    if product:
        return render_template('product_details.html', product=product)
    else:
        return "Product not found", 404

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
# def detect_emotion():
#     cap = cv2.VideoCapture(0)  # Open the camera
#     emotion_detector = FER(mtcnn=True)

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print("Failed to grab frame")
#             break
        
#         emotions = emotion_detector.detect_emotions(frame)
#         if emotions:
#             dominant_emotion = max(emotions[0]["emotions"], key=emotions[0]["emotions"].get)
#             print(f"Detected Emotion: {dominant_emotion}")
        
#         cv2.imshow('Mood Detection', frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()
#     return render_template('recommendations.html', products=None, mood=None)

# detect_emotion()

# def get_recommendations(mood):
#     try:
#         # Define recommendation queries based on mood
#         queries = {
#             'happy': {"category": {"$in": ['joy', 'fun', 'celebration']}},
#             'sad': {"category": {"$in": ['comfort', 'soothe', 'relax']}},
#             'angry': {"category": {"$in": ['calm', 'stress relief', 'exercise']}},
#             'surprised': {"category": {"$in": ['novelty', 'gift', 'unique']}},
#             'fear': {"category": {"$in": ['security', 'self-care', 'safety']}},
#             'disgusted': {"category": "wellness", "price": {"$lt": 125}}
#         }

#         query = queries.get(mood, {})
#         recommendations = list(mongo.db.products.find(query))
#         return recommendations
#     except Exception as e:
#         print(f"Error getting recommendations: {e}")
#         return []

# @app.route('/product/<product_id>')
# def product_details(product_id):
#     # Fetch the product from the MongoDB database using the product_id
#     product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
    
#     if product:
#         # Render the product details page and pass the product data
#         return render_template('product_details.html', product=product)
#     else:
#         # Handle the case where the product is not found
#         return "Product not found", 404

@app.route('/add_to_cart/<product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []  # Initialize cart in session if it doesn't exist

    # Add product to cart
    session['cart'].append(product_id)
    return redirect(url_for('cart'))

# Route to display the cart
@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    return render_template('cart.html', cart=cart_items)

@app.route('/log_activity', methods=['POST'])
def log_activity():
    user_id = session.get('user_id')
    activity = request.json.get('activity')
    if user_id and activity:
        mongo.db.activity_feed.insert_one({
            'user_id': user_id,
            'activity': activity,
            'timestamp': datetime.datetime.now()
        })
        return {'status': 'Activity logged'}, 200
    return {'status': 'Failed to log activity'}, 400

@app.route('/activity_feed')
def activity_feed():
    user_id = session.get('user_id')
    activities = mongo.db.activity_feed.find({'user_id': user_id}).sort('timestamp', -1)
    return render_template('activity_feed.html', activities=activities)

@app.route('/share_cart', methods=['POST'])
def share_cart():
    user_id = session.get('user_id')
    shared_with = request.json.get('shared_with')  # List of user IDs
    if user_id and shared_with:
        for recipient_id in shared_with:
            mongo.db.shared_carts.insert_one({
                'user_id': user_id,
                'shared_with': recipient_id,
                'cart_items': mongo.db.carts.find_one({'user_id': user_id})['items']
            })
        return {'status': 'Cart shared successfully'}, 200
    return {'status': 'Failed to share cart'}, 400

@app.route('/shared_carts')
def shared_carts():
    user_id = session.get('user_id')
    carts = mongo.db.shared_carts.find({'shared_with': user_id})
    return render_template('shared_carts.html', carts=carts)

@app.route('/share_purchase', methods=['POST'])
def share_purchase():
    user_id = session.get('user_id')
    shared_with = request.json.get('shared_with')  # List of user IDs
    purchase_details = request.json.get('purchase_details')
    if user_id and shared_with and purchase_details:
        for recipient_id in shared_with:
            mongo.db.shared_purchases.insert_one({
                'user_id': user_id,
                'shared_with': recipient_id,
                'purchase_details': purchase_details
            })
        return {'status': 'Purchase shared successfully'}, 200
    return {'status': 'Failed to share purchase'}, 400

@app.route('/apply_discount', methods=['POST'])
def apply_discount():
    user_id = session.get('user_id')
    if user_id:
        # Example logic for applying a discount
        cart_items = mongo.db.carts.find_one({'user_id': user_id})['items']
        discount = calculate_discount(cart_items)  # Implement this function based on your logic
        return {'status': 'Discount applied', 'discount': discount}, 200
    return {'status': 'Failed to apply discount'}, 400

def calculate_discount(cart_items):
    # Implement your discount logic here
    return 10  # Example discount value

app.config["MONGO_URI"] = "mongodb://localhost:27017/mydatabase"
mongo = PyMongo(app)


@app.route('/create_group_purchase', methods=['POST'])
def create_group_purchase():
    user_id = session.get('user_id')
    if not user_id:
        return {'status': 'Unauthorized'}, 401
    
    group_name = request.json.get('group_name')
    products = request.json.get('products')
    members = request.json.get('members')

    group_purchase = {
        'group_name': group_name,
        'created_by': user_id,
        'members': members,
        'products': products,
        'discount': calculate_group_discount(members)  # Implement this function based on your logic
    }

    mongo.db.group_purchases.insert_one(group_purchase)
    return {'status': 'Group purchase created successfully'}, 200

def calculate_group_discount(members):
    # Example logic for calculating discount based on the number of members
    return 10 if len(members) > 5 else 5

@app.route('/group_purchases')
def group_purchases():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    group_purchases = mongo.db.group_purchases.find()
    group_purchases_list = list(group_purchases)
    return render_template('group_purchases.html', group_purchases=group_purchases_list)

@app.route('/join_group_purchase/<group_id>', methods=['POST'])
def join_group_purchase(group_id):
    user_id = session.get('user_id')
    if not user_id:
        return {'status': 'Unauthorized'}, 401
    
    mongo.db.group_purchases.update_one(
        {'_id': ObjectId(group_id)},
        {'$addToSet': {'members': user_id}}
    )
    return {'status': 'Joined group purchase successfully'}, 200

@app.route('/group_purchases')
def view_group_purchases():
    group_purchases = mongo.db.group_purchases.find()
    return render_template('group_purchases.html', group_purchases=group_purchases)






