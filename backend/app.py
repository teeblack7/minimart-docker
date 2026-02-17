

import os
from datetime import datetime
from decimal import Decimal

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# -----------------------------------------------------------------------------
# App setup
# -----------------------------------------------------------------------------
app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///minimart.db")

# Some platforms provide postgres URLs like "postgres://", SQLAlchemy expects "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------
class Product(db.Model):
    __tablename__ = "catalog_products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default="")
    price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CartItem(db.Model):
    """
    Simple single-cart implementation.
    In real apps you’d link carts to users/sessions.
    Here we use a single cart_id (default) so your index.html works immediately.
    """
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.String(64), nullable=False, index=True)  # e.g., "default"
    product_id = db.Column(db.Integer, db.ForeignKey("catalog_products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    product = db.relationship("Product")


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Numeric(10, 2), nullable=False, default=0)


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("catalog_products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    order = db.relationship("Order", backref=db.backref("items", lazy=True))
    product = db.relationship("Product")


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _cart_id_from_request() -> str:
    """
    For now, always use a single cart id so the plain HTML frontend works
    without sessions/auth/cookies.
    You can extend this later to read X-Cart-Id header or a cookie.
    """
    return "default"


def _money(val) -> float:
    # Convert Decimal/None to a JSON-friendly float with 2dp
    if val is None:
        return 0.0
    if isinstance(val, Decimal):
        return float(val.quantize(Decimal("0.01")))
    return float(val)


def _cart_summary(cart_id: str):
    items = CartItem.query.filter_by(cart_id=cart_id).all()
    out_items = []
    total = Decimal("0.00")

    for ci in items:
        unit = ci.product.price
        line_total = (unit * ci.quantity)
        total += line_total
        out_items.append({
            "cart_item_id": ci.id,
            "product_id": ci.product.id,
            "name": ci.product.name,
            "price": _money(unit),
            "quantity": ci.quantity,
            "line_total": _money(line_total),
        })

    return {"items": out_items, "total": _money(total)}


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/products")
def list_products():
    products = Product.query.order_by(Product.id.asc()).all()
    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "description": p.description or "",
            "price": _money(p.price),
        }
        for p in products
    ])


@app.post("/api/products")
def create_product():
    """
    Admin endpoint (no auth in this simple demo).
    Body: { "name": "...", "price": 12.34, "description": "..." }
    """
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    description = (data.get("description") or "").strip()
    price = data.get("price", None)

    if not name:
        return jsonify({"error": "name is required"}), 400
    if price is None:
        return jsonify({"error": "price is required"}), 400

    try:
        price_dec = Decimal(str(price)).quantize(Decimal("0.01"))
    except Exception:
        return jsonify({"error": "price must be a number"}), 400

    if price_dec < 0:
        return jsonify({"error": "price must be >= 0"}), 400

    p = Product(name=name, description=description, price=price_dec)
    db.session.add(p)
    db.session.commit()

    return jsonify({
        "message": "Product created",
        "product": {"id": p.id, "name": p.name, "description": p.description, "price": _money(p.price)}
    }), 201


@app.get("/api/cart")
def get_cart():
    cart_id = _cart_id_from_request()
    return jsonify(_cart_summary(cart_id))


@app.post("/api/cart")
def add_to_cart():
    """
    Body: { "product_id": 1, "quantity": 1 }
    If quantity omitted, defaults to 1.
    If item already in cart, increments quantity.
    """
    cart_id = _cart_id_from_request()
    data = request.get_json(silent=True) or {}

    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if product_id is None:
        return jsonify({"error": "product_id is required"}), 400

    try:
        product_id = int(product_id)
        quantity = int(quantity)
    except Exception:
        return jsonify({"error": "product_id and quantity must be integers"}), 400

    if quantity <= 0:
        return jsonify({"error": "quantity must be >= 1"}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "product not found"}), 404

    existing = CartItem.query.filter_by(cart_id=cart_id, product_id=product_id).first()
    if existing:
        existing.quantity += quantity
    else:
        db.session.add(CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity))

    db.session.commit()
    return jsonify({"message": "Added to cart", "cart": _cart_summary(cart_id)}), 200


@app.post("/api/checkout")
def checkout():
    """
    Creates an order from current cart and clears the cart.
    Returns: { message, order_id, total }
    """
    cart_id = _cart_id_from_request()
    cart_items = CartItem.query.filter_by(cart_id=cart_id).all()

    if not cart_items:
        return jsonify({"message": "Cart is empty"}), 400

    total = Decimal("0.00")
    order = Order(total=Decimal("0.00"))
    db.session.add(order)
    db.session.flush()  # get order.id

    for ci in cart_items:
        unit = ci.product.price
        line_total = unit * ci.quantity
        total += line_total

        db.session.add(OrderItem(
            order_id=order.id,
            product_id=ci.product_id,
            quantity=ci.quantity,
            unit_price=unit
        ))

    order.total = total

    # Clear cart
    CartItem.query.filter_by(cart_id=cart_id).delete()
    db.session.commit()

    return jsonify({
        "message": "Checkout successful",
        "order_id": order.id,
        "total": _money(order.total)
    }), 200


# -----------------------------------------------------------------------------
# Dev-only: auto create tables (no migrations)
# -----------------------------------------------------------------------------
with app.app_context():
    if os.getenv("AUTO_CREATE_TABLES", "0") == "1":
        db.create_all()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)