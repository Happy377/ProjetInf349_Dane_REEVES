import time
import urllib.request

from flask import Flask, jsonify, json, request, g

# L'import de rq ne fonctionne pas donc je ne peux pas l'utiliser
# Je vais laisser le code pour demontrer que j'ai fais le codage
# from redis import Redis
# from rq import Queue, Worker
# from rq.registry import StartedJobRegistry

from controllers import put_card, put_shipping
from exceptions import *
from feedbacks import order_shower
from feedbacks.error_messages import *
from feedbacks.order_shower import *
from models import create_tables
from jinja2 import Template

# L'intention était à l'origine d'avoir seulement cette partie
# dans app.py et le main dans le fichier main.py mais cela ne
# marchais pas
app = Flask(__name__)
app.config.from_object(__name__)

# Unusable redis code
# redis_conn = Redis()
# q = Queue(connection=redis_conn)

# Unusable redis code
# @app.cli.command('worker')
# def worker():
#     if q.jobs.count == 0:
#         new_worker = Worker(q)
#         new_worker.work()
#         print('Worker created')
#     else:
#         print('A worker already exists')


@app.cli.command('init_db')
def init_db():
    create_tables()
    print('Initialized the database.')


# Request handlers
@app.before_request
def before_request():
    g.db = db
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


# cherche la liste de tout les produits et les renvois
@app.route('/')
def product_list():
    with urllib.request.urlopen("http://dimprojetu.uqac.ca/~jgnault/shops/products/") as response:
        data = response.read()

        productsdata = json.loads(data)
        product_list_data = productsdata['products']

        # structure de contrôle pour vérifier qu'aucune string ne contienne de \x00 ou NUL
        for product in product_list_data:
            for element in product:
                if type(product[element]) == str:
                    if "\x00" in product[element]:
                        product[element] = product[element].replace("\x00", "")

        Product.insert_many(product_list_data).on_conflict_ignore().execute()

    return jsonify(productsdata), 200


# Permet de créer un order avec un id et une quantity avec
# toute les vérifications nécéssaires
@app.route('/order', methods=['POST'])
def place_order():
    global ordered_product
    try:
        wrapped_data = request.get_json()
        if 'product' in wrapped_data:
            data = wrapped_data['product']
            if data['quantity'] < 1:
                raise KeyError
            ordered_product = Product.get_or_none(Product.id == data['id'])
            if ordered_product is None:
                raise KeyError
            if not ordered_product.in_stock:
                raise ValueError

            total_weight = ordered_product.weight * data['quantity']
            if total_weight <= 500:
                shipping_price = 5
            elif 500 < total_weight <= 2000:
                shipping_price = 10
            else:
                shipping_price = 25

            new_order = Order(
                total_price=ordered_product.price * data['quantity'],
                paid="false",
                shipping_price=shipping_price
            )
            new_order.save()

            order_recap = OrderedProduct(
                product=data['id'],
                order=new_order.id,
                quantity=data['quantity']
            )
            order_recap.save()

            return 'Location: /order/%d' % new_order.id, 302

        if 'products' in wrapped_data:
            total_weight = 0
            total_price = 0
            shipping_price = 0
            data = wrapped_data['products']

            new_order = Order(
                paid="false"
            )
            new_order.save()

            for product in data:
                if product['quantity'] < 1:
                    raise KeyError
                ordered_product = Product.get_or_none(Product.id == product['id'])
                if ordered_product is None:
                    raise KeyError
                if not ordered_product.in_stock:
                    raise ValueError
                total_weight = total_weight + ordered_product.weight * product['quantity']
                if total_weight <= 500:
                    shipping_price = 5
                elif 500 < total_weight <= 2000:
                    shipping_price = 10
                else:
                    shipping_price = 25
                total_price = total_price + ordered_product.price * product['quantity']

                order_recap = OrderedProduct(
                    product=product['id'],
                    order=new_order.id,
                    quantity=product['quantity']
                )
                order_recap.save()

            updated_order = Order.update(
                total_price=total_price,
                shipping_price=shipping_price
            ).where(Order.id == new_order.id)
            updated_order.execute()

            return 'Location: /order/%d' % new_order.id, 302

    except KeyError:
        return jsonify(order_creation_error), 422
    except ValueError:
        return jsonify(not_in_stock_error), 422


# Permet d'ajouter le shipping_information (modification de l'order)
# ou juste récupérer les informations sur un order
@app.route('/order/<int:order_id>', methods=['GET', 'PUT'])
def order(order_id):
    global card_information
    try:
        if Order.get_or_none(Order.id == order_id) is None:
            raise UnknownOrderIdError

        if request.method == 'PUT':

            # Unusable redis code
            # if q.fetch_job(str(order_id)).get_status() != 'finished':
            #     raise PaymentConflictError

            data = request.get_json()

            # Permet de s'assurer que les données envoyé par le client sont dans le bon format
            if 'order' in data:
                if 'credit_card' in data:
                    raise ValueError
            if 'order' not in data:
                if 'credit_card' not in data:
                    raise ValueError

            if 'order' in data:
                shipping_information = put_shipping.put_shipping(data['order'], order_id)
                if shipping_information == KeyError:
                    raise KeyError
                if shipping_information == ValueError:
                    raise ValueError
            elif 'credit_card' in data:
                order_to_check = Order.get(Order.id == order_id)
                if order_to_check.shipping_information is None:
                    raise NoShippingInfoError

                # Unusable redis code
                # job = q.enqueue(put_card.put_card, job_id=str(order_id), args=(data, order_id))
                # card_information = job.return_value()

                card_information = put_card.put_card(data, order_id)
                if card_information == UnprocessableError:
                    raise UnprocessableError
            else:
                raise ValueError

            return jsonify(order_shower.show_order(order_id)), 200
        else:
            return jsonify(order_shower.show_order(order_id)), 200
            # if q.fetch_job(str(order_id)).get_status() == 'started':
            #     return 202, "Accepted"
            # else:
            #     return jsonify(order_shower.show_order(order_id)), 200

    except ValueError:
        return 404
    except UnknownOrderIdError:
        return 404
    except MissingFieldError:
        return jsonify(missing_fields_error), 422
    except NoShippingInfoError:
        return jsonify(missing_fields_shipping_error), 422

    # Erreur qui ne devrais plus avoir lieu avec l'erreur de paiement de la deuxième partie
    except UnprocessableError:
        return jsonify(unprocessable_error), 422
    except RedundantPaymentError:
        return jsonify(redundant_payment_error), 422

    # Unusable redis code
    # Si on essaye de modifier une commande qui est en train d'être payée
    # except PaymentConflictError:
    #     return 409, "Conflict"


if __name__ == '__main__':
    app.run()
