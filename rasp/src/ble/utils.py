from abc import ABC, abstractmethod
from utils.models import DatabaseManager
from bleak import BleakClient, BleakScanner
import asyncio
from utils.packet_parser import PacketParser
from utils.models import Logs
import datetime
import os

# *****************************************************************************
# *                                                                           *
# *  ***********************    BLE STEPS    ***************************  *
# *                                                                           *
# *  *************** <><><><><><><><><><><><><><><><><><><><> *************  *
# *                                                                           *
# *****************************************************************************


class BleHandshake:
    def __init__(self, context, client):
        self.client = client
        self.context = context

    async def set_log(self):
        print("Handshake received")
        data = await self.client.read_gatt_char(self.context.characteristic_uuid)
        data_headers = data[:12]
        data_body = data[12:]

        parser = PacketParser()
        headers = parser.parse_headers(data_headers)
        id_device, _, trasnport_layer, id_protocol, _ = headers
        body = parser.parse_body(data_body, id_protocol)
        custom_epoch = body[2]

        print(f"Handshake from | device id: {id_device} custom_epoch: {custom_epoch}")

        seconds, milliseconds = divmod(custom_epoch, 1000)
        custom_epoch = datetime.datetime.utcfromtimestamp(
            seconds).replace(tzinfo=datetime.timezone.utc)
        custom_epoch = custom_epoch.replace(microsecond=milliseconds * 1000)

        print(f"Handshake | custom epoch {custom_epoch.timestamp()}")
        custom_epoch = datetime.datetime.utcnow().timestamp() - custom_epoch.timestamp()

        now = datetime.datetime.utcnow()
        now = now.replace(tzinfo=datetime.timezone.utc).timestamp()
        if self.context.init_timesamp is not None:
            time_to_connect = now - self.context.init_timesamp
            tries = self.context.tries
            ble_state_machine = "not using states"
            if os.environ.get("BLE_USE_STATES", "True").upper() == "TRUE":
                ble_state_machine = "using states"
            log = Logs.create(
                timestamp=datetime.datetime.utcnow(),
                id_device=id_device,
                custom_epoch=custom_epoch,
                time_to_connect=time_to_connect,
                id_protocol=id_protocol,
                transport_layer=trasnport_layer,
                tries=tries,
                ble_state_machine=ble_state_machine,
            )
            print("Saving log!")
            log.save()
            self.context.init_timesamp = None

    async def run(self):
        conf = DatabaseManager.get_default_config()
        first_msg = f"con{conf.transport_layer}{conf.id_protocol}".encode()
        print("Starting the handshake")
        await self.client.write_gatt_char(self.context.characteristic_uuid, first_msg)
        await self.set_log()
        print("Handshake completed")


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
        print("\t\tData received and saved!")


class Connecting:
    def __init__(self, context):
        self.context = context

    async def run(self):
        try:
            self.context.state = self
            print("Device is connecting")
            scanner = BleakScanner()
            devices = await scanner.discover()
            print("Discovered devices:")
            [print(device) for device in devices]
            print("\n\n")
            for device in devices:
                if device.name == self.context.device_name:
                    print(f"Device found: {device}")
                    client = BleakClient(device, timeout=20)
                    await client.connect()
                    print("Connected!")
                    # self.context.succesful_connection_timestamp = datetime.datetime.utcnow()
                    # self.context.succesful_connection_timestamp.replace(tzinfo=datetime.timezone.utc)
                    return client
            print("Device not found")
            print("Trying again...")
            raise TimeoutError("Failed to connect")
        except Exception as e:
            print(
                f"Exception in CONNECTING, trying again: {self.context.tries} \n Error was:\n \t{e} ")
            self.context.tries += 1
            await self.context.transition_to(ConnectingState())
            return None


# *****************************************************************************
# *                                                                           *
# *  ***********************    BLE STATES    ***************************  *
# *                                                                           *
# *  *************** <><><><><><><><><><><><><><><><><><><><> *************  *
# *                                                                           *
# *****************************************************************************

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
        return await Connecting(context).run()


