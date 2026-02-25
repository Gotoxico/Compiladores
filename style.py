from tkinter import ttk

def styleConfig():
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "TButton",
        font=("Segoe UI", 11, "bold"),
        padding=10
    )

    style.configure(
        "Treeview",
        background="white",
        foreground="#333333",
        rowheight=28,
        fieldbackground="white",
        font=("Segoe UI", 11)
    )

    style.configure(
        "Treeview.Heading",
        font=("Segoe UI", 11, "bold"),
        background="#1f4e79",
        foreground="white"
    )

    style.map(
        "Treeview",
        background=[("selected", "#4a90e2")],
        foreground=[("selected", "white")]
    )

    return style