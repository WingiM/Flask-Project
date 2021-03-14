from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from flask_wtf.file import FileRequired, FileField, FileAllowed
from wtforms.validators import DataRequired


class AddProductForm(FlaskForm):
    name = StringField('Название товара', validators=[DataRequired()])
    search_tags = StringField('Теги для поиска', validators=[DataRequired()])
    image = FileField('Изображение товара', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'Images only!'])])
    price = IntegerField('Цена товара', validators=[DataRequired()])
    submit = SubmitField('Добавить товар')
