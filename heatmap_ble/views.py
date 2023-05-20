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



import numpy as np
import pandas as pd

def create_heatmap(ble_devices):
    # Create a DataFrame from ble_devices
    df = pd.DataFrame(ble_devices)

    # Convert the timestamp column to datetime type
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Create a pivot table with addresses as rows, timestamps as columns, and RSSI values as values
    pivot_table = df.pivot_table(index='address', columns='timestamp', values='rssi', fill_value=0)

    # Convert the pivot table to a numpy array for plotting
    heatmap_data = pivot_table.values

    # Set up the heatmap plot
    fig, ax = plt.subplots()
    cmap = plt.cm.get_cmap('hot')

    # Plot the heatmap
    im = ax.imshow(heatmap_data, cmap=cmap)

    # Configure the colorbar
    cbar = plt.colorbar(im)
    cbar.set_label('RSSI')

    # Set labels and title
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Address')
    ax.set_title('RSSI Heatmap')

    # Convert the plot to an image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8').replace('\n', '')
    buf.close()

    return image_base64


async def ble_devices(request):
    ble_devices = await scan_ble_devices()
    heatmap_image = create_heatmap(ble_devices)
    return render(request, 'heatmap.html', {'heatmap_image': heatmap_image})

