from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_migrate import Migrate
from models import db, User, Category, Farmer, Cart, CartItem, Animal
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import hmac
import re
import os

secret_key = os.urandom(16)
print(secret_key.hex())

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


# from dotenv import load_dotenv
# load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False
app.config['SECRET_KEY'] = secret_key
app.config['JWT_SECRET_KEY'] = secret_key
CORS(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


migrate = Migrate(app, db)

db.init_app(app)
bcrypt.init_app(app)

# Import models after initializing db
# from models import Animal, Farmer, User, Category, Cart, CartItem

def safe_str_cmp(a, b):
    return hmac.compare_digest(a, b)

def validate_email(email):
    valid = re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None
    print(f"Validating email '{email}': {'valid' if valid else 'invalid'}")
    return valid

def validate_username(username):
    return len(username) >= 3

def validate_password(password):
    return len(password) >= 8

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print("Received data:", data)

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')  # Change to password instead of password_hash
    address = data.get('address', '')
    role = data.get('role', 'user').lower()

    if not username:
        return jsonify({'message': 'Username is required'}), 400
    if not email:
        return jsonify({'message': 'Email is required'}), 400
    if not validate_email(email):
        return jsonify({'message': 'Invalid email format'}), 400
    if not password:
        return jsonify({'message': 'Password is required'}), 400
    if not validate_password(password):
        return jsonify({'message': 'Password does not meet requirements'}), 400
    if role not in ['farmer', 'user']:
        return jsonify({'message': 'Invalid role specified'}), 400
    
    # Generate a password hash
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        address=address,
        role=role
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Registration successful'}), 200


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    app.logger.debug(f"Login attempt with data: {data}")

    try:
        username = data['username']
        password = data['password']
        role = data['role'].lower()

        if not username or not password:
            return jsonify({'message': 'Username and password are required'}), 400

        user_class = Farmer if role == 'farmer' else User
        user = user_class.query.filter_by(username=username).first()

        if not user:
            app.logger.debug(f"User not found: {username}")
            return jsonify({'message': 'User not found'}), 404

        app.logger.debug(f"Found user: {user}")



        # Check if the provided password matches the stored password hash
        # try:
        #     password_match = bcrypt.check_password_hash(user.password_hash, password)
        # except ValueError as e:
        #     app.logger.error(f"Password hash check failed: {e}")
        #     return jsonify({'message': 'Invalid password hash'}), 500

        # if not password_match:
        #     app.logger.debug(f"Invalid password for user: {username}")
        #     return jsonify({'message': 'Invalid password'}), 401

        if user.role != role:
            app.logger.debug(f"Role mismatch for user: {username}. Expected: {role}, Found: {user.role}")
            return jsonify({'message': 'Role does not match'}), 401

        access_token = create_access_token(identity={'id': user.id, 'role': role, 'username': user.username})
        return jsonify(access_token=access_token, id=user.id, username=username, role=role), 200
    except KeyError as e:
        app.logger.error(f"Missing data in request: {e}")
        return jsonify({'message': 'Missing data in request', 'error': str(e)}), 400
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({'message': 'Login error', 'error': str(e)}), 500


# @app.route('/login', methods=['POST'])
# def login():
#         data = request.get_json()
#         print(data)
        
#         # email = data.get("email")
#         password_hash = str(data.get("password"))
#         username = data.get("username")
#         # role = data.get("role").lower()

#         user = User.query.filter_by(username=username).first()

#         if user is None:
#             return jsonify({'error': 'Unauthorized'}), 401

#         if not bcrypt.check_password_hash(user.password_hash, password_hash):
#             return jsonify({'error': 'Unauthorized, incorrect password'}), 401
        
#         access_token = create_access_token(identity=username)
#         user.access_token = access_token
#         return jsonify ({'message': 'Username added successfully'}), 201



@app.route('/farmer/animals', methods=['POST'])
@jwt_required()
def add_animal():
    claims = get_jwt_identity()
    if claims['role'] != 'farmer':
        return jsonify({'message': 'Unauthorized'}), 403
    new_animal = Animal(
        type=request.json['type'],
        breed=request.json['breed'],
        price=request.json['price'],
        description=request.json['description'],
        farmer_id=claims['id'],
        status='Available'
    )
    if 'image_url' in request.json:
       new_animal.image_url = request.json['image_url']
    db.session.add(new_animal)
    db.session.commit()
    return jsonify({'message': 'Animal added successfully'}), 201
  
@app.route('/farmer/animals/<int:animal_id>', methods=['PATCH'])
@jwt_required()
def update_animal(animal_id):
    claims = get_jwt_identity()
    animal = Animal.query.filter_by(id=animal_id, farmer_id=claims['id']).first()
    if animal:
        animal.type = request.json.get('type', animal.type)
        animal.breed = request.json.get('breed', animal.breed)
        animal.price = request.json.get('price', animal.price)
        animal.description = request.json.get('description', animal.description)
        animal.image_url = request.json['image_url']
        animal.status = request.json.get('status', animal.status)
        db.session.commit()
        return jsonify({'message': 'Animal updated successfully'}), 200
    return jsonify({'message': 'Animal not found'}), 404

@app.route('/animals', methods=['GET'])
def list_animals():
    animals = Animal.query.all()
    return jsonify([animal.serialize() for animal in animals]), 200

@app.route('/animals/categories', methods=['GET'])
# def search_animals_by_category(id):
    # category = Category.query.filter(Category.id==id).first()
    # if category:
    #     animals = Animal.query.filter_by(category_id=category.id).all()
    #     return jsonify([animal.serialize() for animal in animals]), 200
    # else:
    #     return jsonify({'message': 'Category not found'}), 404

def list_categories():
    categories = Category.query.all()
    return jsonify([category.serialize() for category in categories]), 200

@app.route('/categories', methods=['POST'])
@jwt_required()
def add_category():
    claims = get_jwt_identity()
    if claims['role'] != 'farmer':
        return jsonify({'message': 'Unauthorized'}), 403
    category_name = request.json['name']
    if Category.query.filter_by(name=category_name).first():
        return jsonify({'message': 'Category already exists'}), 409
    new_category = Category(name=category_name)
    db.session.add(new_category)
    db.session.commit()
    return jsonify({'message': 'Category added successfully'}), 201


@app.route('/cart', methods=['GET'])
@jwt_required()
def get_cart():
    claims = get_jwt_identity()
    user_id = claims['id']
    cart = Cart.query.filter_by(user_id=user_id, status='Pending').first()
    if not cart:
        return jsonify({'message': 'Cart not found'}), 404
    return jsonify(cart.serialize()), 200

@app.route('/cart', methods=['POST'])
@jwt_required()
def add_to_cart():
    claims = get_jwt_identity()
    user_id = claims['id']
    data = request.get_json()
    animal_id = data.get('animal_id')
    quantity = data.get('quantity', 1)

    animal = Animal.query.get(animal_id)
    if not animal:
        return jsonify({'message': 'Animal not found'}), 404

    cart = Cart.query.filter_by(user_id=user_id, status='Pending').first()
    if not cart:
        cart = Cart(user_id=user_id, total_price=0)
        db.session.add(cart)
        db.session.commit()

    cart_item = CartItem.query.filter_by(cart_id=cart.id, animal_id=animal_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart.id, animal_id=animal_id, quantity=quantity, unit_price=animal.price)
        db.session.add(cart_item)

    cart.total_price += animal.price * quantity
    db.session.commit()
    return jsonify({'message': 'Item added to cart'}), 201

@app.route('/cart/item/<int:cart_item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(cart_item_id):
    claims = get_jwt_identity()
    user_id = claims['id']

    cart_item = CartItem.query.get(cart_item_id)
    if not cart_item:
        return jsonify({'message': 'Cart item not found'}), 404

    cart = Cart.query.filter_by(id=cart_item.cart_id, user_id=user_id, status='Pending').first()
    if not cart:
        return jsonify({'message': 'Cart not found'}), 404

    cart.total_price -= cart_item.unit_price * cart_item.quantity
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Item removed from cart'}), 200

@app.route('/cart/checkout', methods=['POST'])
@jwt_required()
def checkout_cart():
    claims = get_jwt_identity()
    user_id = claims['id']
    cart = Cart.query.filter_by(user_id=user_id, status='Pending').first()
    if not cart:
        return jsonify({'message': 'Cart not found'}), 404

    cart.status = 'Confirmed'
    db.session.commit()
    return jsonify({'message': 'Checkout successful'}), 200

# Farmer Routes to See Orders

@app.route('/farmer/orders', methods=['GET'])
@jwt_required()
def get_farmer_orders():
    claims = get_jwt_identity()
    if claims['role'] != 'farmer':
        return jsonify({'message': 'Unauthorized'}), 403

    farmer_id = claims['id']
    animals = Animal.query.filter_by(farmer_id=farmer_id).all()
    animal_ids = [animal.id for animal in animals]

    cart_items = CartItem.query.filter(CartItem.animal_id.in_(animal_ids)).all()
    orders = {}
    for item in cart_items:
        if item.cart_id not in orders:
            orders[item.cart_id] = []
        orders[item.cart_id].append(item.serialize())

    return jsonify(orders), 200

# Error handling
@app.errorhandler(404)
def not_found_error(error):
    print(error)
    return jsonify({'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    print(error)
    return jsonify({'message': 'An internal error occurred'}), 500

if __name__ == '__main__':
  with app.app_context():
    db.create_all()
    app.run(debug=True, host='0.0.0.0')
