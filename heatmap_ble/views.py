from django.shortcuts import render
from django.http import HttpResponse
import bluetooth
import asyncio
from django.shortcuts import render
from bleak import BleakScanner
import datetime
import matplotlib.pyplot as plt
import io
import urllib, base64
import json
import time

def index(request):
    return HttpResponse("Hello, World!")

def calculate_distance(rssi):
    tx_power = -59  # the signal strength in dBm at 1 meter distance
    n = 2.0  # the path-loss exponent (typically between 2.0 and 4.0)
    distance = 10 ** ((tx_power - rssi) / (10 * n))
    return distance

# Bleak BLE Device Information Scan
async def scan_ble_devices():
    ble_devices = []
    for loop_num in range(1, 6):  # Run the loop five times
        devices = await BleakScanner.discover()
        loop_ble_devices = []
        for device in devices:
            ble_device = {
                'address': device.address,
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'rssi': device.rssi,
                'loop_number': loop_num
            }
            loop_ble_devices.append(ble_device)
            ble_devices.append(ble_device)

        # Save loop_ble_devices to a JSON file
        filename = f'ble_devices_loop_{loop_num}.json'
        with open(filename, 'w') as file:
            json.dump(loop_ble_devices, file)

        time.sleep(5)  # Wait for 5 seconds before the next loop

    # Save all ble_devices to a JSON file
    with open('ble_devices.json', 'w') as file:
        json.dump(ble_devices, file)

    return ble_devices



# Function Sent in BLE Device
async def ble_devices(request):
    ble_devices = await scan_ble_devices()
    return render(request, 'heatmap_device.html', {'ble_devices': ble_devices})

