import asyncio
import datetime
import os
import threading
import time
from abc import ABC, abstractmethod

import pygatt
from bleak import BleakClient

from utils.general import diff_to_now_utc_timestamp, now_utc_timestamp
from utils.models import DatabaseManager, Logs
from utils.packet_parser import PacketParser
from utils.prints import console

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

    def char_write(self, data):
        raise NotImplementedError

    def char_read():
        raise NotImplementedError

    def subscribe(self, notify_function):
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
                auto_reconnect=True,
            )
            self.connected = True

    def disconnect(self):
        if self.client is not None:
            self.client.disconnect()
            # unsuscribe
            self.notify_thread.join()
            self.client = None
            self.connected = False

    def char_read(self):
        return self.client.char_read(self.characteristic_uuid, timeout=3)

    def char_write(self, data):
        self.client.char_write(self.characteristic_uuid, data, wait_for_response=False)

    def subscribe(self, notify_function):
        if self.notify_thread is None:
            self.notify_thread = threading.Thread(
                target=self.client.subscribe,
                args=(self.characteristic_uuid,),
                kwargs={"callback": notify_function, "wait_for_response": False},
            )
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
        console.print("Connected!", style="info")

    def disconnect(self):
        console.print("Disconnecting...", style="danger")
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
        data = self.context.ble_core.char_read()
        data_headers, data_body = data[:12], data[12:]

        parser = PacketParser()
        headers = parser.parse_headers(data_headers)
        id_device, _, transport_layer, id_protocol, _ = headers
        body = parser.parse_body(data_body, id_protocol)

        dif = diff_to_now_utc_timestamp(body[2])
        now = now_utc_timestamp()

        if self.context.init_timestamp is not None:
            time_to_connect = now - self.context.init_timestamp
            tries = self.context.tries

            ble_state_machine = "not using states"
            if os.environ.get("BLE_USE_STATES", "True").upper() == "TRUE":
                ble_state_machine = "using states"

            log = Logs.create(
                timestamp=now,
                id_device=id_device,
                custom_epoch=dif,
                time_to_connect=time_to_connect,
                id_protocol=id_protocol,
                transport_layer=transport_layer,
                tries=tries,
                ble_state_machine=ble_state_machine,
            )
            log.save()
            console.print("Log saved!", style="info")
            self.context.init_timestamp = None

    def run(self):
        console.print("Sending first message...", style="info")

        parser = PacketParser()
        conf = DatabaseManager.get_default_config()
        self.context.ble_core.char_write(parser.pack_config(conf))
        self.set_log()
        console.print("Handshake done!", style="info")


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


class Connecting:
    def __init__(self, context):
        self.context = context

    def run(self):
        self.context.state = self
        console.print(f"Connecting to device, attempt #[{self.context.tries}] ...",style = "warning")

        try:
            self.context.ble_core.connect()
            return True
        except Exception as e:
            console.print(f"Failed to connect to device: {e}", style="danger")

        console.print(f"Trying again: {self.context.tries}", style="warning")
        self.context.tries += 1
        return False

      

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
        console.print("Device is disconnected", style="warning")
        context.ble_core.disconnect()


class ConnectingState(DeviceState):
    def handle(self, context):
        return Connecting(context).run()


class ConnectedState(DeviceState):
    def __init__(self):
        self.data_available = False
        self.notify_thread = None

    def notify_callback(self, handle, value):
        expected_data = b"CHK_DATA"
        if expected_data in value:
            console.print("\nNotification received - Checking data", style="note")
            self.data_available = True

    def handle(self, context, client):
        context.state = self
        self.ble_handshake = BleHandshake(context)
        self.read_data = ReadData(context)

        context.ble_core.subscribe(self.notify_callback)
        while True:
            while True:
                with console.status("[dim medium_orchid1]Waiting for data...", spinner="dots"):
                    context.ble_core.subscribe(self.notify_callback)
                    time.sleep(2)
                if self.data_available:
                    break

            if self.data_available:
                self.ble_handshake.run()
                self.read_data.run()
                self.data_available = False
                if context.transport_layer == "D":
                    context.ble_core.disconnect()
                    time.sleep(int(os.environ.get("SESP_BLE_DISC_TIMEOUT_SEC", 4)))
                    return


