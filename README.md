# todo_cli
# Command-Line Todo List Manager

A simple and flexible command-line todo list manager built with Python. This tool allows you to manage tasks, projects, due dates, and notes, all stored in a markdown file for easy portability and editing. You can also sort and filter tasks, move tasks between projects, and add notes to both tasks and projects.

## Features

- **Task Management**: Add, complete, delete, and move tasks.
- **Project Management**: Add and delete projects. Automatically link tasks to projects.
- **Sorting and Filtering**: Sort tasks by completion status, project, or due date. Filter tasks by project.
- **Notes**: Add notes to both tasks and projects.
- **Due Dates**: Assign due dates to tasks and sort tasks by their due dates.
- **Markdown-based**: All tasks, projects, and notes are stored in a markdown file for easy portability and manual editing.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/todo_cli.git
    cd todo_cli
    ```

2. Install the necessary dependencies (if any).

3. Make the `todo.py` script executable:
    ```bash
    chmod +x todo.py
    ```

4. (Optional) Add an alias for the `todo` command to your `.bashrc` or `.zshrc`:
    ```bash
    alias todo='python3 /path/to/todo.py'
    ```

## Usage

### Add a Task
```bash
todo add --task "Create database" --project "Website" --due 2024-09-20
```
### List all tasks
```todo list```

### List all tasks by due date
```todo list --sort due```

### List all tasks by project
```todo list --project "Website"```

### Complete a task
```todo list --project "Website"```

### Delete a task
```todo delete "Create database"```

### Move a task to a different project
```todo move-task "Create database" "Backend Development"```

### Add a note to a task or a project
```todo add-note "Create database" "Ensure normalization of tables"```

### Delete a project and all associated tasks
```todo delete-project "Website"```

### Clear completed tasks
```todo clear-completed```

## Future Enhancements
Task Prioritization: Add priority levels to tasks and allow sorting/filtering by priority.
Reminder System: Set reminders for tasks nearing their due date.

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests to improve the functionality of the todo list manager.

## License
This project is licensed under the MIT License.
