import tkinter as tk
from tkinter import messagebox
# No longer need filedialog here since app.py handles it

class ColorInjector(tk.Frame):
    def __init__(self, parent, modifier):
        super().__init__(parent)
        
        self.xml_modifier = modifier

        self.ui_entries = []
        self.preview_widgets = []
        self.row_widgets = []
        self.color_list = []
        self.offsetx = 1 # Reduced offset since we removed top rows
        self.offsety = 0
        
        #do it one by one, start simple
        self.build_ui()

    def build_ui(self):
        #future code - make this look nicer later
        # I removed the file loading widgets from here.
        
        # Create a container for the list of colors
        self.list_frame = tk.Frame(self)
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create the button frame at the bottom
        self.btn_frame = tk.Frame(self, pady=10)
        self.btn_frame.pack(side="bottom", fill="x")
        
        tk.Button(self.btn_frame, text="Generate Preview", command=self.update_preview).pack(side="left", padx=10)
        tk.Button(self.btn_frame, text="Inject XML", command=self.inject_entries).pack(side="left", padx=10)
        
        # --- NEW REFRESH BUTTON ---
        tk.Button(self.btn_frame, text="↻ Refresh UI", command=self.populate_color_rows, bg="#4CAF50", fg="white", font=("Arial", 9, "bold")).pack(side="right", padx=10)

    def populate_color_rows(self):
        #start fresh every time we load
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        self.ui_entries.clear()
        self.preview_widgets.clear()
        
        #get the colors from the backend
        raw_colors = self.xml_modifier.get_colors()
        
        #safety check if no file loaded or no colors found
        if not raw_colors:
            tk.Label(self.list_frame, text="No editable colors found (or no file loaded).").pack()
            return

        excluded_colors = {"FFFFFF", "000000", "#FFFFFF", "#000000"}
        
        #save this to self so i can use it in the validation function later
        self.color_list = [c for c in raw_colors if c[1] not in excluded_colors]

        # Headers
        headers = ["ID Name", "Original", "Preview", "New Hex"]
        for col, text in enumerate(headers):
            lbl = tk.Label(self.list_frame, text=text, font=("Arial", 10, "bold"))
            lbl.grid(row=0, column=col+self.offsety, pady=5, padx=10)

        #loop through and create the controls
        for i, (c_id, hex_val) in enumerate(self.color_list):
            current_row = i + 1
            
            id_label = tk.Label(self.list_frame, text=c_id)
            id_label.grid(row=current_row, column=0+self.offsety, padx=5)
            
            hex_label = tk.Label(self.list_frame, text=f"#{hex_val}")
            hex_label.grid(row=current_row, column=1+self.offsety, padx=5)
            
            canvas = tk.Canvas(self.list_frame, height=20, width=20, bg=f"#{hex_val}", bd=1, relief="solid")
            canvas.grid(row=current_row, column=2+self.offsety, padx=5)
            
            entry = tk.Entry(self.list_frame, width=15)
            entry.insert(0, f"{hex_val}") 
            entry.grid(row=current_row, column=3+self.offsety, padx=10)
            self.ui_entries.append(entry)

    def run_validation_and_preview(self):
        # Clean old previews (which are in column 4)
        for widget in self.preview_widgets:
            widget.destroy()
        self.preview_widgets.clear()
        
        clean_data = []
        has_error = False
        
        for i, entry_widget in enumerate(self.ui_entries):
            raw_val = entry_widget.get().strip()
            final_color = raw_val if raw_val.startswith("#") else f"#{raw_val}"
            current_row = i + 1

            try:
                canvas = tk.Canvas(self.list_frame, height=20, width=20, bg=final_color, bd=1, relief="solid")
                canvas.grid(row=current_row, column=4+self.offsety, padx=10)
                self.preview_widgets.append(canvas)
                
                #use self.color_list here
                original_id = self.color_list[i][0]
                clean_data.append((original_id, raw_val))

            except tk.TclError:
                has_error = True
                err_lbl = tk.Label(self.list_frame, text="Invalid", fg="red", font=("Arial", 9, "bold"))
                err_lbl.grid(row=current_row, column=4+self.offsety)
                self.preview_widgets.append(err_lbl)
        
        if has_error:
            return False, []
        else:
            return True, clean_data

    def update_preview(self):
        self.run_validation_and_preview()

    def inject_entries(self):
        if not self.xml_modifier.root:
             messagebox.showwarning("Warning", "No file loaded!")
             return

        is_valid, data = self.run_validation_and_preview()
        
        if not is_valid:
            messagebox.showerror("Injection Failed", "Please fix the red 'Invalid' fields before injecting.")
            return
        
        try:
            self.xml_modifier.inject_colors(data)
            messagebox.showinfo("Success", "Colors injected and file saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save XML: {e}")