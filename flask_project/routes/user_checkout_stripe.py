"""
Routes for creating and ending a stripe checkout session
"""

from flask import json, redirect, request, render_template, url_for, jsonify, abort
from flask_login import current_user

from server import app, get_db
from .endpoints import user_bp, api_bp
from .forms import UserPurchaseForm, serialize_form
from .cart import validate_product_id, get_user_cart

import stripe
from stripe_keys import STRIPE_API_KEY, STRIPE_ENDPOINT_SECRET
stripe.api_key = STRIPE_API_KEY

STRIPE_REFERRAL_URL = "http://localhost:5002"

# Create a stripe checkout session with their provided api
# https://stripe.com/docs/api/checkout/sessions
# cart is an array of (<product_id:str>, <quantity:int>)
def create_stripe_session(cart):
    items = []
    PLACEHOLDER_STRIPE_IMAGE = "https://thumbs.dreamstime.com/z/portrait-attractive-young-woman-who-sitting-cafe-cafe-urban-lifestyle-random-portrait-portrait-attractive-184387567.jpg"

    with app.app_context():
        db = get_db()
        for id, quantity in cart:
            product = db.get_entry_by_id("products", id)

            # get all images of product for stripe
            images = []
            image_url = product["image_url"]
            if image_url and image_url != '':
                images.append(PLACEHOLDER_STRIPE_IMAGE)
            
            product_url = STRIPE_REFERRAL_URL+url_for("user_bp.product_page", id=product["id"])

            # TODO: Stripe allows you to keep track of product, so replace id with our id
            stripe_product = stripe.Product.create(
                name=product["name"],
                url=product_url,
                images=images,
                description=product["description"],
                metadata={
                    "db_id": product["id"],
                }
            )

            stripe_price = stripe.Price.create(
                currency="aud",
                product=stripe_product.id,
                unit_amount=int(100*product["unit_price"]),
            )

            item = {
                "price": stripe_price.id,
                "quantity": quantity,
            }
            items.append(item)

    # setup payment type 
    config = dict(
        payment_method_types=['card'],
        line_items=items,
        mode='payment',
        shipping_address_collection={
            'allowed_countries': ['AU'],
        },
        success_url=STRIPE_REFERRAL_URL+"/checkout_status?session_id={CHECKOUT_SESSION_ID}&success=true",
        cancel_url=STRIPE_REFERRAL_URL+"/checkout_status?session_id={CHECKOUT_SESSION_ID}&success=false",
    )

    # add current user data if it exists
    # TODO: Add stored customer credit card or billing address if it exists
    if current_user.get_id() is not None:
        id = current_user.get_id()
        with app.app_context():
            db = get_db()
            user = db.get_entry_by_id("users", ord(id))
            config["customer_email"] = user["email"]

    session = stripe.checkout.Session.create(**config)
    return session

# Use stripe to immediately buy the product
@api_bp.route('/transaction/buy', methods=['POST'])
def product_buy():
    form = UserPurchaseForm(meta=dict(csrf=False))
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 403
    
    if not validate_product_id(form.id.data):
        form.id.errors.append("Invalid product id")
        return jsonify(serialize_form(form)), 403

    id = form.id.data
    quantity = form.quantity.data
    session = create_stripe_session([(id, quantity)])
    return redirect(session.url, code=303)

# Setups stripe and redirects the user there
# TODO: store stripe sessions and keep data persisting
# TODO: pass in billing address and card information if stored
@user_bp.route('/checkout', methods=['POST'])
def cart_checkout():
    cart = get_user_cart()
    items = list(cart.to_list())
    if len(items) == 0:
        abort(403)

    session = create_stripe_session(items)
    return redirect(session.url, code=303)

# when stripe succeeds, it goes to this page
# shows a list of the stripe items in the checkout session
# the price and quantity may have changed, so we use the stripe ones
@user_bp.route("/checkout_status", methods=['GET'])
def checkout_status():
    try:
        session_id = request.args['session_id']
        is_success = request.args['success']
        session = stripe.checkout.Session.retrieve(session_id)
        line_items = stripe.checkout.Session.list_line_items(session_id, limit=100)
    except stripe.error.InvalidRequestError as ex:
        print("Customer tried to access checkout successful without session")
        abort(403)
    except KeyError as ex:
        print(ex)
        abort(403)

    is_success = True if is_success == 'true' else False
    print(f"Checkout completed with success={is_success}")

    # get the product from the database
    # override the cost and quantity of the product with actual checkout price
    products = []
    total_items = 0
    total_cost = 0
    with app.app_context():
        db = get_db()
        for item in line_items.data:
            quantity = item.quantity
            unit_price = item.price.unit_amount / 100

            stripe_product = stripe.Product.retrieve(item.price.product)
            id = stripe_product.metadata.db_id

            product = db.get_entry_by_id("products", id)
            product.update(quantity=quantity, unit_price=unit_price)
            products.append(product)

            total_cost += quantity*unit_price
            total_items += quantity

    data = dict(
        is_success=is_success,
        products=products, 
        summary=dict(total_items=total_items, total_cost=total_cost))

    # TODO: Determine if this session belonged to the cart, and if it did empty it
    # cart.empty()
    return render_template("checkout_status.html", **data)

# stripe webhook where we process sessions from our stripe api
# TODO: Use the information here to update our customer's orders 
# TODO: Customer's paymetn and billing address could be included here
#       if it is and user hasn't update their profile, we add this in for them
@api_bp.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    signature_header = request.headers.get("Stripe-Signature")
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, signature_header, STRIPE_ENDPOINT_SECRET)
    except ValueError as ex:
        return jsonify(dict(error='Invalid payload')), 400
    except stripe.error.SignatureVerificationError as ex:
        return jsonify(dict(error="Invalid signature")), 400
    
    # if the checkout sesson was completed, update store to reflect this
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print("Confirmed that the session was successful")
        print(session)

    return jsonify(dict(success=True)), 200