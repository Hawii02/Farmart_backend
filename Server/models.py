from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates, relationship
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from bcrypt import gensalt, hashpw
import re

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)
bcrypt = Bcrypt()

class Category(db.Model, SerializerMixin):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    animals = db.relationship('Animal', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'
    
class Animal(db.Model, SerializerMixin):
    __tablename__ = 'animals'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Available')
    description = db.Column(db.Text)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'))
    image_url = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    @validates('price')
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
    
    serialize_rules = ('-farmer_id', '-category_id') 

    def serialize(self):
        return {c: getattr(self, c) for c in self.__table__.columns.keys() if c not in self.serialize_rules}
    
    def __repr__(self):
        return f'<Animal {self.type} {self.breed} in category {self.category.name}>'
    
class Farmer(db.Model, SerializerMixin):
    __tablename__ = 'farmers'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    farm_name = db.Column(db.String(100))
    address = db.Column(db.String(255))
    role = db.Column(db.String(10), nullable=False)
    animals = db.relationship('Animal', backref='farmer', lazy=True)
    
    @validates('username')
    def validate_username(self, key, username):
        if len(username) < 3:
            raise ValueError('Username must be at least 3 characters long.')
        return username

    @validates('email')
    def validate_email(self, key, address):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", address):
            raise ValueError("Invalid email address")
        return address
    
    serialize_rules = ('-password_hash',)

    def set_password(self, password):
        # Ensure password meets complexity requirements before hashing
        password_regex = r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}'
        if not re.match(password_regex, password):
            raise ValueError("Password must contain at least 8 characters, including one number, one lowercase and one uppercase letter.")
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Farmer {self.username} at {self.farm_name}>'

    
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    address = db.Column(db.String(255))
    role = db.Column(db.String(10), nullable=False)

    @validates('username')
    def validate_username(self, key, username):
        if len(username) < 3:
            raise ValueError('Username must be at least 3 characters long.')
        return username

    @validates('email')
    def validate_email(self, key, address):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", address):
            raise ValueError("Invalid email address")
        return address

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    total_price = db.Column(db.Float)
    status = db.Column(db.String(20), default='Pending')
    order_date = db.Column(db.DateTime, onupdate=db.func.now())
    items = db.relationship('CartItem', backref='cart', lazy=True)

    def __repr__(self):
        return f'<Cart {self.id} by User {self.user_id}>'

class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'))
    animal_id = db.Column(db.Integer, db.ForeignKey('animals.id'))
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float)
    
    def __repr__(self):
        return f'<CartItem for Cart {self.cart_id}, Animal {self.animal_id}>'