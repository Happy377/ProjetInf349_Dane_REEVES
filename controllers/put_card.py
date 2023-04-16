import time

from flask import json
import urllib.request
from urllib.error import HTTPError

from feedbacks.order_shower import *
from exceptions import *


def put_card(data, order_id):
    global payment_data
    try:
        # Following code used so that one can observe job status
        # time.sleep(60)
        order_to_pay = Order.get(Order.id == order_id)
        if order_to_pay.paid == 'true':
            raise RedundantPaymentError

        amount_due = order_to_pay.total_price + order_to_pay.shipping_price
        data['amount_charged'] = amount_due

        payment_request = urllib.request.Request("http://dimprojetu.uqac.ca/~jgnault/shops/pay/")

        payment_request.add_header("Content-Type", "application/json; charset=utf-8")

        body = json.dumps(data)

        with urllib.request.urlopen("http://dimprojetu.uqac.ca/~jgnault/shops/pay/", body.encode("utf-8")) as result:
            payment_data = json.loads(result.read())

        card_data = payment_data['credit_card']

        credit_card_info = CreditCard(
            name=card_data['name'],
            first_digits=card_data['first_digits'],
            last_digits=str(card_data['last_digits']),
            expiration_year=card_data['expiration_year'],
            expiration_month=card_data['expiration_month']
        )
        credit_card_info.save()

        transaction_data = payment_data['transaction']

        transaction_info = Transaction(
            display_id=transaction_data['id'],
            success=transaction_data['success'],
            amount_charged=transaction_data['amount_charged']
        )
        transaction_info.save()

        update_paid = Order.update(
            credit_card=credit_card_info.id,
            paid='true',
            transaction=transaction_info.id
        ).where(Order.id == order_id)
        update_paid.execute()

    except RedundantPaymentError:
        return RedundantPaymentError
    except HTTPError:
        order_to_pay = Order.get(Order.id == order_id)
        amount_due = order_to_pay.total_price + order_to_pay.shipping_price

        # Je trouve pas ça logique de laisser le amount_charged si il y a eu une erreur
        transaction_error_info = Transaction(
            success='false',
            amount_charged=amount_due
        )
        transaction_error_info.save()

        order_paymenet_error = Order.update(
            transaction=transaction_error_info.id
        ).where(Order.id == order_id)
        order_paymenet_error.execute()
