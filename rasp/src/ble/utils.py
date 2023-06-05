from abc import ABC, abstractmethod
from utils.models import DatabaseManager
import pygatt
import time
import threading
from utils.packet_parser import PacketParser
from utils.models import Logs
import datetime
import os
import asyncio
import pytz
from bleak import BleakClient
from threading import Thread
from utils.prints import console,print
# *****************************************************************************
# *                                                                           *
# *  ***********************    BLE CORE    ***************************  *
# *                                                                           *
# *  *************** <><><><><><><><><><><><><><><><><><><><> *************  *
# *                                                                           *
# *****************************************************************************
class BleCore:

    def __init__():
        pass

    def char_write(self,data):
        raise NotImplementedError
       
    def char_read():
        raise NotImplementedError

    def subscribe(self,notify_function):
        raise NotImplementedError
    
    def re_create(self):
        raise NotImplementedError
    



class PygattCore(BleCore):
    def __init__(self, device_mac, characteristic_uuid):
        self.adapter = pygatt.GATTToolBackend()
        self.device_mac = device_mac
        self.characteristic_uuid = characteristic_uuid
        self.client = None
        self.adapter.start()
        self.connected = False
        self.notify_thread = None
    
    def connect(self):
        if self.client is None:
            self.client = self.adapter.connect(
                self.device_mac,
                address_type=pygatt.BLEAddressType.public,
                timeout=10,
                auto_reconnect=True)
            self.connected = True

    def disconnect(self):
        if self.client is not None:
            self.client.disconnect()
            # unsuscribe
            self.notify_thread.join()
            self.client = None
            self.connected = False
    def char_read(self):
        return self.client.char_read(self.characteristic_uuid,timeout =3)
    
    def char_write(self,data):
        self.client.char_write(self.characteristic_uuid, data, wait_for_response=False)

    def subscribe(self,notify_function):
        self.notify_thread = threading.Thread(target=self.client.subscribe, args=(self.characteristic_uuid,),
                                      kwargs={"callback":notify_function, "wait_for_response": False})
        self.notify_thread.start()

    def reset(self):
        self.disconnect()
        self.__init__(self.device_mac, self.characteristic_uuid)



class BleakCore(BleCore):
    def __init__(self, device_mac, characteristic_uuid):
        self.device_mac = device_mac
        self.characteristic_uuid = characteristic_uuid
        self.client = None
        self.connected = False
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def connect(self):
        self.loop.run_until_complete(self._connect())

    async def _connect(self):
        self.client = BleakClient(self.device_mac)
        self.connected = await self.client.connect()
        console.print("Connected!",style = "info")

    def disconnect(self):
        console.print("Disconnecting...",style = "danger")
        self.loop.run_until_complete(self._disconnect())
        self.loop.close()

    async def _disconnect(self):
        if self.client is not None:
            await self.client.stop_notify(self.characteristic_uuid)
            await self.client.disconnect()
            self.client = None
            self.connected = False

    def char_read(self):
        return self.loop.run_until_complete(self._char_read())

    async def _char_read(self):
        if self.client is not None and self.connected:
            return await self.client.read_gatt_char(self.characteristic_uuid)

    def char_write(self, data):
        self.loop.run_until_complete(self._char_write(data))

    async def _char_write(self, data):
        if self.client is not None and self.connected:
            await self.client.write_gatt_char(self.characteristic_uuid, data)

    def subscribe(self, notify_function):
        self.loop.run_until_complete(self._subscribe(notify_function))


    async def _subscribe(self, notify_function):
        if self.client is not None and self.connected:
            print("Subscribing to characteristic")
            await self.client.start_notify(self.characteristic_uuid, notify_function)

    def reset(self):
        self.disconnect()
        self.__init__(self.device_mac, self.characteristic_uuid)


# *****************************************************************************
# *                                                                           *
# *  ***********************    BLE STEPS    ***************************  *
# *                                                                           *
# *  *************** <><><><><><><><><><><><><><><><><><><><> *************  *
# *                                                                           *
# *****************************************************************************



