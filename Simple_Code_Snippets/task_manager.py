import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser
import datetime
import json
import os
import platform
import threading
import time
import uuid

# --- Constants ---
DEFAULT_DATA_FILE = "tasks.json"
DEFAULT_THEME = "default"
SUPPORTED_THEMES = ["default", "dark"]  # Extend as needed

# --- Helper Functions ---

def show_notification(title, message):
    """Shows a desktop notification."""
    if platform.system() == "Darwin":  # macOS
        try:
            import pync
            pync.notify(message, title=title)
        except ImportError:
            print("pync not installed. Please install it using 'pip install pync'")
    elif platform.system() == "Linux":
        try:
            import notify2
            notify2.init("Task Manager")
            notification = notify2.Notification(title, message)
            notification.show()
        except ImportError:
            print("notify2 not installed. Please install it using 'pip install notify2'")
    elif platform.system() == "Windows":
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=10)
        except ImportError:
            print("win10toast not installed. Please install it using 'pip install win10toast'")
    else:
        print(f"Desktop notifications not supported on {platform.system()}")

def is_valid_date(date_string):
    """Checks if a string is a valid date in YYYY-MM-DD format."""
    try:
        datetime.datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# --- Core Classes ---

class Task:
    def __init__(self, title, description="", deadline=None, priority="Normal",
                 project=None, category=None, completed=False, task_id=None):
        self.task_id = task_id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.deadline = deadline  # YYYY-MM-DD format
        self.priority = priority
        self.project = project
        self.category = category
        self.completed = completed

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "deadline": self.deadline,
            "priority": self.priority,
            "project": self.project,
            "category": self.category,
            "completed": self.completed
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data["title"],
            description=data["description"],
            deadline=data["deadline"],
            priority=data["priority"],
            project=data["project"],
            category=data["category"],
            completed=data["completed"],
            task_id=data["task_id"]
        )


class TaskManager:
    def __init__(self, data_file=DEFAULT_DATA_FILE):
        self.data_file = data_file
        self.tasks = self.load_tasks()
        self.history = []  # List of actions for undo/redo
        self.history_index = -1

    def load_tasks(self):
        """Loads tasks from the data file."""
        try:
            with open(self.data_file, "r") as f:
                data = json.load(f)
                return [Task.from_dict(task_data) for task_data in data]
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print("Error decoding JSON.  Starting with an empty task list.")
            return []

    def save_tasks(self):
        """Saves tasks to the data file."""
        task_data = [task.to_dict() for task in self.tasks]
        try:
            with open(self.data_file, "w") as f:
                json.dump(task_data, f, indent=4)
        except Exception as e:
            print(f"Error saving tasks: {e}")
            messagebox.showerror("Error", f"Error saving tasks: {e}")

    def add_task(self, task):
        """Adds a task and records the action in history."""
        self.tasks.append(task)
        self.record_action("add", task)
        self.save_tasks()

    def update_task(self, task_id, updated_task):
         """Updates an existing task and records the action in history."""
         old_task = self.get_task(task_id)
         if old_task:
             index = self.tasks.index(old_task)
             self.tasks[index] = updated_task
             self.record_action("update", old_task, updated_task)  # Store old and new
             self.save_tasks()
         else:
             print(f"Task with ID {task_id} not found.")

    def delete_task(self, task_id):
        """Deletes a task and records the action in history."""
        task = self.get_task(task_id)
        if task:
            self.tasks = [t for t in self.tasks if t.task_id != task_id]
            self.record_action("delete", task)
            self.save_tasks()
        else:
            print(f"Task with ID {task_id} not found.")

    def get_task(self, task_id):
        """Retrieves a task by its ID."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def record_action(self, action_type, task, new_task=None):
        """Records an action for undo/redo."""
        # Trim history if we've undone and then done a new action
        self.history = self.history[:self.history_index + 1]

        action = {
            "type": action_type,
            "task": task.to_dict() if isinstance(task, Task) else task,
            "new_task": new_task.to_dict() if isinstance(new_task, Task) else new_task
        }
        self.history.append(action)
        self.history_index += 1

    def undo(self):
        """Undoes the last action."""
        if self.history_index >= 0:
            action = self.history[self.history_index]
            action_type = action["type"]
            task_data = action["task"]  # Always stored as dict

            if action_type == "add":
                task_id = task_data["task_id"]
                self.tasks = [t for t in self.tasks if t.task_id != task_id]
            elif action_type == "delete":
                task = Task.from_dict(task_data)
                self.tasks.append(task)
            elif action_type == "update":
                # Restore to the original state before the update
                old_task = Task.from_dict(task_data)
                new_task_data = action["new_task"]
                new_task_id = new_task_data["task_id"]
                # Replace the 'new_task' with the old_task
                for i, t in enumerate(self.tasks):
                    if t.task_id == new_task_id:
                        self.tasks[i] = old_task
                        break

            self.history_index -= 1
            self.save_tasks()
        else:
            print("Nothing to undo.")

    def redo(self):
        """Redoes the last undone action."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            action = self.history[self.history_index]
            action_type = action["type"]
            task_data = action["task"]

            if action_type == "add":
                task = Task.from_dict(task_data)
                self.tasks.append(task)
            elif action_type == "delete":
                task_id = task_data["task_id"]
                self.tasks = [t for t in self.tasks if t.task_id != task_id]
            elif action_type == "update":
                new_task_data = action["new_task"]
                new_task = Task.from_dict(new_task_data)
                # Update to the 'new_task' state
                for i, t in enumerate(self.tasks):
                    if t.task_id == new_task.task_id:
                        self.tasks[i] = new_task
                        break

            self.save_tasks()
        else:
            print("Nothing to redo.")


