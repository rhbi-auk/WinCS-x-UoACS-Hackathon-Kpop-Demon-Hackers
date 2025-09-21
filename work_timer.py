import tkinter as tk
from tkinter import messagebox
import time
import os

class WorkTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Work Timer")
        self.root.geometry("640x640")
        self.root.configure(bg='#F5F5DC')  # Beige background
        
        # Timer variables
        self.original_work_time = 50 * 60  # 50 minutes
        self.work_time = 50 * 60
        self.break_time = 5 * 60
        self.time_remaining = self.work_time
        self.is_working = True
        self.is_running = False
        self.start_time = None
        
        # Posture state (0-4)
        self.posture_state = 0
        
        # Load images
        self.posture_images = []
        self.computer_image = None
        self.load_images()
        
        # Create GUI elements
        self.create_widgets()
        
        # Start the timer update loop
        self.update_timer()
    
    def load_images(self):
        # Try to load images using Tkinter's PhotoImage
        try:
            # Load posture images
            for i in range(1, 5):
                image_path = f"posture{i}.png"
                if os.path.exists(image_path):
                    img = tk.PhotoImage(file=image_path).zoom(4,4)
                    # Store a reference to prevent garbage collection
                    self.posture_images.append(img)
                else:
                    print(f"Image not found: {image_path}")
                    self.posture_images = None
                    break
            
            # Load computer image
            computer_path = "computer-removebg-preview.png"
            if os.path.exists(computer_path):
                self.computer_image = tk.PhotoImage(file=computer_path).subsample(2,2)
            else:
                print(f"Image not found: {computer_path}")
                self.computer_image = None
                
        except Exception as e:
            print(f"Error loading images: {e}")
            # Fallback to drawing if images can't be loaded
            self.posture_images = None
            self.computer_image = None
    
    def create_widgets(self):
        # Main title
        title_label = tk.Label(
            self.root, 
            text="Work Timer", 
            font=("Arial", 24, "bold"),
            fg='#4B3621',  # Dark brown text
            bg='#F5F5DC'   # Beige background
        )
        title_label.pack(pady=10)
        
        # Timer display
        self.timer_label = tk.Label(
            self.root,
            text="50:00",
            font=("Arial", 48, "bold"),  # Larger font for timer
            fg='#8B4513',  # Saddle brown
            bg='#F5F5DC'
        )
        self.timer_label.pack(pady=5)
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text="Work Mode",
            font=("Arial", 14),
            fg='#4B3621',
            bg='#F5F5DC'
        )
        self.status_label.pack(pady=5)
        
        # Control buttons (placed BEFORE the images)
        button_frame = tk.Frame(self.root, bg='#F5F5DC')
        button_frame.pack(pady=10)
        
        self.start_button = tk.Button(
            button_frame,
            text="Start",
            command=self.start_timer,
            font=("Arial", 14),
            bg='#A3BE8C',  # Sage green
            fg='#4B3621',
            width=10,
            relief=tk.RAISED,
            bd=2
        )
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.reset_button = tk.Button(
            button_frame,
            text="Reset",
            command=self.reset_timer,
            font=("Arial", 14),
            bg='#EBCB8B',  # Light tan
            fg='#4B3621',
            width=10,
            relief=tk.RAISED,
            bd=2
        )
        self.reset_button.pack(side=tk.LEFT, padx=10)
        
        # Time adjustment buttons frame (placed BEFORE the images)
        adjust_frame = tk.Frame(self.root, bg='#F5F5DC')
        adjust_frame.pack(pady=10)
        
        # Decrease time button (-60 seconds)
        self.decrease_button = tk.Button(
            adjust_frame,
            text="-60s",
            command=self.decrease_time,
            font=("Arial", 12),
            bg='#D2B48C',  # Tan
            fg='#4B3621',
            width=6,
            height=1,
            relief=tk.RAISED,
            bd=2
        )
        self.decrease_button.pack(side=tk.LEFT, padx=5)
        
        # Increase time button (+60 seconds)
        self.increase_button = tk.Button(
            adjust_frame,
            text="+60s",
            command=self.increase_time,
            font=("Arial", 12),
            bg='#D2B48C',  # Tan
            fg='#4B3621',
            width=6,
            height=1,
            relief=tk.RAISED,
            bd=2
        )
        self.increase_button.pack(side=tk.LEFT, padx=5)
        
        # Main content frame for images
        content_frame = tk.Frame(self.root, bg='#F5F5DC')
        content_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Canvas for avatar and computer
        self.canvas = tk.Canvas(
            content_frame,
            width=600,
            height=350,  # Increased height
            bg='#F5F5DC',
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Draw the initial scene
        self.draw_scene()

    def draw_scene(self):
        self.canvas.delete("all")
        
        # Center positions for avatar and computer
        canvas_center_x = 300  # Half of canvas width (600/2)
        canvas_center_y = 175  # Half of canvas height (350/2)
        
        # Draw avatar on the left side (facing right)
        if self.posture_images and len(self.posture_images) >= 4:
            avatar_x = canvas_center_x + 15  # Left of center
            avatar_y = canvas_center_y + 20   # Slightly below center
            
            # Use the appropriate posture image based on state
            img_index = min(self.posture_state, 3)  # Ensure we don't go out of bounds
            self.canvas.create_image(avatar_x, avatar_y, image=self.posture_images[img_index], anchor=tk.CENTER)
        else:
            # Fallback if posture images not available
            self.draw_avatar_fallback(canvas_center_x - 120, canvas_center_y + 20)
        
        # Draw computer on the right side (facing left)
        if self.computer_image:
            comp_x = canvas_center_x + 120  # Right of center
            comp_y = canvas_center_y + 20   # Same height as avatar
            self.canvas.create_image(comp_x, comp_y, image=self.computer_image, anchor=tk.CENTER)
        else:
            # Fallback if computer image not available
            comp_width = 100
            comp_height = 70
            comp_x = canvas_center_x + 120 - comp_width/2
            comp_y = canvas_center_y + 20 - comp_height/2
            
            # Computer monitor
            self.canvas.create_rectangle(
                comp_x, comp_y,
                comp_x + comp_width, comp_y + comp_height,
                fill='#2F4F4F', outline='#2F4F4F', width=2
            )
        
        # Draw a simple desk/table between them
        desk_width = 200
        desk_height = 10
        desk_x = canvas_center_x - 300
        desk_y = canvas_center_y + 70

    def draw_avatar_fallback(self, x, y):
        # Fallback drawing if images aren't available
        head_y = y - 40
        
        # Calculate positions based on posture state
        neck_length = 20 + (self.posture_state * 8)
        shoulder_y = head_y + neck_length
        back_curve = self.posture_state * 12
        
        # Draw head (facing right)
        self.canvas.create_oval(
            x - 25, head_y - 25,
            x + 25, head_y + 25,
            fill='#FFEBCD', outline='#DEB887', width=2
        )
        
        # Draw eyes (looking right toward the computer)
        self.canvas.create_oval(
            x + 5, head_y - 10,
            x + 15, head_y,
            fill='#4B3621'
        )
        
        # Draw mouth (changes with posture state)
        mouth_y = head_y + 10
        if self.posture_state < 3:
            self.canvas.create_line(
                x - 5, mouth_y,
                x + 5, mouth_y,
                fill='#4B3621', width=2
            )
        else:
            self.canvas.create_arc(
                x - 5, mouth_y - 3,
                x + 5, mouth_y + 3,
                start=0, extent=-180,
                fill='', outline='#4B3621', width=2
            )
        
        # Draw neck
        self.canvas.create_line(
            x, head_y + 25,
            x, shoulder_y,
            fill='#FFEBCD', width=6
        )
        
        # Draw shoulders
        self.canvas.create_line(
            x - 30, shoulder_y,
            x + 30, shoulder_y,
            fill='#FFEBCD', width=16
        )
        
        # Draw back (curves based on posture state)
        self.canvas.create_line(
            x, shoulder_y,
            x - back_curve, shoulder_y + 80,
            fill='#FFEBCD', width=10
        )

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.start_time = time.time()
            self.start_button.config(text="Pause")
            self.status_label.config(text="Work Mode")
        else:
            self.is_running = False
            self.start_button.config(text="Resume")
            mode = "Work" if self.is_working else "Break"
            self.status_label.config(text=f"{mode} Mode")
    
    def reset_timer(self):
        self.is_running = False
        self.is_working = True
        self.work_time = self.original_work_time
        self.time_remaining = self.work_time
        self.posture_state = 0
        self.start_button.config(text="Start")
        self.status_label.config(text="Work Mode")
        self.update_timer_display()
        self.draw_scene()
    
    def update_timer(self):
        if self.is_running:
            elapsed = time.time() - self.start_time
            self.time_remaining -= elapsed
            
            # Update posture based on time remaining
            self.update_posture_state()
            
            if self.time_remaining <= 0:
                self.is_running = False
                if self.is_working:
                    # Work period ended, start break
                    self.is_working = False
                    self.time_remaining = self.break_time
                    self.show_break_message()
                    self.posture_state = 0  # Reset posture after break
                    self.status_label.config(text="Break Mode")
                else:
                    # Break ended, start work period
                    self.is_working = True
                    self.work_time = self.original_work_time
                    self.time_remaining = self.work_time
                    self.show_work_message()
                    self.status_label.config(text="Work Mode")
                
                self.draw_scene()
                self.start_time = time.time()
                self.is_running = True
            
            self.start_time = time.time()
        
        self.update_timer_display()
        self.root.after(1000, self.update_timer)
    
    def update_timer_display(self):
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        timer_text = f"{int(minutes):02d}:{int(seconds):02d}"
        
        self.timer_label.config(text=timer_text)
        self.draw_scene()  # Redraw to update time remaining text

    def decrease_time(self):
        self.time_remaining -= 60
        if self.time_remaining < 0:
            self.time_remaining = 0
        if self.is_working:
            self.work_time = self.time_remaining
        self.update_posture_state()
        self.update_timer_display()
    
    def increase_time(self):
        self.time_remaining += 60
        if self.is_working:
            self.work_time = self.time_remaining
        self.update_posture_state()
        self.update_timer_display()
    
    def update_posture_state(self):
        if self.is_working:
            minutes_remaining = self.time_remaining // 60
            
            # Set posture state based on time remaining thresholds
            if minutes_remaining >= 41:  # 50-41 minutes
                self.posture_state = 0  # Good
            elif minutes_remaining >= 31:  # 40-31 minutes
                self.posture_state = 1  # Fair
            elif minutes_remaining >= 21:  # 30-21 minutes
                self.posture_state = 2  # Moderate
            elif minutes_remaining >= 11:  # 20-11 minutes
                self.posture_state = 3  # Poor
            else:  # 10-0 minutes
                self.posture_state = 4  # Very Poor
        else:
            # During breaks, posture is always good
            self.posture_state = 0
            
        self.draw_scene()

    def show_break_message(self):
        break_tasks = [
            "1. Correct your posture",
            "2. Stand up and walk around",
            "3. Look away from your screen",
            "4. Stretch your arms and shoulders"
        ]
        
        message = "Time for a break!\n\nPlease do the following:\n\n" + "\n".join(break_tasks)
        messagebox.showinfo("Break Time!", message)
        
    def show_work_message(self):
        messagebox.showinfo("Work Time", "Break is over! Time to get back to work.")

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkTimer(root)
    root.mainloop()