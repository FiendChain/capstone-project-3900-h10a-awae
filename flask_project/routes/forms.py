
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from flask_uploads import UploadSet, IMAGES, configure_uploads

from wtforms import StringField, IntegerField, FloatField, SubmitField
from wtforms.fields.core import BooleanField
from wtforms.fields.simple import HiddenField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, EqualTo, InputRequired, Length, NumberRange, AnyOf, Optional, ValidationError
from wtforms.widgets.core import Input

import phonenumbers

from server import app


# TODO: Find a better place to put this

valid_categories = ["coffee", "cofveve", "latte", "brown"]
valid_delivery_units = ["days", "weeks", "months", "years"]
valid_images = UploadSet('images', IMAGES)

configure_uploads(app, (valid_images,))

class ProductForm(FlaskForm):
    # optional id field to form 
    id = HiddenField()

    # the incoming image can either be: original static, new upload, none
    # the following are the required conditions for each transition of the image
    # stays as original static:  if image_url and not image_changed
    # stays as none:             if not image_url and not image_changed
    # original static -> none:   if image_url and image_changed and not image
    # original static -> upload: if image_url and image_changed and image
    # none -> upload:            if not image_url and image_changed and image
    image_url = HiddenField() # stores the static url if it exists
    image_changed = BooleanField(validators=[InputRequired()], default=False)
    image = FileField(validators=[Optional(), FileAllowed(valid_images, message="Images allowed only")])

    name = StringField(validators=[Length(5, 40), InputRequired(message="Product name is required")])
    unit_price = FloatField(validators=[NumberRange(min=0, max=1000), InputRequired()])
    category = StringField(validators=[AnyOf(valid_categories), InputRequired()])
    description = StringField(validators=[Length(0, 250)])
    est_delivery_amount = IntegerField(validators=[NumberRange(min=1, max=1000), InputRequired()])
    est_delivery_units = StringField(validators=[AnyOf(valid_delivery_units), InputRequired()])
    in_stock = IntegerField(validators=[NumberRange(min=0, max=10000), InputRequired()])


    submit_button = SubmitField('Submit Form')

class LoginForm(FlaskForm):
    name = StringField(validators=[Length(5, 40), InputRequired(message="Username is required")])
    password = StringField(validators=[Length(5, 40), InputRequired(message="Password is required")])
    remember_me = BooleanField(validators=[Optional()], default=True)

class PhoneValidator:
    def __init__(self, length=10, message="Invalid phone number"):
        self.length = length
        self.message = message

    def __call__(self, form, field):
        if len(field.data) < self.length:
            raise ValidationError(f'Phone number must have at least {self.length} digits')
        try:
            input_number = phonenumbers.parse(field.data)
            if not phonenumbers.is_valid_number(input_number):
                raise ValidationError(self.message)
        except:
            input_number = phonenumbers.parse("+61"+field.data)
            if not phonenumbers.is_valid_number(input_number):
                raise ValidationError(self.message)

# form for registering the user
class RegisterForm(FlaskForm):
    username = StringField(validators=[Length(5,40), InputRequired(message="Username is required")])
    password = StringField("password", validators=[Length(5, 40), InputRequired(message="Password is required")])
    confirm_password = StringField(validators=[Length(5, 40), InputRequired(message="You must confirm your password"), EqualTo("password")])
    email = EmailField(validators=[Email(), InputRequired(message="Email is required")])
    phone = StringField(validators=[PhoneValidator(), InputRequired()])
    remember_me = BooleanField(validators=[Optional()], default=True)

# form for adding or removing products from the cart
class UserPurchaseForm(FlaskForm):
    id = StringField(Length(2,100), validators=[InputRequired(message="Product id required")])
    quantity = IntegerField(validators=[NumberRange(min=0, max=1000), InputRequired()])

# form for editing the user's details
class UserProfileLoginSecurityForm(FlaskForm):
    password = StringField(validators=[Length(5, 40), InputRequired(message="Original password is required")])
    new_password = StringField("new_password", validators=[Length(5, 40), InputRequired(message="Password is required")])
    confirm_password = StringField(validators=[Length(5, 40), InputRequired(message="You must confirm your new password"), EqualTo("new_password")])
    email = EmailField(validators=[Email(), InputRequired(message="Email is required")])
    phone = StringField(validators=[PhoneValidator(), InputRequired()])

def serialize_form(form):
    data = [] 
    for field in form:
        name = field.id
        value = field.data
        errors = field.errors

        if isinstance(field, FileField):
            continue

        data.append({"name": name, "value": value, "errors": errors})

    return data