# --- GUI Classes ---

class TaskForm(simpledialog.Dialog):
    def __init__(self, parent, title=None, task=None):
        self.task = task  # The Task object being edited (None for new tasks)
        self.title_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.deadline_var = tk.StringVar()
        self.priority_var = tk.StringVar()
        self.project_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.completed_var = tk.BooleanVar()
        super().__init__(parent, title=title)

    def body(self, master):
        tk.Label(master, text="Title:").grid(row=0, column=0, sticky=tk.W)
        self.title_entry = tk.Entry(master, textvariable=self.title_var, width=50)
        self.title_entry.grid(row=0, column=1, sticky=tk.EW)

        tk.Label(master, text="Description:").grid(row=1, column=0, sticky=tk.W)
        self.description_entry = tk.Text(master, height=5, width=40)
        self.description_entry.grid(row=1, column=1, sticky=tk.EW)

        tk.Label(master, text="Deadline (YYYY-MM-DD):").grid(row=2, column=0, sticky=tk.W)
        self.deadline_entry = tk.Entry(master, textvariable=self.deadline_var)
        self.deadline_entry.grid(row=2, column=1, sticky=tk.EW)

        tk.Label(master, text="Priority:").grid(row=3, column=0, sticky=tk.W)
        self.priority_combo = ttk.Combobox(master, textvariable=self.priority_var,
                                            values=["High", "Normal", "Low"], state="readonly")
        self.priority_combo.grid(row=3, column=1, sticky=tk.EW)

        tk.Label(master, text="Project:").grid(row=4, column=0, sticky=tk.W)
        self.project_entry = tk.Entry(master, textvariable=self.project_var)
        self.project_entry.grid(row=4, column=1, sticky=tk.EW)

        tk.Label(master, text="Category:").grid(row=5, column=0, sticky=tk.W)
        self.category_entry = tk.Entry(master, textvariable=self.category_var)
        self.category_entry.grid(row=5, column=1, sticky=tk.EW)

        tk.Label(master, text="Completed:").grid(row=6, column=0, sticky=tk.W)
        self.completed_check = tk.Checkbutton(master, variable=self.completed_var)
        self.completed_check.grid(row=6, column=1, sticky=tk.W)


        # Initialize fields if editing an existing task
        if self.task:
            self.title_var.set(self.task.title)
            self.description_entry.delete("1.0", tk.END)  # Clear text widget first
            self.description_entry.insert("1.0", self.task.description)
            self.deadline_var.set(self.task.deadline or "")
            self.priority_var.set(self.task.priority)
            self.project_var.set(self.task.project or "")
            self.category_var.set(self.task.category or "")
            self.completed_var.set(self.task.completed)
        else:
            self.priority_var.set("Normal")  # Default priority

        return self.title_entry  # initial focus

    def apply(self):
        title = self.title_var.get().strip()
        description = self.description_entry.get("1.0", tk.END).strip()
        deadline = self.deadline_var.get().strip()
        priority = self.priority_var.get()
        project = self.project_var.get().strip()
        category = self.category_var.get().strip()
        completed = self.completed_var.get()

        if not title:
            messagebox.showerror("Error", "Title cannot be empty.")
            return None  # Prevents the dialog from closing

        if deadline and not is_valid_date(deadline):
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
            return None

        if self.task:
            # Update existing task
            self.task.title = title
            self.task.description = description
            self.task.deadline = deadline
            self.task.priority = priority
            self.task.project = project
            self.task.category = category
            self.task.completed = completed
            return self.task
        else:
            # Create a new task
            new_task = Task(title=title, description=description, deadline=deadline,
                            priority=priority, project=project, category=category,
                            completed=completed)
            return new_task  # Return the new task object


