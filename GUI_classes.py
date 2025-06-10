""" GUI for producing the overal results of the championship. 
NEXT STEPS:
- Box at the top: loading messages 
    - Loading data
    - Error for all Es (i.e. no final, but results exist)
- Display what the user has selected in the box at the top
- Add the 2 Winners of individual classes to the table, they are 20th or 19th if Eliminated in the other round
- Who else can qualify (need to look at running orders) what they need
"""
import customtkinter as ctk
import pandas as pd
from tkinter import ttk
import threading
import time
from champ_placement import plaza

class ErrorFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.setup_error_display()
        
    def setup_error_display(self):
        self.error_textbox = ctk.CTkTextbox(self, height=50, width=200)
        self.error_textbox.pack(pady=5, padx=10, fill="x")
        self.error_textbox.configure(state="disabled")
        
    def show_error(self, message):
        self.error_textbox.configure(state="normal")
        self.error_textbox.delete("1.0", "end")
        self.error_textbox.insert("1.0", f"Error: {message}")
        self.error_textbox.configure(state="disabled")

    def clear_error(self):
        self.error_textbox.configure(state="normal")
        self.error_textbox.delete("1.0", "end")
        self.error_textbox.configure(state="disabled")

class InputPage(ctk.CTkFrame):
    def __init__(self, master, switch_to_results_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.switch_to_results = switch_to_results_callback
        self.setup_page()
        
    def setup_page(self):
        # Title
        title_label = ctk.CTkLabel(self, text="Championship Placement Tracker", 
                                 font=("Arial", 24, "bold"))
        title_label.pack(pady=20)
        
        # Error Frame
        self.error_frame = ErrorFrame(self)
        self.error_frame.pack(pady=10, padx=10, fill="x")
        
        # Height Selection
        height_label = ctk.CTkLabel(self, text="Select Height", font=("Arial", 16))
        height_label.pack(pady=5)
        
        heights = ["Small", "Medium", "Intermediate", "Large"]
        self.height_var = ctk.StringVar()
        self.height_combo = ctk.CTkComboBox(self, values=heights, variable=self.height_var,
                                          font=("Arial", 14))
        self.height_combo.pack(pady=5)
        
        # URL Entries
        jumping_label = ctk.CTkLabel(self, text="Jumping URL (Optional)", font=("Arial", 16))
        jumping_label.pack(pady=5)
        self.jumping_entry = ctk.CTkEntry(self, placeholder_text="Enter jumping URL",
                                        font=("Arial", 14))
        self.jumping_entry.pack(pady=5)
        
        agility_label = ctk.CTkLabel(self, text="Agility URL (Optional)", font=("Arial", 16))
        agility_label.pack(pady=5)
        self.agility_entry = ctk.CTkEntry(self, placeholder_text="Enter agility URL",
                                        font=("Arial", 14))
        self.agility_entry.pack(pady=5)
        
        # Find Button
        self.find_button = ctk.CTkButton(
            self,
            text="Find Champ Class",
            command=self.switch_to_results,
            font=("Arial", 16)
        )
        self.find_button.pack(pady=20)

class ResultsPage(ctk.CTkFrame):
    def __init__(self, master, switch_to_input_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.switch_to_input = switch_to_input_callback
        self.refresh_event = threading.Event()
        self.refresh_thread = None
        self.setup_page()
        
    def setup_page(self):
        # Title
        title_frame = ctk.CTkFrame(self)
        title_frame.pack(fill="x", pady=10, padx=10)
        
        title_label = ctk.CTkLabel(title_frame, text="Championship Results", 
                                   font=("Arial", 24, "bold"))
        title_label.pack(side="left")
        
        # Back Button
        back_button = ctk.CTkButton(
            title_frame,
            text="Back",
            command=self.switch_to_input,  # Navigate back to InputPage
            font=("Arial", 16)
        )
        back_button.pack(side="right", padx=10)
        
        # Error Frame
        self.error_frame = ErrorFrame(self)
        self.error_frame.pack(pady=10, padx=10, fill="x")
        
        # Results Table
        self.setup_table()
        
        # Timer Label
        self.timer_label = ctk.CTkLabel(self, text="", font=("Arial", 16))
        self.timer_label.pack(pady=10)
        
        # Refresh Button
        self.refresh_button = ctk.CTkButton(
            self,
            text="Manual Refresh",
            command=self.trigger_refresh,
            font=("Arial", 16)
        )
        self.refresh_button.pack(pady=10)
        
    def setup_table(self):
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 12))  # Set font for table content
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"))  # Set font for headers
        # Create a style for the highlighted row
        style.configure("Cutoff.Treeview", background="#FFE4B5")  # Light orange color
        
        self.table = ttk.Treeview(self, selectmode="browse", show="headings")
        self.table['columns'] = ('Place', 'Handler', 'Dog', 'Points', 'Round1', 'Round2')
        
        for col in self.table['columns']:
            self.table.column(col, anchor="w", width=120)  # Increased width
            self.table.heading(col, text=col, anchor="w")
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.table.yview)
        x_scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.table.xview)
        self.table.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Pack scrollbars and table
        y_scrollbar.pack(side="right", fill="y")
        self.table.pack(pady=10, padx=10, fill="both", expand=True)
        x_scrollbar.pack(side="bottom", fill="x")
        
    def update_results(self, data):
        for item in self.table.get_children():
            self.table.delete(item)
            
        for index, row in data.iterrows():
            handler, dog = row['Pairing']
            item = self.table.insert('', 'end', values=(
                index,
                handler,
                dog,
                row['Points'],
                row['Round 1'],
                row['Round 2']
            ))
            
            # Highlight the 20th row
            if index == 20:
                self.table.tag_configure('cutoff', background='#FFE4B5')  # Light orange
                self.table.item(item, tags=('cutoff',))
            
    def trigger_refresh(self):
        self.refresh_event.set()

    def update_timer_label(self, text):
        self.timer_label.configure(text=text)


