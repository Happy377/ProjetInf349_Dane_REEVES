import time

from feedbacks.order_shower import *


def put_shipping(data, order_id):
    try:
        if 'credit_card' in data:
            raise ValueError
        if 'email' in data:
            shipping_email = data['email']
        else:
            raise KeyError
        if 'shipping_information' in data:
            shipping_data = data['shipping_information']
        else:
            raise KeyError
        for coordinate in ["country", "address", "postal_code", "city", "province"]:
            if shipping_data[coordinate] is None:
                return KeyError

        shipping_info = ShippingInformation(
            country=shipping_data['country'],
            address=shipping_data['address'],
            postal_code=shipping_data['postal_code'],
            city=shipping_data['city'],
            province=shipping_data['province'],
        )
        shipping_info.save()

        updated_order = Order.update(
            email=shipping_email,
            shipping_information=shipping_info.id
        ).where(Order.id == order_id)
        updated_order.execute()
    except KeyError:
        return KeyError
    except ValueError:
        return ValueError
