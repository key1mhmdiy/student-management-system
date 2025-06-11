import tkinter as tk
from tkinter import *
from tkinter import ttk,messagebox
from style import apply_styles
from database import CREATE_TABLE,INSERT_STUDENTS, SHOW_ALL_STUDENTS, SEARCH_STUDENTS, UPDATE_STUDENTS, DELETE_STUDENTS
CREATE_TABLE()

win=tk.Tk()
win.title("Students Management System")
win.geometry("600x400")
win.resizable(False, False)

style = ttk.Style()
style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
style.configure("Treeview", font=("Helvetica", 10), rowheight=25)

selected_id = None

def show_students_in_treeview():
    for item in tree.get_children():
        tree.delete(item)
    students = SHOW_ALL_STUDENTS()
    for student in students:
        tree.insert("", "end", values=(student["id"], student["name"], student["family"], student["age"], student["grade"]))

    global selected_id
    selected_id = None
    entry_name.delete(0, tk.END)
    entry_family.delete(0, tk.END)
    entry_age.delete(0, tk.END)
    entry_grade.delete(0, tk.END)

def on_tree_select(event):
    global selected_id
    selected_item=tree.focus()
    if not selected_item:
        return
    
    values=tree.item(selected_item,"values")
    selected_id=int(values[0])

    entry_name.delete(0,tk.END)
    entry_name.insert(0, values[1])

    entry_family.delete(0,tk.END)
    entry_family.insert(0, values[2])

    entry_age.delete(0,tk.END)
    entry_age.insert(0, values[3])

    entry_grade.delete(0,tk.END)
    entry_grade.insert(0, values[4])

def add_students():
    try:
        name=entry_name.get()
        family=entry_family.get()
        age=entry_age.get()
        grade=entry_grade.get()
        INSERT_STUDENTS(name,family,int(age),int(grade))
        show_students_in_treeview()
    except ValueError:
        messagebox.showerror("Error", "Please enter numeric values for Age and Grade")

def delete_students():
    global selected_id
    if selected_id is None:
        return
    DELETE_STUDENTS(selected_id)
    show_students_in_treeview()

    entry_name.delete(0,tk.END)
    entry_family.delete(0,tk.END)
    entry_age.delete(0,tk.END)
    entry_grade.delete(0,tk.END)
    selected_id=None

def update_students():
    global selected_id
    if selected_id is None:
        return
    
    name=entry_name.get()
    family=entry_family.get()
    age=int(entry_age.get())
    grade=int(entry_grade.get())

    UPDATE_STUDENTS(selected_id,name,family,age,grade)
    show_students_in_treeview()

def search_students():
    keyword=entry_search.get()
    if not keyword:
        show_students_in_treeview()
        return
    results=SEARCH_STUDENTS(keyword)
    for item in tree.get_children():
        tree.delete(item)
    for student in results:
        tree.insert("","end",values=(student["id"],student["name"],student["family"],student["age"],student["grade"]))   


tree = ttk.Treeview(win, columns=("ID", "Name", "Family", "Age", "Grade"), show="headings")
scrollbar = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
scrollbar.place(x=570, y=150, height=200)
tree.configure(yscrollcommand=scrollbar.set)

tree.heading("ID", text="ID")
tree.heading("Name", text="Name")
tree.heading("Family", text="Family")
tree.heading("Age", text="Age")
tree.heading("Grade", text="Grade")

for index, student in enumerate(SHOW_ALL_STUDENTS()):
    tag = "evenrow" if index % 2 == 0 else "oddrow"
    tree.insert("", "end", values=(student["id"], student["name"], student["family"], student["age"], student["grade"]), tags=(tag,))

tree.place(x=20, y=150, width=550, height=200)
tree.bind("<<TreeviewSelect>>", on_tree_select)
scrollbar.config(command=tree.yview)

row_styles=apply_styles()
tree.tag_configure("evenrow", **row_styles["evenrow"])
tree.tag_configure("oddrow", **row_styles["oddrow"])

def create_labeled_entry(label_text, x, y):
    label = tk.Label(win, text=label_text, bg="#f0f2f5")
    label.place(x=x, y=y)
    entry = tk.Entry(win)
    entry.place(x=x, y=y+20)
    return entry

entry_name = create_labeled_entry("NAME", 20, 10)
entry_family = create_labeled_entry("FAMILY", 160, 10)
entry_age = create_labeled_entry("AGE", 300, 10)
entry_grade = create_labeled_entry("GRADE", 440, 10)
label_search = tk.Label(win,text="Search (Name/Family):")
label_search.place(x=20, y=70)
entry_search = tk.Entry(win)
entry_search.place(x=160, y=70)

button_search = ttk.Button(win, text="SEARCH", command=search_students)
button_search.place(x=320, y=65)

button_add=ttk.Button(win,text="ADD_STUDENTS",command=add_students)
button_add.place(x=20,y=110)

button_delete=ttk.Button(win,text="DELETE_STUDENT",command=delete_students)
button_delete.place(x=160,y=110)

button_update = ttk.Button(win, text="UPDATE_STUDENT", command=update_students)
button_update.place(x=300, y=110)

show_students_in_treeview()
win.mainloop()
