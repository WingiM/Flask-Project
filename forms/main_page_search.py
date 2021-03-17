from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class AddProductForm(FlaskForm):
    to_find = StringField(validators=[DataRequired()])
    submit = SubmitField('Поиск по сайту')
