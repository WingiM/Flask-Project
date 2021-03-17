from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from data import db_session


class CatalogFilterForm(FlaskForm):
    sess = db_session.create_session()
    price = StringField('Диапазон цены')
    types = StringField('Теги товара')
    sorting = RadioField('Сортировка',
                         choices=[('0', 'По возрастанию цены'), ('1', 'По убыванию цены'), ('2', 'По наименованию')])
    submit = SubmitField('Применить')
