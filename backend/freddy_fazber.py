from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re
from jinja2 import Template
from flask import render_template
import smtplib

# Email details
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication

from jinja2 import Template
import threading

import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
from fpdf import FPDF
import os


def generate_invoice_pdf(order, customer, pizzas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Invoice for Order #{order.id}", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Customer: {customer.username}", ln=True)
    pdf.cell(200, 10, txt=f"Delivery Location: {order.location}", ln=True)
    pdf.cell(200, 10, txt=f"Delivery Time: {order.delivery_time}", ln=True)
    pdf.ln(10)

    pdf.cell(200, 10, txt="Items Ordered:", ln=True)

    total_cost = 0
    for pizza in pizzas:
        # Add the base pizza price
        base_price = pizza["price"]
        pdf.cell(
            200, 10, txt=f"- {pizza['name']} (Base Price: ${base_price:.2f})", ln=True
        )

        # Calculate and display toppings with their prices
        if pizza["toppings"]:
            toppings_cost = 0
            pdf.set_font("Arial", size=10)  # Smaller font for toppings
            for topping in pizza["toppings"]:
                # Fetch topping price from database
                topping_obj = Topping.query.filter_by(name=topping).first()
                if topping_obj:
                    topping_price = topping_obj.price
                    toppings_cost += topping_price
                    pdf.cell(
                        200, 8, txt=f"    + {topping} (${topping_price:.2f})", ln=True
                    )

            # Display subtotal for this pizza with toppings
            pdf.set_font("Arial", size=12)
            item_total = base_price + toppings_cost
            pdf.cell(200, 10, txt=f"    Subtotal: ${item_total:.2f}", ln=True)
            total_cost += item_total
        else:
            total_cost += base_price
            pdf.cell(200, 8, txt="    No toppings", ln=True)
            pdf.cell(200, 10, txt=f"    Subtotal: ${base_price:.2f}", ln=True)

        pdf.ln(5)  # Add some space between pizza items

    pdf.ln(5)
    pdf.set_font("Arial", "B", size=12)  # Bold font for total
    pdf.cell(200, 10, txt=f"Total Cost: ${total_cost:.2f}", ln=True)

    filename = f"invoice_order_{order.id}.pdf"
    filepath = os.path.join("invoices", filename)
    os.makedirs("invoices", exist_ok=True)
    pdf.output(filepath)
    return filepath


def send_email_async_with_invoice(order_details, recipient_email, pdf_path):
    def send_email():
        sender_email = "freddyfivebearurur@gmail.com"
        app_password = "eqtm mkmm agud ngsj"

        # Create the email message
        msg = MIMEMultipart("related")  # Use "related" to allow inline images
        msg["Subject"] = "Your Pizza Order Details"
        msg["From"] = sender_email
        msg["To"] = recipient_email

        # HTML content with inline logo reference
        html_content = f"""
        <html>
        <body>
            <div style="text-align: center;">
                <img src="cid:logo" alt="Pizza Restaurant Logo" style="width: 600px; height: auto;" />
            </div>
            {order_details}
        </body>
        </html>
        """
        msg.attach(MIMEText(html_content, "html"))

        # Attach the logo image
        logo_path = "static/pizzas/logo/freddy_logo.png"
        try:
            with open(logo_path, "rb") as img_file:
                logo_image = MIMEImage(img_file.read())
                logo_image.add_header("Content-ID", "<logo>")
                msg.attach(logo_image)
        except Exception as e:
            print(f"Error attaching the logo image: {e}")
            return

        # Attach the invoice PDF
        try:
            with open(pdf_path, "rb") as pdf_file:
                pdf_attachment = MIMEApplication(pdf_file.read(), _subtype="pdf")
                pdf_attachment.add_header(
                    "Content-Disposition", "attachment", filename="Faktura.pdf"
                )
                msg.attach(pdf_attachment)
        except Exception as e:
            print(f"Error attaching the PDF: {e}")
            return

        # Send the email
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, app_password)
                server.sendmail(sender_email, recipient_email, msg.as_string())
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error: {e}")

    threading.Thread(target=send_email).start()


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pizzeria.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    surname = db.Column(db.String(80), nullable=False)
    telephone_number = db.Column(db.String(20), nullable=False)


class Pizza(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    details = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_path = db.Column(
        db.String(200), nullable=False, default="static/pizzas/goated.png"
    )


class Topping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)


from datetime import datetime


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # New fields for location and delivery time
    location = db.Column(db.String(255), nullable=False)  # Store the delivery location
    delivery_time = db.Column(db.DateTime, nullable=False)  # Store the delivery time

    # Add the relationship to OrderItem
    items = db.relationship("OrderItem", backref="order", lazy=True)


# Association table for OrderItem and Topping
order_item_topping = db.Table(
    "order_item_topping",
    db.Column(
        "order_item_id", db.Integer, db.ForeignKey("order_item.id"), primary_key=True
    ),
    db.Column("topping_id", db.Integer, db.ForeignKey("topping.id"), primary_key=True),
)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizza.id"), nullable=False)
    toppings = db.relationship(
        "Topping", secondary=order_item_topping, backref="order_items", lazy="dynamic"
    )


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)  # Optional comment field
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


