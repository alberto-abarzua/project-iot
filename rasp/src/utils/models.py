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

from utils.general import diff_to_now_utc_timestamp, milis_to_utc_timestamp
from utils.prints import console

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
    protocol_id = CharField(null=True)
    message_length = IntegerField(null=True)
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
    RGYR_X = BlobField(null=True)
    RGYR_Y = BlobField(null=True)
    RGYR_Z = BlobField(null=True)

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
    protocol_id = CharField()
    time_to_connect = TimestampField(resolution=3, null=True)
    custom_epoch = TimestampField(resolution=3, null=True)
    tries = IntegerField()
    ble_state_machine = CharField()

    class Meta:
        database = db


class Config(Model):
    config_name = CharField(unique=True, primary_key=True)
    status = IntegerField()
    protocol_id = CharField()
    bmi270_sampling = IntegerField()
    bmi270_sensibility = IntegerField()
    bmi270_gyro_sensibility = IntegerField()
    bme688_sampling = IntegerField()
    discontinuous_time = IntegerField()
    tcp_port = IntegerField()
    udp_port = IntegerField()
    host_ip_addr = CharField()
    ssid = CharField()
    password = CharField()

    transport_layer = CharField()
    last_access = DateTimeField()

    def was_recently_accessed(self, time_ref):
        now = datetime.datetime.utcnow()
        recent_acess = (now - self.last_access).total_seconds() < 60
        away_from_time_ref = (now - time_ref).total_seconds() > 90
        return recent_acess and away_from_time_ref

    def was_changed(self, start_layer, start_protocol):
        return self.protocol_id != start_protocol or self.transport_layer != start_layer

    class Meta:
        database = db

    def __str__(self):
        return (
            f"Config: {self.config_name}\n"
            f"Protocol: {self.protocol_id}\n"
            f"Transport Layer: {self.transport_layer}\n"
            f"Last Access: {self.last_access}\n"
            f"Status: {self.status}\n"
            f"BMI270 Sampling: {self.bmi270_sampling}\n"
            f"BMI270 Sensibility: {self.bmi270_sensibility}\n"
            f"BMI270 Gyro Sensibility: {self.bmi270_gyro_sensibility}\n"
            f"BME688 Sampling: {self.bme688_sampling}\n"
            f"Discontinuous Time: {self.discontinuous_time}\n"
            f"TCP Port: {self.tcp_port}\n"
            f"UDP Port: {self.udp_port}\n"
            f"Host IP Addr: {self.host_ip_addr}\n"
            f"SSID: {self.ssid}\n"
            f"Password: {self.password}\n"
        )


class DatabaseManager:
    MODELS = [Data, Logs, Config, Loss]

    @staticmethod
    def db_init():
        console.print("Initializing database", style="setup")
        db.connect()
        if os.environ.get("DROP_DB_ON_START", "TRUE").upper() == "TRUE":
            try:
                db.drop_tables(DatabaseManager.MODELS)
            except Exception as e:
                print(e)
                pass

        db.create_tables(DatabaseManager.MODELS)

        current_config = DatabaseManager.get_default_config()
        console.print(f"Current config: {current_config}", style="setup")

    @staticmethod
    def db_close():
        db.close()

    @staticmethod
    def get_last_log():
        res = Logs.select().order_by(Logs.id.desc()).get()
        return res

    @staticmethod
    def get_default_config():
        config, _ = Config.get_or_create(
            config_name="default",
            defaults={
                "protocol_id": os.environ.get("DEFAULT_PROTOCOL_ID"),
                "transport_layer": os.environ.get("DEFAULT_TRANSPORT_LAYER"),
                "last_access": datetime.datetime.utcnow(),
                "status": 0,
                "bmi270_sampling": 100,
                "bmi270_sensibility": 0,
                "bmi270_gyro_sensibility": 0,
                "bme688_sampling": 100,
                "discontinuous_time": os.environ.get("DISCONTINUOUS_TIMEOUT", 1),
                "tcp_port": os.environ.get("CONTROLLER_TCP_PORT"),
                "udp_port": os.environ.get("CONTROLLER_UDP_PORT"),
                "host_ip_addr": os.environ.get("CONTROLLER_SERVER_HOST"),
                "ssid": os.environ.get("WIFI_SSID"),
                "password": os.environ.get("WIFI_PASSWORD"),

            },
        )
        return config
    

    @staticmethod
    def update_config(**kwargs):
        current_config = DatabaseManager.get_default_config()

        for key, value in kwargs.items():
            if key in current_config._meta.fields:
                setattr(current_config, key, value)

        current_config.save()
                

    @staticmethod
    def get_latest_data(self,num_values = 200):
        return Data.select().order_by(Data.id.desc()).limit(num_values)




    @staticmethod
    def save_data_to_db(headers, body):
        console.print("Saving data to database ...", style="info", end=" ")
        new_entry = Data.create()
        custom_epoch = DatabaseManager.get_last_log().custom_epoch
        id_device, mac, transport_layer, protocol_id, message_length = headers
        body = [1] + list(body)
        _, batt_level, raw_timestamp = body[:3]
        raw_timestamp += custom_epoch.timestamp() * 1000

        timestamp = milis_to_utc_timestamp(raw_timestamp)

        new_entry.id_device = id_device
        new_entry.mac = "".join(format(x, "02x") for x in mac)
        new_entry.transport_layer = transport_layer
        new_entry.protocol_id = protocol_id
        new_entry.message_length = message_length
        new_entry.batt_level = batt_level

        new_entry.timestamp = timestamp

        if protocol_id >= 2:
            temp, press, hum, Co = body[3 : 3 + 4]
            new_entry.temp = temp
            new_entry.press = press
            new_entry.hum = hum
            new_entry.Co = Co
            if protocol_id == 3 or protocol_id == 4:
                RMS = body[7]
                new_entry.RMS = RMS
                if protocol_id == 4:
                    AMP_X, FREQ_X, AMP_Y, FREQ_Y, AMP_Z, FREQ_Z = body[8:14]
                    new_entry.AMP_X = AMP_X
                    new_entry.FREQ_X = FREQ_X
                    new_entry.AMP_Y = AMP_Y
                    new_entry.FREQ_Y = FREQ_Y
                    new_entry.AMP_Z = AMP_Z
                    new_entry.FREQ_Z = FREQ_Z
            elif protocol_id == 5:
                ACC_X, ACC_Y, ACC_Z,RGYR_X, RGYR_Y, RGYR_Z = body[7:]
                new_entry.ACC_X = ACC_X
                new_entry.ACC_Y = ACC_Y
                new_entry.ACC_Z = ACC_Z
                new_entry.RGYR_X = RGYR_X
                new_entry.RGYR_Y = RGYR_Y
                new_entry.RGYR_Z = RGYR_Z
        new_entry.save()
        console.print("Data saved to database", style="important")
        dif = diff_to_now_utc_timestamp(raw_timestamp)
        console.print(f"\nLatency: {dif:.5f}\n\n", style="important")
        dif_in_miliseconds = int(dif * 1000)
        Loss.get_or_create(data=new_entry, bytes_lost=0, latency=dif_in_miliseconds)
