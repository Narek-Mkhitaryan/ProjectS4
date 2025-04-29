import sqlite3
import bcrypt
import uuid
from datetime import datetime, timedelta
import random
from config import DATABASE_NAME, COMMISSION_RATE

def add_employee(cursor, name, is_manager=False, password=None):
    """Add an employee to the employees table"""
    employee_id = str(uuid.uuid4())
    password_hash = None
    if password:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute(
        "INSERT INTO employees (id, name, is_manager, password_hash) VALUES (?, ?, ?, ?)",
        (employee_id, name, is_manager, password_hash)
    )
    return employee_id

def add_sale(cursor, employee_id, amount, sale_date):
    """Add a sale to the sales table"""
    commission = amount * COMMISSION_RATE
    cursor.execute(
        "INSERT INTO sales (employee_id, amount, commission, sale_date) VALUES (?, ?, ?, ?)",
        (employee_id, amount, commission, sale_date)
    )

def populate_database():
    """Create employees and add sales"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # List of employees
    employees = [
        {"name": "Manager", "is_manager": True, "password": "manager123"},
        {"name": "Ashot", "is_manager": False, "password": None},
        {"name": "Ashotik", "is_manager": False, "password": None},
        {"name": "Vardan", "is_manager": False, "password": None},
        {"name": "Karen", "is_manager": False, "password": None},
    ]

    # Clear tables for a clean start (remove if you want to preserve existing data)
    cursor.execute("DELETE FROM sales")
    cursor.execute("DELETE FROM employees")

    # Add employees
    employee_ids = {}
    for emp in employees:
        emp_id = add_employee(cursor, emp["name"], emp["is_manager"], emp["password"])
        employee_ids[emp["name"]] = emp_id

    # Generate sales for each employee
    start_date = datetime(2025, 3, 1)
    end_date = datetime(2025, 4, 28)
    days_range = (end_date - start_date).days

    for emp_name, emp_id in employee_ids.items():
        for _ in range(20):
            # Random date in the range
            random_days = random.randint(0, days_range)
            sale_date = (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d %H:%M:%S")
            # Random sale amount
            amount = random.randint(5000, 50000)
            add_sale(cursor, emp_id, amount, sale_date)

    # Save changes
    conn.commit()
    conn.close()
    print("5 employees and 100 sales records successfully added to the database.")

if __name__ == "__main__":
    populate_database()