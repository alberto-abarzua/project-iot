import datetime
import os

from peewee import (
    AutoField,
    BlobField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
    PostgresqlDatabase,
    TimestampField,
)

db = PostgresqlDatabase(
    os.environ.get("POSTGRES_DB"),
    user=os.environ.get("POSTGRES_USER"),
    password=os.environ.get("POSTGRES_PASSWORD"),
    host=os.environ.get("POSTGRES_HOST"),
    port=os.environ.get("POSTGRES_PORT"),
)


class Data(Model):
    id = AutoField()
    id_device = IntegerField(null=True)
    mac = CharField(null=True)
    transport_layer = CharField(null=True)
    id_protocol = CharField(null=True)
    message_length = IntegerField(null=True)
    val = CharField(null=True)
    batt_level = CharField(null=True)
    timestamp = TimestampField(resolution=3, null=True)
    temp = CharField(null=True)
    press = IntegerField(null=True)
    hum = CharField(null=True)
    Co = IntegerField(null=True)
    RMS = IntegerField(null=True)
    AMP_X = IntegerField(null=True)
    FREQ_X = IntegerField(null=True)
    AMP_Y = IntegerField(null=True)
    FREQ_Y = IntegerField(null=True)
    AMP_Z = IntegerField(null=True)
    FREQ_Z = IntegerField(null=True)
    ACC_X = BlobField(null=True)
    ACC_Y = BlobField(null=True)
    ACC_Z = BlobField(null=True)

    class Meta:
        database = db


class Loss(Model):
    id = AutoField()
    data = ForeignKeyField(Data, backref="losses", null=True)
    bytes_lost = IntegerField()
    latency = IntegerField(null=True)

    class Meta:
        database = db


class Logs(Model):
    id = AutoField()
    timestamp = TimestampField(resolution=3, null=True)
    id_device = IntegerField()
    transport_layer = CharField()
    id_protocol = CharField()
    custom_epoch = TimestampField(resolution=3, null=True)

    class Meta:
        database = db


class Config(Model):
    config_name = CharField(unique=True, primary_key=True)
    id_protocol = CharField()
    transport_layer = CharField()
    last_access = DateTimeField()

    def was_recently_accessed(self, time_ref):
        now = datetime.datetime.now()
        recent_acess = (now - self.last_access).total_seconds() < 60
        away_from_time_ref = (now - time_ref).total_seconds() > 90
        return recent_acess and away_from_time_ref

    def was_changed(self, start_layer, start_protocol):
        return self.id_protocol != start_protocol or self.transport_layer != start_layer

    class Meta:
        database = db


class DatabaseManager:
    MODELS = [Data, Logs, Config, Loss]

    def db_init(self):
        db.connect()
        try:
            if os.environ.get("DEBUG"):
                db.drop_tables(self.MODELS)
        except Exception as e:
            print(e)
            pass
        db.create_tables(self.MODELS)

    def db_close(self):
        db.close()

    def get_last_log(self):
        return Logs.select().order_by(Logs.id.desc()).get()

    def get_default_config(self):
        config, _ = Config.get_or_create(
            config_name="default",
            defaults={
                "id_protocol": 4,
                "transport_layer": "U",
                "last_access": datetime.datetime.now(),
            },
        )
        return config
