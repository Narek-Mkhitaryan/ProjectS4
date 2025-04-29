import sqlite3
from config import DATABASE_NAME

def migrate_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Adding sale_count column to employees table
    try:
        cursor.execute("ALTER TABLE employees ADD COLUMN sale_count INTEGER DEFAULT 0")
        print("sale_count column added to employees table")
    except sqlite3.OperationalError as e:
        print(f"Error adding sale_count: {e}")
    
    # Adding items column to sales table
    try:
        cursor.execute("ALTER TABLE sales ADD COLUMN items TEXT")
        print("items column added to sales table")
    except sqlite3.OperationalError as e:
        print(f"Error adding items: {e}")
    
    conn.commit()
    conn.close()
    print("Database migration completed")

if __name__ == "__main__":
    migrate_database()