
import os
import sys
import tempfile
import subprocess
import zipfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

# ==========================================
# TEMP FILE MANAGEMENT SYSTEM
# PROFESSIONAL GUI DASHBOARD
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
current_folder = tempfile.gettempdir()
selected_paths = set()
activity_history = []

root = tk.Tk()
root.title("Temp File Management System")
root.geometry("1250x780")
root.minsize(1000, 650)
root.configure(bg="#f1f5f9")

# COLORS
DARK = "#14213d"
SIDEBAR = "#101b32"
BLUE = "#2563eb"
LIGHT_BLUE = "#dbeafe"
BG = "#f1f5f9"
WHITE = "#ffffff"
TEXT = "#1e293b"
GRAY = "#64748b"
RED = "#dc2626"
GREEN = "#15803d"

# ==========================================
# STYLE
# ==========================================

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background=WHITE,
    foreground=TEXT,
    rowheight=32,
    fieldbackground=WHITE,
    font=("Segoe UI", 10)
)

style.configure(
    "Treeview.Heading",
    background="#e2e8f0",
    foreground=DARK,
    font=("Segoe UI", 10, "bold"),
    padding=9
)

style.map(
    "Treeview",
    background=[("selected", LIGHT_BLUE)],
    foreground=[("selected", DARK)]
)

# ==========================================
# FUNCTIONS
# ==========================================

def human_size(size):
    if size < 1024:
        return f"{size} B"
    elif size < 1024 ** 2:
        return f"{size / 1024:.2f} KB"
    elif size < 1024 ** 3:
        return f"{size / (1024 ** 2):.2f} MB"
    return f"{size / (1024 ** 3):.2f} GB"


def log_activity(message):
    time_now = datetime.now().strftime("%H:%M:%S")
    entry = f"[{time_now}] {message}"

    activity_history.append(entry)

    activity_box.insert("end", entry + "\n")
    activity_box.see("end")

    status_label.config(text=message)


def update_selection_count():
    selected_count.config(
        text=f"Selected Files: {len(selected_paths)}"
    )
 

def load_files():
    global selected_paths

    for item in file_table.get_children():
        file_table.delete(item)

    if not os.path.isdir(current_folder):
        messagebox.showerror("Error", "Folder not found!")
        return

    search_text = search_var.get().lower().strip()
    total_count = 0
    total_size = 0
    visible_count = 0
    valid_paths = set()

    try:
        with os.scandir(current_folder) as entries:
            files = sorted(entries, key=lambda e: e.name.lower())

            for entry in files:
                if not entry.is_file(follow_symlinks=False):
                    continue

                try:
                    info = entry.stat(follow_symlinks=False)
                    path = os.path.abspath(entry.path)

                    total_count += 1
                    total_size += info.st_size
                    valid_paths.add(path)

                    if search_text and search_text not in entry.name.lower():
                        continue

                    extension = os.path.splitext(entry.name)[1] or "File"

                    modified = datetime.fromtimestamp(
                        info.st_mtime
                    ).strftime("%d-%m-%Y %H:%M")

                    checkbox = "☑" if path in selected_paths else "☐"

                    file_table.insert(
                        "",
                        "end",
                        values=(
                            checkbox,
                            entry.name,
                            extension,
                            human_size(info.st_size),
                            modified,
                            path
                        )
                    )

                    visible_count += 1

                except (PermissionError, OSError):
                    continue

        # Remove selections for files no longer present
        selected_paths.intersection_update(valid_paths)

        total_label.config(text=str(total_count))
        size_label.config(text=human_size(total_size))

        visible_label.config(
            text=f"Displaying {visible_count} of {total_count} files"
        )

        update_selection_count()

    except (PermissionError, OSError) as error:
        messagebox.showerror("Folder Error", str(error))


def choose_folder():
    global current_folder

    folder = filedialog.askdirectory(
        initialdir=current_folder,
        title="Select TEMP Folder"
    )

    if folder:
        current_folder = folder
        selected_paths.clear()
        folder_label.config(text=current_folder)

        load_files()
        log_activity("Folder changed successfully")


def refresh_files():
    load_files()
    log_activity("File list refreshed")


