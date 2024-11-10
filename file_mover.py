import os
import shutil
import time
import threading
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog, messagebox

# Function to move old files
def move_old_files(downloads_folder, target_folder, days_threshold):
    try:
        time_threshold = datetime.now() - timedelta(days=days_threshold)

        for filename in os.listdir(downloads_folder):
            file_path = os.path.join(downloads_folder, filename)
            
            if os.path.isfile(file_path):
                file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                # Move file if older than threshold
                if file_mod_time < time_threshold:
                    shutil.move(file_path, target_folder)
                    print(f"Moved: {filename}")
                    
    except Exception as e:
        print(f"Error: {e}")

# Background task to periodically check for old files
def background_task(downloads_folder, target_folder, days_threshold, interval=3600):
    while True:
        move_old_files(downloads_folder, target_folder, days_threshold)
        time.sleep(interval)  # Check every 'interval' seconds

# GUI setup function to start the background task
def start_monitoring():
    downloads_folder = downloads_folder_entry.get()
    target_folder = target_folder_entry.get()
    days_threshold = int(days_entry.get())
    
    if not downloads_folder or not target_folder:
        messagebox.showwarning("Input Error", "Please select both folders.")
        return

    # Start the background thread
    monitoring_thread = threading.Thread(
        target=background_task, 
        args=(downloads_folder, target_folder, days_threshold), 
        daemon=True
    )
    monitoring_thread.start()
    messagebox.showinfo("Monitoring Started", "The application is now monitoring the downloads folder in the background.")

# Folder selection dialog functions
def browse_downloads_folder():
    folder_selected = filedialog.askdirectory()
    downloads_folder_entry.delete(0, tk.END)
    downloads_folder_entry.insert(0, folder_selected)

def browse_target_folder():
    folder_selected = filedialog.askdirectory()
    target_folder_entry.delete(0, tk.END)
    target_folder_entry.insert(0, folder_selected)

# Create main application window
app = tk.Tk()
app.title("Automatic File Mover")
app.geometry("500x250")

# Downloads folder selection
tk.Label(app, text="Downloads Folder:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
downloads_folder_entry = tk.Entry(app, width=40)
downloads_folder_entry.grid(row=0, column=1, padx=10, pady=10)
tk.Button(app, text="Browse", command=browse_downloads_folder).grid(row=0, column=2, padx=10, pady=10)

# Target folder selection
tk.Label(app, text="Target Folder:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
target_folder_entry = tk.Entry(app, width=40)
target_folder_entry.grid(row=1, column=1, padx=10, pady=10)
tk.Button(app, text="Browse", command=browse_target_folder).grid(row=1, column=2, padx=10, pady=10)

# Days threshold input
tk.Label(app, text="Days Threshold:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
days_entry = tk.Entry(app, width=10)
days_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
days_entry.insert(0, "10")  # Default value

# Start Monitoring button
tk.Button(app, text="Start Monitoring", command=start_monitoring).grid(row=3, column=1, padx=10, pady=20)

# Run the application
app.mainloop()
