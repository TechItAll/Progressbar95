import tkinter as tk
from tkinter import ttk
import threading
import time

class ProgressBar95:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Progressbar 95")
        
        # Remove window decorations (title bar, buttons, etc.)
        self.root.overrideredirect(True)
        
        # Set window size and position (back to original height without buttons)
        self.window_width = 400
        self.window_height = 60
        self.root.geometry(f"{self.window_width}x{self.window_height}+100+100")
        
        # Make window stay on top
        self.root.attributes('-topmost', True)
        
        # Progress value (0-100)
        self.progress_value = 0
        
        # Variables for dragging
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self.setup_ui()
        self.setup_drag_functionality()
        self.setup_keyboard_controls()
        
    def setup_ui(self):
        # Main frame with classic Windows 95 style border
        self.main_frame = tk.Frame(
            self.root,
            relief='sunken',
            bd=2,
            bg='#c0c0c0'  # Classic Windows 95 gray
        )
        self.main_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Progress bar area
        self.progress_frame = tk.Frame(
            self.main_frame,
            relief='sunken',
            bd=1,
            bg='#9e9e9e',  # Darker gray background like Progressbar 95
            height=32  # Increased to account for border
        )
        self.progress_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.progress_frame.pack_propagate(False)
        
        # Progress fill (BLACK debug segments)
        self.progress_fill = tk.Frame(
            self.progress_frame,
            bg='#000000',  # BLACK for debug/testing
            height=32,  # Match parent height to fill completely
            bd=0,  # No border
            relief='flat'
        )
        
        # Percentage label with transparent background
        self.percent_label = tk.Label(
            self.progress_frame,
            text="0%",
            font=('MS Sans Serif', 10, 'bold'),
            fg='white',  # White text
            bd=0,
            highlightthickness=0
        )
        self.percent_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Make label background transparent
        self.percent_label.config(bg=self.progress_frame.cget('bg'))
        
        self.update_progress_display()
    
    def setup_drag_functionality(self):
        # Bind drag events to all widgets so you can drag from anywhere
        widgets_to_bind = [self.root, self.main_frame, self.progress_frame, self.percent_label]
        
        for widget in widgets_to_bind:
            widget.bind('<Button-1>', self.start_drag)
            widget.bind('<B1-Motion>', self.on_drag)
            widget.bind('<ButtonRelease-1>', self.stop_drag)
    
    def setup_keyboard_controls(self):
        # Bind keyboard controls
        self.root.bind('<Escape>', self.exit_program)
        self.root.bind('<Control-c>', self.exit_program)
        self.root.bind('<KeyPress-minus>', lambda e: self.decrease_progress())
        self.root.bind('<KeyPress-equal>', lambda e: self.increase_progress())  # = key (plus without shift)
        
        # Make sure the window can receive keyboard focus
        self.root.focus_set()
    
    def start_drag(self, event):
        # Record the starting position for dragging
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        
        # Get current window position
        self.window_start_x = self.root.winfo_x()
        self.window_start_y = self.root.winfo_y()
    
    def on_drag(self, event):
        # Calculate new window position
        delta_x = event.x_root - self.drag_start_x
        delta_y = event.y_root - self.drag_start_y
        
        new_x = self.window_start_x + delta_x
        new_y = self.window_start_y + delta_y
        
        # Move the window
        self.root.geometry(f"{self.window_width}x{self.window_height}+{new_x}+{new_y}")
    
    def stop_drag(self, event):
        # Dragging stopped
        pass
    
    def update_progress_display(self):
        # Update the visual progress bar
        progress_width = int((self.progress_value / 100) * (self.window_width - 20))
        
        # Remove old progress fill
        self.progress_fill.place_forget()
        
        # Place new progress fill with updated width
        if progress_width > 0:
            self.progress_fill.place(x=0, y=0, width=progress_width, height=32)
        
        # Update percentage text
        self.percent_label.config(text=f"{self.progress_value}%")
    
    def set_progress(self, value):
        """Set the progress value (0-100)"""
        self.progress_value = max(0, min(100, value))
        self.update_progress_display()
    
    def increase_progress(self):
        """Increase progress by 5%"""
        self.set_progress(self.progress_value + 5)
    
    def decrease_progress(self):
        """Decrease progress by 5%"""
        self.set_progress(self.progress_value - 5)
    
    def exit_program(self, event=None):
        """Exit the program"""
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        # Start the GUI main loop
        self.root.mainloop()

if __name__ == "__main__":
    # Create and run the progress bar window
    progressbar = ProgressBar95()
    progressbar.run()