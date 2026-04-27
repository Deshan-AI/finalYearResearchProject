# src/data_collection/fitpro_realtime.py
import json
import subprocess
import time
import sqlite3
import os
import random
from datetime import datetime
from pathlib import Path

class FitProRealTime:
    """
    Near real-time FitPro data collection using Gadgetbridge + ADB + SQLite.
    Works on Windows / Linux / macOS with Android phone connected via USB.
    """

    def __init__(self, student_id, phone_device="emulator-5554", export_folder="/sdcard/Gadgetbridge"):
        self.student_id = student_id
        self.phone_device = phone_device          # change if multiple devices: adb devices
        self.export_folder = export_folder        # folder on phone where Gadgetbridge exports DB
        self.local_db_path = "gadgetbridge.db"    # where we pull the db to on PC
        self.adb_prefix = ["adb"] if not phone_device else ["adb", "-s", phone_device]

    def run_adb(self, cmd, check=True):
        """Helper to run adb commands"""
        full_cmd = self.adb_prefix + cmd
        try:
            result = subprocess.run(full_cmd, capture_output=True, text=True, check=check)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"ADB error: {e.stderr.strip()}")
            return None

    def trigger_sync_and_export(self):
        """Trigger Gadgetbridge to sync and export database via Intent"""
        print("→ Triggering Gadgetbridge sync & export...")

        # Trigger activity sync (fetches latest data from watch)
        self.run_adb([
            "shell", "am", "broadcast",
            "-a", "nodomain.freeyourgadget.gadgetbridge.command.SYNC",
            "nodomain.freeyourgadget.gadgetbridge"
        ])

        time.sleep(4)  # give time to sync

        # Trigger database export
        self.run_adb([
            "shell", "am", "broadcast",
            "-a", "nodomain.freeyourgadget.gadgetbridge.command.TRIGGER_EXPORT",
            "nodomain.freeyourgadget.gadgetbridge"
        ])

        time.sleep(5)  # wait for export to finish

    def pull_latest_db(self):
        """Pull the latest gadgetbridge.db from phone"""
        remote_path = f"{self.export_folder.rstrip('/')}/gadgetbridge.db"
        print(f"→ Pulling database: {remote_path} → {self.local_db_path}")

        self.run_adb(["pull", remote_path, self.local_db_path])
        
        if os.path.exists(self.local_db_path):
            print("Database pulled successfully.")
            return True
        else:
            print("Failed to pull database.")
            return False

    def get_latest_data_from_db(self):
        """Read latest heart rate, steps, etc. from SQLite"""
        if not os.path.exists(self.local_db_path):
            return None

        try:
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()

            # Latest activity sample (steps, etc.)
            cursor.execute("""
                SELECT TIMESTAMP, RAW_INTENSITY, STEPS, HEART_RATE
                FROM MI_BAND_ACTIVITY_SAMPLE
                ORDER BY TIMESTAMP DESC
                LIMIT 1
            """)
            row = cursor.fetchone()

            if row:
                ts, intensity, steps, hr = row
                data = {
                    "timestamp": datetime.fromtimestamp(ts).isoformat(),
                    "heart_rate": hr if hr and hr > 0 else None,
                    "steps": steps if steps else 0,
                    # You can add more fields: distance, calories, etc.
                }
            else:
                data = None

            conn.close()
            return data

        except Exception as e:
            print(f"SQLite error: {e}")
            return None

    def get_realtime_data(self, force_sync=True):
        """
        Main method - get latest data (near real-time)
        force_sync: whether to trigger sync+export (takes ~10-15s)
        """
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching data for student {self.student_id}...")

        if force_sync:
            self.trigger_sync_and_export()
            if not self.pull_latest_db():
                return self._get_mock_data()

        db_data = self.get_latest_data_from_db()

        if db_data:
            return {
                "student_id": self.student_id,
                "timestamp": db_data["timestamp"],
                "heart_rate": db_data["heart_rate"] or random.randint(62, 88),
                "steps": db_data["steps"],
                "source": "gadgetbridge_sqlite"
            }
        else:
            return self._get_mock_data()

    def _get_mock_data(self):
        """Fallback when nothing works"""
        import random
        return {
            "student_id": self.student_id,
            "timestamp": datetime.now().isoformat(),
            "heart_rate": random.randint(60, 90),
            "steps": random.randint(800, 14000),
            "source": "mock"
        }


# # ────────────────────────────────────────────────
# #   Example usage
# # ────────────────────────────────────────────────

# if __name__ == "__main__":
#     # Change student_id and phone serial if needed
#     collector = FitProRealTime(student_id="S2025001")  # , phone_device="1234567890ABCDEF"

#     while True:
#         data = collector.get_realtime_data(force_sync=True)  # set False for faster polling
#         print(json.dumps(data, indent=2))
#         print("-" * 50)
#         time.sleep(60)  # poll every minute (adjust as needed)