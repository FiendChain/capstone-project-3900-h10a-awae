
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from flask_uploads import UploadSet, IMAGES, configure_uploads

from wtforms import StringField, IntegerField, FloatField, SubmitField
from wtforms import validators
from wtforms.fields.core import BooleanField
from wtforms.fields.simple import HiddenField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, EqualTo, InputRequired, Length, NumberRange, AnyOf, Optional, ValidationError
from wtforms.widgets.core import Input

import phonenumbers
import os

from server import app


# TODO: Find a better place to put this

# valid_product_sort = ["price_low_to_high", "price_high_to_low"]
valid_delivery_units = ["days", "weeks", "months", "years"]
valid_images = UploadSet('images', IMAGES)

configure_uploads(app, (valid_images,))

class ImageExtensionValidator:
    def __init__(self, valid_exts=None):
        self.valid_exts = valid_exts

    def __call__(self, form, field):
        file = field.data
        if not file:
            raise ValidationError("File not provided")
        # if file provided, make sure that it has a valid filename
        if file.filename == '':
            raise ValidationError("File must have a name") 
        if '.' not in file.filename:
            raise ValidationError("File must have an extension")
        
        ext = os.path.splitext(file.filename)[-1]
        if self.valid_exts and ext not in self.valid_exts:
            valid_exts = ','.join(self.valid_exts)
            raise ValidationError(f"File must have the following extensions ({valid_exts})") 
        
class ProductForm(FlaskForm):
    # optional id field to form 
    id = HiddenField()
    image_url = HiddenField()

    # the incoming image can either be: original static, new upload, none
    # the following are the required conditions for each transition of the image
    # stays as original:  if not image_changed
    # original -> none:   if image_changed and not image
    # original -> upload: if image_changed and image
    image_changed = BooleanField(validators=[InputRequired()], default=False)
    image = FileField(validators=[Optional(), FileAllowed(valid_images, message="Images allowed only")])

    name = StringField(validators=[Length(5, 40), InputRequired(message="Product name is required")])
    unit_price = FloatField(validators=[NumberRange(min=0, max=1000), InputRequired()])
    category = StringField(validators=[InputRequired()])
    brand = StringField(validators=[Length(0, 250)])
    description = StringField(validators=[Length(0, 250)])
    stock = IntegerField(validators=[NumberRange(min=0, max=10000), InputRequired()])
    delivery_days = IntegerField(validators=[NumberRange(min=1, max=1000), InputRequired()])
    warranty_days = IntegerField(validators=[NumberRange(min=1, max=1000), InputRequired()])

    submit_button = SubmitField('Submit Form')

class LoginForm(FlaskForm):
    name = StringField(validators=[Length(5, 40), InputRequired(message="Username is required")])
    password = StringField(validators=[Length(5, 40), InputRequired(message="Password is required")])
    remember_me = BooleanField(validators=[Optional()], default=True)

class PhoneValidator:
    def __init__(self, length=8, message="Invalid phone number"):
        self.length = length
        self.message = message

    def __call__(self, form, field):
        if len(field.data) < self.length:
            raise ValidationError(f'Phone number must have at least {self.length} digits')

        try:
            try:
                input_number = phonenumbers.parse(field.data)
            except:
                input_number = phonenumbers.parse("+612"+field.data)
        except:
            raise ValidationError("Phone number is not a valid format")

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

# form for product search
class ProductSearchParams(FlaskForm):
    name = StringField(Optional(), validators=[Length(0,100)], default="")
    categories = StringField(Optional(), default="")
    sort_type = StringField(Optional(), default="price_low_to_high")

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