def toggle_file(event):
    region = file_table.identify_region(event.x, event.y)

    if region != "cell":
        return

    column = file_table.identify_column(event.x)
    item = file_table.identify_row(event.y)

    if not item:
        return

    # First column is the checkbox
    if column == "#1":
        values = list(file_table.item(item, "values"))
        path = values[5]

        if path in selected_paths:
            selected_paths.remove(path)
            values[0] = "☐"
        else:
            selected_paths.add(path)
            values[0] = "☑"

        file_table.item(item, values=values)
        update_selection_count()


def select_all():
    search_text = search_var.get().lower().strip()

    for item in file_table.get_children():
        values = list(file_table.item(item, "values"))
        path = values[5]

        selected_paths.add(path)
        values[0] = "☑"

        file_table.item(item, values=values)

    update_selection_count()
    log_activity("All visible files selected")


def clear_selection():
    selected_paths.clear()
    load_files()
    log_activity("Selection cleared")


def search_files(*args):
    load_files()


def run_module(filename):

    file_path = os.path.join(BASE_DIR, filename)

    if not os.path.isfile(file_path):
        messagebox.showerror(
            "Error",
            filename + " not found!"
        )
        return

    try:
        if os.name == "nt":

            subprocess.Popen(
                [
                    "cmd.exe",
                    "/k",
                    sys.executable,
                    "-u",
                    file_path
                ],
                cwd=BASE_DIR,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )

        else:
            subprocess.Popen(
                [sys.executable, "-u", file_path],
                cwd=BASE_DIR
            )

        log_activity(filename + " started")

    except Exception as error:
        messagebox.showerror("Execution Error", str(error))


# ==========================================
# BACKUP SELECTED FILES
# ==========================================

def backup_selected():
    existing = [
        path for path in selected_paths
        if os.path.isfile(path)
    ]

    if not existing:
        messagebox.showwarning(
            "No Files Selected",
            "Please select files before creating backup."
        )
        return

    save_path = filedialog.asksaveasfilename(
        title="Save ZIP Backup",
        defaultextension=".zip",
        filetypes=[("ZIP Files", "*.zip")],
        initialfile="Temp_Backup.zip"
    )

    if not save_path:
        return

    try:
        with zipfile.ZipFile(
            save_path,
            "w",
            zipfile.ZIP_DEFLATED
        ) as zipf:

            for path in existing:
                zipf.write(path, arcname=os.path.basename(path))

        log_activity(
            f"ZIP backup created: {len(existing)} files"
        )

        messagebox.showinfo(
            "Backup Successful",
            f"{len(existing)} files backed up successfully!\n\n"
            f"Saved at:\n{save_path}"
        )

    except Exception as error:
        messagebox.showerror("Backup Error", str(error))


# ==========================================
# DELETE SELECTED FILES
# ==========================================

def delete_selected():
    existing = [
        path for path in selected_paths
        if os.path.isfile(path)
    ]

    if not existing:
        messagebox.showwarning(
            "No Files Selected",
            "Please select files to delete."
        )
        return

    confirm = messagebox.askyesno(
        "Confirm Deletion",
        f"Are you sure you want to permanently delete "
        f"{len(existing)} selected files?\n\n"
        "This action cannot be undone."
    )

    if not confirm:
        return

    deleted = 0
    failed = 0

    for path in existing:
        try:
            os.remove(path)
            deleted += 1
            selected_paths.discard(path)

        except OSError:
            failed += 1

    load_files()

    log_activity(
        f"Deleted: {deleted} files | Failed: {failed}"
    )

    messagebox.showinfo(
        "Delete Report",
        f"Successfully deleted: {deleted}\n"
        f"Failed: {failed}"
    )


# ==========================================
# ACTIVITY REPORT
# ==========================================

def activity_report():
    if not activity_history:
        messagebox.showinfo("Report", "No activity available.")
        return

    save_path = filedialog.asksaveasfilename(
        title="Save Activity Report",
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")],
        initialfile="Activity_Report.txt"
    )

    if not save_path:
        return

    try:
        with open(save_path, "w", encoding="utf-8") as report:
            report.write("TEMP FILE MANAGEMENT SYSTEM\n")
            report.write("=" * 45 + "\n\n")

            report.write("\n".join(activity_history))

        messagebox.showinfo(
            "Report Saved",
            "Activity report saved successfully!"
        )

    except OSError as error:
        messagebox.showerror("Report Error", str(error))


