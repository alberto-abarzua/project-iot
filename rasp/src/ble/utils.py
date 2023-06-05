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

    def set_log(self):
        print("Handshake received")
        time.sleep(1)
        print("Reading data")
        data = self.client.char_read(self.context.characteristic_uuid,timeout = 10)
        data_headers = data[:12]
        data_body = data[12:]

        parser = PacketParser()
        headers = parser.parse_headers(data_headers)
        id_device, _, transport_layer, id_protocol, _ = headers
        body = parser.parse_body(data_body, id_protocol)
        custom_epoch = body[2]

        print(f"Handshake from | device id: {id_device} custom_epoch: {custom_epoch}")

        seconds, milliseconds = divmod(custom_epoch, 1000)
        custom_epoch = datetime.datetime.utcfromtimestamp(seconds).replace(tzinfo=datetime.timezone.utc)
        custom_epoch = custom_epoch.replace(microsecond=milliseconds * 1000)

        print(f"Handshake | custom epoch {custom_epoch.timestamp()}")
        custom_epoch_diff = datetime.datetime.utcnow().timestamp() - custom_epoch.timestamp()

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
        print("Starting the handshake")
        self.client.char_write(self.context.characteristic_uuid, first_msg, wait_for_response=False)
        self.set_log()
        print("Handshake completed")



class ReadData:
    def __init__(self, context, client):
        self.client = client
        self.context = context

    def run(self):
        data = self.client.char_read(self.context.characteristic_uuid)
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
            print("Device is connecting")
            adapter = pygatt.GATTToolBackend()
            adapter.start()
            time.sleep(2)  # Give the adapter some time to start
            try:
                connected_device = adapter.connect(self.context.device_mac, address_type=pygatt.BLEAddressType.public
                                                   , timeout=3, auto_reconnect=True)
                print("Connected!")
                return connected_device
            except Exception as e:
                print(f"Failed to connect to device: {e}")
            print("Device not found")
            print("Trying again...")
            raise TimeoutError("Failed to connect")
        
        except Exception as e:
            print(f"Exception in CONNECTING, trying again: {self.context.tries} \n Error was:\n \t{e}")
            self.context.tries += 1
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
        self.ble_handshake = BleHandshake(context, client)
        self.read_data = ReadData(context, client)
        print("Device is connected")
        print("Setting notification callback (start_notify)")

        self.notify_thread = threading.Thread(target=client.subscribe, args=(context.characteristic_uuid,),
                                      kwargs={"callback": self.notify_callback, "wait_for_response": False})
        self.notify_thread.start()
        while True:
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
    def __init__(self, device_name, characteristic_uuid,device_mac, transport_layer):
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
    def __init__(self, device_name, characteristic_uuid,device_mac, transport_layer):
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
        if value == expected_data:
            print("Notification received - Checking data")
            self.data_available = True

    def transition_to(self, state: DeviceState, client=None):
        return None

    def _run(self):

        self.connecting = Connecting(self)

        while True:
            try:
                client = self.connecting.run()
                if client is None:
                    continue
                self.client = client
                time.sleep(0.2)
                print("Setting notification callback (start_notify)")
                # self.client.subscribe(self.characteristic_uuid, callback=self.notify_callback)
                # run this on thread
                self.notify_thread = threading.Thread(target=client.subscribe, args=(self.characteristic_uuid,),
                                      kwargs={"callback": self.notify_callback, "wait_for_response": False})
                self.notify_thread.start()
                self.ble_handshake = BleHandshake(self, client)
                self.read_data = ReadData(self, client)
                print("Device is connected")
                # self.ble_handshake.run()
                print("Setting notification callback (start_notify)")
                while True:
                    time.sleep(0.1)
                    if self.data_available:
                        self.ble_handshake.run()
                        self.read_data.run()
                        self.data_available = False
                        if self.transport_layer == "D":
                            time.sleep(os.environ.get("SESP_BLE_DISC_TIMEOUT_SEC", 4))
                            self.client.disconnect()
                            return
            except Exception as e:
                print(e)
                print("Error while connecting")
                time.sleep(0.2)
                continue

    def run(self):
        self._run()



class BleManager:

    def __init__(self, device_name, characteristic_uuid, device_mac,transport_layer):
        self.state = DisconnectedState()
        self.device_name = device_name
        self.characteristic_uuid = characteristic_uuid
        self.device_mac = device_mac
        self.transport_layer = transport_layer
        self.use_states = os.environ.get("BLE_USE_STATES", "True").upper() == "TRUE"
        print(f"Starting BLE manager using mode: -->  {self.transport_layer} and using states: {self.use_states}")

        if (self.use_states):
            self.manager = StatefulBleManager(
                device_name, characteristic_uuid,device_mac, transport_layer)
        else:
            self.manager = StatelessBleManager(
                device_name, characteristic_uuid,device_mac, transport_layer)

    def run(self):
        self.manager.run()
