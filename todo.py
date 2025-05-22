#!/usr/bin/env python3
import argparse
import os
import sqlite3
from datetime import datetime

# Database setup
DB_PATH = os.path.expanduser("~/todolist.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            project TEXT,
            due_date TEXT,
            status TEXT NOT NULL DEFAULT 'incomplete'
        )
    """)
    conn.commit()
    conn.close()

init_db() # Initialize the database

def add_task(task_description, project="General", due_date=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (description, project, due_date, status)
        VALUES (?, ?, ?, ?)
    """, (task_description, project, due_date, 'incomplete'))
    conn.commit()
    conn.close()
    print(f'Task "{task_description}" added to project "{project}" successfully to the database!')


def open_todolist(sort_by=None, project_name=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = "SELECT id, description, project, due_date, status FROM tasks"
    params = []
    conditions = []

    if project_name:
        conditions.append("project = ?")
        params.append(project_name)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # Sorting logic
    if sort_by == "status":
        # 'incomplete' before 'completed'
        query += " ORDER BY status DESC"
    elif sort_by == "project":
        # Sort by project, then by description for consistent ordering
        query += " ORDER BY project ASC, description ASC"
    elif sort_by == "due":
        # Sort by due_date, tasks with no due date (NULL) last, then by description
        query += " ORDER BY CASE WHEN due_date IS NULL OR due_date = '' THEN 1 ELSE 0 END, due_date ASC, description ASC"
    else:
        # Default sort by ID (order of addition)
        query += " ORDER BY id ASC"

    cursor.execute(query, tuple(params))
    tasks_rows = cursor.fetchall()
    conn.close()

    if not tasks_rows:
        print("No tasks found.")
        return

    print("Current tasks:")
    for index, row in enumerate(tasks_rows, start=1):
        task_id, description, project, due_date, status = row
        status_indicator = "[x]" if status == "completed" else "[ ]"
        due_date_str = f" (Due: {due_date})" if due_date else ""
        project_str = f" (Project: {project})" if project else "" # Assuming project can be NULL
        # Output format: 1. [ ] Task description (Project: MyProject) (Due: YYYY-MM-DD)
        print(f"{index}. {status_indicator} {description}{project_str}{due_date_str}")


def complete_task(task_description_part):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    task_id_to_complete = None
    # Find the oldest, incomplete task that matches the description part
    cursor.execute("""
        SELECT id FROM tasks
        WHERE description LIKE ? AND status = 'incomplete'
        ORDER BY id ASC
        LIMIT 1
    """, (f"%{task_description_part}%",))
    row = cursor.fetchone()

    if row:
        task_id_to_complete = row[0]

    updated_rows = 0
    if task_id_to_complete is not None:
        cursor.execute("""
            UPDATE tasks
            SET status = 'completed'
            WHERE id = ?
        """, (task_id_to_complete,))
        conn.commit()
        updated_rows = cursor.rowcount
    
    conn.close()

    if updated_rows > 0:
        print(f"Task containing '{task_description_part}' (ID: {task_id_to_complete}) marked as completed!")
    else:
        print(f"Task containing '{task_description_part}' not found or already completed.")


def clear_completed_tasks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM tasks WHERE status = 'completed'")
    deleted_rows = cursor.rowcount # Get the number of rows deleted
    conn.commit()
    conn.close()
    
    if deleted_rows > 0:
        print(f"Cleared {deleted_rows} completed task(s) from the database.")
    else:
        print("No completed tasks found to clear.")


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
