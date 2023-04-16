from models import *

# Dictionnaire de retour par defaut
order_string_base = {
    "order": {
        "id": None,
        "total_price": None,
        "email": 'null',
        "credit_card": {},
        "shipping_information": {},
        "paid": 'false',
        "transaction": {},
        "product": {
            "id": None,
            "quantity": None
        },
        "shipping_price": None
    }
}


def show_order(order_id):
    try:
        order_to_show = Order.get_or_none(Order.id == order_id)
        if not order_to_show:
            raise ValueError
        formatted_order = order_string_base
        content = formatted_order['order']
        content['id'] = order_to_show.id
        content['total_price'] = order_to_show.total_price
        content['paid'] = order_to_show.paid
        content['shipping_price'] = order_to_show.shipping_price

        # for later
        # order_list = OrderedProduct.select().where(OrderedProduct.product==order_id)
        # for ordered_product in order_list:

        if len(OrderedProduct.select().where(OrderedProduct.order == order_id)) == 0:
            raise ValueError
        elif len(OrderedProduct.select().where(OrderedProduct.order == order_id)) > 1:
            if 'product' in content:
                content.pop('product')
            content['products'] = []
            for ordered_product_to_show in OrderedProduct.select().where(OrderedProduct.order == order_id):
                products_list = content['products']
                product_id = ordered_product_to_show.product_id
                product_quantity = ordered_product_to_show.quantity
                product_dict = {'id': product_id, 'quantity': product_quantity}
                products_list.append(product_dict)
        elif len(OrderedProduct.select().where(OrderedProduct.order == order_id)) == 1:
            ordered_product_to_show = OrderedProduct.get(OrderedProduct.order == order_id)
            product_content = content['product']
            product_content['id'] = ordered_product_to_show.product_id
            product_content['quantity'] = ordered_product_to_show.quantity
        else:
            raise ValueError

        if not order_to_show.email is None and not order_to_show.shipping_information is None:
            content['email'] = order_to_show.email
            shipping_information_to_show = ShippingInformation.get_or_none(
                ShippingInformation.id == order_to_show.shipping_information
            )
            shipping_information_content = content['shipping_information']
            shipping_information_content['country'] = shipping_information_to_show.country
            shipping_information_content['address'] = shipping_information_to_show.address
            shipping_information_content['postal_code'] = shipping_information_to_show.postal_code
            shipping_information_content['city'] = shipping_information_to_show.city
            shipping_information_content['province'] = shipping_information_to_show.province

        if not order_to_show.credit_card is None:
            credit_card_to_show = CreditCard.get(
                CreditCard.id == order_to_show.credit_card
            )
            credit_card_content = content['credit_card']
            credit_card_content['name'] = credit_card_to_show.name
            credit_card_content['first_digits'] = credit_card_to_show.first_digits
            credit_card_content['last_digits'] = credit_card_to_show.last_digits
            credit_card_content['expiration_year'] = credit_card_to_show.expiration_year
            credit_card_content['expiration_month'] = credit_card_to_show.expiration_month

        if not order_to_show.transaction is None:
            transaction_to_show = Transaction.get(
                Transaction.id == order_to_show.transaction
            )
            transaction_content = content['transaction']
            transaction_content['success'] = transaction_to_show.success
            transaction_content['amount_charged'] = transaction_to_show.amount_charged
            if transaction_to_show.success == 'true':
                transaction_content['id'] = transaction_to_show.display_id
                transaction_content['error'] = {}
            else:
                transaction_content['error'] = {
                    "code": "card-declined",
                    "name": "La carte de crédit a été déclinée"
                }

    except ValueError:
        return 404

    return formatted_order
