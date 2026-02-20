import tkinter as tk
from tkinter import ttk
import threading
import time
import random
import math
from tkinter import font
import os
os.system('cls' if os.name == 'nt' else 'clear')  # Clear console for better readability

class Segment:
    """Represents a falling segment in the game"""
    def __init__(self, x, y, color='#0066cc', value=5, segment_type='blue', points=100, speed=2):
        self.x = x
        self.y = y
        self.color = color  # Segment color
        self.value = value  # Progress value when caught (5%)
        self.segment_type = segment_type  # 'blue', 'yellow', 'black'
        self.points = points  # Points awarded when caught
        self.width = 30
        self.height = 20
        self.speed = speed  # Falling speed - now customizable per segment!
        self.widget = None  # Will hold the tkinter widget

class ProgressBar95:
    def __init__(self):
        # ===========================================
        # EASY SPEED CONFIGURATION - ADJUST THESE!
        # ===========================================
        self.BLUE_SPEED = 3      # Blue segments fall faster (harder to catch) / Default 3
        self.YELLOW_SPEED = 2    # Yellow segments fall slower (easier to catch) / Default 2
        self.BLACK_SPEED = 2     # Black debug segments speed / Default 2 but idk why theres a speed here cuz debug segments dont fall
        self.RED_SPEED = 4       # Red segments fall FAST (game over segments!)
        
        # ===========================================
        # EASY POINTS CONFIGURATION - ADJUST THESE!
        # ===========================================
        self.BLUE_POINTS = 100   # Points for catching blue segments
        self.YELLOW_POINTS = 50  # Points for catching yellow segments (corrupted)
        self.BLACK_POINTS = 0    # Points for black segments (debug only)
        self.RED_POINTS = 0      # Red segments = game over (no points)
        
        # ===========================================
        # DEBUG CONFIGURATION - ADJUST THIS!
        # ===========================================
        self.DEBUG_MODE = False   # Enable/disable debug controls (- = keys and B Y spawning)
        
        # ===========================================
        # SPAWN WEIGHTS - ADJUST THESE! (Higher = more frequent)
        # ===========================================
        self.BLUE_WEIGHT = 70    # Blue segments spawn most often
        self.YELLOW_WEIGHT = 25  # Yellow segments spawn regularly  
        self.RED_WEIGHT = 5      # Red segments spawn rarely (DANGER!)
        # ===========================================
        
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
        self.progress_segments = []  # List of progress segments: [{'color': '#color', 'value': 5, 'type': 'blue'}, ...]
        
        # Point system
        self.total_points = 0
        self.blue_segments_caught = 0
        self.yellow_segments_caught = 0
        self.black_segments_added = 0
        
        # Game over system
        self.red_segment_hit = False
        self.game_frozen = False
        self.freeze_start_time = 0
        self.scan_progress_used = False
        self.in_blue_screen = False
        
        # Game variables
        self.segments = []  # List of falling segments
        self.max_segments = 5
        self.last_spawn_time = time.time()
        self.spawn_delay = random.uniform(1.0, 3.0)  # Random spawn timing
        self.game_running = False
        self.game_ended = False
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
        
        # Debug-controlled keyboard shortcuts
        if self.DEBUG_MODE:
            self.root.bind('<KeyPress-minus>', lambda e: self.decrease_progress())
            self.root.bind('<KeyPress-equal>', lambda e: self.increase_progress())  # = key (plus without shift)
            self.root.bind('<KeyPress-b>', lambda e: self.spawn_debug_blue())
            self.root.bind('<KeyPress-y>', lambda e: self.spawn_debug_yellow())
            self.root.bind('<KeyPress-r>', lambda e: self.spawn_debug_red())  # RED DANGER!
        
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
    
    def add_progress_segment(self, color, value, segment_type='blue', points=0):
        """Add a colored progress segment"""
        if self.progress_value + value <= 100:
            self.progress_segments.append({
                'color': color, 
                'value': value, 
                'type': segment_type
            })
            self.progress_value += value
            self.total_points += points
            
            # Track segment counts for end screen stats
            if segment_type == 'blue':
                self.blue_segments_caught += 1
            elif segment_type == 'yellow':
                self.yellow_segments_caught += 1
            elif segment_type == 'black':
                self.black_segments_added += 1
            
            self.update_progress_display()
            
            # Check for game completion
            if self.progress_value >= 100:
                self.end_game()
            
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
        if not self.DEBUG_MODE:
            return
            
        success = self.add_progress_segment('#000000', 5, 'black', self.BLACK_POINTS)  # Use configurable points
        if success:
            print(f"Debug: Black segment added! +5% -> {self.progress_value}%")
        else:
            print("Progress bar full - cannot add more segments!")
    
    def decrease_progress(self):
        """Remove the last segment"""
        if not self.DEBUG_MODE:
            return
            
        success = self.remove_last_segment()
        if success:
            print(f"Debug: Last segment removed! -> {self.progress_value}%")
        else:
            print("No segments to remove!")
    
    def spawn_debug_blue(self):
        """Debug: Spawn a blue segment manually"""
        if not self.DEBUG_MODE:
            return
        
        # Random X position within screen bounds
        x = random.randint(50, self.screen_width - 80)
        y = -30  # Start above screen
        
        segment = Segment(x, y, '#0066cc', 5, 'blue', self.BLUE_POINTS, self.BLUE_SPEED)
        segment.width = 15
        segment.height = 25
        
        # Create visual widget for the segment on the fullscreen window
        segment.widget = tk.Frame(
            self.screen_window,
            bg=segment.color,
            width=segment.width,
            height=segment.height,
            relief='raised',
            bd=1
        )
        segment.widget.place(x=x, y=y)
        
        self.segments.append(segment)
        print(f"Debug: Blue segment spawned at position {x}")
    
    def spawn_debug_yellow(self):
        """Debug: Spawn a yellow segment manually"""
        if not self.DEBUG_MODE:
            return
        
        # Random X position within screen bounds
        x = random.randint(50, self.screen_width - 80)
        y = -30  # Start above screen
        
        segment = Segment(x, y, '#cccc00', 5, 'yellow', self.YELLOW_POINTS, self.YELLOW_SPEED)
        segment.width = 15
        segment.height = 25
        
        # Create visual widget for the segment on the fullscreen window
        segment.widget = tk.Frame(
            self.screen_window,
            bg=segment.color,
            width=segment.width,
            height=segment.height,
            relief='raised',
            bd=1
        )
        segment.widget.place(x=x, y=y)
        
        self.segments.append(segment)
        print(f"Debug: Yellow segment spawned at position {x}")
    
    def spawn_debug_red(self):
        """Debug: Spawn a RED segment manually - DANGER!"""
        if not self.DEBUG_MODE:
            return
        
        # Random X position within screen bounds
        x = random.randint(50, self.screen_width - 80)
        y = -30  # Start above screen
        
        segment = Segment(x, y, '#cc0000', 0, 'red', self.RED_POINTS, self.RED_SPEED)
        segment.width = 15
        segment.height = 25
        
        # Create visual widget for the segment on the fullscreen window
        segment.widget = tk.Frame(
            self.screen_window,
            bg=segment.color,
            width=segment.width,
            height=segment.height,
            relief='raised',
            bd=1
        )
        segment.widget.place(x=x, y=y)
        
        self.segments.append(segment)
        print(f"💀 Debug: RED DANGER SEGMENT spawned at position {x}!")
    
    def exit_program(self, event=None):
        """Exit the program"""
        self.game_running = False
        self.game_ended = True
        
        # Clean up segments
        for segment in self.segments:
            if segment.widget:
                segment.widget.destroy()
        
        # Clean up windows
        try:
            if hasattr(self, 'screen_window'):
                self.screen_window.destroy()
            if hasattr(self, 'end_window'):
                self.end_window.destroy()
            if hasattr(self, 'blue_screen'):
                self.blue_screen.destroy()
        except:
            pass
            
        self.root.quit()
        self.root.destroy()
    
    def start_game(self):
        """Start the game loop"""
        self.game_running = True
        self.game_loop()
    
    def game_loop(self):
        """Main game loop - handles segment spawning, movement, and collision detection"""
        if not self.game_running or self.game_ended or self.in_blue_screen:
            return
        
        current_time = time.time()
        
        # Don't spawn or update if game is frozen (red segment effect)
        if not self.game_frozen:
            # Spawn new segments if needed (only if game hasn't ended)
            if (not self.game_ended and len(self.segments) < self.max_segments and 
                current_time - self.last_spawn_time > self.spawn_delay):
                self.spawn_segment()
                self.last_spawn_time = current_time
                self.spawn_delay = random.uniform(1.0, 3.0)  # Random next spawn
            
            # Update all segments
            self.update_segments()
            
            # Check for collisions (only if game hasn't ended)
            if not self.game_ended:
                self.check_collisions()
        
        # Schedule next game loop iteration
        self.root.after(50, self.game_loop)  # 20 FPS
    
    def spawn_segment(self):
        """Spawn a new segment at the top of the screen"""
        # Random X position within screen bounds
        x = random.randint(50, self.screen_width - 80)
        y = -30  # Start above screen
        
        # Calculate spawn probabilities based on weights
        total_weight = self.BLUE_WEIGHT + self.YELLOW_WEIGHT + self.RED_WEIGHT
        blue_chance = self.BLUE_WEIGHT / total_weight
        yellow_chance = self.YELLOW_WEIGHT / total_weight
        # red_chance = self.RED_WEIGHT / total_weight (remaining probability)
        
        # Randomly choose segment type based on weights
        rand = random.random()
        if rand < blue_chance:
            # Blue segment (normal) - faster speed, more points
            segment = Segment(x, y, '#0066cc', 5, 'blue', self.BLUE_POINTS, self.BLUE_SPEED)
        elif rand < blue_chance + yellow_chance:
            # Yellow segment (corrupted) - slower speed, fewer points
            segment = Segment(x, y, '#cccc00', 5, 'yellow', self.YELLOW_POINTS, self.YELLOW_SPEED)
        else:
            # RED segment (GAME OVER!) - fast speed, deadly
            segment = Segment(x, y, '#cc0000', 0, 'red', self.RED_POINTS, self.RED_SPEED)
        
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
    
    def check_collisions(self):
        """Check if segments collide with the progress bar window"""
        if self.game_frozen:  # Don't check collisions when game is frozen
            return
            
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
                
                # RED SEGMENT = INSTANT GAME OVER!
                if segment.segment_type == 'red':
                    print("💀 RED SEGMENT HIT - GAME OVER!")
                    self.trigger_red_segment_hit()
                    segments_to_remove.append(segment)
                    continue
                
                # Regular collision logic for other segments
                collision_x_relative = segment.x - window_x
                progress_pixels = int((self.progress_value / 100) * (window_width - 20))
                empty_start = progress_pixels + 10  # Account for padding
                
                if collision_x_relative > empty_start:
                    # Caught in empty area - add colored progress!
                    success = self.add_progress_segment(
                        segment.color, 
                        segment.value, 
                        segment.segment_type, 
                        segment.points
                    )
                    if success:
                        print(f"{segment.segment_type.title()} segment caught! +{segment.value}% (+{segment.points} points) -> {self.progress_value}%")
                    else:
                        print("Progress bar full!")
                else:
                    # Hit filled area - segment breaks
                    print(f"{segment.segment_type.title()} segment broken on filled area!")
                
                segments_to_remove.append(segment)
        
        # Remove caught/broken segments
        for segment in segments_to_remove:
            self.remove_segment(segment)
    
    def trigger_red_segment_hit(self):
        """Handle red segment collision - freeze game and show ERROR"""
        self.red_segment_hit = True
        self.game_frozen = True
        self.freeze_start_time = time.time()
        
        # Change percentage text to ERROR
        self.percent_label.config(text="ERROR", fg="red")
        
        # Schedule blue screen after 1 second freeze
        self.root.after(1000, self.show_blue_screen)
    
    def update_segments(self):
        """Update positions of all falling segments"""
        if self.game_frozen:  # Don't update when frozen
            return
            
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
    
    def show_blue_screen(self):
        """Show the blue screen of death with scan options"""
        if self.in_blue_screen:
            return
            
        self.in_blue_screen = True
        
        # Hide main progress bar window
        self.root.withdraw()
        
        # Create blue screen window
        self.blue_screen = tk.Toplevel()
        self.blue_screen.title("SYSTEM ERROR")
        self.blue_screen.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.blue_screen.configure(bg='#002eb3')  # Classic BSOD blue
        self.blue_screen.attributes('-topmost', True)
        self.blue_screen.overrideredirect(True)
        
        # Error message
        error_text = tk.Label(
            self.blue_screen,
            text="⚠️ CRITICAL SYSTEM ERROR ⚠️\n\nA red segment has corrupted the progress bar.\nSystem recovery options:",
            font=('MS Sans Serif', 16, 'bold'),
            bg='#002eb3',
            fg='white',
            justify='center'
        )
        error_text.pack(pady=100)
        
        # Button frame
        button_frame = tk.Frame(self.blue_screen, bg='#002eb3')
        button_frame.pack(pady=50)
        
        # Scan Progress button (only if not already used or debug mode)
        if not self.scan_progress_used or self.DEBUG_MODE:
            scan_btn = tk.Button(
                button_frame,
                text="🔧 SCAN PROGRESS\n(Recovery Mode)",
                font=('MS Sans Serif', 14, 'bold'),
                bg='#0066cc',
                fg='white',
                width=20,
                height=3,
                command=self.start_scan_progress
            )
            scan_btn.pack(side='left', padx=20)
        
        # Continue/Quit button
        quit_btn = tk.Button(
            button_frame,
            text="❌ CONTINUE\n(Quit Game)",
            font=('MS Sans Serif', 14, 'bold'),
            bg='#cc0000',
            fg='white',
            width=20,
            height=3,
            command=self.quit_from_blue_screen
        )
        quit_btn.pack(side='right', padx=20)
    
    def start_scan_progress(self):
        """Start the scan progress mini-game"""
        # Mark scan progress as used
        self.scan_progress_used = True
        
        # Clear blue screen content
        for widget in self.blue_screen.winfo_children():
            widget.destroy()
        
        # Scan progress title
        title_label = tk.Label(
            self.blue_screen,
            text="⚡ EMERGENCY SCAN PROGRESS ⚡\n\nClick rapidly to complete scan before error spreads!",
            font=('MS Sans Serif', 14, 'bold'),
            bg='#002eb3',
            fg='white',
            justify='center'
        )
        title_label.pack(pady=50)
        
        # Progress bars frame
        bars_frame = tk.Frame(self.blue_screen, bg='#002eb3')
        bars_frame.pack(pady=50)
        
        # Player progress bar (green)
        tk.Label(bars_frame, text="🟢 SCAN PROGRESS:", font=('MS Sans Serif', 12, 'bold'), 
                bg='#002eb3', fg='white').pack(anchor='w')
        self.scan_progress_frame = tk.Frame(bars_frame, relief='sunken', bd=2, bg='#c0c0c0', height=30, width=400)
        self.scan_progress_frame.pack(pady=5)
        self.scan_progress_frame.pack_propagate(False)
        
        self.scan_fill = tk.Frame(self.scan_progress_frame, bg='#00cc00', height=26)
        
        # Error progress bar (red) 
        tk.Label(bars_frame, text="🔴 ERROR SPREAD:", font=('MS Sans Serif', 12, 'bold'), 
                bg='#002eb3', fg='white').pack(anchor='w', pady=(20,0))
        self.error_progress_frame = tk.Frame(bars_frame, relief='sunken', bd=2, bg='#c0c0c0', height=30, width=400)
        self.error_progress_frame.pack(pady=5)
        self.error_progress_frame.pack_propagate(False)
        
        self.error_fill = tk.Frame(self.error_progress_frame, bg='#cc0000', height=26)
        
        # Click button
        self.click_btn = tk.Button(
            self.blue_screen,
            text="🖱️ CLICK TO SCAN!",
            font=('MS Sans Serif', 16, 'bold'),
            bg='#00cc00',
            fg='white',
            width=20,
            height=2,
            command=self.scan_click
        )
        self.click_btn.pack(pady=50)
        
        # Initialize scan progress values
        self.scan_progress = 0
        self.error_progress = 0
        self.scan_active = True
        
        # Start error progress timer
        self.update_error_progress()
    
    def scan_click(self):
        """Handle scan progress clicks"""
        if not self.scan_active:
            return
            
        self.scan_progress += 8  # Each click = 8% progress
        if self.scan_progress > 100:
            self.scan_progress = 100
            
        # Update visual
        scan_width = int((self.scan_progress / 100) * 396)  # 396 = 400 - 4px padding
        self.scan_fill.place(x=0, y=0, width=scan_width, height=26)
        
        # Check win condition
        if self.scan_progress >= 100:
            self.scan_success()
    
    def update_error_progress(self):
        """Update the error progress (automatic)"""
        if not self.scan_active:
            return
            
        self.error_progress += 1  # Error spreads 1% every update
        if self.error_progress > 100:
            self.error_progress = 100
            
        # Update visual
        error_width = int((self.error_progress / 100) * 396)
        self.error_fill.place(x=0, y=0, width=error_width, height=26)
        
        # Check lose condition
        if self.error_progress >= 100:
            self.scan_failure()
        else:
            # Continue updating error progress
            self.blue_screen.after(100, self.update_error_progress)  # Update every 100ms
    
    def scan_success(self):
        """Player successfully completed scan progress"""
        self.scan_active = False
        
        # Show success message
        success_label = tk.Label(
            self.blue_screen,
            text="✅ SCAN COMPLETE - SYSTEM RECOVERED!\n\nReturning to normal operation...",
            font=('MS Sans Serif', 14, 'bold'),
            bg='#002eb3',
            fg='#00ff00',
            justify='center'
        )
        success_label.pack(pady=20)
        
        # Return to game after 2 seconds
        self.blue_screen.after(2000, self.return_to_game)
    
    def scan_failure(self):
        """Player failed scan progress - game over"""
        self.scan_active = False
        
        # Show failure message
        failure_label = tk.Label(
            self.blue_screen,
            text="❌ SCAN FAILED - SYSTEM CORRUPTED!\n\nError has spread too far to recover.",
            font=('MS Sans Serif', 14, 'bold'),
            bg='#002eb3',
            fg='#ff0000',
            justify='center'
        )
        failure_label.pack(pady=20)
        
        # Quit after 3 seconds
        self.blue_screen.after(3000, self.quit_from_blue_screen)
    
    def return_to_game(self):
        """Return to the main game after successful scan"""
        # Clean up blue screen
        self.blue_screen.destroy()
        self.in_blue_screen = False
        
        # Reset game state - CRITICAL for unfreezing!
        self.red_segment_hit = False
        self.game_frozen = False
        
        # Remove any red segments still on screen
        red_segments = [seg for seg in self.segments if seg.segment_type == 'red']
        for seg in red_segments:
            self.remove_segment(seg)
        
        # Reset percentage text
        self.percent_label.config(text=f"{self.progress_value}%", fg="white")
        
        # Show main window again
        self.root.deiconify()
        
        # Force game loop to continue
        self.root.focus_set()
        
        # CRITICAL: Restart the game loop since it stops during blue screen
        self.game_loop()
        
        print("🎮 System recovered! Game continues... (UNFROZEN)")
        print(f"Debug: game_frozen={self.game_frozen}, in_blue_screen={self.in_blue_screen}")
    
    def quit_from_blue_screen(self):
        """Quit game from blue screen"""
        self.exit_program()
    
    def end_game(self):
        """End the game and show results screen"""
        self.game_ended = True
        self.game_running = False
        
        # Stop all falling segments
        for segment in self.segments:
            if segment.widget:
                segment.widget.destroy()
        self.segments.clear()
        
        # Hide the fullscreen window
        self.screen_window.withdraw()
        
        # Show end screen
        self.show_end_screen()
    
    def show_end_screen(self):
        """Display the end screen with results"""
        # Create end screen window (increased height to fit all content)
        self.end_window = tk.Toplevel(self.root)
        self.end_window.title("Progressbar 95 - Complete!")
        self.end_window.geometry("500x700+200+100")  # Increased height from 600 to 700
        self.end_window.configure(bg='#c0c0c0')
        self.end_window.attributes('-topmost', True)
        self.end_window.resizable(True, True)  # Allow resizing
        
        # Title
        title_label = tk.Label(
            self.end_window,
            text="Progress Complete!",
            font=('MS Sans Serif', 16, 'bold'),
            bg='#c0c0c0',
            fg='black'
        )
        title_label.pack(pady=20)
        
        # Progress bar replica
        self.create_end_screen_progress_bar()
        
        # Stats
        self.create_end_screen_stats()
        
        # Pie chart
        self.create_pie_chart()
        
        # Points display
        points_label = tk.Label(
            self.end_window,
            text=f"Total Points: {self.total_points}",
            font=('MS Sans Serif', 14, 'bold'),
            bg='#c0c0c0',
            fg='blue'
        )
        points_label.pack(pady=10)
        
        # Debug indicator
        if self.DEBUG_MODE:
            debug_label = tk.Label(
                self.end_window,
                text="⚠️ DEBUGGING MODE ON",
                font=('MS Sans Serif', 12, 'bold'),
                bg='#c0c0c0',
                fg='red'
            )
            debug_label.pack(pady=5)
        
        # Close button
        close_btn = tk.Button(
            self.end_window,
            text="Close Game",
            font=('MS Sans Serif', 12),
            command=self.exit_program,
            relief='raised',
            bd=2
        )
        close_btn.pack(pady=20)
    
    def create_end_screen_progress_bar(self):
        """Create a replica of the progress bar showing final segments"""
        bar_frame = tk.Frame(
            self.end_window,
            relief='sunken',
            bd=2,
            bg='#c0c0c0'
        )
        bar_frame.pack(pady=20, padx=50, fill='x')
        
        self.end_progress_frame = tk.Frame(
            bar_frame,
            relief='sunken',
            bd=1,
            bg='#9e9e9e',
            height=32
        )
        self.end_progress_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.end_progress_frame.pack_propagate(False)
        
        # Store the frame reference for dynamic width calculation
        self.end_progress_frame.update_idletasks()  # Force geometry update
        
        # Use after() to ensure frame is properly sized before placing segments
        self.end_window.after(10, self.place_end_screen_segments)
        
        # Add percentage text
        percent_label = tk.Label(
            self.end_progress_frame,
            text="100%",
            font=('MS Sans Serif', 10, 'bold'),
            fg='white',
            bd=0,
            highlightthickness=0,
            bg='#9e9e9e'
        )
        percent_label.place(relx=0.5, rely=0.5, anchor='center')
    
    def place_end_screen_segments(self):
        """Place progress segments with dynamic width calculation"""
        # Get actual frame width after it's been rendered
        self.end_progress_frame.update_idletasks()
        actual_width = self.end_progress_frame.winfo_width()
        
        # Fallback to minimum width if not yet sized
        if actual_width <= 1:
            actual_width = 400
        
        # Recreate segments with dynamic width
        current_x = 0
        
        for segment in self.progress_segments:
            segment_width = int((segment['value'] / 100) * actual_width)
            if segment_width > 0:
                fill = tk.Frame(
                    self.end_progress_frame,
                    bg=segment['color'],
                    height=32,
                    bd=0,
                    relief='flat'
                )
                fill.place(x=current_x, y=0, width=segment_width, height=32)
                current_x += segment_width
    
    def create_end_screen_stats(self):
        """Create statistics display"""
        stats_frame = tk.Frame(self.end_window, bg='#c0c0c0')
        stats_frame.pack(pady=10)
        
        # Calculate percentages (excluding black segments)
        total_colored = self.blue_segments_caught + self.yellow_segments_caught
        if total_colored > 0:
            blue_percent = round((self.blue_segments_caught / total_colored) * 100)
            yellow_percent = round((self.yellow_segments_caught / total_colored) * 100)
        else:
            blue_percent = yellow_percent = 0
        
        correct_label = tk.Label(
            stats_frame,
            text=f"Correct: {blue_percent}%",
            font=('MS Sans Serif', 12, 'bold'),
            bg='#c0c0c0',
            fg='#0066cc'
        )
        correct_label.pack(pady=5)
        
        corrupt_label = tk.Label(
            stats_frame,
            text=f"Corrupt: {yellow_percent}%",
            font=('MS Sans Serif', 12, 'bold'),
            bg='#c0c0c0',
            fg='#cccc00'
        )
        corrupt_label.pack(pady=5)
        
        # Segment counts
        counts_label = tk.Label(
            stats_frame,
            text=f"Blue: {self.blue_segments_caught} | Yellow: {self.yellow_segments_caught}",
            font=('MS Sans Serif', 10),
            bg='#c0c0c0',
            fg='black'
        )
        counts_label.pack(pady=5)
    
    def create_pie_chart(self):
        """Create a simple pie chart showing segment distribution"""
        chart_frame = tk.Frame(self.end_window, bg='#c0c0c0')
        chart_frame.pack(pady=20)
        
        canvas = tk.Canvas(chart_frame, width=200, height=200, bg='white')
        canvas.pack()
        
        # Calculate angles for pie chart
        total_colored = self.blue_segments_caught + self.yellow_segments_caught
        if total_colored == 0:
            # No segments, show empty circle
            canvas.create_oval(10, 10, 190, 190, outline='gray', fill='lightgray', width=2)
            canvas.create_text(100, 100, text="No segments", font=('Arial', 10))
            return
        
        blue_angle = (self.blue_segments_caught / total_colored) * 360
        yellow_angle = (self.yellow_segments_caught / total_colored) * 360
        
        # Handle special cases for better rendering
        if self.blue_segments_caught > 0 and self.yellow_segments_caught == 0:
            # All blue - draw full blue circle
            canvas.create_oval(10, 10, 190, 190, fill='#0066cc', outline='black', width=2)
        elif self.yellow_segments_caught > 0 and self.blue_segments_caught == 0:
            # All yellow - draw full yellow circle
            canvas.create_oval(10, 10, 190, 190, fill='#cccc00', outline='black', width=2)
        else:
            # Mixed colors - draw pie slices
            current_angle = 0
            
            # Blue slice
            if blue_angle > 0:
                canvas.create_arc(10, 10, 190, 190, 
                                start=current_angle, extent=blue_angle,
                                fill='#0066cc', outline='black', width=2)
                current_angle += blue_angle
            
            # Yellow slice
            if yellow_angle > 0:
                canvas.create_arc(10, 10, 190, 190, 
                                start=current_angle, extent=yellow_angle,
                                fill='#cccc00', outline='black', width=2)
    
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