from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField


class CatalogFilterForm(FlaskForm):
    price = StringField('Диапазон цены')
    types = StringField('Теги товара')
    sorting = RadioField('Сортировка',
                         choices=[('0', 'По возрастанию цены'), ('1', 'По убыванию цены'), ('2', 'По наименованию')],
                         default='0')
    submit = SubmitField('Применить')
