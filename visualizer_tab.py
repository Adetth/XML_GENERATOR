import tkinter as tk
from tkinter import ttk

class GridVisualizer(tk.Frame):
    def __init__(self, parent, modifier):
        super().__init__(parent)
        self.xml_modifier = modifier
        
        tk.Label(self, text="Form Grid Visualizer", font=("Arial", 12, "bold")).pack(pady=10)
        
        self.canvas = tk.Canvas(self)
        self.scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.grid_frame = tk.Frame(self.canvas)
        
        self.grid_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        
        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.build_ui()

    def build_ui(self):
        tk.Label(self.grid_frame, text="Load a file to visualize the grid formatting.", fg="gray").pack()

    def refresh_ui(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
            
        if not self.xml_modifier.root:
            tk.Label(self.grid_frame, text="No file loaded.").pack()
            return
            
        grid_data = self.xml_modifier.get_rowcols()
        format_map = self.xml_modifier.get_format_map()
        rows = grid_data["rows"]
        cols = grid_data["columns"]
        
        if not rows and not cols:
            tk.Label(self.grid_frame, text="No grid data found in XML.").pack()
            return

        tk.Label(self.grid_frame, text="", width=15, height=2, bg="#E0E0E0", relief="solid", bd=1).grid(row=0, column=0)
        
        # COLUMN METADATA (Headers)
        for c_idx, col in enumerate(cols):
            bg_color = format_map.get((-1, c_idx), "#E0E0E0")
            fg_color = "white" if bg_color.upper() in ["#0B2531", "#000000"] else "black"
            disp_name = col.get("_display_name", "")[:15]
            lbl = tk.Label(self.grid_frame, text=disp_name, width=15, height=2, bg=bg_color, fg=fg_color, relief="solid", bd=1, font=("Arial", 9, "bold"))
            lbl.grid(row=0, column=c_idx + 1)
            
        # ROW METADATA AND DATA CELLS
        for r_idx, row in enumerate(rows):
            # Row Metadata (Left Headers)
            bg_color = format_map.get((r_idx, -1), "#E0E0E0")
            fg_color = "white" if bg_color.upper() in ["#0B2531", "#000000"] else "black"
            disp_name = row.get("_display_name", "")[:15]
            lbl = tk.Label(self.grid_frame, text=disp_name, width=15, height=2, bg=bg_color, fg=fg_color, relief="solid", bd=1, font=("Arial", 9, "bold"))
            lbl.grid(row=r_idx + 1, column=0)
            
            # Data Cells (Main Grid)
            for c_idx in range(len(cols)):
                data_bg = format_map.get((r_idx, c_idx), "#FFFFFF") # Data cells default to WHITE
                fg_color = "white" if data_bg.upper() in ["#0B2531", "#000000"] else "black"
                
                lbl = tk.Label(self.grid_frame, text="Data", width=15, height=2, bg=data_bg, fg=fg_color, relief="solid", bd=1)
                lbl.grid(row=r_idx + 1, column=c_idx + 1)