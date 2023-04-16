class RedundantPaymentError(Exception):
    pass


class UnknownOrderIdError(Exception):
    pass


class NoShippingInfoError(Exception):
    pass


class MissingFieldError(Exception):
    pass


class PaymentError(Exception):
    pass


class UnprocessableError(Exception):
    pass


# For if one tries to modify info on an order whose payment is being processed
# Not used because redis is broken
# class PaymentConflictError(Exception):
#     pass