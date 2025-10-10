"""
Migration script to add user_id column to existing receipts table.
Run this once to upgrade the database schema.
"""
import sqlite3
import os
from pathlib import Path

def migrate_database(db_path: str = "checko.db"):
    """
    Add user_id column to receipts table if it doesn't exist.
    Set all existing receipts to user_id='test_user' for backward compatibility.
    """
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    print(f"🔧 Starting migration for {db_path}...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if user_id column already exists
        cursor.execute("PRAGMA table_info(receipts)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'user_id' in columns:
            print("✅ Column 'user_id' already exists in receipts table. No migration needed.")
            conn.close()
            return True
        
        print("📝 Adding 'user_id' column to receipts table...")
        
        # Add the column with a default value
        cursor.execute("""
            ALTER TABLE receipts 
            ADD COLUMN user_id TEXT NOT NULL DEFAULT 'test_user'
        """)
        
        # Create index on user_id for better query performance
        print("📝 Creating index on user_id...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_receipts_user_id 
            ON receipts(user_id)
        """)
        
        # Create composite index for user_id + processed
        print("📝 Creating composite index on (user_id, processed)...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_receipts_user_processed 
            ON receipts(user_id, processed)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Migration completed successfully!")
        print("ℹ️  All existing receipts have been assigned user_id='test_user'")
        print("ℹ️  New receipts will use actual Telegram user IDs")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.close()
        return False


if __name__ == "__main__":
    import sys
    
    # Get database path from command line or use default
    db_path = sys.argv[1] if len(sys.argv) > 1 else "checko.db"
    
    success = migrate_database(db_path)
    sys.exit(0 if success else 1)

