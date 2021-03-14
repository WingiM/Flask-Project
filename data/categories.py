from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase
import sqlalchemy


class Categories(SqlAlchemyBase, SerializerMixin):
    association_table = sqlalchemy.Table(
        'categories_to_products',
        SqlAlchemyBase.metadata,
        sqlalchemy.Column('category', sqlalchemy.Integer,
                          sqlalchemy.ForeignKey('categories.id')),
        sqlalchemy.Column('product', sqlalchemy.Integer,
                          sqlalchemy.ForeignKey('products.id'))
    )

    __tablename__ = 'categories'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True)

    def __repr__(self):
        return self.name
