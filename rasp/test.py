import pygatt
from time import sleep

DEVICE_ADDRESS = 'AC:67:B2:38:41:D2'
CHARACTERISTIC_UUID = "0000ff01-0000-1000-8000-00805F9B34FB"

STATE_DISCONNECTED = 0
STATE_CONNECTING = 1
STATE_CONNECTED = 2

adapter = pygatt.GATTToolBackend()
state = STATE_DISCONNECTED

def handle_connection_event(event):
    global state
    if event == 'disconnected':
        print('The device disconnected.')
        state = STATE_DISCONNECTED
    elif event == 'connected':
        print('The device connected.')
        state = STATE_CONNECTED

def connect():
    global state
    state = STATE_CONNECTING
    adapter.start()  # Start the adapter before connecting
    print('Adapter started.')
    try:
        print('Attempting to connect to the device...')
        device = adapter.connect(DEVICE_ADDRESS, address_type=pygatt.BLEAddressType.public, timeout=10, auto_reconnect=True)
        # device.subscribe(CHARACTERISTIC_UUID, callback=handle_notification)
        print('Device connected!')
    except Exception as e:
        print('Connection failed:', e)

def disconnect():
    global state
    state = STATE_DISCONNECTED
    adapter.stop()
    print('Disconnected from the device.')

def handle_notification(handle, value):
    print('Notification received:', value.hex())

while True:
    if state == STATE_DISCONNECTED:
        print('Current state: Disconnected.')
        connect()
    elif state == STATE_CONNECTING:
        print('Current state: Connecting...')
        connect()
        sleep(1)
    elif state == STATE_CONNECTED:
        print('Current state: Connected.')
        sleep(1)
