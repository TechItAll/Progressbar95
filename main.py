import tkinter as tk
from tkinter import ttk
import threading
import time
import random
import os
os.system('cls' if os.name == 'nt' else 'clear')  # Clear console for better readability

class Segment:
    """Represents a falling segment in the game"""
    def __init__(self, x, y, color='#0066cc', value=5):
        self.x = x
        self.y = y
        self.color = color  # Blue segments
        self.value = value  # Progress value when caught (5%)
        self.width = 30
        self.height = 20
        self.speed = 2  # Falling speed
        self.widget = None  # Will hold the tkinter widget

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
        
        # Progress value (0-100) - now supporting multiple colors
        self.progress_value = 0
        self.progress_segments = []  # List of progress segments: [{'color': '#color', 'value': 5}, ...]
        
        # Game variables
        self.segments = []  # List of falling segments
        self.max_segments = 5
        self.last_spawn_time = time.time()
        self.spawn_delay = random.uniform(1.0, 3.0)  # Random spawn timing
        self.game_running = False
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Create invisible fullscreen window for segments
        self.screen_window = tk.Toplevel(self.root)
        self.screen_window.overrideredirect(True)
        self.screen_window.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.screen_window.attributes('-transparentcolor', 'white')
        self.screen_window.configure(bg='white')
        self.screen_window.attributes('-topmost', True)
        
        # Variables for dragging
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self.setup_ui()
        self.setup_drag_functionality()
        self.setup_keyboard_controls()
        self.start_game()
        
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
        
        # List to store multiple colored progress fills
        self.progress_fills = []
        
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
        
        # Make label background transparent and ensure it stays on top
        self.percent_label.config(bg=self.progress_frame.cget('bg'))
        self.percent_label.lift()  # Bring to front
        
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
        """Update the visual progress bar with multiple colored segments"""
        # Clear all existing progress fills
        for fill in self.progress_fills:
            fill.destroy()
        self.progress_fills.clear()
        
        # Calculate total progress and create colored segments
        current_x = 0
        total_width = self.window_width - 20  # Account for padding
        
        for segment in self.progress_segments:
            segment_width = int((segment['value'] / 100) * total_width)
            if segment_width > 0:
                fill = tk.Frame(
                    self.progress_frame,
                    bg=segment['color'],
                    height=32,
                    bd=0,
                    relief='flat'
                )
                fill.place(x=current_x, y=0, width=segment_width, height=32)
                self.progress_fills.append(fill)
                current_x += segment_width
        
        # Update percentage text and keep it on top
        self.percent_label.config(text=f"{self.progress_value}%")
        self.percent_label.lift()  # Keep percentage text visible above colored segments
    
    def set_progress(self, value):
        """Set the progress value (0-100)"""
        self.progress_value = max(0, min(100, value))
        self.update_progress_display()
    
    def add_progress_segment(self, color, value):
        """Add a colored progress segment"""
        if self.progress_value + value <= 100:
            self.progress_segments.append({'color': color, 'value': value})
            self.progress_value += value
            self.update_progress_display()
            return True
        return False
    
    def remove_last_segment(self):
        """Remove the last progress segment"""
        if self.progress_segments:
            last_segment = self.progress_segments.pop()
            self.progress_value -= last_segment['value']
            self.update_progress_display()
            return True
        return False
    
    def increase_progress(self):
        """Add a black segment (5%)"""
        success = self.add_progress_segment('#000000', 5)  # Black segment
        if success:
            print(f"Black segment added! +5% -> {self.progress_value}%")
        else:
            print("Progress bar full - cannot add more segments!")
    
    def decrease_progress(self):
        """Remove the last segment"""
        success = self.remove_last_segment()
        if success:
            print(f"Last segment removed! -> {self.progress_value}%")
        else:
            print("No segments to remove!")
    
    def exit_program(self, event=None):
        """Exit the program"""
        self.game_running = False
        # Clean up segments
        for segment in self.segments:
            if segment.widget:
                segment.widget.destroy()
        if hasattr(self, 'screen_window'):
            self.screen_window.destroy()
        self.root.quit()
        self.root.destroy()
    
    def start_game(self):
        """Start the game loop"""
        self.game_running = True
        self.game_loop()
    
    def game_loop(self):
        """Main game loop - handles segment spawning, movement, and collision detection"""
        if not self.game_running:
            return
        
        current_time = time.time()
        
        # Spawn new segments if needed
        if (len(self.segments) < self.max_segments and 
            current_time - self.last_spawn_time > self.spawn_delay):
            self.spawn_segment()
            self.last_spawn_time = current_time
            self.spawn_delay = random.uniform(1.0, 3.0)  # Random next spawn
        
        # Update all segments
        self.update_segments()
        
        # Check for collisions
        self.check_collisions()
        
        # Schedule next game loop iteration
        self.root.after(50, self.game_loop)  # 20 FPS
    
    def spawn_segment(self):
        """Spawn a new blue segment at the top of the screen"""
        # Random X position within screen bounds
        x = random.randint(50, self.screen_width - 80)
        y = -30  # Start above screen
        
        segment = Segment(x, y, '#0066cc', 5)  # Blue segment worth 5%
        # Make segments thinner like progress bar segments
        segment.width = 15  # Thinner like progress bar segments
        segment.height = 25
        
        # Create visual widget for the segment on the fullscreen window
        segment.widget = tk.Frame(
            self.screen_window,  # Use fullscreen window instead of progress bar
            bg=segment.color,
            width=segment.width,
            height=segment.height,
            relief='raised',
            bd=1  # Smaller border for thinner look
        )
        segment.widget.place(x=x, y=y)
        
        self.segments.append(segment)
    
    def update_segments(self):
        """Update positions of all falling segments"""
        segments_to_remove = []
        
        for segment in self.segments:
            # Move segment down
            segment.y += segment.speed
            
            # Update visual position
            if segment.widget:
                segment.widget.place(x=segment.x, y=segment.y)
            
            # Check if segment hit the bottom of screen
            if segment.y > self.screen_height:
                segments_to_remove.append(segment)
        
        # Remove segments that hit the bottom
        for segment in segments_to_remove:
            self.remove_segment(segment)
    
    def check_collisions(self):
        """Check if segments collide with the progress bar window"""
        window_x = self.root.winfo_x()
        window_y = self.root.winfo_y()
        window_width = self.window_width
        window_height = self.window_height
        
        segments_to_remove = []
        
        for segment in self.segments:
            # Check if segment overlaps with progress bar window
            if (segment.x < window_x + window_width and
                segment.x + segment.width > window_x and
                segment.y < window_y + window_height and
                segment.y + segment.height > window_y):
                
                # Collision detected!
                # Check if collision is in empty part of progress bar
                collision_x_relative = segment.x - window_x
                progress_pixels = int((self.progress_value / 100) * (window_width - 20))
                empty_start = progress_pixels + 10  # Account for padding
                
                if collision_x_relative > empty_start:
                    # Caught in empty area - add colored progress!
                    success = self.add_progress_segment(segment.color, segment.value)
                    if success:
                        print(f"Blue segment caught! +{segment.value}% -> {self.progress_value}%")
                    else:
                        print("Progress bar full!")
                else:
                    # Hit filled area - segment breaks
                    print("Segment broken on filled area!")
                
                segments_to_remove.append(segment)
        
        # Remove caught/broken segments
        for segment in segments_to_remove:
            self.remove_segment(segment)
    
    def remove_segment(self, segment):
        """Remove a segment from the game"""
        if segment in self.segments:
            self.segments.remove(segment)
        if segment.widget:
            segment.widget.destroy()
    
    def run(self):
        # Start the GUI main loop
        self.root.mainloop()

if __name__ == "__main__":
    # Create and run the progress bar window
    progressbar = ProgressBar95()
    progressbar.run()