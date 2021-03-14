import flask
from flask import jsonify

from . import db_session
from .categories import Categories
from .products import Products

blueprint = flask.Blueprint(
    'products_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/products', methods=["GET"])
def get_products():
    sess = db_session.create_session()
    products = sess.query(Products).all()
    if not products:
        return jsonify({'error': 'no products found'})
    return jsonify(
        {
            'products':
                [item.to_dict(only=('id', 'name', 'stringed_categories', 'image', 'price', 'about')) for item in products]
        }
    )


@blueprint.route('/api/products/<string:filter>', methods=["GET"])
def get_filtered_products(filter):
    sess = db_session.create_session()
    all_categories = sess.query(Categories).all()
    if filter not in [i.name for i in all_categories]:
        return jsonify({'error': 'unknown category'})
    products = []
    for i in sess.query(Products).all():
        for j in i.categories:
            if j.name == filter:
                products.append(i)
    if not products:
        return jsonify({'error': 'not products with such filter'})
    return jsonify(
        {
            'products':
                [item.to_dict(only=('id', 'name', 'stringed_categories', 'image', 'price', 'about')) for item in products]
        }
    )


@blueprint.route('/api/products/<int:product_id>', methods=["GET"])
def get_product(product_id):
    sess = db_session.create_session()
    product = sess.query(Products).get(product_id)
    if not product:
        return jsonify({'error': 'no product with such name'})
    return jsonify(
        {
            'product': product.to_dict(only=('id', 'name', 'categories', 'image', 'price', 'about'))
        }
    )


