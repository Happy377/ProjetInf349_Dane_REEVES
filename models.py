from peewee import *
from dotenv import load_dotenv
import os

load_dotenv()

db = PostgresqlDatabase(
    os.environ.get("DB_NAME"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    host=os.environ.get("DB_HOST"),
    port=os.environ.get("DB_PORT")
)


def create_tables():
    with db:
        db.create_tables([Product, OrderedProduct, CreditCard, ShippingInformation, Transaction, Order])


class BaseModel(Model):
    class Meta:
        database = db


class Product(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField(unique=True)
    in_stock = CharField()
    description = TextField()
    price = FloatField()
    weight = IntegerField()
    image = CharField()
    type = CharField()
    height = IntegerField()


class CreditCard(BaseModel):
    name = CharField()
    first_digits = CharField()
    last_digits = CharField()
    expiration_year = IntegerField()
    expiration_month = IntegerField()


class ShippingInformation(BaseModel):
    country = CharField()
    address = CharField()
    postal_code = CharField()
    city = CharField()
    province = CharField()


class Transaction(BaseModel):
    display_id = CharField(null=True)
    success = CharField()
    amount_charged = IntegerField()
    error = CharField(null=True)


class Order(BaseModel):
    total_price = FloatField(default=0)
    email = CharField(null=True)
    credit_card = ForeignKeyField(CreditCard, unique=True, null=True)
    shipping_information = ForeignKeyField(ShippingInformation, unique=True, null=True)
    paid = CharField()
    transaction = ForeignKeyField(Transaction, unique=True, null=True)
    shipping_price = FloatField(default=0)


class OrderedProduct(BaseModel):
    product = ForeignKeyField(Product)
    order = ForeignKeyField(Order)
    quantity = IntegerField()

