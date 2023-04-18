from peewee import *
from main import db

class TestModel(Model):
    name = CharField()

    class Meta:
        database = db
