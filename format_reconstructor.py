import tkinter as tk
from tkinter import messagebox

class FormatReconstructor(tk.Frame):
    # Added refresh_callback to the init parameters
    def __init__(self, parent, modifier, refresh_callback=None):
        super().__init__(parent)
        self.xml_modifier = modifier
        self.refresh_callback = refresh_callback # Save it for later
        self.build_ui()

    def build_ui(self):
        btn_frame = tk.Frame(self, pady=10)
        btn_frame.pack(side="top", fill="x", padx=10)
        
        # --- NEW REFRESH BUTTON (Top Right) ---
        tk.Button(btn_frame, text="↻ Refresh UI", command=self.refresh_ui, bg="#4CAF50", fg="white", font=("Arial", 9, "bold")).pack(side="right")

        tk.Button(btn_frame, text="RUN MASTER FORMATTING LOOP", width=50, height=2, bg="#c1e1c1", font=("Arial", 10, "bold"), command=self.run_master_loop).pack(pady=10)

        log_label = tk.Label(self, text="Action Log:", font=("Arial", 9, "bold"))
        log_label.pack(anchor="w", padx=10)
        
        self.log_text = tk.Text(self, height=15, bg="#f4f4f4", state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        print(message)
        
    def refresh_ui(self):
        # Clears the log to give you a clean slate
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
        self.log("UI Refreshed. Log cleared.")
        
        # Fire the global app sync just in case
        if self.refresh_callback:
            self.refresh_callback()

    def run_master_loop(self):
        if not self.xml_modifier.root:
            messagebox.showwarning("Warning", "Load a Master XML file first!")
            return
            
        self.log("Starting Master Formatting Loop...")
        success = self.xml_modifier.apply_master_formatting()
        
        if success:
            self.log("SUCCESS: File formatted and saved automatically!")
            
            # THE MAGIC SYNC TRIGGER: Tell app.py to refresh all other tabs!
            if self.refresh_callback:
                self.refresh_callback()
                self.log("UI Sync: Told Color Modifier tab to fetch latest colors.")
                
            messagebox.showinfo("Success", "Master formatting applied successfully!")
        else:
            self.log("ERROR: Something went wrong during formatting.")