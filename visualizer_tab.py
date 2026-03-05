import tkinter as tk
from tkinter import ttk

class GridVisualizer(tk.Frame):
    def __init__(self, parent, modifier):
        super().__init__(parent)
        self.xml_modifier = modifier
        self.font_size = 9  # Default zoom level
        
        tk.Label(self, text="Form Grid Visualizer", font=("Arial", 12, "bold")).pack(pady=5)
        
        # --- NEW TOP CONTROL FRAME ---
        self.ctrl_frame = tk.Frame(self)
        self.ctrl_frame.pack(fill="x", pady=5, padx=10)
        
        # Toggle Mode
        self.view_mode = tk.StringVar(value="member")
        tk.Radiobutton(self.ctrl_frame, text="Member Name", variable=self.view_mode, value="member", command=self.refresh_ui).pack(side="left", padx=5)
        tk.Radiobutton(self.ctrl_frame, text="Dimension Name", variable=self.view_mode, value="dimension", command=self.refresh_ui).pack(side="left", padx=5)
        tk.Radiobutton(self.ctrl_frame, text="Row/Col Type", variable=self.view_mode, value="type", command=self.refresh_ui).pack(side="left", padx=5)
        
        # Refresh Button
        tk.Button(self.ctrl_frame, text="↻ Refresh UI", command=self.refresh_ui, bg="#4CAF50", fg="white", font=("Arial", 9, "bold")).pack(side="right", padx=5)
        
        # --- ZOOM CONTROLS ---
        tk.Button(self.ctrl_frame, text="+", command=self.zoom_in, font=("Arial", 10, "bold"), width=2).pack(side="right", padx=2)
        tk.Button(self.ctrl_frame, text="-", command=self.zoom_out, font=("Arial", 10, "bold"), width=2).pack(side="right", padx=2)
        tk.Label(self.ctrl_frame, text="Zoom:", font=("Arial", 9, "bold")).pack(side="right", padx=2)
        # -----------------------------
        
        self.canvas = tk.Canvas(self)
        self.scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        
        # The Trick: The frame itself is dark, and we pad the top and left by 1px
        self.grid_frame = tk.Frame(self.canvas, bg="#2c3e50", padx=1, pady=1)
        
        self.grid_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        
        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.build_ui()

    def build_ui(self):
        # Initial empty state (needs bg="white" so it covers the dark frame)
        tk.Label(self.grid_frame, text="Load a file to visualize the grid formatting.", fg="gray", bg="white").grid(row=0, column=0, padx=20, pady=20)

    def zoom_in(self):
        if self.font_size < 16:  # Max zoom
            self.font_size += 1
            self.refresh_ui()

    def zoom_out(self):
        if self.font_size > 6:   # Min zoom
            self.font_size -= 1
            self.refresh_ui()

    def _get_display_text(self, item_data):
        """Helper to extract the correct string based on the toggle switch."""
        mode = self.view_mode.get()
        real_dims = [k for k in item_data.keys() if not k.startswith("_")]
        
        if mode == "dimension":
            return "\n".join([dim[:18] for dim in real_dims])
        elif mode == "member":
            return "\n".join([str(item_data[dim])[:18] for dim in real_dims])
        elif mode == "type":
            return item_data.get("_type", "UNKNOWN")[:15]
        else:
            return item_data.get("_display_name", "")[:15]

    def refresh_ui(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
            
        if not self.xml_modifier.root:
            tk.Label(self.grid_frame, text="No file loaded.", bg="white").grid(row=0, column=0, padx=20, pady=20)
            return
            
        grid_data = self.xml_modifier.get_rowcols()
        format_map = self.xml_modifier.get_format_map()
        rows = grid_data["rows"]
        cols = grid_data["columns"]
        
        if not rows and not cols:
            tk.Label(self.grid_frame, text="No grid data found in XML.", bg="white").grid(row=0, column=0, padx=20, pady=20)
            return

        # Define dynamic fonts based on zoom level
        header_font = ("Arial", self.font_size, "bold")
        data_font = ("Arial", self.font_size)

        # Top-left empty corner cell
        # Notice bd=0 and padx=(0,1), pady=(0,1) to create the seamless grid lines
        tk.Label(self.grid_frame, text="", width=15, bg="#E0E0E0", bd=0).grid(row=0, column=0, sticky="nsew", padx=(0, 1), pady=(0, 1))
        
        # COLUMN METADATA (Headers)
        for c_idx, col in enumerate(cols):
            bg_color = format_map.get((0, c_idx + 1), "#E0E0E0")
            fg_color = "white" if bg_color.upper() in ["#0B2531", "#000000"] else "black"
            disp_name = self._get_display_text(col)
            
            lbl = tk.Label(self.grid_frame, text=disp_name, width=15, bg=bg_color, fg=fg_color, font=header_font, bd=0, pady=4)
            lbl.grid(row=0, column=c_idx + 1, sticky="nsew", padx=(0, 1), pady=(0, 1))
            
        # ROW METADATA AND DATA CELLS
        for r_idx, row in enumerate(rows):
            
            # Row Metadata (Left Headers)
            bg_color = format_map.get((r_idx + 1, 0), "#E0E0E0")
            fg_color = "white" if bg_color.upper() in ["#0B2531", "#000000"] else "black"
            disp_name = self._get_display_text(row)
            
            lbl = tk.Label(self.grid_frame, text=disp_name, width=15, bg=bg_color, fg=fg_color, font=header_font, bd=0, pady=4)
            lbl.grid(row=r_idx + 1, column=0, sticky="nsew", padx=(0, 1), pady=(0, 1))
            
            # Data Cells (Main Grid)
            for c_idx in range(len(cols)):
                data_bg = format_map.get((r_idx + 1, c_idx + 1), "#FFFFFF") 
                fg_color = "white" if data_bg.upper() in ["#0B2531", "#000000"] else "black"
                
                lbl = tk.Label(self.grid_frame, text="Data", width=15, bg=data_bg, fg=fg_color, font=data_font, bd=0)
                lbl.grid(row=r_idx + 1, column=c_idx + 1, sticky="nsew", padx=(0, 1), pady=(0, 1))