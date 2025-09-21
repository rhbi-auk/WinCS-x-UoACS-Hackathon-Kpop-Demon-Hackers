import tkinter as tk
from tkinter import messagebox
import time

class PostureTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Posture Pomodoro Timer")
        self.root.geometry("500x700")
        self.root.configure(bg='#2E3440')
        
        # Timer variables
        self.work_time = 50 * 60
        self.break_time = 10 * 60
        self.time_remaining = self.work_time
        self.is_working = True
        self.is_running = False
        self.start_time = None
        
        # Posture state (0-4, with 4 being the worst posture)
        self.posture_state = 0
        
        # Avatar part positions (will be updated as posture changes)
        self.avatar_parts = {}
        
        # Create GUI elements
        self.create_widgets()
        
        # Start the timer update loop
        self.update_timer()
    
    def create_widgets(self):
        # Main title
        title_label = tk.Label(
            self.root, 
            text="Posture Pomodoro Timer", 
            font=("Arial", 20, "bold"),
            fg='#D8DEE9',
            bg='#2E3440'
        )
        title_label.pack(pady=20)
        
        # Timer display
        self.timer_label = tk.Label(
            self.root,
            text="50:00",
            font=("Arial", 36, "bold"),
            fg='#88C0D0',
            bg='#2E3440'
        )
        self.timer_label.pack(pady=10)
        
        # Time adjustment buttons frame
        adjust_frame = tk.Frame(self.root, bg='#2E3440')
        adjust_frame.pack(pady=10)
        
        # Decrease time button (-60 seconds)
        self.decrease_button = tk.Button(
            adjust_frame,
            text="-60s",
            command=self.decrease_time,
            font=("Arial", 12),
            bg='#BF616A',
            fg='#2E3440',
            width=6
        )
        self.decrease_button.pack(side=tk.LEFT, padx=5)
        
        # Increase time button (+60 seconds)
        self.increase_button = tk.Button(
            adjust_frame,
            text="+60s",
            command=self.increase_time,
            font=("Arial", 12),
            bg='#A3BE8C',
            fg='#2E3440',
            width=6
        )
        self.increase_button.pack(side=tk.LEFT, padx=5)
        
        # Avatar canvas
        self.avatar_canvas = tk.Canvas(
            self.root,
            width=300,
            height=300,
            bg='#3B4252',
            highlightthickness=0
        )
        self.avatar_canvas.pack(pady=20)
        
        # Draw the initial avatar
        self.draw_avatar()
        
        # Control buttons
        button_frame = tk.Frame(self.root, bg='#2E3440')
        button_frame.pack(pady=20)
        
        self.start_button = tk.Button(
            button_frame,
            text="Start",
            command=self.start_timer,
            font=("Arial", 14),
            bg='#A3BE8C',
            fg='#2E3440',
            width=10
        )
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.reset_button = tk.Button(
            button_frame,
            text="Reset",
            command=self.reset_timer,
            font=("Arial", 14),
            bg='#EBCB8B',
            fg='#2E3440',
            width=10
        )
        self.reset_button.pack(side=tk.LEFT, padx=10)
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text="Ready to work!",
            font=("Arial", 14),
            fg='#D8DEE9',
            bg='#2E3440'
        )
        self.status_label.pack(pady=10)
    
    def decrease_time(self):
        if self.time_remaining > 60:
            self.time_remaining -= 60
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
            elapsed_work_time = self.work_time - self.time_remaining
            
            if elapsed_work_time >= 40 * 60:
                self.posture_state = 4  # Very Poor
            elif elapsed_work_time >= 30 * 60:
                self.posture_state = 3  # Poor
            elif elapsed_work_time >= 20 * 60:
                self.posture_state = 2  # Moderate
            elif elapsed_work_time >= 10 * 60:
                self.posture_state = 1  # Fair
            else:
                self.posture_state = 0  # Good
        else:
            self.posture_state = 0
            
        self.draw_avatar()
    
    def draw_avatar(self):
        # Clear the canvas
        self.avatar_canvas.delete("all")
        
        # Base coordinates
        center_x = 150
        head_y = 100
        
        # Calculate positions based on posture state
        neck_length = 30 + (self.posture_state * 10)
        shoulder_y = head_y + neck_length
        back_curve = self.posture_state * 15
        
        # Draw head
        head = self.avatar_canvas.create_oval(
            center_x - 30, head_y - 30,
            center_x + 30, head_y + 30,
            fill='#E5E9F0', outline='#D8DEE9', width=2
        )
        self.avatar_parts["head"] = head
        
        # Draw eyes
        left_eye = self.avatar_canvas.create_oval(
            center_x - 15, head_y - 10,
            center_x - 5, head_y,
            fill='#2E3440'
        )
        right_eye = self.avatar_canvas.create_oval(
            center_x + 5, head_y - 10,
            center_x + 15, head_y,
            fill='#2E3440'
        )
        self.avatar_parts["left_eye"] = left_eye
        self.avatar_parts["right_eye"] = right_eye
        
        # Draw mouth (changes with posture state)
        mouth_y = head_y + 15
        if self.posture_state < 3:
            mouth = self.avatar_canvas.create_line(
                center_x - 10, mouth_y,
                center_x + 10, mouth_y,
                fill='#2E3440', width=2
            )
        else:
            mouth = self.avatar_canvas.create_arc(
                center_x - 10, mouth_y - 5,
                center_x + 10, mouth_y + 5,
                start=0, extent=-180,
                fill='', outline='#2E3440', width=2
            )
        self.avatar_parts["mouth"] = mouth
        
        # Draw neck
        neck = self.avatar_canvas.create_line(
            center_x, head_y + 30,
            center_x, shoulder_y,
            fill='#E5E9F0', width=8
        )
        self.avatar_parts["neck"] = neck
        
        # Draw shoulders
        shoulders = self.avatar_canvas.create_line(
            center_x - 50, shoulder_y,
            center_x + 50, shoulder_y,
            fill='#E5E9F0', width=20
        )
        self.avatar_parts["shoulders"] = shoulders
        
        # Draw back (curves based on posture state)
        back = self.avatar_canvas.create_line(
            center_x, shoulder_y,
            center_x - back_curve, shoulder_y + 100,
            fill='#E5E9F0', width=12
        )
        self.avatar_parts["back"] = back
        
        # Draw chair
        chair_y = shoulder_y + 120
        chair = self.avatar_canvas.create_rectangle(
            center_x - 70, chair_y,
            center_x + 70, chair_y + 20,
            fill='#5E81AC', outline='#81A1C1'
        )
        self.avatar_parts["chair"] = chair
        
        # Draw desk
        desk_y = shoulder_y + 40
        desk = self.avatar_canvas.create_rectangle(
            center_x - 100, desk_y,
            center_x + 100, desk_y + 10,
            fill='#5E81AC', outline='#81A1C1'
        )
        self.avatar_parts["desk"] = desk
        
        # Draw computer
        screen_height = 50
        computer = self.avatar_canvas.create_rectangle(
            center_x - 30, desk_y - screen_height,
            center_x + 30, desk_y,
            fill='#BF616A', outline='#D08770'
        )
        self.avatar_parts["computer"] = computer
        
        # Draw posture state indicator
        posture_labels = ["Good", "Fair", "Moderate", "Poor", "Very Poor"]
        posture_text = f"Posture: {posture_labels[self.posture_state]}"
        time_elapsed = (self.work_time - self.time_remaining) // 60
        time_text = f"Time Elapsed: {time_elapsed} min"
        
        posture_indicator = self.avatar_canvas.create_text(
            center_x, 20,
            text=posture_text,
            font=("Arial", 12, "bold"),
            fill='#D8DEE9'
        )
        self.avatar_parts["posture_text"] = posture_indicator
        
        time_indicator = self.avatar_canvas.create_text(
            center_x, 40,
            text=time_text,
            font=("Arial", 10),
            fill='#D8DEE9'
        )
        self.avatar_parts["time_text"] = time_indicator
    
    def move_avatar_part(self, part_name, new_x, new_y):
        """Move a specific avatar part to new coordinates"""
        if part_name in self.avatar_parts:
            self.avatar_canvas.coords(self.avatar_parts[part_name], new_x, new_y)
    
    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.start_time = time.time()
            self.start_button.config(text="Pause")
        else:
            self.is_running = False
            self.start_button.config(text="Resume")
    
    def reset_timer(self):
        self.is_running = False
        self.is_working = True
        self.time_remaining = self.work_time
        self.posture_state = 0
        self.start_button.config(text="Start")
        self.status_label.config(text="Ready to work!")
        self.update_timer_display()
        self.draw_avatar()
    
    def update_timer(self):
        if self.is_running:
            elapsed = time.time() - self.start_time
            self.time_remaining -= elapsed
            
            self.update_posture_state()
            
            if self.time_remaining <= 0:
                self.is_running = False
                if self.is_working:
                    self.is_working = False
                    self.time_remaining = self.break_time
                    self.show_break_message()
                    self.posture_state = 0
                else:
                    self.is_working = True
                    self.time_remaining = self.work_time
                
                self.draw_avatar()
                self.start_time = time.time()
                self.is_running = True
            
            self.start_time = time.time()
        
        self.update_timer_display()
        self.root.after(1000, self.update_timer)
    
    def update_timer_display(self):
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        timer_text = f"{int(minutes):02d}:{int(seconds):02d}"
        mode_text = "Work Mode" if self.is_working else "Break Time!"
        
        self.timer_label.config(text=timer_text)
        self.status_label.config(text=mode_text)
    
    def show_break_message(self):
        break_tasks = [
            "1. Correct your posture",
            "2. Stand up and walk around",
            "3. Look away from the screen for 20 seconds",
            "4. Stretch your arms and shoulders",
            "5. Take deep breaths for relaxation"
        ]
        
        message = "Time for a break!\n\nPlease do the following:\n\n" + "\n".join(break_tasks)
        messagebox.showinfo("Break Time!", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = PostureTimer(root)
    root.mainloop()