class BleHandshake:
    def __init__(self, context):
        self.context = context

    def set_log(self):
        print("Handshake received")
        data = self.context.ble_core.char_read()
        data_headers, data_body = data[:12], data[12:]


        parser = PacketParser()
        headers = parser.parse_headers(data_headers)
        id_device, _, transport_layer, id_protocol, _ = headers
        body = parser.parse_body(data_body, id_protocol)
        custom_epoch = body[2] #custom epoch in millies

        print(f"Handshake from | device id: {id_device} custom_epoch: {custom_epoch}")

        seconds, milliseconds = divmod(custom_epoch, 1000)
        custom_epoch = datetime.datetime.fromtimestamp(seconds,tz=pytz.utc)
        custom_epoch = custom_epoch.replace(microsecond=milliseconds * 1000)
        utc_now = datetime.datetime.now(tz = pytz.utc)
        print(f"Handshake | custom epoch {custom_epoch.timestamp()}")
        custom_epoch_diff = utc_now.timestamp() - custom_epoch.timestamp()
        print("Handshake | custom epoch diff", custom_epoch_diff)
        now = datetime.datetime.utcnow()
        now = now.replace(tzinfo=datetime.timezone.utc).timestamp()
        if self.context.init_timestamp is not None:
            time_to_connect = now - self.context.init_timestamp
            tries = self.context.tries
            ble_state_machine = "not using states"
            if os.environ.get("BLE_USE_STATES", "True").upper() == "TRUE":
                ble_state_machine = "using states"
            log = Logs.create(
                timestamp=datetime.datetime.utcnow(),
                id_device=id_device,
                custom_epoch=custom_epoch_diff,
                time_to_connect=time_to_connect,
                id_protocol=id_protocol,
                transport_layer=transport_layer,
                tries=tries,
                ble_state_machine=ble_state_machine,
            )
            print("Saving log!")
            log.save()
            self.context.init_timestamp = None


    def run(self):
        conf = DatabaseManager.get_default_config()
        first_msg = f"con{conf.transport_layer}{conf.id_protocol}".encode()
        self.context.ble_core.char_write(first_msg)
        self.set_log()



class ReadData:
    def __init__(self, context):
        self.context = context

    def run(self):
        data = self.context.ble_core.char_read()
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

    def run(self):
        try:
            self.context.state = self
            print(f"Device is connecting {self.context.tries} ")
            
            try:
                self.context.ble_core.connect()
                return True
            except Exception as e:
                print(f"Failed to connect to device: {e}")
            print("Trying again...")
            self.context.tries += 1

        except Exception as e:
            print(f"Exception in CONNECTING, trying again: {self.context.tries} \n Error was:\n \t{e}")
            self.context.tries += 1


# *****************************************************************************
# *                                                                           *
# *  ***********************    BLE STATES    ***************************  *
# *                                                                           *
# *  *************** <><><><><><><><><><><><><><><><><><><><> *************  *
# *                                                                           *
# *****************************************************************************

class DeviceState(ABC):
    @abstractmethod
    def handle(self, context):
        pass


class DisconnectedState(DeviceState):
    def handle(self, context):
        context.state = self
        print("Device is disconnected")


class ConnectingState(DeviceState):
    def handle(self, context):
        return Connecting(context).run()



class ConnectedState(DeviceState):
    def __init__(self):
        self.data_available = False
        self.notify_thread = None

    def notify_callback(self, handle, value):
        expected_data = b"CHK_DATA"
        if value == expected_data:
            print("Notification received - Checking data")
            self.data_available = True

    def handle(self, context, client):
        context.state = self
        self.ble_handshake = BleHandshake(context)
        self.read_data = ReadData(context)

        context.ble_core.subscribe(self.notify_callback)

        while True:
            console.print("Waiting for data...",style = "light_info")
            context.ble_core.subscribe(self.notify_callback)

            time.sleep(2)
            if self.data_available:
                self.ble_handshake.run()
                self.read_data.run()
                self.data_available = False
                if context.transport_layer == "D":
                    time.sleep(os.environ.get("SESP_BLE_DISC_TIMEOUT_SEC", 4))
                    client.disconnect()
                    return