class TaskListGUI:
    def __init__(self, root, task_manager, theme_manager):
        self.root = root
        self.task_manager = task_manager
        self.theme_manager = theme_manager
        self.root.title("Task Management Application")

        self.create_widgets()
        self.update_task_list()
        self.theme_manager.apply_theme(self)  # Initial theme application


    def create_widgets(self):
        # --- Menu Bar ---
        self.menubar = tk.Menu(self.root)
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="New Task", command=self.add_task)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        self.menubar.add_cascade(label="File", menu=filemenu)

        editmenu = tk.Menu(self.menubar, tearoff=0)
        editmenu.add_command(label="Undo", command=self.undo)
        editmenu.add_command(label="Redo", command=self.redo)
        self.menubar.add_cascade(label="Edit", menu=editmenu)

        theme_menu = tk.Menu(self.menubar, tearoff=0)
        for theme in SUPPORTED_THEMES:
            theme_menu.add_command(label=theme.capitalize(), command=lambda t=theme: self.set_theme(t))
        self.menubar.add_cascade(label="Themes", menu=theme_menu)


        self.root.config(menu=self.menubar)

        # --- Task List Treeview ---
        self.tree = ttk.Treeview(self.root, columns=("Title", "Deadline", "Priority", "Project", "Category", "Completed"), show="headings")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Deadline", text="Deadline")
        self.tree.heading("Priority", text="Priority")
        self.tree.heading("Project", text="Project")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Completed", text="Completed")

        # --- Column Widths ---  Adjust as needed
        self.tree.column("Title", width=200)
        self.tree.column("Deadline", width=100)
        self.tree.column("Priority", width=80)
        self.tree.column("Project", width=120)
        self.tree.column("Category", width=120)
        self.tree.column("Completed", width=80)


        self.tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.edit_selected_task) # Double-click to edit

        # --- Buttons ---
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=5)

        self.add_button = tk.Button(self.button_frame, text="Add Task", command=self.add_task)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.edit_button = tk.Button(self.button_frame, text="Edit Task", command=self.edit_selected_task, state=tk.DISABLED)
        self.edit_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = tk.Button(self.button_frame, text="Delete Task", command=self.delete_selected_task, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        # --- Bind Treeview Selection ---
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def on_tree_select(self, event):
        """Enables/disables edit/delete buttons based on selection."""
        if self.tree.selection():
            self.edit_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
        else:
            self.edit_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)

    def add_task(self):
        """Opens the task form to add a new task."""
        form = TaskForm(self.root, title="Add New Task")
        if form.result:
            new_task = form.result
            self.task_manager.add_task(new_task)
            self.update_task_list()

    def edit_selected_task(self, event=None):
        """Opens the task form to edit the selected task."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select a task to edit.")
            return

        task_id = selected_item[0]
        task = self.task_manager.get_task(task_id)

        if not task:
            messagebox.showerror("Error", f"Task with ID {task_id} not found.")
            return

        form = TaskForm(self.root, title="Edit Task", task=task)
        if form.result:
            updated_task = form.result
            self.task_manager.update_task(task_id, updated_task)
            self.update_task_list()

    def delete_selected_task(self):
        """Deletes the selected task after confirmation."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select a task to delete.")
            return

        task_id = selected_item[0]
        task = self.task_manager.get_task(task_id)

        if not task:
            messagebox.showerror("Error", f"Task with ID {task_id} not found.")
            return

        if messagebox.askyesno("Confirm", f"Are you sure you want to delete task '{task.title}'?"):
            self.task_manager.delete_task(task_id)
            self.update_task_list()

    def update_task_list(self):
        """Refreshes the task list in the treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for task in self.task_manager.tasks:
            self.tree.insert("", tk.END, iid=task.task_id, values=(task.title, task.deadline or "",
                                                               task.priority, task.project or "",
                                                               task.category or "", task.completed))
            if task.completed:
                self.tree.item(task.task_id, tags=('completed',))

        self.tree.tag_configure('completed', foreground='grey')  # Example tag config


        # Schedule reminders (crude implementation)
        threading.Thread(target=self.schedule_reminders, daemon=True).start()

    def schedule_reminders(self):
        """Schedules desktop notifications for upcoming deadlines."""
        now = datetime.datetime.now()
        for task in self.task_manager.tasks:
            if task.deadline:
                try:
                    deadline = datetime.datetime.strptime(task.deadline, '%Y-%m-%d')
                    time_diff = (deadline - now).total_seconds()
                    if 0 < time_diff <= 3600 * 24:  # Within 24 hours
                        time.sleep(max(0, time_diff - 60))  # Wait until almost deadline
                        show_notification("Task Reminder", f"Task '{task.title}' is due soon!")
                except ValueError:
                    print(f"Invalid date format for task '{task.title}'")
                except Exception as e:
                    print(f"Error scheduling reminder for task '{task.title}': {e}")


    def undo(self):
        """Undoes the last action."""
        self.task_manager.undo()
        self.update_task_list()

    def redo(self):
        """Redoes the last undone action."""
        self.task_manager.redo()
        self.update_task_list()

    def set_theme(self, theme_name):
        """Sets the application theme."""
        self.theme_manager.set_theme(theme_name)
        self.theme_manager.apply_theme(self)


class ThemeManager:
    def __init__(self, default_theme=DEFAULT_THEME):
        self.current_theme = default_theme
        self.themes = {
            "default": {
                "background": "white",
                "foreground": "black",
                "button_bg": "#f0f0f0",
                "button_fg": "black",
                "tree_bg": "white",
                "tree_fg": "black",
                "tree_heading_bg": "#e0e0e0",
                "tree_heading_fg": "black",
            },
            "dark": {
                "background": "#333333",
                "foreground": "white",
                "button_bg": "#555555",
                "button_fg": "white",
                "tree_bg": "#444444",
                "tree_fg": "white",
                "tree_heading_bg": "#666666",
                "tree_heading_fg": "white",
            }
        }

    def set_theme(self, theme_name):
        if theme_name in self.themes:
            self.current_theme = theme_name
        else:
            print(f"Theme '{theme_name}' not found. Using default theme.")
            self.current_theme = "default"

    def apply_theme(self, gui):
        theme = self.themes.get(self.current_theme, self.themes["default"])

        gui.root.configure(bg=theme["background"])

        # Apply styles to widgets
        style = ttk.Style()
        style.configure("TButton", background=theme["button_bg"], foreground=theme["button_fg"])
        style.configure("Treeview", background=theme["tree_bg"], foreground=theme["tree_fg"])
        style.configure("Treeview.Heading", background=theme["tree_heading_bg"], foreground=theme["tree_heading_fg"])

        # Apply to standard widgets
        for widget in gui.root.winfo_children():
            widget_type = widget.winfo_class()
            if widget_type in ("Frame", "Label", "Entry", "Text", "Checkbutton"):
                widget.configure(bg=theme["background"], fg=theme["foreground"])
            if widget_type == "Button":
                widget.configure(bg=theme["button_bg"], fg=theme["button_fg"])
        #Specific Treeview headings workaround, apply style directly
        style.configure("Treeview.Heading", background=theme["tree_heading_bg"], foreground=theme["tree_heading_fg"])
        gui.tree.tag_configure('completed', foreground='grey') # Retain complete tag, even when theme changes
        gui.tree.configure(style="Treeview")  # Apply the style to the Treeview

# --- Main ---

if __name__ == "__main__":
    root = tk.Tk()
    task_manager = TaskManager()
    theme_manager = ThemeManager()
    gui = TaskListGUI(root, task_manager, theme_manager)
    root.mainloop()