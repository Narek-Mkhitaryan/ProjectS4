import tkinter as tk
from database import init_db
from gui import SalesApp

print("Tkinter import successful")
print("Database import successful")
print("gui.SalesApp import successful")

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = SalesApp(root)
    root.mainloop()