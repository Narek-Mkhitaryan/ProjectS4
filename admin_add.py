import sqlite3
import bcrypt
import uuid

# Connect to the database
conn = sqlite3.connect('/mnt/c/Users/User_/Desktop/Project/sales.db')
c = conn.cursor()

# Check the structure of the employees table
c.execute("PRAGMA table_info(employees)")
columns = [col[1] for col in c.fetchall()]
required_columns = ['id', 'name', 'is_manager', 'password_hash', 'sale_count']
missing_columns = [col for col in required_columns if col not in columns]

if missing_columns:
    print(f"Error: The employees table is missing columns: {missing_columns}")
else:
    # Generate password hash
    password = "manager123".encode('utf-8')
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

    # Add administrator
    admin_id = str(uuid.uuid4())
    c.execute("""
        INSERT INTO employees (id, name, is_manager, password_hash, sale_count)
        VALUES (?, ?, ?, ?, ?)
    """, (admin_id, "Manager", 1, hashed_password, 0))

    # Commit changes
    conn.commit()
    print("Administrator successfully added: name 'Manager', password 'manager123'")

# Close the connection
conn.close()