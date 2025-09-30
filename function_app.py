import tkinter as tk
from tkinter import ttk

from tkinter import filedialog, messagebox
from openpyxl import Workbook
import sqlite3
import pandas as pd

# Create database
conn = sqlite3.connect("functions.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS functions (
    sno INTEGER PRIMARY KEY AUTOINCREMENT,
    function_date TEXT,
    function_name TEXT,
    organised_by TEXT,
    resource_person TEXT,
    time TEXT,
    total_participants INTEGER,
    photo_path TEXT,
    welcome_address TEXT,
    chief_guest_address TEXT,
    vote_of_thanks TEXT
)
""")
conn.commit()

# Upload photo function
def upload_photo():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
    )
    if file_path:
        photo_var.set(file_path)

# Submit function
def submit_data():
    cursor.execute("""
    INSERT INTO functions (function_date, function_name, organised_by, resource_person, time, 
                           total_participants, photo_path, welcome_address, chief_guest_address, vote_of_thanks)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        date_var.get(),
        name_var.get(),
        organiser_var.get(),
        resource_var.get(),
        time_var.get(),
        participants_var.get(),
        photo_var.get(),
        welcome_var.get(),
        chief_var.get(),
        vote_var.get()
    ))
    conn.commit()
    messagebox.showinfo("Success", "Data Submitted Successfully!")

# Update function
def update_data():
    try:
        sno = int(sno_var.get())
        cursor.execute("""
        UPDATE functions SET function_date=?, function_name=?, organised_by=?, resource_person=?,
                             time=?, total_participants=?, photo_path=?, welcome_address=?, 
                             chief_guest_address=?, vote_of_thanks=? WHERE sno=?
        """, (
            date_var.get(),
            name_var.get(),
            organiser_var.get(),
            resource_var.get(),
            time_var.get(),
            participants_var.get(),
            photo_var.get(),
            welcome_var.get(),
            chief_var.get(),
            vote_var.get(),
            sno
        ))
        conn.commit()
        messagebox.showinfo("Success", "Data Updated Successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))
       
def view_data():
    view_win = tk.Toplevel(root)
    view_win.title("View Functions Data")
    
    # Frame for Treeview and Scrollbar
    frame = tk.Frame(view_win)
    frame.pack(fill="both", expand=True)
    
    # Scrollbars
    tree_scroll_y = tk.Scrollbar(frame)
    tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    tree_scroll_x = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
    tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Treeview
    tree = ttk.Treeview(frame, yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
    tree.pack(fill="both", expand=True)
    
    tree_scroll_y.config(command=tree.yview)
    tree_scroll_x.config(command=tree.xview)
    
    # Columns
    tree["columns"] = ("S.No", "Date", "Name", "Organised By", "Resource Person",
                       "Time", "Total Participants", "Photo Path", "Welcome", 
                       "Chief Guest", "Vote of Thanks")
    
    tree.column("#0", width=0, stretch=tk.NO)
    for col in tree["columns"]:
        tree.column(col, anchor=tk.W, width=120)
        tree.heading(col, text=col)
    
    # Fetch data
    cursor.execute("SELECT * FROM functions")
    rows = cursor.fetchall()
    
    # Insert data
    for row in rows:
        tree.insert("", tk.END, values=row)


# Generate Report (Excel)
import os

def generate_report():
    import pandas as pd  # ensure pandas is imported
    # Define full path on D: drive
    file_path = r"D:\function_report.xlsx"
    
    # Fetch data from database
    df = pd.read_sql_query("SELECT * FROM functions", conn)
    
    # Save Excel file
    df.to_excel(file_path, index=False)
    
    # Show message with full path
    messagebox.showinfo("Report", f"Report generated successfully at:\n{file_path}")

'''def generate_report():
    df = pd.read_sql_query("SELECT * FROM functions", conn)
    df.to_excel(r"C:\function_report.xlsx", index=False)
    messagebox.showinfo("Report", "Report generated as C:\\function_report.xlsx")'''

# Tkinter GUI
root = tk.Tk()
root.title("Function Data Collection App")

# Variables
sno_var = tk.StringVar()
date_var = tk.StringVar()
name_var = tk.StringVar()
organiser_var = tk.StringVar()
resource_var = tk.StringVar()
time_var = tk.StringVar()
participants_var = tk.StringVar()
photo_var = tk.StringVar()
welcome_var = tk.StringVar()
chief_var = tk.StringVar()
vote_var = tk.StringVar()

# Layout
fields = [
    ("S.No (for update only)", sno_var),
    ("Function Date", date_var),
    ("Function Name", name_var),
    ("Organised By", organiser_var),
    ("Resource Person", resource_var),
    ("Time", time_var),
    ("Total Participants", participants_var),
    ("Photo Path", photo_var),
    ("Welcome Address", welcome_var),
    ("Chief Guest Address", chief_var),
    ("Vote of Thanks", vote_var)
]

for i, (label, var) in enumerate(fields):
    tk.Label(root, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="w")
    tk.Entry(root, textvariable=var, width=40).grid(row=i, column=1, padx=5, pady=5)

tk.Button(root, text="Upload Photo", command=upload_photo).grid(row=7, column=2, padx=5)

# Buttons
tk.Button(root, text="Submit", command=submit_data, bg="green", fg="white").grid(row=12, column=0, pady=10)
tk.Button(root, text="Update", command=update_data, bg="orange", fg="white").grid(row=12, column=1, pady=10)
tk.Button(root, text="Generate Report", command=generate_report, bg="blue", fg="white").grid(row=12, column=2, pady=10)
# --- Add View Button in your GUI ---
tk.Button(root, text="View Records", command=view_data, bg="purple", fg="white").grid(row=13, column=1, pady=10)


root.mainloop()
