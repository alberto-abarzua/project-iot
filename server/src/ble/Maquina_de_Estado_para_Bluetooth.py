import asyncio
from bleak import BleakClient, BleakScanner
import struct

YOUR_DEVICE_NAME = "ESP_GATTS_DEMO"
YOUR_CHARACTERISTIC_UUID = "0000ff01-0000-1000-8000-00805F9B34FB"

async def run():
    scanner = BleakScanner()
    devices = await scanner.discover()
    print("Discovered devices:")
    [print(device) for device in devices]
    for device in devices:
        if device.name == YOUR_DEVICE_NAME:
            print("Found device, connecting...")
            print(f"Device found: {device}")
            client = BleakClient(device)
            await client.connect()

            # After successful connection, read the characteristic value
            raw_data = await client.read_gatt_char(YOUR_CHARACTERISTIC_UUID)
            print("this is the first raw data",raw_data)
            # then write the vlaue "Hello World" back to the device
            await client.write_gatt_char(YOUR_CHARACTERISTIC_UUID, b"vlaue!")
            # and read the value again to verify
            
            raw_data = await client.read_gatt_char(YOUR_CHARACTERISTIC_UUID)

            # value = struct.unpack("s", bytes(raw_data))[0]
            value = raw_data
            print(f"Characteristic Value: {value}")

            # Now store this value in your database

            await client.disconnect()

loop = asyncio.get_event_loop()
loop.run_until_complete(run())