from abc import ABC, abstractmethod

from bleak import BleakClient, BleakScanner
import asyncio

class BleHandshake:
    def __init__(self, context, client):
        self.client = client
        self.context = context

    async def run(self):
        first_msg = b"con"
        first_msg += b"C"  # "D" for discontinuous, "C" for continuous
        first_msg += b"1"  # protocol id
        print("Sending connect request")
        await self.client.write_gatt_char(self.context.characteristic_uuid, first_msg)
        print("Sent connect request")


class ReadData:
    def __init__(self, context, client):
        self.client = client
        self.context = context

    async def run(self):
        data = await self.client.read_gatt_char(self.context.characteristic_uuid)
        ptr = "<bbi"
        print("Received length: ", len(data))
        print("Received data: ", data)
        # print(unpack(ptr, data))


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
        print("Device is connected")
        await BleHandshake(context, client).run()
        await asyncio.sleep(5)
        print("setting up notifications")
        await client.start_notify(context.characteristic_uuid, self.notify_callback)
        while True:
            await asyncio.sleep(1)
            if self.data_available:
                await ReadData(context, client).run()
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

    async def run(self):
        client = await self.transition_to(ConnectingState())
        if client is not None:
            await self.transition_to(ConnectedState(), client)
            await client.disconnect()
            await self.transition_to(DisconnectedState())
