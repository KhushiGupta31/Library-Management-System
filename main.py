import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

DB_NAME = "library.db"


def connect_db():
    return sqlite3.connect(DB_NAME)

def sum(a,b):
    return a+b

print(sum(3,2))
    

def setup_database():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                category TEXT DEFAULT '',
                total_copies INTEGER NOT NULL DEFAULT 1,
                available_copies INTEGER NOT NULL DEFAULT 1
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS loans (
                loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                borrower TEXT NOT NULL,
                issue_date TEXT NOT NULL,
                return_date TEXT,
                status TEXT NOT NULL DEFAULT 'Issued',
                FOREIGN KEY (book_id) REFERENCES books(book_id)
            )
        """)


class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("1000x650")
        self.root.minsize(850, 550)
        self.root.configure(bg="#f3f5f7")

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TLabel", background="#f3f5f7", font=("Segoe UI", 10))

        heading = tk.Label(
            root, text="Library Management System",
            font=("Segoe UI", 20, "bold"), bg="#f3f5f7", fg="#183153"
        )
        heading.pack(pady=(15, 8))

        form = ttk.LabelFrame(root, text="Book details", padding=12)
        form.pack(fill="x", padx=18, pady=6)

        self.title_var = tk.StringVar()
        self.author_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.copies_var = tk.StringVar(value="1")
        self.search_var = tk.StringVar()

        fields = [
            ("Title", self.title_var),
            ("Author", self.author_var),
            ("Category", self.category_var),
            ("Copies", self.copies_var),
        ]
        for col, (label, var) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=0, column=col, sticky="w", padx=5)
            ttk.Entry(form, textvariable=var, width=25 if col < 3 else 10).grid(
                row=1, column=col, sticky="ew", padx=5, pady=(3, 0)
            )
        form.columnconfigure(0, weight=2)
        form.columnconfigure(1, weight=2)
        form.columnconfigure(2, weight=2)

        actions = ttk.Frame(root)
        actions.pack(fill="x", padx=18, pady=7)
        ttk.Button(actions, text="Add Book", command=self.add_book).pack(side="left", padx=3)
        ttk.Button(actions, text="Update Selected", command=self.update_book).pack(side="left", padx=3)
        ttk.Button(actions, text="Delete Selected", command=self.delete_book).pack(side="left", padx=3)
        ttk.Button(actions, text="Clear Form", command=self.clear_form).pack(side="left", padx=3)

        search_frame = ttk.Frame(root)
        search_frame.pack(fill="x", padx=18, pady=(5, 7))
        ttk.Label(search_frame, text="Search title, author, or category:").pack(side="left", padx=(0, 8))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=35)
        search_entry.pack(side="left")
        search_entry.bind("<KeyRelease>", lambda _event: self.load_books())
        ttk.Button(search_frame, text="Refresh", command=self.load_books).pack(side="left", padx=8)

        table_frame = ttk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=18, pady=5)
        columns = ("id", "title", "author", "category", "total", "available")
        self.books_tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        headings = {
            "id": "ID", "title": "Title", "author": "Author", "category": "Category",
            "total": "Total Copies", "available": "Available"
        }
        widths = {"id": 55, "title": 260, "author": 200, "category": 140, "total": 100, "available": 100}
        for col in columns:
            self.books_tree.heading(col, text=headings[col])
            self.books_tree.column(col, width=widths[col], anchor="w" if col in ("title", "author", "category") else "center")
        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.books_tree.yview)
        xscroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.books_tree.xview)
        self.books_tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.books_tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.books_tree.bind("<<TreeviewSelect>>", self.on_select)

        loan_frame = ttk.LabelFrame(root, text="Issue / return a book", padding=10)
        loan_frame.pack(fill="x", padx=18, pady=(5, 14))
        self.borrower_var = tk.StringVar()
        ttk.Label(loan_frame, text="Borrower's name").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Entry(loan_frame, textvariable=self.borrower_var, width=28).grid(row=1, column=0, padx=5, pady=3)
        ttk.Button(loan_frame, text="Issue Selected Book", command=self.issue_book).grid(row=1, column=1, padx=8)
        ttk.Button(loan_frame, text="Return Selected Book", command=self.return_book).grid(row=1, column=2, padx=8)
        ttk.Button(loan_frame, text="View Loan Records", command=self.view_loans).grid(row=1, column=3, padx=8)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(root, textvariable=self.status_var, anchor="w", bg="#e7edf4", fg="#183153", padx=12, pady=5).pack(fill="x", side="bottom")

        self.selected_book_id = None
        self.load_books()

    def selected_id(self):
        selected = self.books_tree.selection()
        if not selected:
            messagebox.showwarning("Select a book", "Please select a book from the table first.")
            return None
        return int(self.books_tree.item(selected[0], "values")[0])

    def add_book(self):
        title = self.title_var.get().strip()
        author = self.author_var.get().strip()
        category = self.category_var.get().strip()
        try:
            copies = int(self.copies_var.get())
            if copies < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid copies", "Copies must be a whole number greater than zero.")
            return
        if not title or not author:
            messagebox.showerror("Missing details", "Please enter both title and author.")
            return
        with connect_db() as conn:
            conn.execute(
                "INSERT INTO books(title, author, category, total_copies, available_copies) VALUES(?,?,?,?,?)",
                (title, author, category, copies, copies)
            )
        self.clear_form()
        self.load_books()
        self.status_var.set(f'Added "{title}".')

    def update_book(self):
        book_id = self.selected_id()
        if book_id is None:
            return
        title = self.title_var.get().strip()
        author = self.author_var.get().strip()
        category = self.category_var.get().strip()
        try:
            new_total = int(self.copies_var.get())
            if new_total < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid copies", "Copies must be a whole number greater than zero.")
            return
        if not title or not author:
            messagebox.showerror("Missing details", "Please enter both title and author.")
            return
        with connect_db() as conn:
            row = conn.execute(
                "SELECT total_copies, available_copies FROM books WHERE book_id=?", (book_id,)
            ).fetchone()
            if not row:
                messagebox.showerror("Not found", "This book no longer exists.")
                return
            old_total, old_available = row
            already_issued = old_total - old_available
            if new_total < already_issued:
                messagebox.showerror("Too few copies", f"{already_issued} copy/copies are currently issued. Total copies cannot be less than that.")
                return
            new_available = new_total - already_issued
            conn.execute(
                "UPDATE books SET title=?, author=?, category=?, total_copies=?, available_copies=? WHERE book_id=?",
                (title, author, category, new_total, new_available, book_id)
            )
        self.load_books()
        self.status_var.set(f"Updated book ID {book_id}.")

    def delete_book(self):
        book_id = self.selected_id()
        if book_id is None:
            return
        with connect_db() as conn:
            active = conn.execute(
                "SELECT COUNT(*) FROM loans WHERE book_id=? AND status='Issued'", (book_id,)
            ).fetchone()[0]
            if active:
                messagebox.showerror("Book is issued", "Return all issued copies before deleting this book.")
                return
            if not messagebox.askyesno("Confirm delete", "Delete the selected book and its loan history?"):
                return
            conn.execute("DELETE FROM loans WHERE book_id=?", (book_id,))
            conn.execute("DELETE FROM books WHERE book_id=?", (book_id,))
        self.clear_form()
        self.load_books()
        self.status_var.set(f"Deleted book ID {book_id}.")

    def clear_form(self):
        self.title_var.set("")
        self.author_var.set("")
        self.category_var.set("")
        self.copies_var.set("1")
        self.selected_book_id = None
        for item in self.books_tree.selection():
            self.books_tree.selection_remove(item)

    def on_select(self, _event=None):
        selected = self.books_tree.selection()
        if not selected:
            return
        values = self.books_tree.item(selected[0], "values")
        self.selected_book_id = int(values[0])
        with connect_db() as conn:
            row = conn.execute(
                "SELECT title, author, category, total_copies FROM books WHERE book_id=?",
                (self.selected_book_id,)
            ).fetchone()
        if row:
            self.title_var.set(row[0])
            self.author_var.set(row[1])
            self.category_var.set(row[2] or "")
            self.copies_var.set(str(row[3]))

    def load_books(self):
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        term = f"%{self.search_var.get().strip()}%"
        with connect_db() as conn:
            rows = conn.execute("""
                SELECT book_id, title, author, category, total_copies, available_copies
                FROM books
                WHERE title LIKE ? OR author LIKE ? OR category LIKE ?
                ORDER BY title COLLATE NOCASE
            """, (term, term, term)).fetchall()
        for row in rows:
            self.books_tree.insert("", "end", values=row)
        self.status_var.set(f"{len(rows)} book record(s) shown.")

    def issue_book(self):
        book_id = self.selected_id()
        if book_id is None:
            return
        borrower = self.borrower_var.get().strip()
        if not borrower:
            messagebox.showerror("Missing borrower", "Enter the borrower's name.")
            return
        with connect_db() as conn:
            row = conn.execute(
                "SELECT title, available_copies FROM books WHERE book_id=?", (book_id,)
            ).fetchone()
            if not row:
                messagebox.showerror("Not found", "Book not found.")
                return
            title, available = row
            if available < 1:
                messagebox.showwarning("Unavailable", "No copies of this book are currently available.")
                return
            conn.execute(
                "INSERT INTO loans(book_id, borrower, issue_date, status) VALUES(?,?,?,'Issued')",
                (book_id, borrower, date.today().isoformat())
            )
            conn.execute("UPDATE books SET available_copies=available_copies-1 WHERE book_id=?", (book_id,))
        self.load_books()
        self.status_var.set(f'Issued "{title}" to {borrower}.')

    def return_book(self):
        book_id = self.selected_id()
        if book_id is None:
            return
        with connect_db() as conn:
            loan = conn.execute("""
                SELECT loan_id, borrower, issue_date
                FROM loans
                WHERE book_id=? AND status='Issued'
                ORDER BY loan_id
                LIMIT 1
            """, (book_id,)).fetchone()
            if not loan:
                messagebox.showinfo("No active issue", "There are no issued copies of this book to return.")
                return
            loan_id, borrower, issue_date = loan
            conn.execute(
                "UPDATE loans SET status='Returned', return_date=? WHERE loan_id=?",
                (date.today().isoformat(), loan_id)
            )
            conn.execute("UPDATE books SET available_copies=available_copies+1 WHERE book_id=?", (book_id,))
        self.load_books()
        self.status_var.set(f"Returned book from {borrower} (issued {issue_date}).")

    def view_loans(self):
        window = tk.Toplevel(self.root)
        window.title("Loan records")
        window.geometry("850x400")
        columns = ("loan_id", "book_id", "title", "borrower", "issue_date", "return_date", "status")
        tree = ttk.Treeview(window, columns=columns, show="headings")
        labels = {
            "loan_id": "Loan ID", "book_id": "Book ID", "title": "Book title",
            "borrower": "Borrower", "issue_date": "Issue date",
            "return_date": "Return date", "status": "Status"
        }
        for col in columns:
            tree.heading(col, text=labels[col])
            tree.column(col, width=115, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        with connect_db() as conn:
            rows = conn.execute("""
                SELECT l.loan_id, l.book_id, b.title, l.borrower, l.issue_date, 
                       COALESCE(l.return_date, '-'), l.status
                FROM loans l JOIN books b ON b.book_id=l.book_id
                ORDER BY l.loan_id DESC
            """).fetchall()
        for row in rows:
            tree.insert("", "end", values=row)


if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()
