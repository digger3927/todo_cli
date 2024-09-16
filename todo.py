#!/usr/bin/env python3
import argparse
from datetime import datetime

def add_task(task, project="General", due_date=None):
    with open("todolist.txt", "a") as t:
        if due_date:
            t.write(f"- [ ] {task} (Project: {project}) (Due: {due_date})\n")
        else:
            t.write(f"- [ ] {task} (Project: {project})\n")
    print(f'Task "{task}" added to project "{project}" successfully!')



def open_todolist(sort_by=None, project_name=None):
    with open("todolist.txt", "r") as t:
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
    with open("todolist.txt", "r") as t:
        lines = t.readlines()

    # Find and mark the task as completed based on its description
    task_found = False
    for i, line in enumerate(lines):
        if task_description in line and "- [ ]" in line:
            lines[i] = lines[i].replace("- [ ]", "- [x]")
            task_found = True
            break

    if task_found:
        with open("todolist.txt", "w") as t:
            t.writelines(lines)
        print(f"Task '{task_description}' marked as completed!")
    else:
        print(f"Task '{task_description}' not found or already completed.")


def delete_task(task_description):
    with open("todolist.txt", "r") as t:
        lines = t.readlines()

    # Find and delete the task based on its description
    task_found = False
    new_lines = []
    for line in lines:
        if task_description in line and "- [ ]" in line or "- [x]" in line:
            task_found = True
            print(f"Deleted task: {line.strip()}")
        else:
            new_lines.append(line)

    if task_found:
        with open("todolist.txt", "w") as t:
            t.writelines(new_lines)
    else:
        print(f"Task '{task_description}' not found.")


def delete_project(project_name):
    project_header = f"--- Project: {project_name} ---"
    project_task_tag = f"(Project: {project_name})"

    with open("todolist.txt", "r") as t:
        lines = t.readlines()

    # Filter out the project header and tasks associated with the project
    new_lines = [line for line in lines if project_header not in line and project_task_tag not in line]

    # Check if any lines were removed (i.e., the project existed)
    if len(new_lines) != len(lines):
        with open("todolist.txt", "w") as t:
            t.writelines(new_lines)
        print(f"Deleted project '{project_name}' and all associated tasks.")
    else:
        print(f"Project '{project_name}' does not exist.")


def move_project(current_project, new_project):
    with open("todolist.txt", "r") as t:
        lines = t.readlines()

    # Update tasks from the current project to the new project
    updated = False
    for i, line in enumerate(lines):
        if f"(Project: {current_project})" in line:
            lines[i] = line.replace(f"(Project: {current_project})", f"(Project: {new_project})")
            updated = True

    if updated:
        with open("todolist.txt", "w") as t:
            t.writelines(lines)
        print(f"Moved tasks from project '{current_project}' to '{new_project}'.")
    else:
        print(f"No tasks found for project '{current_project}'.")

def add_project(project_name):
    project_header = f"--- Project: {project_name} ---"

    with open("todolist.txt", "r") as t:
        lines = t.readlines()

    # Check if the project header already exists
    project_exists = any(project_header in line for line in lines)

    if project_exists:
        print(f"Project '{project_name}' already exists.")
    else:
        # Add the new project header
        with open("todolist.txt", "a") as t:
            t.write(f"\n{project_header}\n")
        print(f"Project '{project_name}' created successfully!")

def move_task(task_description, new_project):
    with open("todolist.txt", "r") as t:
        lines = t.readlines()

    # Find the task by its description and update its project
    task_found = False
    for i, line in enumerate(lines):
        if task_description in line:
            # Replace the current project with the new project
            if "(Project:" in line:
                lines[i] = line.split("(Project:")[0] + f"(Project: {new_project})\n"
            else:
                # If no project exists, add the new project
                lines[i] = line.strip() + f" (Project: {new_project})\n"
            task_found = True
            break

    if task_found:
        with open("todolist.txt", "w") as t:
            t.writelines(lines)
        print(f'Task "{task_description}" moved to project "{new_project}".')
    else:
        print(f'Task "{task_description}" not found.')


def add_note(description, note, is_project=False):
    with open("todolist.txt", "r") as t:
        lines = t.readlines()

    # Determine if we are working with a task or a project
    task_found = False
    for i, line in enumerate(lines):
        if is_project:
            # Handle project note addition
            if f"--- Project: {description} ---" in line:
                if "(Note:" in line:
                    lines[i] = line.split("(Note:")[0] + f"(Note: {note})\n"
                else:
                    lines[i] = line.strip() + f" (Note: {note})\n"
                task_found = True
                break
        else:
            # Handle task note addition
            if description in line:
                if "(Note:" in line:
                    lines[i] = line.split("(Note:")[0] + f"(Note: {note})\n"
                else:
                    lines[i] = line.strip() + f" (Note: {note})\n"
                task_found = True
                break

    if task_found:
        with open("todolist.txt", "w") as t:
            t.writelines(lines)
        print(f'Note added to {"project" if is_project else "task"} "{description}": {note}')
    else:
        print(f'{"Project" if is_project else "Task"} "{description}" not found.')




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

# Add a subparser for the 'delete' command
delete_parser = subparsers.add_parser('delete', help='Delete a task by description')
delete_parser.add_argument('task_description', help='Part of the task description to delete')

# Add a subparser for the 'delete-project' command
delete_project_parser = subparsers.add_parser('delete-project', help="Delete a project.  This will delete all associated tasks")
delete_project_parser.add_argument('project_name', help='Name of the project to be deleted')

# Add a subparser for the 'move-project' command
move_project_parser = subparsers.add_parser('move-project', help='Move tasks from one project to another')
move_project_parser.add_argument('current_project', help='Current project name')
move_project_parser.add_argument('new_project', help='New project name')

# Subparser for adding projects
add_project_parser = subparsers.add_parser('add-project', help='Add a new project')
add_project_parser.add_argument('project_name', help='Name of the project to add')

# Subparser to move individual tasks to a different project
move_task_parser = subparsers.add_parser('move-task', help='Move a task to a new project')
move_task_parser.add_argument('task_description', help='Part of the task description to move')
move_task_parser.add_argument('new_project', help='New project name')

# Add parser for task and project notes.
add_note_parser = subparsers.add_parser('add-note', help='Add a note to a task or project')
add_note_parser.add_argument('description', help='Part of the task or project description to add a note to')
add_note_parser.add_argument('note', help='The note to add')
add_note_parser.add_argument('--project', action='store_true', help='Specify this flag to add a note to a project')



# Parse the arguments
args = parser.parse_args()

if args.command == 'add' and args.task:
    project = args.project if args.project else "General"
    add_task(args.task, project, due_date=args.due)
elif args.command == 'list':
    open_todolist(sort_by=args.sort, project_name=args.project)
elif args.command == 'complete':
    complete_task(args.task_description)
elif args.command == 'delete':
    delete_task(args.task_description)
elif args.command == 'delete-project':
    delete_project(args.project_name)
elif args.command == 'move-task':
    move_task(args.task_description, args.new_project)
elif args.command == 'add-note':
    add_note(args.description, args.note, is_project=args.project)
else:
    print("Please provide a valid command.")
