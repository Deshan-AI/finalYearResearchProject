# src/data_collection/fitpro_ble.py
"""
FitPro Smart Watch - Bluetooth Low Energy (BLE) Connection
this file read data connect watch
"""

import asyncio
from bleak import BleakClient, BleakScanner
from datetime import datetime
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FitProBLE:
    """
    FitPro Watch Bluetooth Connection Class
    """
    
    # ============= Bluetooth Service UUIDs =============
    # These are the standard services for the FitPro watch
    HEART_RATE_SERVICE = "0000180d-0000-1000-8000-00805f9b34fb"
    HEART_RATE_CHARACTERISTIC = "00002a37-0000-1000-8000-00805f9b34fb"
    
    BATTERY_SERVICE = "0000180f-0000-1000-8000-00805f9b34fb"
    BATTERY_CHARACTERISTIC = "00002a19-0000-1000-8000-00805f9b34fb"
    
    DEVICE_INFO_SERVICE = "0000180a-0000-1000-8000-00805f9b34fb"
    
    # ============= FitPro Custom UUIDs =============
    
    FITPRO_STEP_CHAR = "0000ff06-0000-1000-8000-00805f9b34fb"
    FITPRO_SLEEP_CHAR = "0000ff07-0000-1000-8000-00805f9b34fb"
    FITPRO_ACTIVITY_CHAR = "0000ff08-0000-1000-8000-00805f9b34fb"
    
    def __init__(self, watch_address):
        """
        Initialize FitPro connection
        
        Parameters:
        watch_address: FitPro watch MAC address (e.g., "AA:BB:CC:DD:EE:FF")
        """
        self.address = watch_address
        self.client = None
        self.is_connected = False
        self.device_name = None
        
        # Data storage
        self.current_heart_rate = None
        self.current_steps = None
        self.current_battery = None
        self.last_data_time = None
        
        logger.info(f"🔧 FitPro BLE initialized for address: {self.address}")
    
    async def connect(self):
        """
        Connect to FitPro watch via Bluetooth
        """
        try:
            logger.info(f"🔄 Connecting to FitPro at {self.address}...")
            
            # Create BLE client
            self.client = BleakClient(self.address)
            
            # Connect to watch
            await self.client.connect()
            self.is_connected = True
            
            # Get device name
            self.device_name = await self.client.get_device_name()
            logger.info(f"✅ Successfully connected to {self.device_name}")
            
            # Get battery level
            await self.get_battery_level()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """
        Watch disconnect
        """
        if self.client and self.is_connected:
            await self.client.disconnect()
            self.is_connected = False
            logger.info("🔌 Disconnected from FitPro watch")
    
    async def get_heart_rate(self):
        """
        Heart Rate read
        Returns: BPM (beats per minute)
        """
        if not self.is_connected:
            logger.warning("Not connected to watch")
            return None
        
        try:
            # Read heart rate characteristic
            data = await self.client.read_gatt_char(self.HEART_RATE_CHARACTERISTIC)
            
            # Heart rate data format:
            # byte 0: flags
            # byte 1: heart rate value (BPM)
            if data and len(data) > 1:
                heart_rate = int(data[1])
                self.current_heart_rate = heart_rate
                self.last_data_time = datetime.now()
                logger.debug(f"❤️ Heart Rate: {heart_rate} BPM")
                return heart_rate
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to read heart rate: {e}")
            return None
    
    async def get_steps(self):
        """
        Step count
        Returns: Number of steps
        """
        if not self.is_connected:
            return None
        
        try:
            # Try custom FitPro characteristic first
            data = await self.client.read_gatt_char(self.FITPRO_STEP_CHAR)
            steps = int.from_bytes(data, byteorder='little')
            self.current_steps = steps
            logger.debug(f"👣 Steps: {steps}")
            return steps
            
        except Exception as e:
            # If custom characteristic fails, try alternative method
            logger.debug(f"Alternative step reading: {e}")
            return None
    
    # async def get_battery_level(self):
    #     """
    #     Battery level
    #     Returns: Battery percentage (0-100)
    #     """
    #     if not self.is_connected:
    #         return None
        
    #     try:
    #         data = await self.client.read_gatt_char(self.BATTERY_CHARACTERISTIC)
    #         battery = int.from_bytes(data, byteorder='little')
    #         self.current_battery = battery
    #         logger.debug(f"🔋 Battery: {battery}%")
    #         return battery
            
    #     except Exception as e:
    #         logger.error(f"Failed to read battery: {e}")
    #         return None
    
    async def start_notifications(self, callback):
        """
        Continuous heart rate update
        (Real-time monitoring)
        
        Parameters:
        callback: Function that gets called when new HR data arrives
        """
        if not self.is_connected:
            await self.connect()
        
        def notification_handler(sender, data):
            """Handle incoming notifications"""
            if data and len(data) > 1:
                heart_rate = int(data[1])
                callback(heart_rate, datetime.now())
        
        try:
            await self.client.start_notify(
                self.HEART_RATE_CHARACTERISTIC,
                notification_handler
            )
            logger.info("📡 Heart rate notifications started")
            return True
        except Exception as e:
            logger.error(f"Failed to start notifications: {e}")
            return False
    
    async def stop_notifications(self):
        """
        Stop continuous notifications
        """
        try:
            await self.client.stop_notify(self.HEART_RATE_CHARACTERISTIC)
            logger.info("📡 Notifications stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop notifications: {e}")
            return False
    
    async def get_all_data(self):
        """
        
        Returns: Dictionary with all data
        """
        heart_rate = await self.get_heart_rate()
        steps = await self.get_steps()
        battery = await self.get_battery_level()
        
        # Calculate HRV from heart rate (approximation)
        hrv = self._calculate_hrv(heart_rate)
        
        return {
            'timestamp': datetime.now(),
            'heart_rate': heart_rate,
            'hrv_value': hrv,
            'step_count': steps,
            'battery': battery,
            'device_name': self.device_name,
            'connection_status': self.is_connected
        }
    
    def _calculate_hrv(self, heart_rate):
        """
        using Heart Rate count HRV (approximation)
        
        HRV (Heart Rate Variability).
        Higher HRV = Better health, Lower HRV = Stress
        """
        if not heart_rate:
            return 50  # Default value
        
        # Rough estimation: Lower heart rate usually means higher HRV
        if heart_rate < 65:
            return 65
        elif heart_rate < 75:
            return 50
        elif heart_rate < 85:
            return 40
        else:
            return 35