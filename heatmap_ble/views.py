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
import seaborn as sns
import numpy as np
import pandas as pd


heatmap_data = []
def index(request):
    return HttpResponse("Hello, World!")

def calculate_distance(rssi):
    tx_power = -59  # the signal strength in dBm at 1 meter distance
    n = 2.0  # the path-loss exponent (typically between 2.0 and 4.0)
    distance = 10 ** ((tx_power - rssi) / (10 * n))
    return distance

def create_heatmap(ble_devices):
    if not ble_devices:
        return None
    df = pd.DataFrame(ble_devices)
    if 'timestamp' not in df.columns:
        return None
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    pivot_table = df.pivot_table(index='address', columns='timestamp', values='rssi', fill_value=0)
    plt.figure(figsize=(10, 8))
    cmap = sns.color_palette("viridis", as_cmap=True)
    sns.heatmap(pivot_table, cmap=cmap, annot=True, fmt=".0f", cbar=True, linewidths=2)
    plt.xlabel('Timestamp')
    plt.ylabel('Address')
    plt.title('RSSI Heatmap')
    xticks_pos = np.arange(len(pivot_table.columns)) + 0.5
    xticks_labels = pivot_table.columns.strftime("%H:%M:%S")
    plt.xticks(xticks_pos, xticks_labels, rotation=45, ha='right')
    yticks_pos = np.arange(len(pivot_table.index)) + 0.5
    yticks_labels = pivot_table.index
    plt.yticks(yticks_pos, yticks_labels)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8').replace('\n', '')
    buf.close()
    return image_base64


def create_heatmap2(ble_devices):
    if not ble_devices:
        return None
    df = pd.DataFrame(ble_devices)
    if 'timestamp' not in df.columns:
        return None
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    pivot_table = df.pivot_table(index='address', columns='timestamp', values='rssi', fill_value=0)
    plt.figure(figsize=(10, 8))
    cmap = sns.color_palette("viridis", as_cmap=True)
    sns.heatmap(pivot_table, cmap=cmap, annot=True, fmt=".0f", cbar=True, linewidths=2)
    plt.xlabel('Timestamp')
    plt.ylabel('Address')
    plt.title('RSSI Heatmap')
    xticks_pos = np.arange(len(pivot_table.columns)) + 0.5
    xticks_labels = pivot_table.columns.strftime("%H:%M:%S")
    plt.xticks(xticks_pos, xticks_labels, rotation=45, ha='right')
    yticks_pos = np.arange(len(pivot_table.index)) + 0.5
    yticks_labels = pivot_table.index
    plt.yticks(yticks_pos, yticks_labels)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8').replace('\n', '')
    buf.close()
    return image_base64


async def add_heatmap(request):
    ble_devices = await scan_ble_devices()
    if ble_devices:
        ble_devices = ble_devices
        heatmap_image = create_heatmap(ble_devices)
        if heatmap_image:
            heatmap_data.append(heatmap_image)
            return HttpResponse("Heatmap added successfully.")
        else:
            return HttpResponse("Invalid data format.")
    else:
        return HttpResponse("Invalid request method.")

def display_heatmaps(request):
    return render(request, 'display_heatmaps.html', {'heatmap_data': heatmap_data})

async def scan_ble_devices():
    loop_count=5
    sleep_duration=1
    ble_devices = []
    for loop_num in range(1, loop_count + 1):  
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
        filename = f'ble_devices_loop_{loop_num}.json'
        with open(filename, 'w') as file:
            json.dump(loop_ble_devices, file)
        time.sleep(sleep_duration)  
    
    with open('ble_devices.json', 'w') as file:
        json.dump(ble_devices, file)
    return ble_devices


def settings(request):
    return render(request, 'settings.html')

async def ble_devices_finder(request):
    ble_devices = await scan_ble_devices()
    heatmap_image = create_heatmap(ble_devices)
    return render(request, 'heatmap.html', {'heatmap_image': heatmap_image,'ble_devices':ble_devices})

