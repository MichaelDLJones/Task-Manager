import tkinter as tk
from tkinter import ttk
from datetime import datetime
import json
from pathlib import Path

class TaskScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Scheduler")
        self.root.geometry("600x400")
        self.tasks = []
        self.load_tasks()
        self.setup_ui()
    
    def setup_ui(self):
        # Input frame
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10, padx=10, fill="x")
        
        ttk.Label(input_frame, text="Task:").grid(row=0, column=0, padx=5)
        self.task_entry = ttk.Entry(input_frame, width=30)
        self.task_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(input_frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5)
        self.date_entry = ttk.Entry(input_frame, width=30)
        self.date_entry.grid(row=1, column=1, padx=5)
        
        ttk.Button(input_frame, text="Add Task", command=self.add_task).grid(row=0, column=2, padx=5)
        ttk.Button(input_frame, text="Delete", command=self.delete_task).grid(row=1, column=2, padx=5)
        
        # Tasks listbox
        self.task_listbox = tk.Listbox(self.root, height=15)
        self.task_listbox.pack(pady=10, padx=10, fill="both", expand=True)
        self.refresh_list()
    
    def add_task(self):
        task = self.task_entry.get()
        date = self.date_entry.get()
        
        if task and date:
            self.tasks.append({"task": task, "date": date})
            self.save_tasks()
            self.refresh_list()
            self.task_entry.delete(0, tk.END)
            self.date_entry.delete(0, tk.END)
    
    def delete_task(self):
        try:
            index = self.task_listbox.curselection()[0]
            self.tasks.pop(index)
            self.save_tasks()
            self.refresh_list()
        except IndexError:
            pass
    
    def refresh_list(self):
        self.task_listbox.delete(0, tk.END)
        for task in sorted(self.tasks, key=lambda x: x["date"]):
            self.task_listbox.insert(tk.END, f"{task['date']} - {task['task']}")
    
    def save_tasks(self):
        Path("tasks.json").write_text(json.dumps(self.tasks))
    
    def load_tasks(self):
        try:
            self.tasks = json.loads(Path("tasks.json").read_text())
        except FileNotFoundError:
            self.tasks = []

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskScheduler(root)
    root.mainloop()