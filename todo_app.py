#!/usr/bin/env python3

class TodoList:
    def __init__(self):
        self.tasks = []
        
    def add_task(self, task):
        """Add a new task to the list"""
        self.tasks.append({"task": task, "completed": False})
        print(f"Added task: {task}")
        
    def view_tasks(self):
        """Display all tasks with their status"""
        if not self.tasks:
            print("No tasks in the list!")
            return
        
        print("\nTODO LIST:")
        for i, task in enumerate(self.tasks, 1):
            status = "OK" if task["completed"] else " "
            print(f"{i}. [{status}] {task['task']}")
            
    def complete_task(self, task_number):
        """Mark a task as completed"""
        if 1 <= task_number <= len(self.tasks):
            self.tasks[task_number - 1]["completed"] = True
            print(f"Marked task {task_number} as completed!")
        else:
            print("Invalid task number!")
            
    def remove_task(self, task_number):
        """Remove a task from the list"""
        if 1 <= task_number <= len(self.tasks):
            removed_task = self.tasks.pop(task_number - 1)
            print(f"Removed task: {removed_task['task']}")
        else:
            print("Invalid task number!")

def main():
    todo = TodoList()
    
    while True:
        print("\n=== Todo List Menu ===")
        print("1. Add task")
        print("2. View tasks")
        print("3. Complete task")
        print("4. Remove task")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            task = input("Enter task: ")
            todo.add_task(task)
        elif choice == "2":
            todo.view_tasks()
        elif choice == "3":
            todo.view_tasks()
            task_num = input("Enter task number to mark as completed: ")
            try:
                todo.complete_task(int(task_num))
            except ValueError:
                print("Please enter a valid number!")
        elif choice == "4":
            todo.view_tasks()
            task_num = input("Enter task number to remove: ")
            try:
                todo.remove_task(int(task_num))
            except ValueError:
                print("Please enter a valid number!")
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 