from peewee import *
import os

db = PostgresqlDatabase(
    os.environ.get("POSTGRES_DB"),
    user=os.environ.get("POSTGRES_USER"),
    password=os.environ.get("POSTGRES_PASSWORD"),
    host=os.environ.get("POSTGRES_HOST"),
    port=os.environ.get("POSTGRES_PORT"))


class Data(Model):
    name = CharField()

    class Meta:
        database = db

class Logs(Model):
    name = CharField()

    class Meta:
        database = db

class Config(Model):
    config_name = CharField(unique = True)
    id_protocol = IntegerField()
    transport_layer_choices = ("TCP","UDP")
    transport_layer = CharField(choices = transport_layer_choices)

    class Meta:
        database = db

class Loss(Model):
    name = CharField()

    class Meta:
        database = db


def db_init():
    db.connect()
    db.create_tables([Data, Logs, Config, Loss])

def db_close():
    db.close()