# *****************************************************************************
# *                                                                           *
# *  ***********************    BLE Manager    ***************************  *
# *                                                                           *
# *  *************** <><><><><><><><><><><><><><><><><><><><> *************  *
# *                                                                           *
# *****************************************************************************

class StatefulBleManager:
    def __init__(self, device_name, characteristic_uuid,device_mac, transport_layer,ble_core):
        self.ble_core = ble_core
        self.state = DisconnectedState()
        self.device_name = device_name
        self.characteristic_uuid = characteristic_uuid
        self.transport_layer = transport_layer
        self.device_mac = device_mac
        self.tries = 1
        self.init_timestamp = datetime.datetime.utcnow()
        self.init_timestamp = self.init_timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()

    def transition_to(self, state: DeviceState, client=None):
        self.state = state
        if client is None:
            return self.state.handle(self)
        else:
            return self.state.handle(self, client)

    def run(self):
        self._run()

    def _run(self):
        client = self.transition_to(ConnectingState())
        if client is not None:
            self.transition_to(ConnectedState(), client)
            client.disconnect()
            self.transition_to(DisconnectedState())

class StatelessBleManager:
    def __init__(self, device_name, characteristic_uuid,device_mac, transport_layer,ble_core):
        self.ble_core = ble_core
        self.state = DisconnectedState()
        self.device_name = device_name
        self.characteristic_uuid = characteristic_uuid
        self.transport_layer = transport_layer
        self.device_mac = device_mac
        self.data_available = True
        self.tries = 1
        self.init_timestamp = datetime.datetime.utcnow()
        self.init_timestamp = self.init_timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
        self.notify_thread = None
        

    def notify_callback(self, handle, value):
        expected_data = b"CHK_DATA"
        print("Notification received")
        if expected_data in value:
            print("Notification received - Checking data")
            self.data_available = True

    def transition_to(self, state: DeviceState, client=None):
        return None

    def _run(self):
        while True:
            try:
                Connecting(self).run()
                if not self.ble_core.connected:
                    continue
                print("Setting notification callback (start_notify)")
                self.ble_core.subscribe(self.notify_callback)
              
                self.ble_handshake = BleHandshake(self)
                self.read_data = ReadData(self)
                self.ble_core.subscribe(self.notify_callback)
                
                
                while True:
                    time.sleep(1)
                    console.print("Waiting for data...",style = "light_info")
                    self.ble_core.subscribe(self.notify_callback)
                    if self.data_available:
                        self.ble_handshake.run()
                        self.read_data.run()
                        self.data_available = False
                        if self.transport_layer == "D":
                            time.sleep(os.environ.get("SESP_BLE_DISC_TIMEOUT_SEC", 4))
                            self.ble_core.disconnect()
                            return
            except Exception as e:
                print(e)
                print("Error while connecting")
                self.ble_core.reset()
                time.sleep(2)
                continue

    def run(self):
        self._run()



class BleManager:

    def __init__(self, device_name, characteristic_uuid, device_mac,transport_layer):
        self.state = DisconnectedState()
        self.device_name = device_name
        self.characteristic_uuid = characteristic_uuid
        self.device_mac = device_mac
        self.ble_core = PygattCore(self.device_mac, self.characteristic_uuid)
        # self.ble_core = BleakCore(self.device_mac, self.characteristic_uuid)
        self.transport_layer = transport_layer
        self.use_states = os.environ.get("BLE_USE_STATES", "True").upper() == "TRUE"
        print(f"Starting BLE manager using mode: -->  {self.transport_layer} and using states: {self.use_states}")

        if (self.use_states):
            self.manager = StatefulBleManager(
                device_name, characteristic_uuid,device_mac, transport_layer,self.ble_core)
        else:
            self.manager = StatelessBleManager(
                device_name, characteristic_uuid,device_mac, transport_layer,self.ble_core)

    def run(self):
        self.manager.run()
