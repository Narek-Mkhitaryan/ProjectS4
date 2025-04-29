import sqlite3
import bcrypt
import uuid
import pandas as pd
from config import DATABASE_NAME, DEFAULT_MANAGER_NAME, DEFAULT_MANAGER_PASSWORD

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    # Employees table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            is_manager BOOLEAN NOT NULL,
            password_hash TEXT,
            sale_count INTEGER DEFAULT 0
        )
    ''')
    # Sales table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            amount REAL NOT NULL,
            commission REAL NOT NULL,
            sale_date TEXT NOT NULL,
            items TEXT,
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        )
    ''')
    # Creating a test manager
    cursor.execute("SELECT * FROM employees WHERE is_manager = 1")
    if not cursor.fetchone():
        password = DEFAULT_MANAGER_PASSWORD.encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        cursor.execute("INSERT INTO employees (id, name, is_manager, password_hash, sale_count) VALUES (?, ?, ?, ?, ?)",
                       (str(uuid.uuid4()), DEFAULT_MANAGER_NAME, 1, hashed, 0))
    conn.commit()
    conn.close()

def add_employee(name, password, is_manager=False):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM employees WHERE name = ?", (name,))
    if cursor.fetchone():
        conn.close()
        return False, "Employee with this name already exists"
    employee_id = str(uuid.uuid4())
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) if password else None
    cursor.execute("INSERT INTO employees (id, name, is_manager, password_hash, sale_count) VALUES (?, ?, ?, ?, ?)",
                  (employee_id, name, is_manager, password_hash, 0))
    conn.commit()
    conn.close()
    return True, "Employee added"

def delete_employee(employee_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
    cursor.execute("DELETE FROM sales WHERE employee_id = ?", (employee_id,))
    conn.commit()
    conn.close()
    return True, "Employee deleted"

def get_employee_by_name(name):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, is_manager, password_hash FROM employees WHERE name = ?", (name,))
    employee = cursor.fetchone()
    conn.close()
    return employee

def get_sales_by_employee(employee_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT sale_date, items, amount, commission FROM sales WHERE employee_id = ? ORDER BY sale_date DESC",
                  (employee_id,))
    sales = cursor.fetchall()
    conn.close()
    return sales

def save_sale(employee_id, amount, commission, sale_date, items_json):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sales (employee_id, amount, commission, sale_date, items) VALUES (?, ?, ?, ?, ?)",
                  (employee_id, amount, commission, sale_date, items_json))
    # Incrementing sales counter
    cursor.execute("UPDATE employees SET sale_count = sale_count + 1 WHERE id = ?", (employee_id,))
    conn.commit()
    conn.close()

def get_all_employees():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM employees")
    employees = cursor.fetchall()
    conn.close()
    return employees

def get_sales_data_for_analysis():
    conn = sqlite3.connect(DATABASE_NAME)
    query = """
    SELECT s.employee_id, s.sale_date, s.amount, s.commission, s.items
    FROM sales s
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_employee_sale_count(employee_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT sale_count FROM employees WHERE id = ?", (employee_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0