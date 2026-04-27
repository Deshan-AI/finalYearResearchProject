# src/automation/rpa_orchestrator.py
from datetime import datetime, timedelta
from src.database.database_setup import get_session
from src.database.models import BurnoutRisk, Student, BioSignalData
from src.bio_processing.burnout_calculator import BurnoutCalculator
import smtplib
import schedule
import time
import threading
import logging
from typing import List, Dict
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - RPA-BOT - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rpa_bot.log'),
        logging.StreamHandler()
    ]
)

class RPABotOrchestrator:
    """
    RPA Bot Orchestrator - Pure Python Implementation
    Acts like an RPA bot without using external RPA tools
    """
    
    def __init__(self):
        self.session = get_session()
        self.bot_name = "BurnoutDetector-BOT"
        self.is_running = False
        self.task_queue = []
        self.completed_tasks = []
        
        # Bot configuration
        self.config = {
            'monitoring_interval': 3600,  # 1 hour in seconds
            'high_risk_threshold': 0.7,
            'medium_risk_threshold': 0.4,
            'enable_email': False,  # Set to True when email configured
            'enable_sms': False,
            'enable_database_logging': True,
            'max_alerts_per_day': 3,
            'cooldown_period': 12  # hours
        }
        
        logging.info(f"🤖 {self.bot_name} initialized successfully")
    
    # ============= RPA Core Functions =============
    
    def start_bot(self):
        """Start the RPA bot orchestrator"""
        self.is_running = True
        logging.info(f"🚀 {self.bot_name} started - Monitoring students...")
        
        # Start scheduler in background thread
        scheduler_thread = threading.Thread(target=self._run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        # Keep main thread running
        try:
            while self.is_running:
                time.sleep(10)
                self._process_queue()
        except KeyboardInterrupt:
            self.stop_bot()
    
    def stop_bot(self):
        """Stop the RPA bot"""
        self.is_running = False
        logging.info(f"🛑 {self.bot_name} stopped")
        logging.info(f"📊 Tasks completed: {len(self.completed_tasks)}")
    
    def _run_scheduler(self):
        """Run scheduled tasks"""
        # Schedule daily tasks
        schedule.every().day.at("08:00").do(self.daily_burnout_check)
        schedule.every().day.at("12:00").do(self.daily_burnout_check)
        schedule.every().day.at("18:00").do(self.daily_burnout_check)
        
        # Schedule weekly reports
        schedule.every().monday.at("09:00").do(self.generate_weekly_report)
        
        # Schedule data cleanup
        schedule.every().sunday.at("23:00").do(self.cleanup_old_data)
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)
    
    def _process_queue(self):
        """Process tasks in queue"""
        if self.task_queue:
            task = self.task_queue.pop(0)
            logging.info(f"📋 Processing task: {task['name']}")
            try:
                result = task['function'](*task.get('args', []))
                self.completed_tasks.append({
                    'task': task['name'],
                    'result': result,
                    'timestamp': datetime.now()
                })
                logging.info(f"✅ Task completed: {task['name']}")
            except Exception as e:
                logging.error(f"❌ Task failed: {task['name']} - {str(e)}")
    
    def add_task(self, task_name, function, *args):
        """Add task to queue"""
        self.task_queue.append({
            'name': task_name,
            'function': function,
            'args': args,
            'added_at': datetime.now()
        })
        logging.info(f"➕ Task added to queue: {task_name}")
    
    # ============= RPA Automation Workflows =============
    
    def daily_burnout_check(self):
        """Main RPA workflow - Daily burnout detection"""
        logging.info("🔍 Starting daily burnout check workflow...")
        
        # Step 1: Collect all active students
        students = self.session.query(Student).all()
        logging.info(f"📊 Found {len(students)} active students")
        
        high_risk_students = []
        medium_risk_students = []
        
        for student in students:
            # Step 2: Get latest bio-signal data
            latest_data = self.session.query(BioSignalData).filter(
                BioSignalData.student_id == student.student_id
            ).order_by(BioSignalData.timestamp.desc()).first()
            
            if latest_data:
                # Step 3: Calculate burnout risk
                risk_result = self._calculate_risk_from_data(latest_data)
                
                # Step 4: Classify risk level
                if risk_result['risk_score'] >= self.config['high_risk_threshold']:
                    high_risk_students.append({
                        'student': student,
                        'risk': risk_result
                    })
                elif risk_result['risk_score'] >= self.config['medium_risk_threshold']:
                    medium_risk_students.append({
                        'student': student,
                        'risk': risk_result
                    })
        
        # Step 5: Process high risk students (Immediate intervention)
        for student_risk in high_risk_students:
            self.add_task(
                "handle_high_risk",
                self.handle_high_risk_student,
                student_risk
            )
        
        # Step 6: Process medium risk students (Preventive actions)
        for student_risk in medium_risk_students[:5]:  # Limit to 5 per cycle
            self.add_task(
                "handle_medium_risk",
                self.handle_medium_risk_student,
                student_risk
            )
        
        # Step 7: Generate summary
        summary = {
            'timestamp': datetime.now(),
            'total_students': len(students),
            'high_risk': len(high_risk_students),
            'medium_risk': len(medium_risk_students),
            'tasks_queued': len(self.task_queue)
        }
        
        # Step 8: Log summary
        self._log_workflow_summary(summary)
        
        # Step 9: Send summary to counselor (optional)
        if high_risk_students:
            self.add_task(
                "alert_counselor",
                self.alert_counselor,
                high_risk_students
            )
        
        return summary
    
    def _calculate_risk_from_data(self, bio_data):
        """Calculate burnout risk from bio-signal data"""
        # Simplified risk calculation
        hrv_component = (1 - min(bio_data.hrv_value / 100, 1)) * 0.4
        sleep_component = (1 - bio_data.sleep_quality) * 0.35
        activity_component = (1 - min(bio_data.step_count / 10000, 1)) * 0.25
        
        risk_score = hrv_component + sleep_component + activity_component
        
        # Determine primary factor
        factors = {
            'HRV': hrv_component,
            'Sleep': sleep_component,
            'Activity': activity_component
        }
        primary_factor = max(factors, key=factors.get)
        
        return {
            'risk_score': round(risk_score, 3),
            'primary_factor': primary_factor,
            'components': factors
        }
    
    def handle_high_risk_student(self, student_risk):
        """RPA workflow for high-risk students"""
        student = student_risk['student']
        risk = student_risk['risk']
        
        logging.warning(f"⚠️ HIGH RISK student detected: {student.anonymous_id}")
        
        # Action 1: Send immediate alert
        self._send_immediate_alert(student, risk)
        
        # Action 2: Log to database
        if self.config['enable_database_logging']:
            self._log_high_risk_event(student, risk)
        
        # Action 3: Schedule counseling appointment
        self._schedule_counseling(student, risk)
        
        # Action 4: Send follow-up email (if enabled)
        if self.config['enable_email']:
            self._send_email_alert(student, risk)
        
        # Action 5: Update student status
        self._update_student_status(student, 'HIGH_RISK')
        
        return {
            'student': student.anonymous_id,
            'action': 'HIGH_RISK_INTERVENTION',
            'timestamp': datetime.now()
        }
    
    def handle_medium_risk_student(self, student_risk):
        """RPA workflow for medium-risk students (Preventive)"""
        student = student_risk['student']
        risk = student_risk['risk']
        
        logging.info(f"⚠️ MEDIUM RISK student detected: {student.anonymous_id}")
        
        # Action 1: Send wellness tips
        self._send_wellness_tips(student, risk)
        
        # Action 2: Schedule follow-up check
        self._schedule_follow_up(student, days=7)
        
        # Action 3: Log preventive action
        self._log_preventive_action(student, risk)
        
        return {
            'student': student.anonymous_id,
            'action': 'PREVENTIVE_CARE',
            'timestamp': datetime.now()
        }
    
    def generate_weekly_report(self):
        """Generate weekly analytics report"""
        logging.info("📊 Generating weekly report...")
        
        # Calculate weekly statistics
        week_ago = datetime.now() - timedelta(days=7)
        
        high_risk_count = self.session.query(BurnoutRisk).filter(
            BurnoutRisk.date >= week_ago,
            BurnoutRisk.risk_level == "HIGH"
        ).count()
        
        medium_risk_count = self.session.query(BurnoutRisk).filter(
            BurnoutRisk.date >= week_ago,
            BurnoutRisk.risk_level == "MEDIUM"
        ).count()
        
        # Generate report
        report = {
            'week_start': week_ago.date(),
            'week_end': datetime.now().date(),
            'high_risk_students': high_risk_count,
            'medium_risk_students': medium_risk_count,
            'bot_performance': {
                'tasks_processed': len(self.completed_tasks),
                'uptime_hours': self._calculate_uptime()
            },
            'recommendations': self._generate_recommendations(high_risk_count, medium_risk_count)
        }
        
        # Save report
        self._save_weekly_report(report)
        
        logging.info(f"✅ Weekly report generated: {high_risk_count} high risk cases")
        return report
    
    def cleanup_old_data(self):
        """Cleanup old data (GDPR compliance)"""
        logging.info("🧹 Starting data cleanup...")
        
        # Delete data older than 6 months
        six_months_ago = datetime.now() - timedelta(days=180)
        
        old_data = self.session.query(BioSignalData).filter(
            BioSignalData.timestamp < six_months_ago
        ).delete()
        
        self.session.commit()
        
        logging.info(f"✅ Cleaned up {old_data} old records")
        return {'deleted_records': old_data}
    
    # ============= Helper Functions =============
    
    def _send_immediate_alert(self, student, risk):
        """Send immediate alert to student"""
        alert_message = f"""
        🔴 URGENT: High Stress Detected
        
        Dear Student,
        
        Our system has detected signs of high stress in your biometric data.
        
        Primary Factor: {risk['primary_factor']}
        Risk Score: {risk['risk_score']}
        
        Immediate Actions:
        1. Take a 10-minute break
        2. Practice deep breathing
        3. Contact counseling center if needed
        
        Counseling Center: +94 XX XXX XXXX
        Email: counseling@university.lk
        
        Stay safe,
        Burnout Detection System
        """
        
        # Print to console (simulate sending)
        print("\n" + "🚨" * 20)
        print(alert_message)
        print("🚨" * 20 + "\n")
        
        # Log the alert
        logging.info(f"Alert sent to {student.anonymous_id}")
    
    def _send_wellness_tips(self, student, risk):
        """Send wellness tips to medium-risk students"""
        tips = {
            'HRV': [
                "Practice deep breathing for 5 minutes",
                "Reduce caffeine intake",
                "Take short breaks between study sessions"
            ],
            'Sleep': [
                "Maintain consistent sleep schedule",
                "Avoid screens 1 hour before bed",
                "Create a relaxing bedtime routine"
            ],
            'Activity': [
                "Take a 15-minute walk daily",
                "Stretch every 2 hours",
                "Join a sports club or activity"
            ]
        }
        
        selected_tips = tips.get(risk['primary_factor'], tips['Activity'])
        
        tip_message = f"""
        🌿 Wellness Tips for You
        
        Based on your recent data, here are personalized tips:
        
        {chr(10).join(['• ' + tip for tip in selected_tips])}
        
        Stay healthy!
        """
        
        print("\n" + "💚" * 20)
        print(tip_message)
        print("💚" * 20 + "\n")
    
    def _schedule_counseling(self, student, risk):
        """Schedule counseling appointment"""
        # This would integrate with university's booking system
        appointment = {
            'student_id': student.anonymous_id,
            'priority': 'HIGH',
            'reason': f"High stress detected - Primary: {risk['primary_factor']}",
            'suggested_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'status': 'PENDING'
        }
        
        print(f"📅 Counseling appointment scheduled for {student.anonymous_id}")
        return appointment
    
    def _schedule_follow_up(self, student, days):
        """Schedule follow-up check"""
        follow_up = {
            'student_id': student.anonymous_id,
            'check_date': (datetime.now() + timedelta(days=days)),
            'type': 'MEDIUM_RISK_FOLLOWUP'
        }
        
        print(f"📅 Follow-up scheduled for {student.anonymous_id} in {days} days")
        return follow_up
    
    def _log_high_risk_event(self, student, risk):
        """Log high risk event to database"""
        # Create alert record (you would have an Alert model)
        alert_record = {
            'student_id': student.anonymous_id,
            'risk_score': risk['risk_score'],
            'primary_factor': risk['primary_factor'],
            'timestamp': datetime.now(),
            'action_taken': 'HIGH_RISK_INTERVENTION'
        }
        
        # In real implementation: self.session.add(alert_record)
        logging.info(f"📝 High risk event logged for {student.anonymous_id}")
    
    def _log_preventive_action(self, student, risk):
        """Log preventive action"""
        logging.info(f"📝 Preventive action logged for {student.anonymous_id}")
    
    def _update_student_status(self, student, status):
        """Update student status in database"""
        # In real implementation: update student record
        logging.info(f"📝 Student {student.anonymous_id} status updated to {status}")
    
    def _log_workflow_summary(self, summary):
        """Log workflow summary"""
        logging.info("📊 Daily Workflow Summary:")
        logging.info(f"   Total Students: {summary['total_students']}")
        logging.info(f"   High Risk: {summary['high_risk']}")
        logging.info(f"   Medium Risk: {summary['medium_risk']}")
        logging.info(f"   Tasks Queued: {summary['tasks_queued']}")
    
    def _calculate_uptime(self):
        """Calculate bot uptime"""
        # Simplified uptime calculation
        return 24  # hours
    
    def _generate_recommendations(self, high_count, medium_count):
        """Generate recommendations based on statistics"""
        recommendations = []
        
        if high_count > 5:
            recommendations.append("Increase counseling staff availability")
        if medium_count > 10:
            recommendations.append("Send mass wellness tips to all students")
        
        recommendations.append("Continue daily monitoring")
        
        return recommendations
    
    def _save_weekly_report(self, report):
        """Save weekly report to file"""
        filename = f"reports/weekly_report_{datetime.now().strftime('%Y%m%d')}.json"
        
        # Create reports directory if not exists
        os.makedirs('reports', exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logging.info(f"💾 Weekly report saved to {filename}")
    
    def alert_counselor(self, high_risk_students):
        """Alert counselor about high-risk students"""
        counselor_message = f"""
        👨‍⚕️ Counselor Alert
        
        {len(high_risk_students)} high-risk students detected today!
        
        Student IDs (anonymous):
        {chr(10).join(['• ' + s['student'].anonymous_id for s in high_risk_students])}
        
        Please review and take appropriate action.
        
        System: {self.bot_name}
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        print("\n" + "📋" * 20)
        print(counselor_message)
        print("📋" * 20 + "\n")
        
        logging.info(f"👨‍⚕️ Counselor alerted about {len(high_risk_students)} high-risk students")


# ============= RPA Bot Runner =============

class RPABotRunner:
    """Main runner for RPA bot"""
    
    def __init__(self):
        self.bot = RPABotOrchestrator()
        self.workflows = {
            '1': self.run_daily_check,
            '2': self.run_manual_check,
            '3': self.generate_report,
            '4': self.show_status,
            '5': self.stop_bot
        }
    
    def run_daily_check(self):
        """Run daily automated check"""
        self.bot.add_task("Daily Check", self.bot.daily_burnout_check)
        print("✅ Daily check scheduled")
    
    def run_manual_check(self):
        """Run manual check for specific student"""
        student_id = input("Enter student ID: ")
        # Manual check logic here
        print(f"🔍 Manual check for {student_id} scheduled")
    
    def generate_report(self):
        """Generate report on demand"""
        self.bot.add_task("Generate Report", self.bot.generate_weekly_report)
        print("📊 Report generation scheduled")
    
    def show_status(self):
        """Show bot status"""
        print(f"\n🤖 Bot Status: {'Running' if self.bot.is_running else 'Stopped'}")
        print(f"📋 Tasks in queue: {len(self.bot.task_queue)}")
        print(f"✅ Completed tasks: {len(self.bot.completed_tasks)}")
        print(f"📝 Check logs: rpa_bot.log")
    
    def stop_bot(self):
        """Stop the bot"""
        self.bot.stop_bot()
        return False
    
    def run(self):
        """Run the RPA bot console"""
        print("\n" + "="*60)
        print("🤖 BURNOUT DETECTION RPA BOT")
        print("="*60)
        
        # Start bot in background
        bot_thread = threading.Thread(target=self.bot.start_bot)
        bot_thread.daemon = True
        bot_thread.start()
        
        running = True
        while running:
            print("\n📋 Available Workflows:")
            print("1. Run Daily Check (Automated)")
            print("2. Run Manual Check")
            print("3. Generate Report")
            print("4. Show Bot Status")
            print("5. Stop Bot")
            
            choice = input("\nSelect workflow (1-5): ")
            
            if choice in self.workflows:
                result = self.workflows[choice]()
                if result is False:  # Stop bot
                    running = False
            else:
                print("❌ Invalid choice")


# ============= Usage Example =============

if __name__ == "__main__":
    # Option 1: Run as automated bot
    runner = RPABotRunner()
    runner.run()
    
    # Option 2: Run directly (without console)
    # bot = RPABotOrchestrator()
    # bot.start_bot()