from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pizzeria.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)


class Pizza(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    details = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_path = db.Column(db.String(200), nullable=False, default='static/pizzas/goated.png')


class Topping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizza.id'), nullable=False)
    toppings = db.relationship('OrderItemTopping', backref='order_item', lazy=True)


class OrderItemTopping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_item_id = db.Column(db.Integer, db.ForeignKey('order_item.id'), nullable=False)
    topping_id = db.Column(db.Integer, db.ForeignKey('topping.id'), nullable=False)


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


# Seed Data
def seed_data():
    if not User.query.first():
        hashed_password1 = generate_password_hash('password123', method='pbkdf2:sha256')
        hashed_password2 = generate_password_hash('password456', method='pbkdf2:sha256')

        user1 = User(username='john_doe', email='john_doe@example.com', password=hashed_password1)
        user2 = User(username='jane_doe', email='jane_doe@example.com', password=hashed_password2)

        pizzas = [
            Pizza(name='Margherita', details='yummers1', price=7.99, image_path='static/pizzas/margherita.jpg'),
            Pizza(name='Pepperoni', details='yummers2', price=8.99, image_path='static/pizzas/pepperoni.jpg'),
            Pizza(name='Veggie', details='yummers3', price=9.99)
        ]

        toppings = [
            Topping(name='Mushrooms', price=1.50),
            Topping(name='Extra Cheese', price=2.00),
            Topping(name='Bacon', price=2.50)
        ]

        db.session.add_all([user1, user2] + pizzas + toppings)
        db.session.commit()


# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.json

    # Validate input
    if not data or 'username' not in data or 'password' not in data or 'email' not in data:
        return jsonify({"message": "Invalid input. Username, email, and password are required."}), 400

    username = data['username']
    email = data['email']
    password = data['password']

    # Validate email format
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        return jsonify({"message": "Invalid email format"}), 400

    # Check for existing username or email
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    try:
        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Create the new user
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        return jsonify({"message": "Registration failed", "error": str(e)}), 500


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"message": "Invalid credentials"}), 401
    return jsonify({"message": "Login successful", "userId": user.id}), 200


@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    response = []

    for pizza in pizzas:
        response.append({
            "id": pizza.id,
            "name": pizza.name,
            "details": pizza.details,
            "price": pizza.price,
            "image_url": f"http://localhost:5000/{pizza.image_path}"  # Full image URL
        })

    return jsonify(response)


@app.route('/toppings', methods=['GET'])
def get_toppings():
    toppings = Topping.query.all()
    return jsonify([{"id": topping.id, "name": topping.name, "price": topping.price} for topping in toppings])


@app.route('/order', methods=['POST'])
def create_order():
    data = request.json
    if not data or 'user_id' not in data or 'items' not in data:
        return jsonify({"message": "Invalid input"}), 400

    try:
        order = Order(user_id=data['user_id'])
        db.session.add(order)
        db.session.commit()

        for item in data['items']:
            order_item = OrderItem(order_id=order.id, pizza_id=item['pizza_id'])
            db.session.add(order_item)
            db.session.commit()

            for topping_id in item.get('topping_ids', []):
                order_item_topping = OrderItemTopping(order_item_id=order_item.id, topping_id=topping_id)
                db.session.add(order_item_topping)

        db.session.commit()
        return jsonify({"message": "Order created successfully", "order_id": order.id}), 201
    except Exception as e:
        return jsonify({"message": "Order creation failed", "error": str(e)}), 500


@app.route('/orders/<int:user_id>', methods=['GET'])
def get_orders(user_id):
    orders = Order.query.filter_by(user_id=user_id).all()
    response = []
    for order in orders:
        items = OrderItem.query.filter_by(order_id=order.id).all()
        response.append({
            "order_id": order.id,
            "created_at": order.created_at,
            "items": [
                {
                    "pizza": Pizza.query.get(item.pizza_id).name,
                    "toppings": [Topping.query.get(topping.topping_id).name for topping in item.toppings]
                } for item in items
            ]
        })
    return jsonify(response)


@app.route('/rate', methods=['POST'])
def rate_pizzeria():
    data = request.json
    if not data or 'user_id' not in data or 'order_id' not in data or 'rating' not in data:
        return jsonify({"message": "Invalid input"}), 400

    order = Order.query.filter_by(id=data['order_id'], user_id=data['user_id']).first()
    if not order:
        return jsonify({"message": "Invalid order for this user"}), 400

    try:
        rating = Rating(user_id=data['user_id'], order_id=data['order_id'], rating=data['rating'])
        db.session.add(rating)
        db.session.commit()
        return jsonify({"message": "Thank you for your feedback!"}), 201
    except Exception as e:
        return jsonify({"message": "Rating submission failed", "error": str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(host='0.0.0.0', port=5000)