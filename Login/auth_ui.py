import tkinter as tk
from tkinter import messagebox
from Login import services

class AuthWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.root.withdraw()

        self.auth_window = tk.Toplevel(self.root)
        self.auth_window.title("Login")
        self.auth_window.geometry("400x400")
        self.auth_window.resizable(True, True)
        self.auth_window.configure(bg="#2E3440")

        self.current_frame = None
        self.show_login_frame()

    def show_login_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = tk.Frame(self.auth_window, bg="#2E3440")
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title = (tk.Label(self.current_frame, text="Login", font=("Arial", 20, "bold"),
                         fg="#D8DEE9", bg="#2E3440"))
        title.pack(anchor="w", pady=(0,20))

        #username
        tk.Label(self.current_frame, text="Username", font=("Arial", 12),
                 fg="#D8DEE9", bg="#2E3440").pack(anchor="w")
        self.login_username_entry = tk.Entry(self.current_frame, font=("Arial", 12), width=30)
        self.login_username_entry.pack(pady=(0, 12))

        tk.Label(self.current_frame, text="Password", font=("Arial", 12),
                 fg="#D8DEE9", bg="#2E3440").pack(anchor="w")
        self.login_password_entry = tk.Entry(self.current_frame, font=("Arial", 12),
                                             width=30, show='*')
        self.login_password_entry.pack(pady=(0, 20))

        #Login Button
        login_button = tk.Button(self.current_frame, text="Login", font=("Arial", 12),
                                    command=self.handle_login, bg='#A3BE8C', fg='#2E3440')
        login_button.pack(pady=(10))

        #Switch to Register
        switch_button = tk.Button(self.current_frame, text="Don't have an account? Register",
                                  command=self.show_register_frame, bg='#A3BE8C', fg='#2E3440',
                                  activebackground='#2E3440', activeforeground='#D8DEE9')
        switch_button.pack()

    def show_register_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = tk.Frame(self.auth_window, bg="#2E3440")
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title = (tk.Label(self.current_frame, text="Create Account", font=("Arial", 20, "bold"),
                         fg='#D8DEE9', bg="#2E3440" ))
        title.pack(anchor="w")

        #Username
        tk.Label(self.current_frame, text="Username", font=("Arial", 12, "bold"),
                 fg="#D8DEE9", bg="#2E3440").pack(anchor="w")
        self.register_username_entry = tk.Entry(self.current_frame, font=("Arial", 12), width=30)
        self.register_username_entry.pack(pady=(0, 10))

        #Password
        tk.Label(self.current_frame, text="Password", font=("Arial", 12, "bold"),
                 fg="#D8DEE9", bg="#2E3440").pack(anchor="w")
        self.register_password_entry = tk.Entry(self.current_frame, show='*', font=("Arial", 12),
                                                width=30)
        self.register_password_entry.pack(pady=(0, 20))

        #duplicate password
        tk.Label(self.current_frame, text="Confirm Password", font=("Arial", 12, "bold"),
                 fg="#D8DEE9", bg="#2E3440").pack(anchor="w")
        self.register_duplicate_password_entry = tk.Entry(self.current_frame, show='*', font=("Arial", 12),
                                                width=30)
        self.register_duplicate_password_entry.pack(pady=(0, 20))

        #Register Button
        register_button = tk.Button(self.current_frame, text="Register", font=("Arial", 12),
                                    command=self.handle_register, bg='#A3BE8C', fg='#2E3440')
        register_button.pack(pady=(10))

        #switch to Login page
        switch_button = tk.Button(self.current_frame, text="Already have an account? Login",
                                  command=self.show_login_frame, bg='#A3BE8C', fg='#2E3440',
                                  activebackground='#2E3440', activeforeground='#D8DEE9')
        switch_button.pack()

    def handle_login(self):
        username = self.login_username_entry.get()
        password = self.login_password_entry.get()

        if services.verify_user(username, password):
            messagebox.showinfo("Success", "Login Successful!")
            self.auth_window.destroy()
            self.on_success()
        else:
            messagebox.showerror("Error", "Login Failed! Invalid useername or password.")

    def handle_register(self):
        username = self.register_username_entry.get()
        password = self.register_password_entry.get()
        duplicate_password = self.register_duplicate_password_entry.get()

        if not services.password_strong(password):
            messagebox.showerror("Error", "Password is weak! It must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one digit")
            return

        if services.create_user(username, password):
            messagebox.showinfo("Success", "User created successfully! Please log in.")
            self.show_login_frame()
        else:
            messagebox.showerror("Error", "Username already exists!")

if __name__ == "__main__":
    # This code only runs when you execute this file directly.
    # It allows you to test the login UI in isolation.

    import sys
    import os

    # To make the 'from Login import ...' imports work correctly,
    # we need to add the parent directory (the project root) to the Python path.
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    from Login import database

    # 1. Create a main Tkinter window to act as the parent.
    root = tk.Tk()
    root.withdraw()  # Hide this root window, we only want to see the login page.

    # 2. Define a dummy function for what to do on a successful login.
    #    For this test, it will just print a message and close the app.
    def placeholder_on_success(username):
        print(f"--- TEST: Login successful for user: {username} ---")
        print("--- TEST: Closing application. ---")
        root.destroy()

    # 3. Initialize the database so that the login/register buttons don't crash.
    print("--- TEST: Initializing database for UI preview... ---")
    database.initialise_database()

    # 4. Create an instance of your AuthWindow to display it.
    print("--- TEST: Launching AuthWindow... ---")
    login_window = AuthWindow(root, placeholder_on_success)

    # 5. Start the Tkinter event loop to show the window and make it interactive.
    root.mainloop()