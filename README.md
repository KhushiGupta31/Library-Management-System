# Library Management System (Python)

A beginner-friendly desktop application built with Python's Tkinter GUI and SQLite database.

## Features
- Add, update, search, and delete books
- Track total and available copies
- Issue a book to a borrower
- Return an issued book
- View issue/return history
- Saves data in `library.db` automatically

## Requirements
- Python 3.10 or newer recommended
- Tkinter (usually included with Python on Windows)
- No third-party Python packages required

## Setup on Windows
1. Extract `Library_Management_System.zip` to a folder.
2. Install Python from https://www.python.org/downloads/ if it is not installed.
3. During Python installation, tick **Add python.exe to PATH**.
4. Open the extracted folder.
5. Click the folder address bar, type `cmd`, and press Enter.
6. Run:

   ```bat
   python main.py
   ```

   If that command does not work, try:

   ```bat
   py main.py
   ```

The application window should open. The `library.db` database file is created automatically in the same folder on first run.

## Basic usage
1. Enter a book title, author, category, and number of copies.
2. Click **Add Book**.
3. Select a book in the table to fill the form.
4. Edit its details and click **Update Selected** to save changes.
5. Use the search box to filter by title, author, or category.
6. To issue a book, select it, enter the borrower's name, and click **Issue Selected Book**.
7. To return a book, select it and click **Return Selected Book**.
8. Click **View Loan Records** to see issue and return history.

## Important notes
- Do not delete `library.db` if you want to keep your saved records.
- Make a backup copy of `library.db` before moving the project or changing its database.
- The Return button returns the oldest active issue for the selected book. For a classroom project this keeps the workflow simple.
- This is a learning/demo project, not a secured multi-user library system.

## Project files
- `main.py` — application source code
- `README.md` — setup and usage instructions
- `requirements.txt` — third-party dependencies (none required)
