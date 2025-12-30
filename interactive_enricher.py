"""
Interactive GUI-like interface for Medicine Enricher
Easy file selection and configuration
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from medicine_enricher import MedicineEnricher
import threading

class MedicineEnricherGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Medicine Data Enricher")
        self.root.geometry("600x400")
        
        self.input_file = ""
        self.output_file = ""
        self.api_key = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title_label = tk.Label(self.root, text="Medicine Data Enricher", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Input file selection
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(input_frame, text="Input Excel File:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        input_path_frame = tk.Frame(input_frame)
        input_path_frame.pack(fill="x", pady=5)
        
        self.input_label = tk.Label(input_path_frame, text="No file selected", 
                                   bg="white", relief="sunken", anchor="w")
        self.input_label.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        tk.Button(input_path_frame, text="Browse", 
                 command=self.select_input_file).pack(side="right")
        
        # Output file selection
        output_frame = tk.Frame(self.root)
        output_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(output_frame, text="Output Excel File:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        output_path_frame = tk.Frame(output_frame)
        output_path_frame.pack(fill="x", pady=5)
        
        self.output_label = tk.Label(output_path_frame, text="Auto-generated", 
                                    bg="white", relief="sunken", anchor="w")
        self.output_label.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        tk.Button(output_path_frame, text="Browse", 
                 command=self.select_output_file).pack(side="right")
        
        # API Key
        api_frame = tk.Frame(self.root)
        api_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(api_frame, text="Groq API Key:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        api_input_frame = tk.Frame(api_frame)
        api_input_frame.pack(fill="x", pady=5)
        
        self.api_entry = tk.Entry(api_input_frame, show="*", font=("Arial", 10))
        self.api_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        tk.Button(api_input_frame, text="Get Key", 
                 command=self.open_groq_console).pack(side="right")
        
        # Progress and status
        self.status_label = tk.Label(self.root, text="Ready to start", 
                                    font=("Arial", 10), fg="blue")
        self.status_label.pack(pady=10)
        
        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.start_button = tk.Button(button_frame, text="Start Enrichment", 
                                     command=self.start_enrichment,
                                     bg="green", fg="white", font=("Arial", 12, "bold"))
        self.start_button.pack(side="left", padx=10)
        
        tk.Button(button_frame, text="Exit", 
                 command=self.root.quit,
                 bg="red", fg="white", font=("Arial", 12)).pack(side="left", padx=10)
    
    def select_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Input Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if file_path:
            self.input_file = file_path
            self.input_label.config(text=os.path.basename(file_path))
            
            # Auto-generate output file name
            if not self.output_file:
                base_name = os.path.splitext(file_path)[0]
                self.output_file = f"{base_name}_enriched.xlsx"
                self.output_label.config(text=os.path.basename(self.output_file))
    
    def select_output_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Select Output Excel File",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            self.output_file = file_path
            self.output_label.config(text=os.path.basename(file_path))
    
    def open_groq_console(self):
        import webbrowser
        webbrowser.open("https://console.groq.com/")
        messagebox.showinfo("Groq Console", "Groq Console opened in your browser.\nCreate an account and get your API key.")
    
    def start_enrichment(self):
        # Validate inputs
        if not self.input_file:
            messagebox.showerror("Error", "Please select an input Excel file!")
            return
        
        if not os.path.exists(self.input_file):
            messagebox.showerror("Error", f"Input file not found: {self.input_file}")
            return
        
        api_key = self.api_entry.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Please enter your Groq API key!")
            return
        
        # Disable button and start processing
        self.start_button.config(state="disabled", text="Processing...")
        self.status_label.config(text="Starting enrichment process...", fg="orange")
        
        # Run in separate thread to avoid freezing UI
        thread = threading.Thread(target=self.run_enrichment, args=(api_key,))
        thread.daemon = True
        thread.start()
    
    def run_enrichment(self, api_key):
        try:
            enricher = MedicineEnricher(api_key)
            result_df = enricher.enrich_excel(self.input_file, self.output_file)
            
            # Show results
            status_counts = result_df['processing_status'].value_counts()
            summary = "\n".join([f"{status}: {count}" for status, count in status_counts.items()])
            
            self.root.after(0, lambda s=summary: self.show_success(s))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda msg=error_msg: self.show_error(msg))
    
    def show_success(self, summary):
        self.status_label.config(text="Enrichment completed successfully!", fg="green")
        self.start_button.config(state="normal", text="Start Enrichment")
        
        messagebox.showinfo("Success", 
                           f"Enrichment completed!\n\nResults saved to:\n{self.output_file}\n\nSummary:\n{summary}")
    
    def show_error(self, error_msg):
        self.status_label.config(text="Enrichment failed!", fg="red")
        self.start_button.config(state="normal", text="Start Enrichment")
        
        messagebox.showerror("Error", f"Enrichment failed:\n{error_msg}")
    
    def run(self):
        self.root.mainloop()

def main():
    try:
        app = MedicineEnricherGUI()
        app.run()
    except ImportError:
        print("❌ tkinter not available. Using command line interface instead.")
        print("Run: python run_enricher.py --help")

if __name__ == "__main__":
    main()