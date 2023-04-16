# Dictionnaires de codes d'erreurs

order_creation_error = {
    "errors": {
        "product": {
            "code": "missing-fields",
            "name": "La création d'une commande nécessite un produit"
        }
    }
}
not_in_stock_error = {
    "errors": {
        "product": {
            "code": "out-of-inventory",
            "name": "Le produit demandé n'est pas en inventaire"
        }
    }
}

missing_fields_error = {
    "errors": {
        "order": {
            "code": "missing-fields",
            "name": "Il manque un ou plusieurs champs qui sont obligatoires",
        }
    }
}

missing_fields_shipping_error = {
    "errors": {
        "order": {
            "code": "missing-fields",
            "name": "Les informations du client sont nécessaire avant d'appliquer une carte de crédit"
        }
    }
}

unprocessable_error = {
    "errors": {
        "credit_card": {
            "code": "card-declined",
            "name": "La carte de crédit a été déclinée"
        }
    }
}

redundant_payment_error = {
    "errors": {
        "order": {
            "code": "already-paid",
            "name": "La commande a déjà été payée."
        }
    }
}
