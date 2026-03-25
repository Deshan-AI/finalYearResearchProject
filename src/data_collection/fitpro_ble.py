# fitpro_ble.py
import asyncio
from bleak import BleakClient

class FitProBLE:
    """Direct BLE connection to FitPro"""
    
    # FitPro Service/Characteristic UUIDs
    HR_SERVICE = "0000180d-0000-1000-8000-00805f9b34fb"
    HR_CHAR = "00002a37-0000-1000-8000-00805f9b34fb"
    
    BATTERY_SERVICE = "0000180f-0000-1000-8000-00805f9b34fb"
    BATTERY_CHAR = "00002a19-0000-1000-8000-00805f9b34fb"
    
    DEVICE_INFO = "0000180a-0000-1000-8000-00805f9b34fb"
    
    # Custom FitPro UUIDs (reverse engineered)
    STEP_CHAR = "0000ff06-0000-1000-8000-00805f9b34fb"
    SLEEP_CHAR = "0000ff07-0000-1000-8000-00805f9b34fb"
    
    def __init__(self, address):
        self.address = address
        self.client = None
        
    async def connect(self):
        """Connect to watch"""
        print(f"🔄 Connecting to {self.address}...")
        self.client = BleakClient(self.address)
        await self.client.connect()
        print(f"✅ Connected!")
        
    async def get_heart_rate(self):
        """Get real-time heart rate"""
        if not self.client:
            await self.connect()
            
        hr_data = await self.client.read_gatt_char(self.HR_CHAR)
        hr_value = int.from_bytes(hr_data, byteorder='little')
        return hr_value
    
    async def get_steps(self):
        """Get step count"""
        if not self.client:
            await self.connect()
            
        step_data = await self.client.read_gatt_char(self.STEP_CHAR)
        steps = int.from_bytes(step_data, byteorder='little')
        return steps
    
    async def get_battery(self):
        """Get battery level"""
        if not self.client:
            await self.connect()
            
        battery = await self.client.read_gatt_char(self.BATTERY_CHAR)
        return int.from_bytes(battery, byteorder='little')
    
    async def start_notifications(self, callback):
        """Get continuous heart rate updates"""
        await self.client.start_notify(
            self.HR_CHAR, 
            callback
        )
        
    async def disconnect(self):
        """Disconnect from watch"""
        if self.client:
            await self.client.disconnect()
            print("🔌 Disconnected")

# Usage
async def main():
    fitpro = FitProBLE("XX:XX:XX:XX:XX")  # Your watch's MAC
    
    # Connect and get data
    hr = await fitpro.get_heart_rate()
    steps = await fitpro.get_steps()
    battery = await fitpro.get_battery()
    
    print(f"❤️ Heart Rate: {hr} bpm")
    print(f"👣 Steps: {steps}")
    print(f"🔋 Battery: {battery}%")
    
    await fitpro.disconnect()

# Run
asyncio.run(main())