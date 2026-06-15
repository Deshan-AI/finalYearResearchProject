# find_fitpro.py
import asyncio
from bleak import BleakScanner

async def scan_fitpro():
    print("="*50)
    print(" FITPRO WATCH SCANNER")
    print("="*50)
    print("\n details:")
    print("   1. FitPro watch ON")
    print("   2. confirm watch is connected to phone's Bluetooth (FitPro app can show this)")
    print("   3. run this script to find watch's MAC address for direct BLE connection")
    print("\n🔍 Scanning... (10 seconds)")
    print("-"*50)
    
    devices = await BleakScanner.discover(timeout=10)
    
    found_devices = []
    for device in devices:
        if device.name:
            name_lower = device.name.lower()
            # FitPro watches common names
            if any(keyword in name_lower for keyword in ['fitpro', 'id107', 'id115', 'id205', 'w17', 'w19']):
                found_devices.append({
                    'name': device.name,
                    'address': device.address,
                    'rssi': device.rssi
                })
                print(f"\n✅ FOUND!")
                print(f"   Name: {device.name}")
                print(f"   MAC Address: {device.address}")
                print(f"   Signal: {device.rssi} dBm")
    
    if not found_devices:
        print("\n No FitPro watch found!")
        print("\n Troubleshooting:")
        print("   1. FitPro app  watch connect")
        print("   2. Make sure watch is ON and within range")
        print("   3. Check Bluetooth settings on phone to confirm watch is connected")
        print("   4. Try running this script again")
    
    return found_devices

if __name__ == "__main__":
    asyncio.run(scan_fitpro())


    #python find_fitpro.py