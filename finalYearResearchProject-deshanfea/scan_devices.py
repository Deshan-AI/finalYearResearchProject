# scan_devices.py
from bleak import BleakScanner
import asyncio

async def scan():
    print("🔍 Scanning for FitPro devices...")
    devices = await BleakScanner.discover()
    
    for d in devices:
        if "FitPro" in d.name or "ID107" in d.name:
            print(f"✅ Found: {d.name} - {d.address}")
            print(f"   RSSI: {d.rssi}")
            
    return devices

# Run
asyncio.run(scan())