# *****************************************************************************
# *                                                                           *
# *  ***********************    BLE Manager    ***************************  *
# *                                                                           *
# *  *************** <><><><><><><><><><><><><><><><><><><><> *************  *
# *                                                                           *
# *****************************************************************************


class StatefulBleManager:
    def __init__(
        self, device_name, characteristic_uuid, device_mac, transport_layer, ble_core
    ):
        self.ble_core = ble_core
        self.state = DisconnectedState()
        self.device_name = device_name
        self.characteristic_uuid = characteristic_uuid
        self.transport_layer = transport_layer
        self.device_mac = device_mac
        self.tries = 1
        self.init_timestamp = datetime.datetime.utcnow()
        self.init_timestamp = self.init_timestamp.replace(
            tzinfo=datetime.timezone.utc
        ).timestamp()

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
        if client:
            self.transition_to(ConnectedState(), client)
            self.transition_to(DisconnectedState())
        else:
            self.transition_to(ConnectingState())


class StatelessBleManager:
    def __init__(
        self, device_name, characteristic_uuid, device_mac, transport_layer, ble_core
    ):
        self.ble_core = ble_core
        self.state = DisconnectedState()
        self.device_name = device_name
        self.characteristic_uuid = characteristic_uuid
        self.transport_layer = transport_layer
        self.device_mac = device_mac
        self.data_available = True
        self.tries = 1
        self.init_timestamp = datetime.datetime.utcnow()
        self.init_timestamp = self.init_timestamp.replace(
            tzinfo=datetime.timezone.utc
        ).timestamp()
        self.notify_thread = None

    def notify_callback(self, handle, value):
        expected_data = b"CHK_DATA"
        if expected_data in value:
            console.print("\nNotification received - Checking data", style="note")
            self.data_available = True

    def transition_to(self, state: DeviceState, client=None):
        return None

    def _run(self):
        while True:
            try:
                Connecting(self).run()
                if not self.ble_core.connected:
                    continue
                self.ble_core.subscribe(self.notify_callback)

                self.ble_handshake = BleHandshake(self)
                self.read_data = ReadData(self)

                while True:
                    with console.status("[dim medium_orchid1]Waiting for data...", spinner="dots"):
                        self.ble_core.subscribe(self.notify_callback)
                        time.sleep(2)
                    
                        if self.data_available:
                            break
                    
                if self.data_available:
                    self.ble_handshake.run()
                    self.read_data.run()
                    self.data_available = False
                    if self.transport_layer == "D":
                        self.ble_core.disconnect()
                        time.sleep(int(os.environ.get("SESP_BLE_DISC_TIMEOUT_SEC", 4)))
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
    def __init__(self, device_name, characteristic_uuid, device_mac, transport_layer):
        self.state = DisconnectedState()
        self.device_name = device_name
        self.characteristic_uuid = characteristic_uuid
        self.device_mac = device_mac
        ble_core_var = os.environ.get("BLE_CORE", "pygatt").upper()
        if ble_core_var == "BLEAK":
            self.ble_core = BleakCore(self.device_mac, self.characteristic_uuid)
        else:
            self.ble_core = PygattCore(self.device_mac, self.characteristic_uuid)
        self.transport_layer = transport_layer
        self.use_states = os.environ.get("BLE_USE_STATES", "True").upper() == "TRUE"
        mode_verbose = "BLE continious" if self.transport_layer == "C" else "BLE discontinious"
        console.print(
            f"Starting BLE manager:\n\t- using mode: {mode_verbose}\n\t-\
              using states: {self.use_states}",
            style="setup",
        )

        if self.use_states:
            self.manager = StatefulBleManager(
                device_name, characteristic_uuid, device_mac, transport_layer, self.ble_core
            )
        else:
            self.manager = StatelessBleManager(
                device_name, characteristic_uuid, device_mac, transport_layer, self.ble_core
            )

    def run(self):
        self.manager.run()
