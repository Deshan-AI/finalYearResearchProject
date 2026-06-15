# src/data_collection/fitpro_collector.py
"""
FitPro Data Collector - save data to database
"""

import asyncio
import threading
from datetime import datetime
from src.database.database_setup import get_session
from src.database.models import BioSignalData, Student
from .fitpro_ble import FitProBLE
import logging

logger = logging.getLogger(__name__)

class FitProCollector:
    """
    FitPro data collector - get data from watch and save to database
    """
    
    def __init__(self, student_id, watch_address):
        """
        Initialize collector
        
        Parameters:
        student_id: Student ID (e.g., STU001)
        watch_address: FitPro watch MAC address
        """
        self.student_id = student_id
        self.watch_address = watch_address
        self.ble = FitProBLE(watch_address)
        self.session = get_session()
        self.is_running = False
        self.collector_thread = None
        
        # Statistics
        self.data_points_collected = 0
        self.last_heart_rate = None
        self.last_steps = None
        
        logger.info(f"📊 FitProCollector initialized for student: {student_id}")
    
    def start_collecting(self, interval_seconds=60):
        """
        Start data collection
        
        Parameters:
        interval_seconds: How often to collect data (seconds)
        """
        if self.is_running:
            logger.warning("Collector already running")
            return
        
        self.is_running = True
        self.collector_thread = threading.Thread(
            target=self._collection_loop,
            args=(interval_seconds,)
        )
        self.collector_thread.daemon = True
        self.collector_thread.start()
        
        logger.info(f"✅ Data collection started (interval: {interval_seconds}s)")
    
    def stop_collecting(self):
        """
        Stop data collection
        """
        self.is_running = False
        if self.collector_thread:
            self.collector_thread.join(timeout=5)
        logger.info("🛑 Data collection stopped")
    
    def _collection_loop(self, interval_seconds):
        """
        Main collection loop (runs in background thread)
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._async_collection_loop(interval_seconds))
    
    async def _async_collection_loop(self, interval_seconds):
        """
        Asynchronous collection loop
        """
        try:
            # Connect to watch
            connected = await self.ble.connect()
            if not connected:
                logger.error(f"Could not connect to FitPro for {self.student_id}")
                self.is_running = False
                return
            
            while self.is_running:
                # Get all data
                data = await self.ble.get_all_data()
                
                if data['heart_rate'] or data['step_count']:
                    # Save to database
                    self._save_to_database(data)
                    self.data_points_collected += 1
                    
                    # Update stats
                    self.last_heart_rate = data['heart_rate']
                    self.last_steps = data['step_count']
                    
                    # Print live data
                    print(f"\n📊 [{self.student_id}] Live Data:")
                    print(f"   ❤️ Heart Rate: {data['heart_rate']} BPM")
                    print(f"   👣 Steps: {data['step_count']}")
                    print(f"   📊 HRV: {data['hrv_value']}")
                    
                    print(f"   ⏰ Time: {data['timestamp'].strftime('%H:%M:%S')}")
                
                # Wait for next collection
                await asyncio.sleep(interval_seconds)
            
            # Disconnect when done
            await self.ble.disconnect()
            
        except Exception as e:
            logger.error(f"Collection error: {e}")
            self.is_running = False
    
    def _save_to_database(self, data):
        """
        Save collected data to database
        """
        try:
            bio_record = BioSignalData(
                student_id=self.student_id,
                timestamp=data['timestamp'],
                heart_rate=data['heart_rate'] if data['heart_rate'] else 70,
                hrv_value=data['hrv_value'] if data['hrv_value'] else 50,
                step_count=data['step_count'] if data['step_count'] else 0,
                sleep_hours=7.0,  # Default - will be updated when sleep data available
                sleep_quality=0.7,
                stress_level=0.3
            )
            
            self.session.add(bio_record)
            self.session.commit()
            logger.debug(f"💾 Data saved to database for {self.student_id}")
            
        except Exception as e:
            logger.error(f"Failed to save to database: {e}")
            self.session.rollback()
    
    def get_statistics(self):
        """
        Get collection statistics
        """
        return {
            'student_id': self.student_id,
            'data_points': self.data_points_collected,
            'last_heart_rate': self.last_heart_rate,
            'last_steps': self.last_steps,
            'is_running': self.is_running,
            'watch_connected': self.ble.is_connected
        }