import customtkinter
import pandas as pd
import tkinter as tk
from tkinter import ttk

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

app = customtkinter.CTk()
app.geometry("800x600")
app.title("Champ Shows 2024")

frame = customtkinter.CTkFrame(master=app) 
frame.pack(pady=20, padx=60, fill="both", expand=True)  

height_title = customtkinter.CTkLabel(frame,text="Pick a hieght", font= ("arial",20))
height_title.pack(pady = 10)

heights = ["Small", "Medium", "Intermediate", "Large"]

combo_box= customtkinter.CTkComboBox(frame, values=heights)
combo_box.pack(pady=10)

url_label = customtkinter.CTkLabel(frame,text="Enter Class URLs", font= ("arial",18))
url_label.pack(pady= 0)

jumping_entry = customtkinter.CTkEntry(frame, placeholder_text = "Jumping (optional)")
jumping_entry.pack(pady = 10)

agility_entry = customtkinter.CTkEntry(frame, placeholder_text = "Agility (optional)")
agility_entry.pack(pady = 10)

# Creating new page with a table in, this needs to be updated to display the results
def create_table():
    # Hide the login frame
    frame.pack_forget()
    
    print(jumping_entry.get(), agility_entry.get())

    # Create a new frame for the table
    table_frame = customtkinter.CTkFrame(master=app)
    table_frame.pack(pady=20, padx=60, fill="both", expand=True)

    label = customtkinter.CTkLabel(master=table_frame, text="Date of Champ Shows", font=("Arial", 36))
    label.pack(pady=24, padx=20, fill="both")
    
    # Refresh button
    def refresh():
        # Clear the existing table
        for item in table.get_children():
            table.delete(item)

        # Read the CSV file
        data = pd.read_csv('Champ shows.csv')

        # Add data to the table
        for index, row in data.iterrows():
            table.insert('', 'end', values=(row['Show Name'], row['Date'], row['Small'], row['Medium'], row['Intermediate'], row['Large'], row['Comments']))

        # Create a refreshed label
        refreshed_label = customtkinter.CTkLabel(master=table_frame, text="Refreshed", font=("Arial", 12), fg_color = "grey")
        refreshed_label.pack(pady=12, padx=10, fill="both")

        # After 2 seconds, remove the refreshed label
        def remove_refreshed_label():
            refreshed_label.pack_forget()

        app.after(2000, remove_refreshed_label)
        print("Page refreshed")

    button = customtkinter.CTkButton(master=table_frame, text="Refresh", command=refresh)
    button.pack(pady=12, padx=10, fill="both")


    # Read the CSV file
    data = pd.read_csv('Champ shows.csv')
    
    # Create a table
    table = ttk.Treeview(table_frame, selectmode="browse", show="headings")
    
    # Define the columns
    table['columns'] = ('Show Name', 'Date', 'Small', 'Medium', 'Intermediate', 'Large', 'Comments')
    
    # Format the columns
    table.column("#0", width=0, stretch=tk.NO)
    table.column("Show Name", anchor=tk.W, width=150)
    table.column("Date", anchor=tk.W, width=100)
    table.column("Small", anchor=tk.W, width=50)
    table.column("Medium", anchor=tk.W, width=50)
    table.column("Intermediate", anchor=tk.W, width=50)
    table.column("Large", anchor=tk.W, width=50)
    table.column("Comments", anchor=tk.W, width=150)
    
    # Create headings
    table.heading("#0", text="", anchor=tk.W)
    table.heading("Show Name", text="Show Name", anchor=tk.W)
    table.heading("Date", text="Date", anchor=tk.W)
    table.heading("Small", text="Small", anchor=tk.W)
    table.heading("Medium", text="Medium", anchor=tk.W)
    table.heading("Intermediate", text="Intermediate", anchor=tk.W)
    table.heading("Large", text="Large", anchor=tk.W)
    table.heading("Comments", text="Comments", anchor=tk.W)

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

    # Add data to the table
    for index, row in data.iterrows():
        table.insert('', 'end', values=(row['Show Name'], row['Date'], row['Small'], row['Medium'], row['Intermediate'], row['Large'], row['Comments']))
    
    # Pack the table
    table.pack(pady=24, padx=10, fill="both", expand=True)    

# Button to the new table
button = customtkinter.CTkButton(frame, text = "Find Champ Class", command = create_table)
button.pack(pady=20)

app.mainloop()