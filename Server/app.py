from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from models import db, Category, Animal, Farmer, User
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
import hmac
import re
import os

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(16).hex()
app.config['JWT_SECRET_KEY'] = os.urandom(16).hex()
CORS(app)

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# Import models after initializing db
from models import Animal, Farmer, User, Category, Cart, CartItem

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
    password_hash = data.get('password_hash')
    address = data.get('address')
    role = data.get('role', 'user').lower()

    if not username:
        return jsonify({'message': 'Username is required'}), 400
    if not email:
        return jsonify({'message': 'Email is required'}), 400
    if not validate_email(email):
        return jsonify({'message': 'Invalid email format'}), 400
    if not password_hash:
        return jsonify({'message': 'Password is required'}), 400
    if not validate_password(password_hash):
        return jsonify({'message': 'Password does not meet requirements'}), 400
    if role not in ['farmer', 'user']:
        return jsonify({'message': 'Invalid role specified'}), 400
    
    new_user = User(
        username=username,
        email=email,
        password=password_hash,
        address=address,
        role=role
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Registration successful'}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        username = data['username']
        password = data['password']
        role = data['role'].lower()

        if not username or not password:
            return jsonify({'message': 'Username and password are required'}), 400

        user_class = Farmer if role == 'farmer' else User
        user = user_class.query.filter_by(username=username).first()

        if not user:
            return jsonify({'message': 'User not found'}), 404

        if not bcrypt.check_password_hash(user.password_hash, password):
            return jsonify({'message': 'Invalid password'}), 401

        if user.role != role:
            return jsonify({'message': 'Role does not match'}), 401

        access_token = create_access_token(identity={'id': user.id, 'role': role, 'username': user.username})
        return jsonify(access_token=access_token, id=user.id, username=username, role=role), 200
    except KeyError as e:
        return jsonify({'message': 'Missing data in request', 'error': str(e)}), 400
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'message': 'Login error', 'error': str(e)}), 500

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
    db.session.add(new_animal)
    db.session.commit()
    return jsonify({'message': 'Animal added successfully'}), 201

@app.route('/farmer/animals/<int:animal_id>', methods=['PUT'])
@jwt_required()
def update_animal(animal_id):
    claims = get_jwt_identity()
    animal = Animal.query.filter_by(id=animal_id, farmer_id=claims['id']).first()
    if animal:
        animal.type = request.json.get('type', animal.type)
        animal.breed = request.json.get('breed', animal.breed)
        animal.price = request.json.get('price', animal.price)
        animal.description = request.json.get('description', animal.description)
        animal.status = request.json.get('status', animal.status)
        db.session.commit()
        return jsonify({'message': 'Animal updated successfully'}), 200
    return jsonify({'message': 'Animal not found'}), 404

@app.route('/animals', methods=['GET'])
def list_animals():
    animals = Animal.query.all()
    return jsonify([animal.serialize() for animal in animals]), 200

@app.route('/animals/by_category', methods=['GET'])
def search_animals_by_category():
    category_name = request.args.get('category')
    category = Category.query.filter_by(name=category_name).first()
    if category:
        animals = Animal.query.filter_by(category_id=category.id).all()
        return jsonify([animal.serialize() for animal in animals]), 200
    return jsonify({'message': 'Category not found'}), 404

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
    db.create_all()
    app.run(debug=True, host='0.0.0.0')