# Seed Data
def seed_data():
    if not User.query.first():
        hashed_password1 = generate_password_hash("password123", method="pbkdf2:sha256")
        hashed_password2 = generate_password_hash("password456", method="pbkdf2:sha256")
        hashed_password3 = generate_password_hash("111111", method="pbkdf2:sha256")

        user1 = User(
            username="john_doe",
            email="freddyfivebearurur@gmail.com",
            password=hashed_password1,
            name="John",  # Add first name
            surname="Doe",  # Add last name
            telephone_number="1234567890",  # Add telephone number
        )

        user2 = User(
            username="jane_doe",
            email="jane_doe@example.com",
            password=hashed_password2,
            name="Jane",  # Add first name
            surname="Doe",  # Add last name
            telephone_number="0987654321",  # Add telephone number
        )
        user3 = User(
            username="1",
            email="1@example.com",
            password=hashed_password3,
            name="1",  # Add first name
            surname="1",  # Add last name
            telephone_number="111111111",  # Add telephone number
        )

        pizzas = [
            Pizza(
                name="Margherita",
                details="A timeless classic with fresh mozzarella, tangy tomato sauce, and fragrant basil leaves.",
                price=7.99,
                image_path="static/pizzas/margherita.jpg",
            ),
            Pizza(
                name="Pepperoni",
                details="A savory favorite topped with spicy pepperoni slices and melted mozzarella cheese.",
                price=8.99,
                image_path="static/pizzas/pepperoni.jpg",
            ),
            Pizza(
                name="Capriciosa",
                details="A delicious pizza with mushrooms, ham, and mozzarella.",
                price=10.99,
                image_path="static/pizzas/capriciosa.png",
            ),
            Pizza(
                name="Hawajska",
                details="Classic Hawaiian pizza with ham and pineapple.",
                price=9.49,
                image_path="static/pizzas/hawajska.png",
            ),
            Pizza(
                name="Romana",
                details="A savory pizza with anchovies, capers, and olives.",
                price=11.49,
                image_path="static/pizzas/romana.png",
            ),
            Pizza(
                name="Stagioni",
                details="Four seasons pizza with artichokes, mushrooms, ham, and olives.",
                price=12.99,
                image_path="static/pizzas/stagioni.png",
            ),
            Pizza(
                name="Vege",
                details="A vegetable-packed pizza with peppers, onions, and olives.",
                price=10.49,
                image_path="static/pizzas/vege.png",
            ),
        ]

        toppings = [
            Topping(name="Mushrooms", price=1.50),
            Topping(name="Extra Cheese", price=2.00),
            Topping(name="Bacon", price=2.50),
        ]

        db.session.add_all([user1, user2, user3] + pizzas + toppings)
        db.session.commit()


# Routes


@app.route("/register", methods=["POST"])
def register():
    data = request.json

    # Validate input
    if (
        not data
        or "username" not in data
        or "password" not in data
        or "email" not in data
        or "name" not in data
        or "surname" not in data
        or "telephone_number" not in data
    ):
        return (
            jsonify(
                {
                    "message": "Invalid input. Username, email, password, name, surname, and telephone_number are required."
                }
            ),
            400,
        )

    username = data["username"]
    email = data["email"]
    password = data["password"]
    name = data["name"]
    surname = data["surname"]
    telephone_number = data["telephone_number"]

    # Validate email format
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(email_regex, email):
        return jsonify({"message": "Invalid email format"}), 400

    # Check for existing username or email
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    try:
        # Hash the password
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        # Create the new user
        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            name=name,
            surname=surname,
            telephone_number=telephone_number,
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:

        app.logger.error(f"Error during registration: {str(e)}")
        return jsonify({"message": "Registration failed", "error": str(e)}), 500


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data["username"]).first()
    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401
    return jsonify({"message": "Login successful", "userId": user.id}), 200


@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    response = []

    base_url = request.host_url.rstrip("/")
    for pizza in pizzas:
        image_url = f"{base_url}/{pizza.image_path}"
        logging.debug(f"Constructed image URL: {image_url}")  # Log the image URL

        response.append(
            {
                "id": pizza.id,
                "name": pizza.name,
                "details": pizza.details,
                "price": pizza.price,
                "image_url": image_url,
            }
        )

    return jsonify(response)


@app.route("/toppings", methods=["GET"])
def get_toppings():
    toppings = Topping.query.all()
    return jsonify(
        [
            {"id": topping.id, "name": topping.name, "price": topping.price}
            for topping in toppings
        ]
    )


