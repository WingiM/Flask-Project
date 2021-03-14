from data.db_session import SqlAlchemyBase
import sqlalchemy


class Products(SqlAlchemyBase):
    association_table = sqlalchemy.Table(
        'users_carts',
        SqlAlchemyBase.metadata,
        sqlalchemy.Column('user', sqlalchemy.Integer,
                          sqlalchemy.ForeignKey('users.id')),
        sqlalchemy.Column('job', sqlalchemy.Integer,
                          sqlalchemy.ForeignKey('products.id'))
    )

    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True)
    search_tags = sqlalchemy.Column(sqlalchemy.String)
    image = sqlalchemy.Column(sqlalchemy.String)
    price = sqlalchemy.Column(sqlalchemy.Integer)

