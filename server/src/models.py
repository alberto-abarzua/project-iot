from peewee import *
import os
import datetime
db = PostgresqlDatabase(
    os.environ.get("POSTGRES_DB"),
    user=os.environ.get("POSTGRES_USER"),
    password=os.environ.get("POSTGRES_PASSWORD"),
    host=os.environ.get("POSTGRES_HOST"),
    port=os.environ.get("POSTGRES_PORT"))


class Data(Model):
    id = AutoField()
    # headers
    id_device = IntegerField(null = True)
    mac = CharField(null = True)
    transport_layer = CharField(null = True)
    id_protocol = CharField(null = True)
    message_length = IntegerField(null = True)
    # body all fields default null
    val = CharField(null=True)
    batt_level = CharField(null=True)
    #microsecnosd
    timestamp = TimestampField(resolution = 3,null=True)
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
    # FOR PROTOCOL null = True4
    ACC_X = BlobField(null=True)
    ACC_Y = BlobField(null=True)
    ACC_Z = BlobField(null=True)

    class Meta:
        database = db


class Loss(Model):
    id = AutoField()
    # forgien key to data
    data = ForeignKeyField(Data, backref='losses', null=True)
    bytes_lost = IntegerField()
    latency = TimestampField(resolution = 3,null=True)
    

    class Meta:
        database = db


class Logs(Model):
    id = AutoField()
    # forgien key to data
    timestamp = TimestampField(resolution = 3,null=True)
    id_device = IntegerField()
    transport_layer = CharField()
    id_protocol = CharField()
    custom_epoch = TimestampField(resolution = 3,null=True)
    class Meta:
        database = db


class Config(Model):
    config_name = CharField(unique=True, primary_key=True)
    id_protocol = CharField()
    transport_layer = CharField()
    #  last access time
    last_access = DateTimeField()

    def was_recently_accesed(self, time_ref):
        now = datetime.datetime.now()
        return (now - self.last_access).total_seconds() < 60 and (now - time_ref).total_seconds() > 60

    def was_changed(self, start_layer, start_protocol):
        return self.id_protocol != start_protocol or self.transport_layer != start_layer

    class Meta:
        database = db


MODELS = [Data, Logs, Config, Loss]


def db_init():
    db.connect()
    try:
        db.drop_tables(MODELS)
    except Exception as e:
        print(e)
        pass
    db.create_tables(MODELS)


def db_close():
    db.close()

def get_last_log():
    # print all logs
    print("this is length",len(Logs.select()))
    for log in Logs.select():
        print("lakjdflkasjdflk;sadjfl;ksjdfl;kasdfl;ksdjf")
        print(log.id, log.timestamp, log.id_device, log.transport_layer, log.id_protocol, log.custom_epoch)
    return Logs.select().order_by(Logs.id.desc()).get()

def get_default_config():
    config, _ = Config.get_or_create(config_name="default", defaults={
        'id_protocol': 0, 'transport_layer': 'T', 'last_access': datetime.datetime.now()})
    return config
