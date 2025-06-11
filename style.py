from tkinter import ttk

def apply_styles():
    style = ttk.Style()

    style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
    style.configure("Treeview", font=("Helvetica", 10), rowheight=25)

    style.configure("TButton", font=("Helvetica", 10), padding=6)

    return {
        "evenrow": {"background": "#f2f2f2"},
        "oddrow": {"background": "#ffffff"}
    }
