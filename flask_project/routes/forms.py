
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from flask_uploads import UploadSet, IMAGES, configure_uploads

from wtforms import StringField, IntegerField, FloatField, SubmitField
from wtforms import validators
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, AnyOf

from server import app


# TODO: Find a better place to put this

valid_categories = ["coffee", "cofveve", "latte", "brown"]
valid_delivery_units = ["days", "weeks", "months", "years"]
valid_images = UploadSet('images', IMAGES)

configure_uploads(app, (valid_images,))

class ProductForm(FlaskForm):
    name = StringField(validators=[Length(5, 40), InputRequired()])
    unit_price = FloatField(validators=[NumberRange(min=0, max=1000), InputRequired()])
    category = StringField(validators=[AnyOf(valid_categories), InputRequired()])
    description = StringField(validators=[Length(0, 250)])
    est_delivery_amount = IntegerField(validators=[NumberRange(min=1, max=1000), InputRequired()])
    est_delivery_units = StringField(validators=[AnyOf(valid_delivery_units), InputRequired()])

    image = FileField(validators=[FileRequired(), FileAllowed(valid_images, message="Images allowed only")])

    submit_button = SubmitField('Submit Form')