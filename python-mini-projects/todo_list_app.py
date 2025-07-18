import datetime

tasks = []

def add_task():
    description = input("Enter task description: ")
    due_date_str = input("Enter due date (YYYY-MM-DD): ")
    try:
        due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return
    priority = input("Enter priority (high, medium, low): ").lower()
    task = {"description": description, "due_date": due_date, "priority": priority, "completed": False}
    tasks.append(task)
    print("Task added successfully!")

def view_tasks():
    if not tasks:
        print("No tasks in the list.")
        return
    for i, task in enumerate(tasks):
        status = "[x]" if task["completed"] else "[ ]"
        print(f"{i+1}. {status} {task['description']} (Due: {task['due_date']}, Priority: {task['priority']})")

def mark_complete():
    view_tasks()
    if not tasks:
        return
    try:
        index = int(input("Enter the number of the task to mark as complete: ")) - 1
        if 0 <= index < len(tasks):
            tasks[index]["completed"] = True
            print("Task marked as complete.")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Invalid input.")

def delete_task():
    view_tasks()
    if not tasks:
        return
    try:
        index = int(input("Enter the number of the task to delete: ")) - 1
        if 0 <= index < len(tasks):
            del tasks[index]
            print("Task deleted successfully!")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Invalid input.")


while True:
    print("\nTo-Do List App")
    print("1. Add task")
    print("2. View tasks")
    print("3. Mark task as complete")
    print("4. Delete task")
    print("5. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        add_task()
    elif choice == "2":
        view_tasks()
    elif choice == "3":
        mark_complete()
    elif choice == "4":
        delete_task()
    elif choice == "5":
        break
    else:
        print("Invalid choice. Please try again.")

print("Exiting To-Do List App.")
