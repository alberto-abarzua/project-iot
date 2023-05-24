from abc import ABC, abstractmethod
from utils.models import DatabaseManager
from bleak import BleakClient, BleakScanner
import asyncio
from utils.packet_parser import PacketParser
from utils.models import Logs
import datetime


class BleHandshake:
    def __init__(self, context, client):
        self.client = client
        self.context = context
        self.first = True

    async def set_log(self, sender, data):
            expected_data = b"START"
            print("in log notify")
            print("data", data)
            if data == expected_data:
                data = await self.client.read_gatt_char(self.context.characteristic_uuid)
                print("reading lata of len", len(data), "data", data)
                data_headers = data[:12]
                data_body = data[12:]

                parser = PacketParser()
                headers = parser.parse_headers(data_headers)
                id_device, _, trasnport_layer, id_protocol, _ = headers
                body = parser.parse_body(data_body, id_protocol)
                custom_epoch = body[2]
                print("Handshake received from device", id_device,
                    "custom epoch", custom_epoch)

                seconds, milliseconds = divmod(custom_epoch, 1000)
                custom_epoch = datetime.datetime.utcfromtimestamp(
                    seconds).replace(tzinfo=datetime.timezone.utc)
                custom_epoch = custom_epoch.replace(microsecond=milliseconds * 1000)
                # When not using sntp:
                print("custom_epcho, time", custom_epoch.timestamp())
                custom_epoch = datetime.datetime.utcnow().timestamp() - custom_epoch.timestamp()
                log = Logs.create(
                    timestamp=datetime.datetime.utcnow(),
                    id_device=id_device,
                    custom_epoch=custom_epoch,
                    id_protocol=id_protocol,
                    transport_layer=trasnport_layer,

                )
                print("log saved")
                log.save()
                self.client.stop_notify(self.context.characteristic_uuid)


    async def run(self):
        # if first:
        # save log

        conf = DatabaseManager.get_default_config()
        first_msg = f"con{conf.transport_layer}{conf.id_protocol}".encode()
        print("Sending connect request")
        await self.client.write_gatt_char(self.context.characteristic_uuid, first_msg)

        if self.first:
            await asyncio.sleep(5)
            self.first = False
            await self.client.start_notify(self.context.characteristic_uuid, self.set_log)
            print("Started notify")

        print("Sent connect request")


class ReadData:
    def __init__(self, context, client):
        self.client = client
        self.context = context

    async def run(self):
        data = await self.client.read_gatt_char(self.context.characteristic_uuid)
        data_headers = data[:12]
        data_body = data[12:]
        parser = PacketParser()
        headers = parser.parse_headers(data_headers)
        _, _, _, id_protocol, _ = headers
        body = parser.parse_body(data_body, id_protocol)
        DatabaseManager.save_data_to_db(headers, body)
        print("Data received and saved!")


class DeviceState(ABC):
    @abstractmethod
    async def handle(self, context):
        pass


class DisconnectedState(DeviceState):
    async def handle(self, context):
        context.state = self
        print("Device is disconnected")


class ConnectingState(DeviceState):
    async def handle(self, context):
        context.state = self
        print("Device is connecting")
        scanner = BleakScanner()
        devices = await scanner.discover()
        print("Discovered devices:")
        [print(device) for device in devices]
        print("\n\n")
        for device in devices:
            if device.name == context.device_name:
                print(f"Device found: {device}")
                client = BleakClient(device)
                await client.connect()
                print("Connected!")
                return client
        print("Device not found")
        print("Trying again...")
        await context.transition_to(ConnectingState())


class ConnectedState(DeviceState):
    def __init__(self):
        self.data_available = False
        

    def notify_callback(self, sender, data):
        expected_data = b"CHK_DATA"
        if data == expected_data:
            print("Notification received - data available")
            self.data_available = True

    async def handle(self, context, client):
        context.state = self
        self.ble_handshake = BleHandshake(context, client)
        self.read_data = ReadData(context, client)
        print("Device is connected")
        await self.ble_handshake.run()
        await asyncio.sleep(5)
        print("setting up notifications")
        await client.start_notify(context.characteristic_uuid, self.notify_callback)
        while True:
            await asyncio.sleep(0.5)
            if self.data_available:
                await self.ble_handshake.run()
                await asyncio.sleep(0.5)
                await self.read_data.run()
                self.data_available = False


class BleManager:
    def __init__(self, device_name, characteristic_uuid):
        self.state = DisconnectedState()
        self.device_name = device_name
        self.characteristic_uuid = characteristic_uuid

    async def transition_to(self, state: DeviceState, client=None):
        self.state = state
        if client is None:
            return await self.state.handle(self)
        else:
            return await self.state.handle(self, client)

    def run(self):
        asyncio.run(self._run())

    async def _run(self):
        client = await self.transition_to(ConnectingState())
        if client is not None:
            await self.transition_to(ConnectedState(), client)
            await client.disconnect()
            await self.transition_to(DisconnectedState())
