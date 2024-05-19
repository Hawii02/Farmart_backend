from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates, relationship
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
import re

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt() 

class Category(db.Model, SerializerMixin):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    animals = db.relationship('Animal', backref='category', lazy=True)

    def _repr_(self):
        return f'<Category {self.name}>'
    
class Animal(db.Model, SerializerMixin):
    __tablename__ = 'animals'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Available')  # e.g., Available, Sold Out, Pending
    description = db.Column(db.Text)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'))
    image_url = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    @validates(price)
    def validate_price(self, key, price):
        if price < 0:
            raise ValueError("Price must be non-negative.")
        return price

    @validates('status')
    def validate_status(self, key, status):
        valid_statuses = {'Available', 'Sold Out', 'Pending'}
        if status not in valid_statuses:
            raise ValueError("Invalid status for animal.")
        return status

    def _repr_(self):
        return f'<Animal {self.type} {self.breed} in category {self.category.name}>'

    
class Farmer(db.Model, SerializerMixin):
    __tablename__ = 'farmers'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    farm_name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    animals = db.relationship('Animal', backref='farmer', lazy=True)

    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError('Username is required.')
        if len(username) < 3:
            raise ValueError('Username must be at least 3 characters long.')
        return username
    
    @validates('email')
    def validate_email(self, key, address):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", address):
            raise ValueError("Invalid email address")
        return address
    
    @validates('password_hash')
    def validate_password(self, key, password):
        password_regex = r'(?=.\d)(?=.[a-z])(?=.*[A-Z]).{8,}'  # Example: At least one number, one lowercase and one uppercase letter, and at least 8 characters
        if not re.match(password_regex, password):
            raise ValueError("Password must contain at least 8 characters, including one number, one lowercase and one uppercase letter.")
        return generate_password_hash(password)
    
    serialize_rules = ('-password_hash',)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def _repr_(self):
        return f'<Farmer {self.username} at {self.farm_name}>'
    
class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    address = db.Column(db.String(255))
    role = db.Column(db.String(10), nullable=False)  # Add role field
    carts = db.relationship('Cart', backref='user', lazy=True)

    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError('Username is required.')
        if len(username) < 3:
            raise ValueError('Username must be at least 3 characters long.')
        return username
    
    @validates('email')
    def validate_email(self, key, address):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", address):
            raise ValueError("Invalid email address")
        return address
    
    @validates('password_hash')
    def validate_password(self, key, password):
        password_regex = r'(?=.\d)(?=.[a-z])(?=.*[A-Z]).{8,}'  # Example: At least one number, one lowercase and one uppercase letter, and at least 8 characters
        if not re.match(password_regex, password):
            raise ValueError("Password must contain at least 8 characters, including one number, one lowercase and one uppercase letter.")
        return generate_password_hash(password)

    serialize_rules = ('-password_hash',)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def _repr_(self):
        return f'<User {self.username}>'
    
class Cart(db.Model, SerializerMixin):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    total_price = db.Column(db.Float)
    status = db.Column(db.String(20), default='Pending')  # e.g., Pending, Confirmed, Rejected
    order_date = db.Column(db.DateTime, onupdate=db.func.now())
    items = db.relationship('CartItem', backref='cart', lazy=True)

    def _repr_(self):
        return f'<Cart {self.id} by User {self.user_id}>'

class CartItem(db.Model, SerializerMixin):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'))
    animal_id = db.Column(db.Integer, db.ForeignKey('animals.id'))
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float)
    
    def _repr_(self):
        return f'<CartItem for Cart {self.cart_id}, Animal {self.animal_id}>'