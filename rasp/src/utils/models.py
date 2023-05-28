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
    time_to_connect = TimestampField(resolution=3, null=True)
    custom_epoch = TimestampField(resolution=3, null=True)
    tries = IntegerField()

    class Meta:
        database = db


class Config(Model):
    config_name = CharField(unique=True, primary_key=True)
    id_protocol = CharField()
    transport_layer = CharField()
    last_access = DateTimeField()

    def was_recently_accessed(self, time_ref):
        now = datetime.datetime.utcnow()
        recent_acess = (now - self.last_access).total_seconds() < 60
        away_from_time_ref = (now - time_ref).total_seconds() > 90
        return recent_acess and away_from_time_ref

    def was_changed(self, start_layer, start_protocol):
        return self.id_protocol != start_protocol or self.transport_layer != start_layer

    class Meta:
        database = db


class DatabaseManager:
    MODELS = [Data, Logs, Config, Loss]

    @staticmethod
    def db_init():
        print("Initializing database")
        db.connect()
        print("getting default config")
        # drop tables
        try:
            db.drop_tables(DatabaseManager.MODELS)
        except:
            pass

        db.create_tables(DatabaseManager.MODELS)
        print(DatabaseManager.get_default_config())
    @staticmethod
    def db_close():
        db.close()
    @staticmethod
    def get_last_log():
        res = Logs.select().order_by(Logs.id.desc()).get()
        print("last log",res.timestamp.timestamp(),res.custom_epoch.timestamp())
        return res
    @staticmethod
    def get_default_config():
        config, _ = Config.get_or_create(
            config_name="default",
            defaults={
                "id_protocol": 0,
                "transport_layer": "C",
                "last_access": datetime.datetime.utcnow(),
            },
        )
        return config
    
    @staticmethod
    def save_data_to_db(headers, body):
        print("Saving to db")
        new_entry = Data.create()
        custom_epoch = DatabaseManager.get_last_log().custom_epoch.replace(tzinfo=datetime.timezone.utc)
        id_device, mac, transport_layer, id_protocol, message_length = headers
        val, batt_level, timestamp = body[:3]
        new_entry.id_device = id_device
        new_entry.mac = ''.join(format(x, '02x') for x in mac)
        print(mac)
        new_entry.transport_layer = transport_layer
        new_entry.id_protocol = id_protocol
        new_entry.message_length = message_length
        new_entry.val = val
        new_entry.batt_level = batt_level
        timestamp += custom_epoch.timestamp() * 1000
        seconds, milliseconds = divmod(timestamp, 1000)
        timestamp = datetime.datetime.utcfromtimestamp(
            seconds).replace(tzinfo=datetime.timezone.utc)
        timestamp = timestamp.replace(microsecond=int(milliseconds) * 1000)
        new_entry.timestamp = timestamp
        if id_protocol >= 1:
            temp, press, hum, Co = body[3: 3 + 4]
            new_entry.temp = temp
            new_entry.press = press
            new_entry.hum = hum
            new_entry.Co = Co
            if id_protocol == 2 or id_protocol == 3:
                RMS = body[7]
                new_entry.RMS = RMS
                if id_protocol == 3:
                    AMP_X, FREQ_X, AMP_Y, FREQ_Y, AMP_Z, FREQ_Z = body[8:14]
                    new_entry.AMP_X = AMP_X
                    new_entry.FREQ_X = FREQ_X
                    new_entry.AMP_Y = AMP_Y
                    new_entry.FREQ_Y = FREQ_Y
                    new_entry.AMP_Z = AMP_Z
                    new_entry.FREQ_Z = FREQ_Z
            else:
                ACC_X, ACC_Y, ACC_Z = body[7:]
                new_entry.ACC_X = ACC_X
                new_entry.ACC_Y = ACC_Y
                new_entry.ACC_Z = ACC_Z
        new_entry.save()
        timestamp_now = datetime.datetime.now(datetime.timezone.utc).timestamp()
        dif_timestamp = timestamp_now - timestamp.timestamp()
        print(
            f"Timestamp now: {timestamp_now}  Timestamp esp {timestamp.timestamp()} \
            | Diff: {dif_timestamp}"
        )
        dif_in_miliseconds = int(dif_timestamp * 1000 )
        Loss.get_or_create(data=new_entry, bytes_lost=0, latency=dif_in_miliseconds)