class ConnectedState(DeviceState):
    def __init__(self):
        self.data_available = True

    def notify_callback(self, sender, data):
        expected_data = b"CHK_DATA"
        if data == expected_data:
            print("Notification received - Checking data")
            self.data_available = True

    async def handle(self, context, client):
        context.state = self
        self.ble_handshake = BleHandshake(context, client)
        self.read_data = ReadData(context, client)
        print("Device is connected")
        await self.ble_handshake.run()
        await asyncio.sleep(0.3)
        print("Setting notification callback (start_notify)")
        await client.start_notify(context.characteristic_uuid, self.notify_callback)
        while True:
            await asyncio.sleep(0.1)
            if self.data_available:
                await self.ble_handshake.run()
                await self.read_data.run()
                self.data_available = False
                if context.transport_layer == "D":
                    await asyncio.sleep(os.environ.get("SESP_BLE_DISC_TIMEOUT_SEC", 4))
                    await client.disconnect()
                    return


# *****************************************************************************
# *                                                                           *
# *  ***********************    BLE Manager    ***************************  *
# *                                                                           *
# *  *************** <><><><><><><><><><><><><><><><><><><><> *************  *
# *                                                                           *
# *****************************************************************************


class StatefullBleManager:
    def __init__(self, device_name, characteristic_uuid, transport_layer):
        self.state = DisconnectedState()
        self.device_name = device_name
        self.characteristic_uuid = characteristic_uuid
        self.transport_layer = transport_layer
        self.tries = 1
        self.init_timesamp = datetime.datetime.utcnow()
        self.init_timesamp = self.init_timesamp.replace(
            tzinfo=datetime.timezone.utc).timestamp()

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


class StatelessBleManager:

    def __init__(self, device_name, characteristic_uuid, transport_layer):
        self.state = DisconnectedState()
        self.device_name = device_name
        self.characteristic_uuid = characteristic_uuid
        self.transport_layer = transport_layer
        self.data_available = True
        self.tries = 1
        self.init_timesamp = datetime.datetime.utcnow()
        self.init_timesamp = self.init_timesamp.replace(
            tzinfo=datetime.timezone.utc).timestamp()

    def notify_callback(self, sender, data):
        expected_data = b"CHK_DATA"
        if data == expected_data:
            print("Notification received - Checking data")
            self.data_available = True

    async def transition_to(self, state: DeviceState, client=None):
        return None

    async def _run(self):

        self.connecting = Connecting(self)

        while True:
            try:
                client = await self.connecting.run()
                if client is None:
                    continue
                self.client = client
                await asyncio.sleep(0.2)
                print("Setting notification callback (start_notify)")
                self.ble_handshake = BleHandshake(self, client)
                self.read_data = ReadData(self, client)
                self.ble_handshake = BleHandshake(self, client)
                self.read_data = ReadData(self, client)
                print("Device is connected")
                await self.ble_handshake.run()
                print("Setting notification callback (start_notify)")
                await client.start_notify(self.characteristic_uuid, self.notify_callback)
                while True:
                    await asyncio.sleep(0.1)
                    if self.data_available:
                        await self.ble_handshake.run()
                        await self.read_data.run()
                        self.data_available = False
                        if self.transport_layer == "D":
                            await asyncio.sleep(os.environ.get("SESP_BLE_DISC_TIMEOUT_SEC", 4))
                            await client.disconnect()
                            return
            except Exception as e:
                print(e)
                print("Error while connecting")
                await asyncio.sleep(0.2)
                continue

    def run(self):
        asyncio.run(self._run())


class BleManager:

    def __init__(self, device_name, characteristic_uuid, transport_layer):
        self.state = DisconnectedState()
        self.device_name = device_name
        self.characteristic_uuid = characteristic_uuid
        self.transport_layer = transport_layer
        self.use_states = os.environ.get("BLE_USE_STATES", "True").upper() == "TRUE"
        print(f"Starting BLE manager using mode: --> ?? {self.transport_layer}")
        if (self.use_states):
            self.manager = StatefullBleManager(
                device_name, characteristic_uuid, transport_layer)
        else:
            self.manager = StatelessBleManager(
                device_name, characteristic_uuid, transport_layer)

    def run(self):
        self.manager.run()
