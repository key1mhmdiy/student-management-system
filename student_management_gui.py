import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
import re


class Database:
    def __init__(self, db_file="students.db"):
        self.db_file = db_file
        self.create_table()

    def connect(self):
        try:
            conn = sqlite3.connect(self.db_file)
            return conn
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            return None

    def create_table(self):
        conn = self.connect()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS student (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        age INTEGER NOT NULL,
                        grade INTEGER NOT NULL
                    )
                """)
                conn.commit()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
            finally:
                conn.close()

    def fetch_all(self):
        conn = self.connect()
        rows = []
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT * FROM student")
                rows = cur.fetchall()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
            finally:
                conn.close()
        return rows

    def search(self, keyword):
        conn = self.connect()
        rows = []
        if conn:
            try:
                cur = conn.cursor()
                like_keyword = f"%{keyword}%"
                cur.execute("""
                    SELECT * FROM student 
                    WHERE name LIKE ? OR id LIKE ?
                """, (like_keyword, like_keyword))
                rows = cur.fetchall()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
            finally:
                conn.close()
        return rows

    def insert(self, name, age, grade):
        conn = self.connect()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("INSERT INTO student (name, age, grade) VALUES (?, ?, ?)", (name, age, grade))
                conn.commit()
                return True
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
                return False
            finally:
                conn.close()
        return False

    def update(self, student_id, name, age, grade):
        conn = self.connect()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("UPDATE student SET name=?, age=?, grade=? WHERE id=?", (name, age, grade, student_id))
                conn.commit()
                return True
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
                return False
            finally:
                conn.close()
        return False

    def delete(self, student_id):
        conn = self.connect()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM student WHERE id=?", (student_id,))
                conn.commit()
                return True
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
                return False
            finally:
                conn.close()
        return False


class StudentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("600x650")
        self.db = Database()

        # Frame بالا: جستجو و اسکرول
        frame_top = tk.Frame(root)
        frame_top.pack(pady=10, fill='x')

        tk.Label(frame_top, text="Search by Name or ID:", font=("Arial", 12)).pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        self.entry_search = tk.Entry(frame_top, textvariable=self.search_var, font=("Arial", 12), width=25)
        self.entry_search.pack(side='left', padx=5)
        self.entry_search.bind("<KeyRelease>", self.on_search)

        btn_clear_search = tk.Button(frame_top, text="Clear Search", command=self.clear_search)
        btn_clear_search.pack(side='left', padx=5)

        # Frame وسط: Treeview و اسکرول عمودی
        frame_tree = tk.Frame(root)
        frame_tree.pack(pady=10, fill='both', expand=True)

        columns = ("id", "name", "age", "grade")

        self.tree_scrollbar = ttk.Scrollbar(frame_tree, orient="vertical")
        self.tree_scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(frame_tree, columns=columns, show="headings",
                                 yscrollcommand=self.tree_scrollbar.set, selectmode='browse')
        self.tree.pack(fill='both', expand=True)
        self.tree_scrollbar.config(command=self.tree.yview)

        for col in columns:
            self.tree.heading(col, text=col.title(), command=lambda _col=col: self.sort_column(_col, False))
            self.tree.column(col, width=120, anchor='center')

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Frame فرم ورود اطلاعات
        frame_form = tk.LabelFrame(root, text="Student Details", font=("Arial", 12))
        frame_form.pack(pady=10, padx=10, fill='x')

        labels = ["ID", "Name", "Age", "Grade"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(frame_form, text=label, font=("Arial", 12)).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            ent = tk.Entry(frame_form, font=("Arial", 12))
            ent.grid(row=i, column=1, padx=10, pady=5, sticky="w")
            self.entries[label.lower()] = ent

        self.entries["id"].config(state="readonly")

        # Frame دکمه‌ها
        frame_buttons = tk.Frame(root)
        frame_buttons.pack(pady=10)

        btn_add = tk.Button(frame_buttons, text="Add Student", width=15, command=self.add_student)
        btn_add.grid(row=0, column=0, padx=5, pady=5)

        btn_update = tk.Button(frame_buttons, text="Update Student", width=15, command=self.update_student)
        btn_update.grid(row=0, column=1, padx=5, pady=5)

        btn_delete = tk.Button(frame_buttons, text="Delete Student", width=15, command=self.delete_student)
        btn_delete.grid(row=1, column=0, padx=5, pady=5)

        btn_clear = tk.Button(frame_buttons, text="Clear Fields", width=15, command=self.clear_fields)
        btn_clear.grid(row=1, column=1, padx=5, pady=5)

        btn_export = tk.Button(frame_buttons, text="Export to CSV", width=32, command=self.export_csv)
        btn_export.grid(row=2, column=0, columnspan=2, pady=10)

        self.load_students()

    # اعتبارسنجی
    def validate_name(self, name):
        if not name:
            return False
        return bool(re.match(r"^[A-Za-z\s]+$", name))

    def validate_age(self, age):
        try:
            age_int = int(age)
            return 1 <= age_int <= 150
        except:
            return False

    def validate_grade(self, grade):
        try:
            grade_int = int(grade)
            return 0 <= grade_int <= 100
        except:
            return False

    # بارگذاری دانش‌آموزها
    def load_students(self, rows=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if rows is None:
            rows = self.db.fetch_all()

        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def on_search(self, event):
        keyword = self.search_var.get().strip()
        if keyword == "":
            self.load_students()
        else:
            rows = self.db.search(keyword)
            self.load_students(rows)

    def clear_search(self):
        self.search_var.set("")
        self.load_students()

    def on_tree_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        values = self.tree.item(selected, "values")

        self.entries["id"].config(state="normal")
        self.entries["id"].delete(0, tk.END)
        self.entries["id"].insert(0, values[0])
        self.entries["id"].config(state="readonly")

        self.entries["name"].delete(0, tk.END)
        self.entries["name"].insert(0, values[1])

        self.entries["age"].delete(0, tk.END)
        self.entries["age"].insert(0, values[2])

        self.entries["grade"].delete(0, tk.END)
        self.entries["grade"].insert(0, values[3])

    def clear_fields(self):
        for key in self.entries:
            self.entries[key].config(state="normal")
            self.entries[key].delete(0, tk.END)
        self.entries["id"].config(state="readonly")

    def add_student(self):
        name = self.entries["name"].get().strip()
        age = self.entries["age"].get().strip()
        grade = self.entries["grade"].get().strip()

        if not self.validate_name(name):
            messagebox.showwarning("Validation Error", "Name must contain only letters and spaces and not be empty.")
            return

        if not self.validate_age(age):
            messagebox.showwarning("Validation Error", "Age must be an integer between 1 and 150.")
            return

        if not self.validate_grade(grade):
            messagebox.showwarning("Validation Error", "Grade must be an integer between 0 and 100.")
            return

        if self.db.insert(name, int(age), int(grade)):
            messagebox.showinfo("Success", f"Student '{name}' added successfully.")
            self.load_students()
            self.clear_fields()

    def update_student(self):
        student_id = self.entries["id"].get().strip()
        name = self.entries["name"].get().strip()
        age = self.entries["age"].get().strip()
        grade = self.entries["grade"].get().strip()

        if not student_id:
            messagebox.showwarning("Warning", "Please select a student to update.")
            return

        if not self.validate_name(name):
            messagebox.showwarning("Validation Error", "Name must contain only letters and spaces and not be empty.")
            return

        if not self.validate_age(age):
            messagebox.showwarning("Validation Error", "Age must be an integer between 1 and 150.")
            return

        if not self.validate_grade(grade):
            messagebox.showwarning("Validation Error", "Grade must be an integer between 0 and 100.")
            return

        if self.db.update(student_id, name, int(age), int(grade)):
            messagebox.showinfo("Success", f"Student ID {student_id} updated successfully.")
            self.load_students()
            self.clear_fields()

    def delete_student(self):
        student_id = self.entries["id"].get().strip()
        if not student_id:
            messagebox.showwarning("Warning", "Please select a student to delete.")
            return

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete student ID {student_id}?"):
            if self.db.delete(student_id):
                messagebox.showinfo("Success", f"Student ID {student_id} deleted successfully.")
                self.load_students()
                self.clear_fields()

    def sort_column(self, col, reverse):
        # گرفتن داده‌های نمایش داده شده
        data_list = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        # تلاش برای تبدیل به عدد (برای سن و نمره و آی‌دی)
        try:
            data_list.sort(key=lambda t: int(t[0]), reverse=reverse)
        except ValueError:
            data_list.sort(key=lambda t: t[0].lower(), reverse=reverse)

        # جابجایی داده‌ها در Treeview
        for index, (val, k) in enumerate(data_list):
            self.tree.move(k, '', index)

        # تغییر جهت مرتب‌سازی برای کلیک بعدی
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def export_csv(self):
        rows = self.db.fetch_all()
        if not rows:
            messagebox.showinfo("No Data", "No student data to export.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv")],
                                                 title="Save as CSV")
        if not file_path:
            return

        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Name", "Age", "Grade"])
                writer.writerows(rows)
            messagebox.showinfo("Success", f"Data exported successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentApp(root)
    root.mainloop()
