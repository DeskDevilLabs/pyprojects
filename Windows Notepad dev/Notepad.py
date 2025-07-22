import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
from datetime import datetime

class SimpleNotepad:
    def __init__(self, root):
        self.root = root
        self.root.title("Cortex Notepad")
        self.root.state("zoomed")

        # Custom fonts
        self.menu_tab_font = ("Arial", 15, "bold")  # For File, Edit, Font Size tabs
        self.menu_item_font = ("Arial", 12)         # For dropdown items
        self.text_font = ("Arial", 12)              # For main text area

        # Colors
        self.bg_color = "#2E2E2E"
        self.fg_color = "#D3D3D3"
        self.text_area_bg = "#333333"
        self.text_area_fg = "#FFFFFF"

        # Set default menu font (works on Windows/Linux)
        self.root.option_add("*Menu.font", self.menu_tab_font)
        
        # Main text area
        self.text_area = tk.Text(
            self.root, 
            wrap=tk.WORD, 
            undo=True,
            font=self.text_font,
            bg=self.text_area_bg, 
            fg=self.text_area_fg,
            insertbackground=self.fg_color
        )
        self.text_area.pack(expand=True, fill=tk.BOTH)

        self.filename = None
        self.create_menus()
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

        # Key bindings
        self.root.bind("<Control-s>", self.save_file)
        self.root.bind("<Control-Shift-s>", self.save_as_file)
        self.root.bind("<Control-f>", self.find_text)
        self.root.bind("<Control-h>", self.replace_text)
        self.root.bind("<Control-d>", self.insert_date_time_stamp)
        self.root.bind("<Control-e>", self.search_selected_word_on_edge)
        self.root.bind("<Control-o>", self.open_file)

        # Auto-save
        self.auto_save_interval = 5 * 60 * 1000  # 5 minutes
        self.root.after(self.auto_save_interval, self.auto_save)

    def auto_save(self):
        if self.filename:
            try:
                with open(self.filename, 'w', encoding="utf-8") as file:
                    file.write(self.text_area.get(1.0, tk.END).strip())
                print("Autosaved at", datetime.now().strftime("%I:%M %p"))
            except Exception as e:
                print("Autosave failed:", e)
        self.root.after(self.auto_save_interval, self.auto_save)

    def create_menus(self):
        # Main menu bar
        menu_bar = tk.Menu(
            self.root, 
            bg=self.bg_color, 
            fg=self.fg_color,
            font=self.menu_tab_font  # This affects menu tabs
        )
        self.root.config(menu=menu_bar)

        # File menu
        file_menu = tk.Menu(
            menu_bar, 
            tearoff=0, 
            bg=self.bg_color, 
            fg=self.fg_color,
            font=self.menu_item_font  # Affects dropdown items
        )
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)

        # Edit menu
        edit_menu = tk.Menu(
            menu_bar, 
            tearoff=0, 
            bg=self.bg_color, 
            fg=self.fg_color,
            font=self.menu_item_font
        )
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo)
        edit_menu.add_command(label="Redo", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut)
        edit_menu.add_command(label="Copy", command=self.copy)
        edit_menu.add_command(label="Paste", command=self.paste)
        edit_menu.add_separator()
        edit_menu.add_command(label="Insert DateTime Stamp", command=self.insert_date_time_stamp)
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", command=self.find_text)
        edit_menu.add_command(label="Replace", command=self.replace_text)
        edit_menu.add_separator()
        edit_menu.add_command(label="Search Selected Word on Edge", command=self.search_selected_word_on_edge)

        # Font Size menu
        font_menu = tk.Menu(
            menu_bar, 
            tearoff=0, 
            bg=self.bg_color, 
            fg=self.fg_color,
            font=self.menu_item_font
        )
        menu_bar.add_cascade(label="Font Size", menu=font_menu)
        for size in range(8, 37, 2):
            font_menu.add_command(
                label=str(size), 
                command=lambda s=size: self.change_font_size(s)
            )

    def new_file(self):
        if self.confirm_unsaved_changes():
            self.filename = None
            self.text_area.delete(1.0, tk.END)
            self.root.title("Untitled - Cortex Notepad")

    def open_file(self, event=None):
        if self.confirm_unsaved_changes():
            path = filedialog.askopenfilename()
            if path:
                with open(path, 'r', encoding="utf-8") as f:
                    content = f.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, content)
                self.filename = path
                self.root.title(f"{self.filename} - Cortex Notepad")

    def save_file(self, event=None):
        if self.filename:
            with open(self.filename, 'w', encoding="utf-8") as file:
                file.write(self.text_area.get(1.0, tk.END).strip())
        else:
            self.save_as_file()

    def save_as_file(self, event=None):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            with open(path, 'w', encoding="utf-8") as f:
                f.write(self.text_area.get(1.0, tk.END).strip())
            self.filename = path
            self.root.title(f"{self.filename} - Cortex Notepad")

    def undo(self): self.text_area.edit_undo()
    def redo(self): self.text_area.edit_redo()
    def cut(self): self.text_area.event_generate("<<Cut>>")
    def copy(self): self.text_area.event_generate("<<Copy>>")
    def paste(self): self.text_area.event_generate("<<Paste>>")

    def exit_app(self):
        if self.confirm_unsaved_changes():
            self.root.quit()

    def confirm_unsaved_changes(self):
        content = self.text_area.get(1.0, tk.END).strip()
        if content and self.filename is None:
            answer = messagebox.askyesnocancel("Save?", "Do you want to save before exiting?")
            if answer: self.save_file()
            return answer is not None
        return True

    def change_font_size(self, size):
        self.font_size = size
        self.text_area.config(font=("Arial", self.font_size))

    def insert_date_time_stamp(self, event=None):
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.text_area.insert(tk.INSERT, dt)

    def search_selected_word_on_edge(self, event=None):
        selected = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
        if selected:
            webbrowser.open(f"https://www.bing.com/search?q={selected}")

    def find_text(self, event=None):
        find_popup = tk.Toplevel(self.root)
        find_popup.title("Find Text")
        find_popup.geometry("300x200")
        find_popup.transient(self.root)
        find_popup.grab_set()

        tk.Label(find_popup, text="Enter text to find:").pack(pady=5)
        find_entry = tk.Entry(find_popup, width=30)
        find_entry.pack(pady=5)

        status_label = tk.Label(find_popup, text="", fg="red")
        status_label.pack()

        self.text_area.tag_config("found", background="yellow")

        search_index = [1.0]

        def highlight_single(start, end):
            self.text_area.tag_remove("found", "1.0", tk.END)
            self.text_area.tag_add("found", start, end)

        def find(direction):
            self.text_area.tag_remove("found", "1.0", tk.END)
            target = find_entry.get()
            if not target:
                status_label.config(text="Empty search query.")
                return

            content = self.text_area.get("1.0", tk.END)
            start_pos = int(float(search_index[0]))

            def search_content(dirn):
                if dirn == "down":
                    idx = content.find(target, start_pos)
                    if idx == -1:
                        idx = content.find(target, 0)  # wrap to top
                else:
                    idx = content.rfind(target, 0, start_pos)
                    if idx == -1:
                        idx = content.rfind(target)  # wrap to bottom
                return idx

            idx = search_content(direction)

            if idx == -1:
                status_label.config(text="No match found.")
            else:
                start = f"1.0 + {idx} chars"
                end = f"1.0 + {idx + len(target)} chars"
                highlight_single(start, end)
                self.text_area.see(start)
                status_label.config(text="")
                search_index[0] = idx + 1 if direction == "down" else idx

        def find_all():
            self.text_area.tag_remove("found", "1.0", tk.END)
            target = find_entry.get()
            if not target:
                status_label.config(text="Empty search query.")
                return

            count = 0
            start = "1.0"
            while True:
                start = self.text_area.search(target, start, stopindex=tk.END)
                if not start:
                    break
                end = f"{start}+{len(target)}c"
                self.text_area.tag_add("found", start, end)
                start = end
                count += 1

            if count == 0:
                status_label.config(text="No matches found.")
            else:
                status_label.config(text=f"{count} matches highlighted.")
                self.text_area.see("1.0")

        # Buttons
        tk.Button(find_popup, text="Find Down", width=10, command=lambda: find("down")).pack(pady=2)
        tk.Button(find_popup, text="Find Up", width=10, command=lambda: find("up")).pack(pady=2)
        tk.Button(find_popup, text="Find All", width=10, command=find_all).pack(pady=2)



    def replace_text(self, event=None):
        replace_popup = tk.Toplevel(self.root)
        replace_popup.title("Find and Replace")
        replace_popup.geometry("350x200")
        replace_popup.transient(self.root)
        replace_popup.resizable(False, False)

        tk.Label(replace_popup, text="Find:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        find_entry = tk.Entry(replace_popup, width=30)
        find_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(replace_popup, text="Replace with:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        replace_entry = tk.Entry(replace_popup, width=30)
        replace_entry.grid(row=1, column=1, padx=10, pady=5)

        match_case_var = tk.BooleanVar()
        match_case_check = tk.Checkbutton(replace_popup, text="Match Case", variable=match_case_var)
        match_case_check.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        def replace_all():
            find_text = find_entry.get()
            replace_text = replace_entry.get()

            content = self.text_area.get("1.0", tk.END)
            if not match_case_var.get():
                content = content.lower()
                find_text = find_text.lower()

            new_content = content.replace(find_text, replace_text)
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, new_content)
            replace_popup.destroy()

        def replace_one():
            start = self.text_area.search(find_entry.get(), "1.0", stopindex=tk.END, nocase=not match_case_var.get())
            if start:
                end = f"{start}+{len(find_entry.get())}c"
                self.text_area.delete(start, end)
                self.text_area.insert(start, replace_entry.get())
                self.text_area.tag_add("match", start, f"{start}+{len(replace_entry.get())}c")
                self.text_area.tag_config("match", background="yellow")
            else:
                tk.messagebox.showinfo("Not Found", "The text you want to replace was not found.")

        tk.Button(replace_popup, text="Replace One", command=replace_one).grid(row=3, column=0, padx=10, pady=15)
        tk.Button(replace_popup, text="Replace All", command=replace_all).grid(row=3, column=1, padx=10, pady=15)

        replace_popup.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleNotepad(root)
    root.mainloop()