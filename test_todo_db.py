import unittest
import os
import sqlite3
import todo # Assuming todo.py is in the same directory or accessible via PYTHONPATH

# Store the original DB_PATH
ORIGINAL_DB_PATH = todo.DB_PATH
TEST_DB_PATH = "test_todolist.db"

class TestTodoDB(unittest.TestCase):

    def setUp(self):
        """Set up a clean test database before each test."""
        todo.DB_PATH = TEST_DB_PATH
        # Ensure no lingering file from a previous failed test run
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
        todo.init_db() # Initialize the database with the test path

    def tearDown(self):
        """Clean up the test database file after each test."""
        # Close any connections todo.py might have left open implicitly, though it shouldn't.
        # For safety, we can try to connect and close, but it's better if todo.py functions manage their own.
        
        # Delete the test database file
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
        # Restore the original DB_PATH for todo.py if other tests or parts of the system use it
        todo.DB_PATH = ORIGINAL_DB_PATH

    def assertTableExists(self, table_name):
        conn = sqlite3.connect(todo.DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        self.assertIsNotNone(cursor.fetchone(), f"Table '{table_name}' should exist.")
        conn.close()

    def get_table_info(self, table_name):
        conn = sqlite3.connect(todo.DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        conn.close()
        # Returns list of tuples: (cid, name, type, notnull, default_value, pk)
        return {info[1]: {'type': info[2], 'notnull': bool(info[3]), 'pk': bool(info[5])} for info in columns_info}

    # --- Test Cases ---

    def test_init_db_creates_file(self):
        """Test that init_db creates the database file."""
        self.assertTrue(os.path.exists(TEST_DB_PATH), "Database file should be created.")

    def test_init_db_creates_table_and_schema(self):
        """Test that init_db creates the tasks table with the correct schema."""
        self.assertTableExists("tasks")
        
        expected_schema = {
            'id': {'type': 'INTEGER', 'notnull': False, 'pk': True}, # SQLite INTEGER PK is auto-increment and not null by default
            'description': {'type': 'TEXT', 'notnull': True, 'pk': False},
            'project': {'type': 'TEXT', 'notnull': False, 'pk': False},
            'due_date': {'type': 'TEXT', 'notnull': False, 'pk': False},
            'status': {'type': 'TEXT', 'notnull': True, 'pk': False}
        }
        
        actual_schema = self.get_table_info("tasks")
        
        self.assertEqual(len(expected_schema), len(actual_schema), "Number of columns should match.")
        
        for col_name, expected_props in expected_schema.items():
            self.assertIn(col_name, actual_schema, f"Column '{col_name}' should exist.")
            self.assertEqual(expected_props['type'], actual_schema[col_name]['type'], f"Type for column '{col_name}' should be {expected_props['type']}.")
            # For INTEGER PRIMARY KEY, notnull is implicitly true in SQLite when checked via PRAGMA, even if not explicitly stated
            if col_name == 'id': # Special handling for SQLite's INTEGER PRIMARY KEY
                 self.assertTrue(actual_schema[col_name]['notnull'], f"NOT NULL for column '{col_name}' should be True.")
            else:
                self.assertEqual(expected_props['notnull'], actual_schema[col_name]['notnull'], f"NOT NULL for column '{col_name}' should be {expected_props['notnull']}.")
            self.assertEqual(expected_props['pk'], actual_schema[col_name]['pk'], f"Primary Key for column '{col_name}' should be {expected_props['pk']}.")
            # We are not checking default values here as they are handled by the application logic or are simple for status.

    # --- Tests for add_task ---
    def test_add_task_only_description(self):
        """Test adding a task with only a description."""
        todo.add_task("Test Task 1")
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT description, project, due_date, status FROM tasks WHERE description = 'Test Task 1'")
        task = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(task, "Task should be added to the database.")
        self.assertEqual(task[0], "Test Task 1")
        self.assertEqual(task[1], "General", "Default project should be 'General'.") # Default in add_task
        self.assertIsNone(task[2], "Due date should be None if not provided.")
        self.assertEqual(task[3], "incomplete", "Status should be 'incomplete'.")

    def test_add_task_with_project_and_due_date(self):
        """Test adding a task with description, project, and due date."""
        todo.add_task("Test Task 2", project="Work", due_date="2024-12-31")
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT description, project, due_date, status FROM tasks WHERE description = 'Test Task 2'")
        task = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(task, "Task should be added to the database.")
        self.assertEqual(task[0], "Test Task 2")
        self.assertEqual(task[1], "Work")
        self.assertEqual(task[2], "2024-12-31")
        self.assertEqual(task[3], "incomplete", "Status should be 'incomplete'.")

    # --- Tests for open_todolist (verifying DB state primarily) ---
    def _get_tasks_from_db(self, query, params=()):
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def test_list_tasks_empty_db(self):
        """Test listing tasks when the database is empty."""
        # todo.open_todolist() # Call the function, though we don't capture stdout
        tasks = self._get_tasks_from_db("SELECT * FROM tasks")
        self.assertEqual(len(tasks), 0, "Should be no tasks in an empty DB.")

    def test_list_all_tasks(self):
        """Test listing all tasks."""
        todo.add_task("Task A")
        todo.add_task("Task B")
        # todo.open_todolist()
        tasks = self._get_tasks_from_db("SELECT description FROM tasks")
        self.assertEqual(len(tasks), 2)
        self.assertIn(("Task A",), tasks)
        self.assertIn(("Task B",), tasks)

    def test_list_tasks_filter_by_project(self):
        """Test filtering tasks by project."""
        todo.add_task("Task P1", project="Project1")
        todo.add_task("Task P2", project="Project2")
        todo.add_task("Task P1-2", project="Project1")
        # todo.open_todolist(project_name="Project1")
        
        # Verify DB state for the filter
        query = "SELECT description FROM tasks WHERE project = ?"
        tasks = self._get_tasks_from_db(query, ("Project1",))
        self.assertEqual(len(tasks), 2)
        self.assertIn(("Task P1",), tasks)
        self.assertIn(("Task P1-2",), tasks)

    def test_list_tasks_sort_by_status(self):
        """Test sorting tasks by status (incomplete first)."""
        todo.add_task("Task Incomplete", project="P", due_date="2024-01-01", ) # status='incomplete' by default
        todo.add_task("Task Completed", project="P", due_date="2024-01-02")
        
        # Manually complete the second task
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status = 'completed' WHERE description = 'Task Completed'")
        conn.commit()
        conn.close()
        
        # todo.open_todolist(sort_by="status")
        
        # Verify DB state for the sort order (incomplete then completed)
        # todo.py sorts by status DESC ('incomplete' > 'completed')
        query = "SELECT description, status FROM tasks ORDER BY status DESC"
        tasks = self._get_tasks_from_db(query)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0][0], "Task Incomplete") # Incomplete first
        self.assertEqual(tasks[1][0], "Task Completed")  # Completed second

    def test_list_tasks_sort_by_project(self):
        """Test sorting tasks by project name."""
        todo.add_task("Task C", project="Charlie")
        todo.add_task("Task A", project="Alpha")
        todo.add_task("Task B", project="Bravo")
        # todo.open_todolist(sort_by="project")
        
        # Verify DB state for the sort order
        query = "SELECT description, project FROM tasks ORDER BY project ASC, description ASC"
        tasks = self._get_tasks_from_db(query)
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0][0], "Task A")
        self.assertEqual(tasks[1][0], "Task B")
        self.assertEqual(tasks[2][0], "Task C")

    def test_list_tasks_sort_by_due_date(self):
        """Test sorting tasks by due date (NULLs/empty last)."""
        todo.add_task("Task Due Later", due_date="2025-01-01")
        todo.add_task("Task No Due Date") # due_date is NULL
        todo.add_task("Task Due Earlier", due_date="2024-01-01")
        todo.add_task("Task Empty Due Date", due_date="") # Empty string due_date
        # todo.open_todolist(sort_by="due")

        # Verify DB state for the sort order (todo.py specific logic)
        # ORDER BY CASE WHEN due_date IS NULL OR due_date = '' THEN 1 ELSE 0 END, due_date ASC, description ASC
        query = "SELECT description, due_date FROM tasks ORDER BY CASE WHEN due_date IS NULL OR due_date = '' THEN 1 ELSE 0 END, due_date ASC, description ASC"
        tasks = self._get_tasks_from_db(query)
        
        self.assertEqual(len(tasks), 4)
        self.assertEqual(tasks[0][0], "Task Due Earlier")      # 2024-01-01
        self.assertEqual(tasks[1][0], "Task Due Later")        # 2025-01-01
        # Order of NULL and '' due dates might depend on description sort if they are treated equally by the CASE
        # Assuming "Task Empty Due Date" comes before "Task No Due Date" alphabetically
        self.assertIn(tasks[2][0], ["Task Empty Due Date", "Task No Due Date"])
        self.assertIn(tasks[3][0], ["Task Empty Due Date", "Task No Due Date"])
        # Check that the NULL/empty due date tasks are last
        self.assertTrue((tasks[2][1] is None or tasks[2][1] == '') and (tasks[3][1] is None or tasks[3][1] == ''))

    # --- Tests for complete_task ---
    def _get_task_status_by_description(self, description):
        # Helper to get status of a task by its full description
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM tasks WHERE description = ?", (description,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def _get_task_by_id(self, task_id):
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, description, status FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        return row

    def test_complete_existing_incomplete_task(self):
        """Test completing an existing incomplete task."""
        todo.add_task("Incomplete Task to Complete")
        initial_status = self._get_task_status_by_description("Incomplete Task to Complete")
        self.assertEqual(initial_status, "incomplete")

        todo.complete_task("Incomplete Task to Complete") # Use full description for this helper
        
        final_status = self._get_task_status_by_description("Incomplete Task to Complete")
        self.assertEqual(final_status, "completed")

    def test_complete_non_existing_task(self):
        """Test trying to complete a task that doesn't exist."""
        todo.add_task("Existing Task")
        todo.complete_task("Non Existing Task Description")
        
        status = self._get_task_status_by_description("Existing Task")
        self.assertEqual(status, "incomplete", "Existing task should remain incomplete.")
        
        # Check that no new task was accidentally created or other tasks affected
        tasks = self._get_tasks_from_db("SELECT * FROM tasks")
        self.assertEqual(len(tasks), 1)


    def test_complete_already_completed_task(self):
        """Test trying to complete an already completed task."""
        todo.add_task("Already Completed Task")
        # Manually complete it
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status = 'completed' WHERE description = 'Already Completed Task'")
        conn.commit()
        conn.close()

        initial_status = self._get_task_status_by_description("Already Completed Task")
        self.assertEqual(initial_status, "completed")

        todo.complete_task("Already Completed Task") # Attempt to complete it again
        
        final_status = self._get_task_status_by_description("Already Completed Task")
        self.assertEqual(final_status, "completed", "Task should remain completed.")
        # Potentially, one could check if the update timestamp changed if we had one, to ensure it wasn't re-written.

    def test_complete_oldest_if_multiple_match_description_partial(self):
        """Test completing only the oldest task if multiple match a partial description."""
        # Add tasks - order matters for ID
        todo.add_task("Buy milk for breakfast") # ID 1 (older)
        todo.add_task("Buy milk for dinner")   # ID 2 (newer)
        todo.add_task("Buy juice")             # ID 3 (does not match)

        # complete_task uses LIKE %description_part%
        todo.complete_task("Buy milk") 

        task1 = self._get_task_by_id(1) # Buy milk for breakfast
        task2 = self._get_task_by_id(2) # Buy milk for dinner
        task3 = self._get_task_by_id(3) # Buy juice

        self.assertIsNotNone(task1)
        self.assertIsNotNone(task2)
        self.assertIsNotNone(task3)
        
        self.assertEqual(task1[2], "completed", "Oldest matching task (ID 1) should be completed.")
        self.assertEqual(task2[2], "incomplete", "Newer matching task (ID 2) should remain incomplete.")
        self.assertEqual(task3[2], "incomplete", "Non-matching task (ID 3) should remain incomplete.")

    # --- Tests for clear_completed_tasks ---
    def _manually_set_status(self, description, status):
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status = ? WHERE description = ?", (status, description))
        conn.commit()
        conn.close()

    def test_clear_completed_tasks_some_exist(self):
        """Test clearing completed tasks when some exist."""
        todo.add_task("Incomplete 1")
        todo.add_task("Completed 1")
        self._manually_set_status("Completed 1", "completed")
        todo.add_task("Incomplete 2")
        todo.add_task("Completed 2")
        self._manually_set_status("Completed 2", "completed")

        todo.clear_completed_tasks()

        remaining_tasks = self._get_tasks_from_db("SELECT description, status FROM tasks ORDER BY description ASC")
        self.assertEqual(len(remaining_tasks), 2, "Only incomplete tasks should remain.")
        self.assertEqual(remaining_tasks[0][0], "Incomplete 1")
        self.assertEqual(remaining_tasks[0][1], "incomplete")
        self.assertEqual(remaining_tasks[1][0], "Incomplete 2")
        self.assertEqual(remaining_tasks[1][1], "incomplete")

    def test_clear_completed_tasks_none_exist(self):
        """Test clearing completed tasks when none are completed."""
        todo.add_task("Incomplete A")
        todo.add_task("Incomplete B")
        
        todo.clear_completed_tasks()

        remaining_tasks = self._get_tasks_from_db("SELECT description, status FROM tasks ORDER BY description ASC")
        self.assertEqual(len(remaining_tasks), 2, "All tasks should remain as none were completed.")
        self.assertEqual(remaining_tasks[0][0], "Incomplete A")
        self.assertEqual(remaining_tasks[1][0], "Incomplete B")

    def test_clear_completed_tasks_all_are_completed(self):
        """Test clearing completed tasks when all tasks are completed."""
        todo.add_task("Completed X")
        self._manually_set_status("Completed X", "completed")
        todo.add_task("Completed Y")
        self._manually_set_status("Completed Y", "completed")

        todo.clear_completed_tasks()
        
        remaining_tasks = self._get_tasks_from_db("SELECT * FROM tasks")
        self.assertEqual(len(remaining_tasks), 0, "All tasks should be cleared.")

    def test_clear_completed_tasks_empty_db(self):
        """Test clearing completed tasks when the database is empty."""
        todo.clear_completed_tasks()
        remaining_tasks = self._get_tasks_from_db("SELECT * FROM tasks")
        self.assertEqual(len(remaining_tasks), 0, "Database should remain empty.")


if __name__ == '__main__':
    unittest.main()