class ChampPlacementGUI:
    def __init__(self):
        self.setup_window()
        self.setup_pages()
        
    def setup_window(self):
        self.root = ctk.CTk()
        self.root.title("Championship Placement Tracker")
        self.root.geometry("1200x800")  # Increased window size
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
    def setup_pages(self):
        self.current_page = None
        self.input_page = InputPage(self.root, self.switch_to_results)
        self.results_page = ResultsPage(self.root, self.show_input_page)  # Pass show_input_page as callback
        self.show_input_page()
        
    def show_input_page(self):
        # Stop any ongoing refresh thread
        if self.results_page.refresh_thread:
            if self.results_page.refresh_thread.is_alive():
                self.results_page.refresh_event.set()
                self.results_page.refresh_thread.join()
        
        # Clear previous inputs
        self.input_page.height_var.set("")
        self.input_page.jumping_entry.delete(0, "end")
        self.input_page.agility_entry.delete(0, "end")
        
        # Switch to InputPage
        if self.current_page:
            self.current_page.pack_forget()
        self.input_page.pack(fill="both", expand=True)
        self.current_page = self.input_page
        
    def show_results_page(self):
        if self.current_page:
            self.current_page.pack_forget()
        self.results_page.pack(fill="both", expand=True)
        self.current_page = self.results_page
        
    def switch_to_results(self):
        # Get values from input page
        height = self.input_page.height_var.get()
        jumping_url = self.input_page.jumping_entry.get()
        agility_url = self.input_page.agility_entry.get()
        
        # Validate inputs
        if not height:
            self.input_page.error_frame.show_error("Height selection is required.")
            return
        
        # Switch to results page
        self.show_results_page()
        
        # Start continuous refresh with new inputs
        if self.results_page.refresh_thread is None or not self.results_page.refresh_thread.is_alive():
            self.results_page.refresh_thread = threading.Thread(
                target=self.continuous_refresh,
                args=(height, jumping_url, agility_url),
                daemon=True
            )
            self.results_page.refresh_thread.start()
            
    def continuous_refresh(self, height, jumping_url, agility_url):
        height_map = {
            "Small": "Sml",
            "Medium": "Med",
            "Intermediate": "Int",
            "Large": "Lge"
        }
        
        while True:
            try:
                self.results_page.error_frame.clear_error()
                champ = plaza(
                    height=height_map.get(height),
                    JUMPING_url=jumping_url if jumping_url else None,
                    AGILITY_url=agility_url if agility_url else None
                )
                top_20, all_results = champ.overall_results()
                self.root.after(0, self.results_page.update_results, all_results)
                
            except Exception as e:
                self.root.after(0, self.results_page.error_frame.show_error, str(e))
                
            # Countdown timer
            time_limit = 120
            while time_limit > 0:
                if self.results_page.refresh_event.is_set():
                    self.results_page.refresh_event.clear()
                    break
                    
                mins, secs = divmod(time_limit, 60)
                self.root.after(0, self.results_page.update_timer_label, 
                              f"Next refresh in {mins:02d}:{secs:02d}")
                time.sleep(1)
                time_limit -= 1

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ChampPlacementGUI()
    app.run()