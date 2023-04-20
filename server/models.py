from peewee import *
from main_server import db

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
