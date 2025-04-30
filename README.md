# Sales Commission Calculator

## Overview

**Sales Commission Calculator** is a desktop Python application created to simplify sales tracking and commission management for small retail teams. Employees can easily log sales and monitor their commissions, while managers can manage staff and view analytical data.

The interface is built using `tkinter`, data is stored in `SQLite`, and built-in machine learning functions provide forecasting and performance analysis.

---

## Features

### Employee Functionality
- Select products from a catalog (e.g., `"iPhone 14 $799"`, `"Sony Headphones $199"`).
- Log sales and view history in a real-time table.
- Commission is calculated automatically (default is 5%).
- Input validation (e.g., message `"Please enter a valid sale amount"` on error).

### Manager Functionality
- Secure login using `bcrypt` password hashing.
- Add and delete employees.
- View sales statistics.
- **Analytics**:
  - 30-day commission forecast using a neural network.
  - Employee performance clustering with K-Means.
  - Graphs visualized using built-in `matplotlib`.

### Logging
- All actions are logged to `sales_app.log` for debugging and reliability.

---

## Installation

> Requires Python 3.8 or higher.

1. Clone the repository:
   ```bash
   git clone https://github.com/username/sales-calculator.git
   cd sales-calculator

2. Create a virtual environment:
   ```bash
   python -m venv venv


3. Activate the environment:

    Windows:
   ```bash
   venv\Scripts\activate

4. macOS/Linux:
   ```bash
   source venv/bin/activate


5. Install dependencies:
   ```bash
   pip install -r requirements.txt


6. Run the application:
   ```bash
   python main.py


## Note for Windows Users

To ensure the application runs correctly on Windows, you need to install and configure **XLaunch** (part of Xming or VcXsrv). This is required for GUI applications using `tkinter` in some WSL environments.

### Steps:

1. Download and install XLaunch from the official source (e.g., [VcXsrv GitHub](https://github.com/ArcticaProject/vcxsrv) or [Xming]).
2. Launch **XLaunch** and configure it as follows:
   - Select **Multiple windows**
   - Choose **Start no client**
   - Check **Disable access control** (for development purposes)
3. Keep XLaunch running in the background before starting the Python application.

This setup enables the graphical interface to appear correctly when running the app from WSL


   
