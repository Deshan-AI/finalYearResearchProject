# src/automation/realtime_monitor.py
from src.data_collection.fitpro_integration import FitProIntegration
from src.ml.predict import BurnoutPredictor
from src.automation.rpa_orchestrator import RPABotOrchestrator
import time

class RealTimeMonitor:
    """Monitor multiple FitPro watches in real-time"""
    
    def __init__(self):
        self.students = {}  # student_id -> FitProIntegration
        self.predictor = BurnoutPredictor()
        self.rpa = RPABotOrchestrator()
        
    def add_student(self, student_id, watch_address):
        """Add a new student with FitPro watch"""
        print(f"➕ Adding student {student_id} with watch {watch_address}")
        integration = FitProIntegration(student_id, watch_address)
        self.students[student_id] = integration
        integration.start_realtime_monitoring()
        
    def check_all_students(self):
        """Check all students for burnout risk"""
        print("\n🔍 Checking all students...")
        
        for student_id, integration in self.students.items():
            # Get latest data from database
            latest = self._get_latest_data(student_id)
            
            if latest:
                # Predict burnout risk
                prediction = self.predictor.predict_single({
                    'hrv': latest.hrv_value,
                    'heart_rate': latest.heart_rate,
                    'step_count': latest.step_count
                })
                
                print(f"📊 {student_id}: {prediction['risk_level']} risk")
                
                # Trigger RPA if high risk
                if prediction['risk_level'] == 'HIGH':
                    self.rpa.trigger_intervention(student_id, prediction)
                    
    def _get_latest_data(self, student_id):
        """Get latest data from database"""
        from src.database.database_setup import get_session
        from src.database.models import BioSignalData
        
        session = get_session()
        return session.query(BioSignalData).filter(
            BioSignalData.student_id == student_id
        ).order_by(BioSignalData.timestamp.desc()).first()
        
    def run(self):
        """Main monitoring loop"""
        print("🚀 Starting Real-Time Monitor...")
        
        while True:
            self.check_all_students()
            time.sleep(300)  # Check every 5 minutes

# Usage
if __name__ == "__main__":
    monitor = RealTimeMonitor()
    
    # Add your friend's FitPro watch
    monitor.add_student(
        student_id="STU001",
        watch_address="XX:XX:XX:XX:XX"  # Your friend's watch MAC
    )
    
    # Start monitoring
    monitor.run()