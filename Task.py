import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
from pathlib import Path
import subprocess
import shutil
import uuid

class TaskScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Scheduler")
        self.root.geometry("650x460")
        self.tasks = []
        self.current_index = None
        self.load_tasks()
        self.setup_ui()
        self.schedule_notifications()
    
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

        ttk.Label(input_frame, text="Time (HH:MM, optional):").grid(row=2, column=0, padx=5)
        self.time_entry = ttk.Entry(input_frame, width=30)
        self.time_entry.grid(row=2, column=1, padx=5)

        ttk.Label(input_frame, text="Description:").grid(row=3, column=0, padx=5)
        self.description_entry = ttk.Entry(input_frame, width=30)
        self.description_entry.grid(row=3, column=1, padx=5)

        ttk.Label(input_frame, text="Notify before:").grid(row=4, column=0, padx=5)
        self.notify_choices = ["None", "1 day", "12 hours", "6 hours", "1 hour"]
        self.notify_combo = ttk.Combobox(input_frame, values=self.notify_choices, state="readonly", width=28)
        self.notify_combo.set("None")
        self.notify_combo.grid(row=4, column=1, padx=5)

        ttk.Button(input_frame, text="Add Task", command=self.add_task).grid(row=0, column=2, padx=5)
        ttk.Button(input_frame, text="Delete", command=self.delete_task).grid(row=1, column=2, padx=5)
        ttk.Button(input_frame, text="Edit Task", command=self.edit_task).grid(row=2, column=2, padx=5)
        ttk.Button(input_frame, text="Update Task", command=self.update_task).grid(row=3, column=2, padx=5)
        
        # Tasks listbox
        self.task_listbox = tk.Listbox(self.root, height=15)
        self.task_listbox.pack(pady=10, padx=10, fill="both", expand=True)
        self.task_listbox.bind("<Double-Button-1>", self.on_item_double_click)
        self.refresh_list()
    
    def add_task(self):
        task = self.task_entry.get().strip()
        date = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()
        description = self.description_entry.get().strip()
        notify_before = self.notify_combo.get()

        if not task:
            messagebox.showwarning("Invalid Input", "Title cannot be empty.")
            return

        if not date:
            messagebox.showwarning("Invalid Input", "Date cannot be empty.")
            return

        if not description:
            messagebox.showwarning("Invalid Input", "Description cannot be empty.")
            return

        try:
            if time_str:
                datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
            else:
                datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Invalid Date/Time", "Please enter date in YYYY-MM-DD format and time in HH:MM format.")
            return

        task_data = {
            "id": str(uuid.uuid4()),
            "task": task,
            "date": date,
            "time": time_str,
            "description": description,
            "notify_before": notify_before,
            "notified": False
        }

        self.tasks.append(task_data)
        self.save_tasks()
        self.refresh_list()

        self.task_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.notify_combo.set("None")
    
    def delete_task(self):
        try:
            index = self.task_listbox.curselection()[0]
            self.tasks.pop(index)
            self.save_tasks()
            self.refresh_list()
            self.current_index = None
        except IndexError:
            pass

    def edit_task(self):
        try:
            index = self.task_listbox.curselection()[0]
        except IndexError:
            messagebox.showwarning("Select a task", "Please select a task to edit.")
            return

        selected = self.tasks[index]
        self.current_index = index
        self.task_entry.delete(0, tk.END)
        self.task_entry.insert(0, selected.get("task", ""))
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, selected.get("date", ""))
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, selected.get("time", ""))
        self.description_entry.delete(0, tk.END)
        self.description_entry.insert(0, selected.get("description", ""))
        self.notify_combo.set(selected.get("notify_before", "None"))

    def on_item_double_click(self, event):
        self.edit_task()

    def update_task(self):
        if self.current_index is None:
            messagebox.showwarning("No task selected", "Please select and edit a task first.")
            return

        task = self.task_entry.get().strip()
        date = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()
        description = self.description_entry.get().strip()
        notify_before = self.notify_combo.get()

        if not task:
            messagebox.showwarning("Invalid Input", "Title cannot be empty.")
            return

        if not date:
            messagebox.showwarning("Invalid Input", "Date cannot be empty.")
            return

        if not description:
            messagebox.showwarning("Invalid Input", "Description cannot be empty.")
            return

        try:
            if time_str:
                datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
            else:
                datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Invalid Date/Time", "Please enter date in YYYY-MM-DD format and time in HH:MM format.")
            return

        existing_id = self.tasks[self.current_index].get("id", str(uuid.uuid4()))
        self.tasks[self.current_index] = {
            "id": existing_id,
            "task": task,
            "date": date,
            "time": time_str,
            "description": description,
            "notify_before": notify_before,
            "notified": False
        }
        self.save_tasks()
        self.refresh_list()
        self.current_index = None

        self.task_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.notify_combo.set("None")

    def refresh_list(self):
        self.task_listbox.delete(0, tk.END)
        for task in sorted(self.tasks, key=lambda x: (x.get("date", ""), x.get("time", ""))):
            time_str = task.get("time", "")
            notify = task.get("notify_before", "None")
            desc = task.get("description", "")
            title = task.get("task", "")
            when = f"{task.get('date', '')} {time_str}" if time_str else task.get("date", "")
            self.task_listbox.insert(tk.END, f"{when} - {title}: {desc} (Notify {notify})")

    def get_event_datetime(self, task):
        date = task.get("date", "")
        time_str = task.get("time", "")
        try:
            if time_str:
                return datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
            return datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return None

    def get_notify_timedelta(self, notify_before):
        mapping = {
            "1 day": timedelta(days=1),
            "12 hours": timedelta(hours=12),
            "6 hours": timedelta(hours=6),
            "1 hour": timedelta(hours=1)
        }
        return mapping.get(notify_before)

    def send_notification(self, title, message):
        if shutil.which("notify-send"):
            try:
                subprocess.run(["notify-send", title, message])
                return
            except Exception:
                pass
        messagebox.showinfo(title, message)

    def schedule_notifications(self):
        now = datetime.now()
        for task in self.tasks:
            if task.get("notified"):
                continue

            notify_before = task.get("notify_before", "None")
            time_delta = self.get_notify_timedelta(notify_before)
            if not time_delta:
                continue

            event_time = self.get_event_datetime(task)
            if not event_time:
                continue

            notify_at = event_time - time_delta
            if notify_at <= now < event_time:
                self.send_notification("Task Reminder", f"{task.get('task', '')} starts at {event_time.strftime('%Y-%m-%d %H:%M')}")
                task["notified"] = True

        self.root.after(60000, self.schedule_notifications)

    def get_data_path(self):
        data_dir = Path.home() / ".task_scheduler"
        data_dir.mkdir(exist_ok=True)
        return data_dir / "tasks.json"
    
    def save_tasks(self):
        self.get_data_path().write_text(json.dumps(self.tasks))

    def load_tasks(self):
        try:
            self.tasks = json.loads(self.get_data_path().read_text())
            for task in self.tasks:
                if "id" not in task:
                    task["id"] = str(uuid.uuid4())
                if "time" not in task:
                    task["time"] = ""
                if "notify_before" not in task:
                    task["notify_before"] = "None"
                if "notified" not in task:
                    task["notified"] = False
        except FileNotFoundError:
            self.tasks = []

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskScheduler(root)
    root.mainloop()