# ==========================================
# EXIT
# ==========================================

def exit_dashboard():
    if messagebox.askyesno(
        "Exit Dashboard",
        "Do you want to close the application?"
    ):
        root.destroy()


# ==========================================
# HEADER
# ==========================================

header = tk.Frame(root, bg=DARK, height=75)
header.pack(fill="x")
header.pack_propagate(False)

tk.Label(
    header,
    text="  TEMP FILE MANAGEMENT SYSTEM",
    font=("Segoe UI", 20, "bold"),
    bg=DARK,
    fg=WHITE
).pack(side="left", padx=15)

tk.Label(
    header,
    text="PROFESSIONAL BACKUP DASHBOARD",
    font=("Segoe UI", 10, "bold"),
    bg=DARK,
    fg="#93c5fd"
).pack(side="right", padx=25)


# ==========================================
# MAIN LAYOUT
# ==========================================

main = tk.Frame(root, bg=BG)
main.pack(fill="both", expand=True)

# ==========================================
# SIDEBAR
# ==========================================

sidebar = tk.Frame(main, bg=SIDEBAR, width=215)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

tk.Label(
    sidebar,
    text="WORKSPACE",
    font=("Segoe UI", 11, "bold"),
    bg=SIDEBAR,
    fg="#94a3b8"
).pack(anchor="w", padx=22, pady=(25, 15))


def sidebar_button(name, command, color="#1e293b"):
    tk.Button(
        sidebar,
        text=name,
        command=command,
        font=("Segoe UI", 10, "bold"),
        bg=color,
        fg=WHITE,
        activebackground=BLUE,
        activeforeground=WHITE,
        relief="flat",
        anchor="w",
        padx=18,
        pady=12,
        cursor="hand2"
    ).pack(fill="x", padx=9, pady=4)


sidebar_button("  📁  Select Folder", choose_folder)
sidebar_button("  🔄  Refresh Files", refresh_files)
sidebar_button("  🔍  Scan Files", lambda: run_module("scanner.py"))
sidebar_button("  📊  Analyze Files", lambda: run_module("analyzer.py"))
sidebar_button("  📂  File Selector", lambda: run_module("selector.py"))

tk.Label(
    sidebar,
    text="BACKUP TOOLS",
    font=("Segoe UI", 9, "bold"),
    bg=SIDEBAR,
    fg="#94a3b8"
).pack(anchor="w", padx=22, pady=(22, 8))

sidebar_button("  📦  Backup Selected", backup_selected, BLUE)
sidebar_button("  🗑  Delete Selected", delete_selected, "#7f1d1d")
sidebar_button("  📋  Activity Report", activity_report)

sidebar_button("  ✖  Exit Dashboard", exit_dashboard)

# ==========================================
# CONTENT AREA
# ==========================================

content = tk.Frame(main, bg=BG)
content.pack(side="left", fill="both", expand=True, padx=22, pady=18)

tk.Label(
    content,
    text="Dashboard Overview",
    font=("Segoe UI", 22, "bold"),
    bg=BG,
    fg=TEXT
).pack(anchor="w")

tk.Label(
    content,
    text="Monitor, select and manage your temporary files",
    font=("Segoe UI", 10),
    bg=BG,
    fg=GRAY
).pack(anchor="w", pady=(3, 15))


# ==========================================
# SUMMARY CARDS
# ==========================================

cards = tk.Frame(content, bg=BG)
cards.pack(fill="x", pady=(0, 15))


def create_card(parent, title, value, accent):
    card = tk.Frame(
        parent,
        bg=WHITE,
        highlightbackground="#dbe3ef",
        highlightthickness=1
    )

    card.pack(side="left", fill="both", expand=True, padx=(0, 12))

    tk.Label(
        card,
        text=title,
        font=("Segoe UI", 10, "bold"),
        bg=WHITE,
        fg=GRAY
    ).pack(anchor="w", padx=17, pady=(13, 3))

    number = tk.Label(
        card,
        text=value,
        font=("Segoe UI", 24, "bold"),
        bg=WHITE,
        fg=accent
    )
    number.pack(anchor="w", padx=17, pady=(0, 13))

    return number


total_label = create_card(
    cards, "TOTAL FILES", "0", BLUE
)

size_label = create_card(
    cards, "TOTAL SIZE", "0 B", GREEN
)


