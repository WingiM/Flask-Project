import flask
from flask import jsonify, request

from . import db_session
from .products import Products

blueprint = flask.Blueprint(
    'products_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/products', methods=["GET"])
def get_products():
    sess = db_session.create_session()
    try:
        types = request.args.get('types', type=str)
        if types:
            types = types.split(',')
        else:
            types = ''
        price = request.args.get('price', type=str)
        if price:
            price = range(*map(int, request.args.get('price', type=str).split('-')))
        else:
            price = range(0, 10 ** 6)
        sorting_orders = {
            None: lambda x: x.price,
            '1': lambda x: -x.price,
            '2': lambda x: x.name
        }
        products = filter(lambda x: x.price in price and all([i in [j.name for j in x.categories] for i in types]),
                          sess.query(Products).all())
        products = list(sorted(products, key=sorting_orders[request.args.get('order')]))
        if not products:
            return jsonify({'error': 'no products found'})
    except KeyError:
        return jsonify({'error': 'Bad request'})
    return jsonify(
        {
            'products':
                [item.to_dict(only=('id', 'name', 'stringed_categories', 'image', 'price', 'about')) for item in
                 products]
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
            'product': product.to_dict(only=('id', 'name', 'stringed_categories', 'image', 'price', 'about'))
        }
    )
