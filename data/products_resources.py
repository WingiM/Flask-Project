from flask import request, jsonify
from flask_restful import Resource
from data import db_session
from data.products import Products


class ProductsListResource(Resource):
    def get(self):
        sess = db_session.create_session()
        try:
            types = request.args.get('types', type=str)
            if types:
                types = types.lower().split(',')
            else:
                types = ''
            price = request.args.get('price', type=str)
            if price:
                price = range(*map(int, request.args.get('price', type=str).split('-')))
            else:
                price = range(0, 10 ** 6)
            order = request.args.get('order')
            if not order:
                order = '0'
            sorting_orders = {
                '0': lambda x: x.price,
                '1': lambda x: -x.price,
                '2': lambda x: x.name
            }
            products = filter(lambda x: x.price in price and all([i in [j.name.lower() for j in x.categories] for i in types]),
                              sess.query(Products).all())
            products = list(sorted(products, key=sorting_orders[order]))
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


class ProductResource(Resource):
    def get(self, product_id):
        sess = db_session.create_session()
        product = sess.query(Products).get(product_id)
        if not product:
            return jsonify({'error': 'no product with such name'})
        return jsonify(
            {
                'product': product.to_dict(only=('id', 'name', 'stringed_categories', 'image', 'price', 'about'))
            }
        )
