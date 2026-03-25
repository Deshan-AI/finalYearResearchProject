# find_watch.py
from bleak import BleakScanner
import asyncio

async def main():
    print("🔍 Scanning for FitPro watches...")
    devices = await BleakScanner.discover()
    
    for d in devices:
        if d.name and ("FitPro" in d.name or "ID107" in d.name):
            print(f"✅ FOUND: {d.name}")
            print(f"   MAC: {d.address}")
            print(f"   RSSI: {d.rssi}")
            print("-" * 30)

asyncio.run(main())