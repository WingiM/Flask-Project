from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase
import sqlalchemy


class Products(SqlAlchemyBase, SerializerMixin):
    association_table = sqlalchemy.Table(
        'users_carts',
        SqlAlchemyBase.metadata,
        sqlalchemy.Column('user', sqlalchemy.Integer,
                          sqlalchemy.ForeignKey('users.id')),
        sqlalchemy.Column('carted_product', sqlalchemy.Integer,
                          sqlalchemy.ForeignKey('products.id'))
    )

    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True)
    image = sqlalchemy.Column(sqlalchemy.String)
    specs = sqlalchemy.Column(sqlalchemy.String)
    about = sqlalchemy.Column(sqlalchemy.String)
    price = sqlalchemy.Column(sqlalchemy.Integer)
    stringed_categories = sqlalchemy.Column(sqlalchemy.String)

    categories = orm.relation('Categories', secondary='categories_to_products', backref='products')

    def __repr__(self):
        return self.name
