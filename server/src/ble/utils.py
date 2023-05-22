import asyncio
from struct import unpack
import asyncio
from bleak import BleakClient, BleakScanner
from abc import ABC, abstractmethod



class BleHandshake:
    def __init__(self, context, client):
        self.client = client
        self.context = context


    async def run(self):
        # send to esp connect request and config
        first_msg = b"con"
        first_msg += b"C"# "D" for discontinuous, "C" for continuous
        first_msg += b"1" # protocol id
        print("Sending connect request")
        await self.client.write_gatt_char(self.context.characteristic_uuid,first_msg)


class ReadData:
    def __init__(self,context,client):
        self.client = client
        self.context = context
    
    async def run(self):
        data = await self.client.read_gatt_char(self.context.characteristic_uuid)
        ptr = "<bbi"
        print("Received length: ",len(data))
        print("Received data: ",data)
        print(unpack(ptr,data))



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
        print('\n\n')
        for device in devices:
            if device.name == context.device_name:
                print(f"Device found: {device}")
                client = BleakClient(device)
                await client.connect()
                print("Connected!")
                return client

class ConnectedState(DeviceState):
    async def handle(self, context, client):
        context.state = self
        await BleHandshake(context, client).run()
        await ReadData(context, client).run()


class BleManager:
    def __init__(self,device_name,characteristic_uuid):
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




