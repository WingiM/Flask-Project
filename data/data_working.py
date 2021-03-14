from data import db_session
from data.products import Products
from data.users import User

db_session.global_init('../db/main_db.db')
sess = db_session.create_session()

user = sess.query(User).get(1)
user.is_admin = True
# product = sess.query(Products).get(1)
# print(product.categories)
sess.commit()


