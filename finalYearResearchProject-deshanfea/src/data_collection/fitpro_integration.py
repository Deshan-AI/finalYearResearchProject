# src/data_collection/fitpro_integration.py
import asyncio
import threading
from datetime import datetime
from src.database.database_setup import get_session
from src.database.models import BioSignalData
from .fitpro_ble import FitProBLE

class FitProIntegration:
    """Full FitPro integration for Week 4"""
    
    def __init__(self, student_id, watch_address):
        self.student_id = student_id
        self.watch_address = watch_address
        self.fitpro = FitProBLE(watch_address)
        self.session = get_session()
        self.is_monitoring = False
        
    def start_realtime_monitoring(self):
        """Start continuous monitoring"""
        self.is_monitoring = True
        
        # Run in background thread
        thread = threading.Thread(target=self._monitor_loop)
        thread.daemon = True
        thread.start()
        
        print(f"✅ Real-time monitoring started for {self.student_id}")
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def monitor():
            try:
                # Connect to watch
                await self.fitpro.connect()
                
                while self.is_monitoring:
                    # Get real-time data
                    hr = await self.fitpro.get_heart_rate()
                    steps = await self.fitpro.get_steps()
                    
                    # Save to database
                    self._save_data(hr, steps)
                    
                    # Wait 5 minutes
                    await asyncio.sleep(300)
                    
            except Exception as e:
                print(f"Error: {e}")
            finally:
                await self.fitpro.disconnect()
        
        loop.run_until_complete(monitor())
        
    def _save_data(self, heart_rate, steps):
        """Save to database"""
        # Estimate HRV from heart rate (simplified)
        hrv = self._estimate_hrv(heart_rate)
        
        record = BioSignalData(
            student_id=self.student_id,
            timestamp=datetime.now(),
            heart_rate=heart_rate,
            hrv_value=hrv,
            step_count=steps
        )
        
        self.session.add(record)
        self.session.commit()
        print(f"💾 Data saved: HR={heart_rate}, Steps={steps}")
        
    def _estimate_hrv(self, heart_rate):
        """Estimate HRV from heart rate"""
        # Lower HR = higher HRV (simplified)
        if heart_rate < 65:
            return 65
        elif heart_rate < 75:
            return 50
        else:
            return 35
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        print("🛑 Monitoring stopped")