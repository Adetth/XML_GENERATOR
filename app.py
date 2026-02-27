import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml_analyzer as XA

# Import tabs
from color_injector import ColorInjector as Tab1
from format_reconstructor import FormatReconstructor as Tab2 
from visualizer_tab import GridVisualizer as Tab3 # <--- IMPORT NEW VISUALIZER

# --- 1. SETUP MAIN WINDOW ---
root = tk.Tk()
root.title("XML Multi Tool Application")
root.geometry("800x600") # Made wider to fit the visual grid

# --- 2. CREATE SHARED BACKEND ---
shared_xml_modifier = XA.XMLAnalyzer()

# --- 3. THE AUTO-SYNC FUNCTION ---
def refresh_all_tabs():
    """Forces tabs to fetch the latest data from the shared memory."""
    tab1.populate_color_rows() 
    tab3.refresh_ui() # <--- SYNC TAB 3

# --- 4. MASTER LOAD FUNCTION ---
def load_master_file():
    filename = filedialog.askopenfilename(filetypes=[("XML Files", "*.xml")])
    if filename:
        try:
            shared_xml_modifier.load_file(filename)
            file_label.config(text=f"Loaded: {filename}")
            tab2.log(f"Master file loaded into engine: {filename}") 
            
            refresh_all_tabs()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {e}")

# --- 5. TOP CONTROL BAR ---
control_frame = tk.Frame(root, pady=10, bg="#f0f0f0")
control_frame.pack(side="top", fill="x")

tk.Button(control_frame, text="Load Master XML File", command=load_master_file, bg="#e1e1e1").pack(side="left", padx=10)
file_label = tk.Label(control_frame, text="No file loaded", fg="gray", bg="#f0f0f0")
file_label.pack(side="left")

# --- 6. NOTEBOOK (TABS) ---
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both", padx=5, pady=5)

# Initialize tabs
tab1 = Tab1(notebook, shared_xml_modifier)
tab2 = Tab2(notebook, shared_xml_modifier, refresh_callback=refresh_all_tabs) 
tab3 = Tab3(notebook, shared_xml_modifier) # <--- INITIALIZE TAB 3

notebook.add(tab1, text="Color Modifier")
notebook.add(tab2, text="Format Reconstructor")
notebook.add(tab3, text="Grid Visualizer") # <--- MOUNT TAB 3

root.mainloop()