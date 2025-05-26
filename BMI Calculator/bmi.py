import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


# Initialize Database 
def init_db():
    conn = sqlite3.connect("bmi_data.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            weight REAL,
            height REAL,
            bmi REAL,
            category TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

# BMI Calculation Logic
def calculate_bmi():
    name = entry_name.get().strip()
    try:
        weight = float(entry_weight.get())
        height = float(entry_height.get())

        if weight <= 0 or height <= 0:
            raise ValueError

        bmi = round(weight / (height ** 2), 2)

        if bmi < 18.5:
            category, color = "Underweight", "#f39c12"
        elif bmi < 25:
            category, color = "Normal", "#27ae60"
        elif bmi < 30:
            category, color = "Overweight", "#f1c40f"
        else:
            category, color = "Obese", "#e74c3c"

        result_label.config(
            text=f"{name}, your BMI is {bmi} ({category})",
            fg=color
        )

        # Save to database
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect("bmi_data.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO records (name, weight, height, bmi, category, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, weight, height, bmi, category, timestamp))
        conn.commit()
        conn.close()

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numeric values for weight and height.")

# View History Function
def view_history():
    name = entry_name.get().strip()
    if not name:
        messagebox.showerror("Missing Name", "Please enter a name to view history.")
        return

    # Creating new window
    history_window = tk.Toplevel(root)
    history_window.title(f"{name}'s BMI History")
    history_window.geometry("700x300")
    history_window.configure(bg="#f4f7f7")

    # Treeview (table)
    columns = ("timestamp", "weight", "height", "bmi", "category")
    tree = ttk.Treeview(history_window, columns=columns, show="headings")
    tree.heading("timestamp", text="Date/Time")
    tree.heading("weight", text="Weight (kg)")
    tree.heading("height", text="Height (m)")
    tree.heading("bmi", text="BMI")
    tree.heading("category", text="Category")
    tree.column("timestamp", width=160)
    tree.column("weight", width=100)
    tree.column("height", width=100)
    tree.column("bmi", width=100)
    tree.column("category", width=120)

    # Add vertical scrollbar
    scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Fetch data from DB
    conn = sqlite3.connect("bmi_data.db")
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, weight, height, bmi, category FROM records WHERE name = ? ORDER BY timestamp DESC', (name,))
    rows = cursor.fetchall()
    conn.close()

    # Insert data into table
    if rows:
        for row in rows:
            tree.insert("", "end", values=row)
    else:
        messagebox.showinfo("No Records", f"No BMI records found for {name}.")

# for graph trends
def view_trend():
    name = entry_name.get().strip()
    if not name:
        messagebox.showerror("Missing Name", "Please enter a name to view trend.")
        return

    # Fetch data from DB
    conn = sqlite3.connect("bmi_data.db")
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, bmi FROM records WHERE name = ? ORDER BY timestamp ASC', (name,))
    data = cursor.fetchall()
    conn.close()

    if not data:
        messagebox.showinfo("No Data", f"No BMI records found for {name}.")
        return

    timestamps, bmis = zip(*data)

    # Create new window
    graph_window = tk.Toplevel(root)
    graph_window.title(f"{name}'s BMI Trend")
    graph_window.geometry("700x400")
    graph_window.configure(bg="#f4f7f7")

    # Create Matplotlib figure
    fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
    ax.plot(timestamps, bmis, marker='o', linestyle='-', color="#207178")
    ax.set_title(f"{name}'s BMI Over Time", fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel("BMI")
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True)

    # Embed the plot into the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)


# GUI Setup
root = tk.Tk()
root.title("BMI Calculator")
root.geometry("450x500")
root.config(bg="#eaf4f4")
root.resizable(False, False)

# Fonts 
TITLE_FONT = ("Segoe UI", 18, "bold")
LABEL_FONT = ("Segoe UI", 11)

# Style for ttk Buttons 
style = ttk.Style()
style.theme_use("default")

style.configure("Primary.TButton",
    font=("Segoe UI", 10),
    padding=6,
    background="#207178",
    foreground="white",
    borderwidth=0
)
style.map("Primary.TButton",
    background=[('active', '#14575d')],
    foreground=[('active', 'white')]
)

style.configure("Secondary.TButton",
    font=("Segoe UI", 10),
    padding=6,
    background="#9dbebb",
    foreground="white",
    borderwidth=0
)
style.map("Secondary.TButton",
    background=[('active', '#6c8c8a')])

# Header 
tk.Label(root, text="🩺 BMI Calculator", font=TITLE_FONT, bg="#eaf4f4", fg="#254e58").pack(pady=20)

# Input Frame
frame = tk.Frame(root, bg="#eaf4f4")
frame.pack(pady=10)

def create_input(label_text, row):
    label = tk.Label(frame, text=label_text, font=LABEL_FONT, bg="#eaf4f4", fg="#2c3e50")
    label.grid(row=row, column=0, padx=10, pady=10, sticky='e')
    entry = tk.Entry(frame, font=LABEL_FONT, width=28, bd=1, relief="solid")
    entry.grid(row=row, column=1, padx=10, pady=10)
    return entry

entry_name = create_input("Name:", 0)
entry_weight = create_input("Weight (kg):", 1)
entry_height = create_input("Height (m):", 2)

# Result Label
result_frame = tk.Frame(root, bg="#eaf4f4")
result_frame.pack(pady=15)

result_label = tk.Label(result_frame, text="", font=("Segoe UI", 13, "bold"), bg="#eaf4f4")
result_label.pack()

# Button Frame 
button_frame = tk.Frame(root, bg="#eaf4f4")
button_frame.pack(pady=10)

ttk.Button(button_frame, text="Calculate BMI", command=calculate_bmi,
           style="Primary.TButton", width=24).pack(pady=8)

ttk.Button(button_frame, text="View History", command=view_history,
           style="Secondary.TButton", width=24).pack(pady=8)

ttk.Button(button_frame, text="View Trend", command=view_trend,
           style="Secondary.TButton", width=24).pack(pady=8)


# Footer
tk.Label(root, text="Live fit, live healthy 💚 by Hiten", font=("Segoe UI", 9),
         bg="#eaf4f4", fg="#6c7a89").pack(side="bottom", pady=15)

# Run 
init_db()
root.mainloop()
