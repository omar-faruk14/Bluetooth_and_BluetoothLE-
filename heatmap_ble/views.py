from django.shortcuts import render
from django.http import HttpResponse
import bluetooth
import asyncio
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
import os
import glob


heatmap_data = []


def index(request):
    return HttpResponse("Hello, World!")


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
    sns.heatmap(pivot_table, cmap=cmap, annot=True, fmt=".0f", cbar=True, linewidths=2,vmax=0,vmin=-100)
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
    
    heatmap = {
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'image': image_base64
    }
    return heatmap


async def add_heatmap(request):
    ble_devices = await scan_ble_devices()
    if ble_devices:
        heatmap = create_heatmap(ble_devices)
        if heatmap:
            heatmap_data.append(heatmap)
            save_heatmap_data(heatmap_data)  # Save the heatmap data to a file
            return HttpResponse("Heatmap added successfully.")
        else:
            return HttpResponse("Invalid data format.")
    else:
        return HttpResponse("Invalid request method.")


MAX_FILES = 15 


def save_heatmap_data(heatmap_data):
    if not os.path.exists('Files'):
        os.makedirs('Files')
    existing_files = glob.glob('Files/*.json')
    num_existing_files = len(existing_files)
    if num_existing_files >= MAX_FILES:
        num_files_to_remove = num_existing_files - MAX_FILES + 1
        sorted_files = sorted(existing_files, key=os.path.getmtime)
        files_to_remove = sorted_files[:num_files_to_remove]
        for file_to_remove in files_to_remove:
            os.remove(file_to_remove)

    # Save the current heatmap data as a new file
    filename = f'Files/heatmap_data_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.json'
    with open(filename, 'w') as file:
        json.dump(heatmap_data, file)


def load_heatmap_data():
    if not os.path.exists('Files'):
        return []
    existing_files = glob.glob('Files/*.json')
    if not existing_files:
        return []
    latest_file = max(existing_files, key=os.path.getctime)
    with open(latest_file, 'r') as file:
        heatmap_data = json.load(file)
    return heatmap_data


def display_heatmaps(request):
    heatmap_data = load_heatmap_data()
    heatmap_data_with_timestamp = []
    for heatmap in heatmap_data:
        timestamp = heatmap['timestamp']
        image = heatmap['image']
        heatmap_with_timestamp = {'timestamp': timestamp, 'image': image}
        heatmap_data_with_timestamp.append(heatmap_with_timestamp)

    return render(request, 'display_heatmaps.html', {'heatmap_data': heatmap_data_with_timestamp})


async def scan_ble_devices():
    loop_count=5
    sleep_duration=1
    ble_devices = []
    for loop_num in range(1, loop_count + 1):  
        devices = await BleakScanner.discover()
        for device in devices:
            ble_device = {
                'address': device.address,
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'rssi': device.rssi,
                'loop_number': loop_num
            }
            ble_devices.append(ble_device)
        time.sleep(sleep_duration)  
    
    with open('ble_devices.json', 'w') as file:
        json.dump(ble_devices, file)
    return ble_devices


def settings(request):
    return render(request, 'settings.html')

def remove_heatmap_files(request):
    existing_files = glob.glob('Files/*.json')
    for file in existing_files:
        os.remove(file)
    heatmap_data.clear()  # Clear the heatmap_data list
    return render(request, 'display_heatmaps.html')




#========================For Manual Settings=============================================================

def manual_settings(request):
    return render(request, 'manual_settings.html')

async def scan_ble_devices2(loop_count, sleep_duration):
    ble_devices = []
    for loop_num in range(1, loop_count + 1):  
        devices = await BleakScanner.discover()
        for device in devices:
            ble_device = {
                'address': device.address,
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'rssi': device.rssi,
                'loop_number': loop_num
            }
            ble_devices.append(ble_device)
        time.sleep(sleep_duration)
    with open('ble_devices.json', 'w') as file:
        json.dump(ble_devices, file)
    return ble_devices


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
    sns.heatmap(pivot_table, cmap=cmap, annot=True, fmt=".0f", cbar=True,linewidths=2,vmax=0,vmin=-100)
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

async def ble_devices_finder(request):
    if request.method == 'POST':
        loop_count = int(request.POST['loop_count'])
        sleep_duration = int(request.POST['sleep_duration'])
        ble_devices = await scan_ble_devices2(loop_count, sleep_duration)
        heatmap_image = create_heatmap2(ble_devices)

    else:
        return HttpResponse("Invalid request method.")

    return render(request, 'heatmap.html', {'heatmap_image': heatmap_image,'ble_devices':ble_devices})

def heatmap_all(request):
    return render(request, 'heatmap_all.html')