# ==========================================
# CURRENT FOLDER
# ==========================================

folder_frame = tk.Frame(content, bg=WHITE)
folder_frame.pack(fill="x", pady=(0, 12))

tk.Label(
    folder_frame,
    text="CURRENT FOLDER",
    font=("Segoe UI", 9, "bold"),
    bg=WHITE,
    fg=GRAY
).pack(anchor="w", padx=13, pady=(9, 2))

folder_label = tk.Label(
    folder_frame,
    text=current_folder,
    font=("Segoe UI", 10),
    bg=WHITE,
    fg=BLUE,
    anchor="w"
)
folder_label.pack(fill="x", padx=13, pady=(0, 9))


# ==========================================
# SEARCH AND SELECTION BAR
# ==========================================

toolbar = tk.Frame(content, bg=BG)
toolbar.pack(fill="x", pady=(0, 10))

search_var = tk.StringVar()

tk.Label(
    toolbar,
    text="Search:",
    font=("Segoe UI", 10, "bold"),
    bg=BG,
    fg=TEXT
).pack(side="left")

search_entry = tk.Entry(
    toolbar,
    textvariable=search_var,
    font=("Segoe UI", 10),
    width=22,
    relief="solid",
    bd=1
)
search_entry.pack(side="left", padx=8, ipady=5)

selected_count = tk.Label(
    toolbar,
    text="Selected Files: 0",
    font=("Segoe UI", 10, "bold"),
    bg=BG,
    fg=BLUE
)
selected_count.pack(side="left", padx=12)

tk.Button(
    toolbar,
    text="Select All",
    command=select_all,
    bg=LIGHT_BLUE,
    fg=DARK,
    relief="flat",
    font=("Segoe UI", 9, "bold"),
    padx=10,
    pady=6
).pack(side="right", padx=3)

tk.Button(
    toolbar,
    text="Clear Selection",
    command=clear_selection,
    bg="#e2e8f0",
    fg=TEXT,
    relief="flat",
    font=("Segoe UI", 9, "bold"),
    padx=10,
    pady=6
).pack(side="right", padx=3)


# ==========================================
# FILE TABLE
# ==========================================

table_frame = tk.Frame(content, bg=WHITE)
table_frame.pack(fill="both", expand=True)

columns = (
    "check",
    "name",
    "type",
    "size",
    "modified",
    "path"
)

file_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    selectmode="browse"
)

file_table.heading("check", text="SELECT")
file_table.heading("name", text="FILE NAME")
file_table.heading("type", text="TYPE")
file_table.heading("size", text="SIZE")
file_table.heading("modified", text="LAST MODIFIED")
file_table.heading("path", text="PATH")

file_table.column("check", width=65, anchor="center", stretch=False)
file_table.column("name", width=230)
file_table.column("type", width=75, anchor="center")
file_table.column("size", width=100, anchor="center")
file_table.column("modified", width=145, anchor="center")
file_table.column("path", width=0, stretch=False)

scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=file_table.yview
)

file_table.configure(yscrollcommand=scrollbar.set)

file_table.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

file_table.bind("<Button-1>", toggle_file)

# ==========================================
# FOOTER
# ==========================================

visible_label = tk.Label(
    content,
    text="Displaying files",
    font=("Segoe UI", 9),
    bg=BG,
    fg=GRAY
)
visible_label.pack(anchor="w", pady=(7, 3))

tk.Label(
    content,
    text="Recent Activity",
    font=("Segoe UI", 12, "bold"),
    bg=BG,
    fg=TEXT
).pack(anchor="w", pady=(5, 5))

activity_box = tk.Text(
    content,
    height=4,
    font=("Consolas", 9),
    bg=WHITE,
    fg=TEXT,
    relief="flat",
    state="normal"
)
activity_box.pack(fill="x")

status_label = tk.Label(
    root,
    text="Ready",
    font=("Segoe UI", 9),
    bg="#e2e8f0",
    fg=TEXT,
    anchor="w",
    padx=15,
    pady=6
)
status_label.pack(fill="x", side="bottom")


# ==========================================
# START APPLICATION
# ==========================================

search_var.trace_add("write", search_files)

folder_label.config(text=current_folder)

load_files()

log_activity("Professional Dashboard started")
log_activity("TEMP folder loaded successfully")
root.mainloop()