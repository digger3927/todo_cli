#!/usr/bin/env python3
import argparse
import os
from datetime import datetime

# Get the user's home directory or a specific directory
home_dir = os.path.expanduser("~")
todo_file_path = os.path.join(home_dir, "todolist.txt")

# Ensure the file exists
if not os.path.exists(todo_file_path):
    with open(todo_file_path, 'w') as f:
        pass  # Create the file if it doesn't exist

def add_task(task, project="General", due_date=None):
    with open(todo_file_path, "a") as t:
        if due_date:
            t.write(f"- [ ] {task} (Project: {project}) (Due: {due_date})\n")
        else:
            t.write(f"- [ ] {task} (Project: {project})\n")
    print(f'Task "{task}" added to project "{project}" successfully!')


def open_todolist(sort_by=None, project_name=None):
    with open(todo_file_path, "r") as t:
        lines = t.readlines()

    if not lines:
        print("No tasks found.")
        return

    tasks = []
    for line in lines:
        if "- [ ]" in line or "- [x]" in line:
            tasks.append(line.strip())

    # Filter tasks by project if a project name is provided
    if project_name:
        tasks = [task for task in tasks if f"(Project: {project_name})" in task]

    # Sort tasks by the requested method
    if sort_by == "status":
        tasks = sorted(tasks, key=lambda x: "[x]" in x)  # Incomplete tasks first
    elif sort_by == "project":
        tasks = sorted(tasks, key=lambda x: x.split("(Project: ")[-1].rstrip(")") if "(Project:" in x else "")
    elif sort_by == "due":
        tasks = sorted(tasks, key=lambda x: datetime.strptime(x.split("(Due: ")[-1].rstrip(")"), "%Y-%m-%d") if "(Due:" in x else datetime.max)

    print("Current tasks:")
    for index, task in enumerate(tasks, start=1):
        print(f"{index}. {task}")


def complete_task(task_description):
    with open(todo_file_path, "r") as t:
        lines = t.readlines()

    # Find and mark the task as completed based on its description
    task_found = False
    for i, line in enumerate(lines):
        if task_description in line and "- [ ]" in line:
            lines[i] = lines[i].replace("- [ ]", "- [x]")
            task_found = True
            break

    if task_found:
        with open(todo_file_path, "w") as t:
            t.writelines(lines)
        print(f"Task '{task_description}' marked as completed!")
    else:
        print(f"Task '{task_description}' not found or already completed.")


def clear_completed_tasks():
    with open(todo_file_path, "r") as t:
        lines = t.readlines()

    # Filter out completed tasks
    incomplete_tasks = [line for line in lines if "- [x]" not in line]

    # Write back only incomplete tasks
    with open(todo_file_path, "w") as t:
        t.writelines(incomplete_tasks)

    print("Cleared all completed tasks.")


# Create the main parser
parser = argparse.ArgumentParser(description='Todo List Manager')

# Create subparsers for 'add' and 'list' commands
subparsers = parser.add_subparsers(dest='command')

# Subparser for the 'add' command
add_parser = subparsers.add_parser('add', help='Add a new task')
add_parser.add_argument('--task', required=True, help='Task to add')
add_parser.add_argument('--project', help='Project to add the task to')
add_parser.add_argument('--due', help='Due date for the task (format: YYYY-MM-DD)')


# Subparser for the 'list' command
list_parser = subparsers.add_parser('list', help='List all tasks')
list_parser.add_argument('--sort', choices=['status', 'project', 'due'], help='Sort tasks by completion status, project, or due date')
list_parser.add_argument('--project', help='Filter tasks by project')

# Add a subparser for the 'complete' command
complete_parser = subparsers.add_parser('complete', help='Mark a task as completed')
complete_parser.add_argument('task_description', help='Part of the task description to mark as completed')

# Add a subparser for the 'clear-completed' command
clear_parser = subparsers.add_parser('clear-completed', help='Clear all completed tasks')

# Parse the arguments
args = parser.parse_args()

if args.command == 'add' and args.task:
    project = args.project if args.project else "General"
    add_task(args.task, project, due_date=args.due)
elif args.command == 'list':
    open_todolist(sort_by=args.sort, project_name=args.project)
elif args.command == 'complete':
    complete_task(args.task_description)
elif args.command == 'clear-completed':
    clear_completed_tasks()
else:
    print("Please provide a valid command.")
