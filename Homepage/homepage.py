#Homepage Python file. Has buttons that leads to all components/features of this application.

import tkinter as tk
from tkinter import ttk

class HomePage:
    #Initialisation
    def __init__(self, root):

        #Root Config
        root.title("Home")
        root.geometry("300x300")

        
        #Two distinct sections: Top Bar and Ticket Actions.
        top_bar_frame = tk.Frame(root)
        top_bar_frame.grid(row=0, column=0, sticky="nsew")

        top_bar_label = tk.Label(top_bar_frame, text="Home")
        top_bar_label.configure(font=("", 30))
        top_bar_label.grid(row=0, column=0, padx=20, pady=10)

        #logout_button = ttk.Button(top_bar_frame, text="Logout", command=Logout)
        #logout_button.grid(row=0, column=1)
        
        #welcome_message_label = ttk.Label(top_bar_frame, text=f"Welcome, {GetCurrentUser()}!")
        #welcome_message_label.grid(row=1, column=0)

        main_body_frame = ttk.LabelFrame(root, borderwidth=10, text="Options")
        main_body_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        #Scale widgets appropriately according to window size.
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=0)
        root.grid_rowconfigure(1, weight=1)


if __name__ == "__main__":
    root = tk.Tk()
    
    home_page = HomePage(root)
    root.mainloop()

#hi