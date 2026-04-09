import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
from pathlib import Path
import subprocess
import shutil
import uuid
from tkcalendar import Calendar

class TaskScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Scheduler")
        self.root.geometry("1000x700")
        self.tasks = []
        self.current_index = None
        self.load_tasks()
        self.setup_ui()
        self.schedule_notifications()
    
    def setup_ui(self):
        # Main container frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left frame for input
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Input frame
        input_frame = ttk.LabelFrame(left_frame, text="Add/Edit Task")
        input_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(input_frame, text="Task:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.task_entry = ttk.Entry(input_frame, width=30)
        self.task_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Date (MM/DD/YYYY):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = ttk.Entry(input_frame, width=30)
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)
        self.date_entry.bind("<KeyRelease>", self.on_date_entry_change)

        ttk.Label(input_frame, text="Time (HH:MM, optional):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.time_entry = ttk.Entry(input_frame, width=30)
        self.time_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Description:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.description_entry = ttk.Entry(input_frame, width=30)
        self.description_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Notify before:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.notify_choices = ["None", "1 day", "12 hours", "6 hours", "1 hour"]
        self.notify_combo = ttk.Combobox(input_frame, values=self.notify_choices, state="readonly", width=28)
        self.notify_combo.set("None")
        self.notify_combo.grid(row=4, column=1, padx=5, pady=5)

        # Button frame
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")
        
        ttk.Button(button_frame, text="Add Task", command=self.add_task).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Edit Task", command=self.edit_task).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Update Task", command=self.update_task).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Delete", command=self.delete_task).pack(side="left", padx=2)
        
        # Tasks listbox
        list_frame = ttk.LabelFrame(left_frame, text="Tasks")
        list_frame.pack(fill="both", expand=True)
        
        self.task_listbox = tk.Listbox(list_frame, height=15)
        self.task_listbox.pack(pady=5, padx=5, fill="both", expand=True)
        self.task_listbox.bind("<Double-Button-1>", self.on_item_double_click)
        self.refresh_list()
        
        # Right frame for calendar
        calendar_frame = ttk.LabelFrame(main_frame, text="Date Picker")
        calendar_frame.pack(side="right", fill="both", padx=(10, 0))
        
        # Create calendar
        self.calendar = Calendar(calendar_frame, selectmode='day', 
                                year=datetime.now().year, 
                                month=datetime.now().month,
                                day=datetime.now().day)
        self.calendar.pack(padx=10, pady=10)
        self.calendar.bind("<<CalendarSelected>>", self.on_calendar_select)
    
    def on_calendar_select(self, event=None):
        """Handle calendar date selection"""
        try:
            selected_date = self.calendar.get_date()
            # get_date() returns a string, but might be in YY format
            # Convert it to proper YYYY format
            if isinstance(selected_date, str):
                # Try parsing as MM/DD/YY first, then reformat to MM/DD/YYYY
                try:
                    date_obj = datetime.strptime(selected_date, "%m/%d/%y")
                    formatted_date = date_obj.strftime("%m/%d/%Y")
                except ValueError:
                    # If that fails, it might already be MM/DD/YYYY
                    formatted_date = selected_date
            else:
                # If it's a date object, format it
                formatted_date = selected_date.strftime("%m/%d/%Y")
            
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, formatted_date)
            self.time_entry.focus()
        except Exception as e:
            pass

    def on_date_entry_change(self, event=None):
        """Handle manual date entry and sync calendar"""
        try:
            date_str = self.date_entry.get().strip()
            if date_str:  # Only process if there's text
                # Try to parse the date (accepts M/D/YYYY or MM/DD/YYYY)
                date_obj = datetime.strptime(date_str, "%m/%d/%Y")
                # Update calendar to show the correct month/year, then select the date
                self.calendar.month = date_obj.month
                self.calendar.year = date_obj.year
                self.calendar.selection_set(date_obj.date())
        except (ValueError, AttributeError, TypeError):
            pass
    
    def parse_and_normalize_date(self, date_str):
        """Parse date in flexible format (M/D/YYYY or MM/DD/YYYY) and return normalized MM/DD/YYYY string"""
        try:
            # Try to parse with flexible format
            date_obj = datetime.strptime(date_str, "%m/%d/%Y")
            # Normalize to MM/DD/YYYY format
            return date_obj.strftime("%m/%d/%Y")
        except ValueError:
            # If that fails, return None
            return None
    
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

        # Parse and normalize date
        normalized_date = self.parse_and_normalize_date(date)
        if not normalized_date:
            messagebox.showwarning("Invalid Date/Time", "Please enter date in M/D/YYYY or MM/DD/YYYY format.")
            return

        try:
            if time_str:
                datetime.strptime(f"{normalized_date} {time_str}", "%m/%d/%Y %H:%M")
            else:
                datetime.strptime(normalized_date, "%m/%d/%Y")
        except ValueError:
            messagebox.showwarning("Invalid Date/Time", "Please enter time in HH:MM format (e.g., 14:30).")
            return

        task_data = {
            "id": str(uuid.uuid4()),
            "task": task,
            "date": normalized_date,
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

        # Parse and normalize date
        normalized_date = self.parse_and_normalize_date(date)
        if not normalized_date:
            messagebox.showwarning("Invalid Date/Time", "Please enter date in M/D/YYYY or MM/DD/YYYY format.")
            return

        try:
            if time_str:
                datetime.strptime(f"{normalized_date} {time_str}", "%m/%d/%Y %H:%M")
            else:
                datetime.strptime(normalized_date, "%m/%d/%Y")
        except ValueError:
            messagebox.showwarning("Invalid Date/Time", "Please enter time in HH:MM format (e.g., 14:30).")
            return

        existing_id = self.tasks[self.current_index].get("id", str(uuid.uuid4()))
        self.tasks[self.current_index] = {
            "id": existing_id,
            "task": task,
            "date": normalized_date,
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
                return datetime.strptime(f"{date} {time_str}", "%m/%d/%Y %H:%M")
            return datetime.strptime(date, "%m/%d/%Y")
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
                self.send_notification("Task Reminder", f"{task.get('task', '')} starts at {event_time.strftime('%m/%d/%Y %H:%M')}")
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
                # Migrate old YYYY-MM-DD format to MM/DD/YYYY format
                if "date" in task and task["date"]:
                    try:
                        if len(task["date"]) == 10 and task["date"][4] == '-':  # Old YYYY-MM-DD format
                            old_date = datetime.strptime(task["date"], "%Y-%m-%d")
                            task["date"] = old_date.strftime("%m/%d/%Y")
                    except (ValueError, IndexError):
                        pass
        except FileNotFoundError:
            self.tasks = []

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskScheduler(root)
    root.mainloop()