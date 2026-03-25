# sync_data.py
from src.data_collection.data_sync import DataSyncManager
from src.database.data_migration import DataMigration
import time
import argparse

def main():
    parser = argparse.ArgumentParser(description='Wearable Data Sync Tool')
    parser.add_argument('--mode', type=str, default='sync',
                       choices=['sync', 'migrate', 'export', 'auto'],
                       help='Operation mode')
    parser.add_argument('--interval', type=int, default=1,
                       help='Sync interval in hours (for auto mode)')
    
    args = parser.parse_args()
    
    print("="*60)
    print("⌚ WEARABLE DATA SYNCHRONIZATION")
    print("="*60)
    
    if args.mode == 'sync':
        print("\n📱 Running one-time data sync...")
        sync_manager = DataSyncManager()
        sync_manager.sync_all_students()
        
    elif args.mode == 'migrate':
        print("\n🔄 Running data migration...")
        migration = DataMigration()
        migration.migrate_mock_to_real()
        
    elif args.mode == 'export':
        print("\n📊 Exporting data to CSV...")
        migration = DataMigration()
        migration.export_to_csv()
        
    elif args.mode == 'auto':
        print(f"\n🔄 Starting auto-sync every {args.interval} hours...")
        sync_manager = DataSyncManager()
        sync_manager.start_auto_sync(args.interval)
        
        # Keep running
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n\n🛑 Auto-sync stopped")
    
    print("\n✅ Operation completed")

if __name__ == "__main__":
    main()