@app.route("/order", methods=["POST"])
def create_order():
    data = request.json
    if (
        not data
        or "user_id" not in data
        or "items" not in data
        or "location" not in data
        or "delivery_time" not in data
    ):
        return jsonify({"message": "Invalid input"}), 400

    try:
        # Parse the delivery time with varying formats
        delivery_time_str = data["delivery_time"]
        delivery_time = None
        try:
            # Attempt to parse full datetime format
            delivery_time = datetime.strptime(delivery_time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # If no seconds provided, default to :00
            try:
                delivery_time = datetime.strptime(delivery_time_str, "%Y-%m-%d %H:%M")
            except ValueError:
                return jsonify({"message": "Invalid delivery time format"}), 400

        order = Order(
            user_id=data["user_id"],
            location=data["location"],
            delivery_time=delivery_time,
        )
        db.session.add(order)
        db.session.commit()

        # Add order items with toppings
        for item in data["items"]:
            order_item = OrderItem(order_id=order.id, pizza_id=item["pizza_id"])
            db.session.add(order_item)

            # Associate toppings directly using the many-to-many relationship
            topping_ids = item.get("topping_ids", [])
            if topping_ids:
                toppings = Topping.query.filter(Topping.id.in_(topping_ids)).all()
                order_item.toppings.extend(toppings)

        db.session.commit()

        customer = db.session.get(User, order.user_id)
        pizzas = []
        for order_item in order.items:
            pizza = db.session.get(Pizza, order_item.pizza_id)
            toppings = [topping.name for topping in order_item.toppings]
            pizzas.append(
                {
                    "name": pizza.name,
                    "toppings": toppings,
                    "price": pizza.price,
                }
            )

        pdf_path = generate_invoice_pdf(order, customer, pizzas)

        # Prepare the email content using the dynamic template
        with open("email_template.html", "r") as templatefile:
            template_content = templatefile.read()

        # Render the email template with order details
        template = Template(template_content)
        email_content = template.render(
            customer_name=customer.username,
            pizzas=pizzas,
            delivery_time=order.delivery_time,
            location=order.location,
        )

        # Send the email asynchronously with the PDF attachment
        send_email_async_with_invoice(email_content, customer.email, pdf_path)

        return (
            jsonify(
                {
                    "message": "Order created successfully",
                    "order_id": order.id,
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Order creation failed", "error": str(e)}), 500


@app.route("/orders/<int:user_id>", methods=["GET"])
def get_orders(user_id):
    # Query orders for the specified user
    orders = Order.query.filter_by(user_id=user_id).all()
    response = []

    for order in orders:
        # Query all order items for the current order
        items = OrderItem.query.filter_by(order_id=order.id).all()

        order_data = {
            "order_id": order.id,
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "location": order.location,  # Include delivery location
            "delivery_time": order.delivery_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),  # Include delivery time
            "items": [],
        }

        for item in items:
            # Fetch the pizza for the current order item
            pizza = Pizza.query.get(item.pizza_id)
            if not pizza:
                app.logger.error(
                    f"Pizza with ID {item.pizza_id} not found for order {order.id}"
                )
                continue

            # Retrieve all toppings for the current order item
            toppings = [topping.name for topping in item.toppings]

            # Append the pizza and toppings info to the order's items list
            order_data["items"].append(
                {
                    "pizza": pizza.name,
                    "toppings": toppings,
                }
            )

        response.append(order_data)

    return jsonify(response)


@app.route("/rate", methods=["POST"])
def rate_pizzeria():
    data = request.json
    if (
        not data
        or "user_id" not in data
        or "order_id" not in data
        or "rating" not in data
    ):
        return jsonify({"message": "Invalid input"}), 400

    order = Order.query.filter_by(id=data["order_id"], user_id=data["user_id"]).first()
    if not order:
        return jsonify({"message": "Invalid order for this user"}), 400

    try:
        # Include the optional comment field
        rating = Rating(
            user_id=data["user_id"],
            order_id=data["order_id"],
            rating=data["rating"],
            comment=data.get("comment"),  # Use .get() to handle optional field
        )
        db.session.add(rating)
        db.session.commit()

        # Print the received rating data into the console for debugging purposes
        print(
            f"Received Rating: User ID: {data['user_id']}, Order ID: {data['order_id']}, Rating: {data['rating']}, Comment: {data.get('comment', 'No comment')}"
        )

        return jsonify({"message": "Thank you for your feedback!"}), 201
    except Exception as e:
        return jsonify({"message": "Rating submission failed", "error": str(e)}), 500


@app.route("/update_user/<int:id>", methods=["PUT"])
def update_user(id):
    # Find the user by ID using get_or_404, which raises a 404 error if not found
    user = User.query.get_or_404(id)

    # Get the updated data from the request
    data = request.get_json()

    # Update user details (validate the input as necessary)
    if "name" in data:
        user.name = data["name"]
    if "surname" in data:
        user.surname = data["surname"]
    if "telephone_number" in data:
        user.telephone_number = data["telephone_number"]

    # Optionally, if you want to allow updating other fields like password or email
    if "password" in data:
        user.password = data["password"]

    if "email" in data:
        user.email = data["email"]

    # Commit the changes to the database
    db.session.commit()

    return (
        jsonify(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "name": user.name,
                "surname": user.surname,
                "telephone_number": user.telephone_number,
            }
        ),
        200,
    )


if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_data()
    app.run(host="0.0.0.0", port=5000)
