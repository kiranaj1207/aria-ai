import tkinter as tk
from tkinter import ttk, scrolledtext, font as tkfont
import threading
import queue
import datetime
import requests
import json
import speech_recognition as sr
import pyttsx3
import re
import time
import random
import math

class PremiumVoiceAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("ARIA • Premium Voice Assistant")
        self.root.geometry("1400x850")
        
        # Luxurious color palette - Deep purple & gold theme
        self.colors = {
            'bg_primary': '#0D0221',      # Deep space purple
            'bg_secondary': '#1A0B2E',     # Rich violet
            'bg_card': '#2D1B4E',          # Amethyst
            'accent_primary': '#F72585',   # Vibrant pink
            'accent_gold': '#FFD60A',      # Pure gold
            'accent_cyan': '#06FFA5',      # Neon cyan
            'text_primary': '#FFFFFF',     # Pure white
            'text_secondary': '#B8A9C9',   # Lavender gray
            'glass_bg': '#251549',         # Dark glass
            'glass_border': '#3D2B5F',     # Purple border
            'success': '#06FFA5',          # Bright green
            'listening': '#F72585',        # Bright pink
            'gradient_1': '#7209B7',       # Purple
            'gradient_2': '#F72585',       # Pink
        }
        
        self.root.configure(bg=self.colors['bg_primary'])
        
        # API Keys
        self.weather_api_key = "e49769670c7f79929a39b0ae4222e114"
        self.news_api_key = "943a03257fdf4ff68cd90c151978c3bb"
        
        # Speech setup
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_lock = threading.Lock()
        self.gui_queue = queue.Queue()
        
        # State
        self.listening = False
        self.current_city = "Bangalore"
        self.speech_enabled = True
        self.live_transcript = ""
        
        # Animation
        self.pulse_angle = 0
        self.pulse_active = False
        
        # Custom fonts
        self.setup_fonts()
        self.setup_ui()
        self.check_queue()
        self.animate_pulse()
        
    def setup_fonts(self):
        """Setup custom fonts for premium look"""
        self.font_title = tkfont.Font(family="Helvetica Neue", size=42, weight="bold")
        self.font_subtitle = tkfont.Font(family="Helvetica Neue", size=13, weight="normal")
        self.font_heading = tkfont.Font(family="Helvetica Neue", size=20, weight="bold")
        self.font_body = tkfont.Font(family="Helvetica Neue", size=12, weight="normal")
        self.font_small = tkfont.Font(family="Helvetica Neue", size=10, weight="bold")
        self.font_transcript = tkfont.Font(family="Courier New", size=13, weight="normal")
        
    def create_glass_card(self, parent, **kwargs):
        """Create glassmorphism effect card"""
        card = tk.Frame(parent, 
                       bg=self.colors['glass_bg'],
                       highlightbackground=self.colors['glass_border'],
                       highlightthickness=1,
                       **kwargs)
        return card
    
    def animate_pulse(self):
        """Animate the listening pulse effect"""
        if self.pulse_active:
            self.pulse_angle = (self.pulse_angle + 15) % 360
            # Create pulsing effect
            intensity = abs(math.sin(math.radians(self.pulse_angle)))
            
            # Update pulse canvas if it exists
            if hasattr(self, 'pulse_canvas'):
                self.pulse_canvas.delete("pulse")
                radius = 60 + (intensity * 15)
                opacity_val = int(100 + (intensity * 155))
                color = self.colors['listening']
                
                # Draw pulsing circle
                x1, y1 = 100 - radius, 100 - radius
                x2, y2 = 100 + radius, 100 + radius
                self.pulse_canvas.create_oval(x1, y1, x2, y2, 
                                              fill="", 
                                              outline=color,
                                              width=3,
                                              tags="pulse")
                
                # Inner circle
                inner_radius = 45
                ix1, iy1 = 100 - inner_radius, 100 - inner_radius
                ix2, iy2 = 100 + inner_radius, 100 + inner_radius
                self.pulse_canvas.create_oval(ix1, iy1, ix2, iy2,
                                              fill=color,
                                              outline="",
                                              tags="pulse")
        
        self.root.after(50, self.animate_pulse)
        
    def setup_ui(self):
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # ============= HEADER SECTION =============
        header_frame = tk.Frame(main_container, bg=self.colors['bg_secondary'], height=160)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Gradient effect bar at top
        gradient_bar = tk.Frame(header_frame, bg=self.colors['accent_primary'], height=3)
        gradient_bar.pack(fill=tk.X)
        
        # Logo and Title Container
        title_container = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        title_container.pack(pady=(25, 12))
        
        # Premium animated logo
        logo_canvas = tk.Canvas(title_container, width=50, height=50, 
                               bg=self.colors['bg_secondary'], 
                               highlightthickness=0)
        logo_canvas.pack(side=tk.LEFT, padx=(0, 20))
        
        # Draw diamond logo with gradient effect
        logo_canvas.create_polygon(25, 5, 45, 25, 25, 45, 5, 25,
                                   fill=self.colors['accent_primary'],
                                   outline=self.colors['accent_gold'],
                                   width=2)
        logo_canvas.create_polygon(25, 15, 35, 25, 25, 35, 15, 25,
                                   fill=self.colors['accent_gold'],
                                   outline="")
        
        # Title and subtitle
        title_text_frame = tk.Frame(title_container, bg=self.colors['bg_secondary'])
        title_text_frame.pack(side=tk.LEFT)
        
        title_label = tk.Label(title_text_frame, 
                              text="ARIA", 
                              font=self.font_title,
                              fg=self.colors['text_primary'],
                              bg=self.colors['bg_secondary'])
        title_label.pack(anchor='w')
        
        subtitle_label = tk.Label(title_text_frame, 
                                 text="AI-Powered Premium Assistant", 
                                 font=self.font_subtitle,
                                 fg=self.colors['text_secondary'],
                                 bg=self.colors['bg_secondary'])
        subtitle_label.pack(anchor='w')
        
        # ============= LIVE TRANSCRIPT BAR =============
        transcript_frame = tk.Frame(header_frame, bg=self.colors['bg_card'], height=50)
        transcript_frame.pack(fill=tk.X, padx=35, pady=(8, 20))
        transcript_frame.pack_propagate(False)
        
        # Animated indicator dot
        indicator_canvas = tk.Canvas(transcript_frame, width=12, height=12,
                                    bg=self.colors['bg_card'],
                                    highlightthickness=0)
        indicator_canvas.pack(side=tk.LEFT, padx=(20, 8), pady=19)
        indicator_canvas.create_oval(2, 2, 10, 10, 
                                     fill=self.colors['accent_cyan'],
                                     outline="")
        
        tk.Label(transcript_frame, 
                text="YOU:", 
                font=self.font_small,
                fg=self.colors['accent_primary'],
                bg=self.colors['bg_card']).pack(side=tk.LEFT, padx=(0, 12), pady=15)
        
        # Live transcript display
        self.transcript_label = tk.Label(transcript_frame,
                                        text="Ready for your command...",
                                        font=self.font_transcript,
                                        fg=self.colors['text_primary'],
                                        bg=self.colors['bg_card'],
                                        anchor='w')
        self.transcript_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=15, padx=(0, 20))
        
        # ============= CONTENT AREA =============
        content_frame = tk.Frame(main_container, bg=self.colors['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=35, pady=25)
        
        # Left panel - Controls (wider)
        left_panel = tk.Frame(content_frame, bg=self.colors['bg_primary'], width=480)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left_panel.pack_propagate(False)
        
        # Main Control Card with animation
        control_card = self.create_glass_card(left_panel)
        control_card.pack(fill=tk.BOTH, expand=False, pady=(0, 20))
        
        # Status indicator with animation
        status_container = tk.Frame(control_card, bg=self.colors['glass_bg'])
        status_container.pack(fill=tk.X, pady=25, padx=30)
        
        status_header = tk.Frame(status_container, bg=self.colors['glass_bg'])
        status_header.pack(fill=tk.X)
        
        tk.Label(status_header,
                text="SYSTEM STATUS",
                font=self.font_small,
                fg=self.colors['text_secondary'],
                bg=self.colors['glass_bg']).pack(side=tk.LEFT)
        
        # Animated status dot
        status_dot_canvas = tk.Canvas(status_header, width=10, height=10,
                                      bg=self.colors['glass_bg'],
                                      highlightthickness=0)
        status_dot_canvas.pack(side=tk.LEFT, padx=(8, 0))
        self.status_dot = status_dot_canvas.create_oval(2, 2, 8, 8,
                                                        fill=self.colors['success'],
                                                        outline="")
        self.status_dot_canvas = status_dot_canvas
        
        # Animated gradient bar
        self.status_indicator = tk.Frame(status_container, bg=self.colors['success'], height=3)
        self.status_indicator.pack(fill=tk.X, pady=(8, 12))
        
        self.status_label = tk.Label(status_container,
                                     text="Ready",
                                     font=self.font_body,
                                     fg=self.colors['text_primary'],
                                     bg=self.colors['glass_bg'])
        self.status_label.pack(anchor='w')
        
        # Pulse animation canvas for listening
        pulse_container = tk.Frame(control_card, bg=self.colors['glass_bg'])
        pulse_container.pack(pady=(10, 20))
        
        self.pulse_canvas = tk.Canvas(pulse_container, width=200, height=200,
                                      bg=self.colors['glass_bg'],
                                      highlightthickness=0)
        self.pulse_canvas.pack()
        
        # Main Microphone Button (on top of pulse)
        self.mic_btn = tk.Button(pulse_container,
                                text="START\nLISTENING",
                                command=self.toggle_listening,
                                font=("Helvetica Neue", 13, "bold"),
                                fg=self.colors['bg_primary'],
                                bg=self.colors['accent_gold'],
                                activebackground=self.colors['listening'],
                                activeforeground=self.colors['text_primary'],
                                relief=tk.FLAT,
                                width=12,
                                height=3,
                                cursor='hand2',
                                borderwidth=0)
        self.mic_btn.place(x=100, y=100, anchor='center')
        
        # Quick Actions
        actions_frame = tk.Frame(control_card, bg=self.colors['glass_bg'])
        actions_frame.pack(fill=tk.X, pady=(15, 25), padx=30)
        
        tk.Label(actions_frame,
                text="QUICK ACTIONS",
                font=self.font_small,
                fg=self.colors['text_secondary'],
                bg=self.colors['glass_bg']).pack(anchor='w', pady=(0, 12))
        
        # Action buttons with gradients
        btn_style = {
            'font': ("Helvetica Neue", 11, "bold"),
            'fg': self.colors['text_primary'],
            'bg': self.colors['bg_card'],
            'activebackground': self.colors['bg_secondary'],
            'activeforeground': self.colors['accent_primary'],
            'relief': tk.FLAT,
            'cursor': 'hand2',
            'borderwidth': 0,
            'pady': 14
        }
        
        weather_btn = tk.Button(actions_frame,
                               text="☀  Weather Update",
                               command=self.get_weather_command,
                               **btn_style)
        weather_btn.pack(fill=tk.X, pady=(0, 10))
        
        news_btn = tk.Button(actions_frame,
                            text="📰  Latest News",
                            command=self.get_news_command,
                            **btn_style)
        news_btn.pack(fill=tk.X, pady=(0, 10))
        
        self.speech_btn = tk.Button(actions_frame,
                                   text="🔊  Speech: ON",
                                   command=self.toggle_speech,
                                   **btn_style)
        self.speech_btn.pack(fill=tk.X)
        
        # City Settings Card
        city_card = self.create_glass_card(left_panel)
        city_card.pack(fill=tk.X)
        
        city_inner = tk.Frame(city_card, bg=self.colors['glass_bg'])
        city_inner.pack(fill=tk.X, pady=25, padx=30)
        
        tk.Label(city_inner,
                text="LOCATION SETTINGS",
                font=self.font_small,
                fg=self.colors['text_secondary'],
                bg=self.colors['glass_bg']).pack(anchor='w', pady=(0, 12))
        
        city_input_frame = tk.Frame(city_inner, bg=self.colors['glass_bg'])
        city_input_frame.pack(fill=tk.X)
        
        self.city_entry = tk.Entry(city_input_frame,
                                  font=self.font_body,
                                  fg=self.colors['text_primary'],
                                  bg=self.colors['bg_card'],
                                  insertbackground=self.colors['accent_primary'],
                                  relief=tk.FLAT,
                                  borderwidth=0)
        self.city_entry.insert(0, self.current_city)
        self.city_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, ipadx=15)
        
        city_btn = tk.Button(city_input_frame,
                           text="UPDATE",
                           command=self.update_city,
                           font=("Helvetica Neue", 10, "bold"),
                           fg=self.colors['bg_primary'],
                           bg=self.colors['accent_primary'],
                           activebackground=self.colors['accent_gold'],
                           activeforeground=self.colors['bg_primary'],
                           relief=tk.FLAT,
                           cursor='hand2',
                           borderwidth=0,
                           padx=20)
        city_btn.pack(side=tk.LEFT, padx=(10, 0), ipady=10)
        
        # Right panel - Information Display
        right_panel = tk.Frame(content_frame, bg=self.colors['bg_primary'])
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Custom notebook style
        style = ttk.Style()
        style.theme_use('default')
        
        style.configure('Premium.TNotebook', 
                       background=self.colors['bg_primary'],
                       borderwidth=0)
        style.configure('Premium.TNotebook.Tab',
                       background=self.colors['bg_card'],
                       foreground=self.colors['text_secondary'],
                       padding=[25, 15],
                       borderwidth=0,
                       font=("Helvetica Neue", 11, "bold"))
        style.map('Premium.TNotebook.Tab',
                 background=[('selected', self.colors['glass_bg'])],
                 foreground=[('selected', self.colors['accent_primary'])])
        
        self.notebook = ttk.Notebook(right_panel, style='Premium.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_conversation_tab()
        self.create_weather_tab()
        self.create_news_tab()
        self.create_reminders_tab()
        
        # Initialize
        welcome_msg = "Welcome! I'm ARIA, your premium AI voice assistant. I'm ready to help you with weather updates, latest news, reminders, and much more. How may I assist you today?"
        self.add_to_conversation(f"ARIA: {welcome_msg}", "assistant")
        self.speak(welcome_msg)
        self.get_weather(speak=False)
        self.get_news(speak=False)
        self.load_reminders()
    
    def create_conversation_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['glass_bg'])
        self.notebook.add(tab, text='  CONVERSATION  ')
        
        self.conversation_text = tk.Text(tab,
                                        font=self.font_body,
                                        bg=self.colors['glass_bg'],
                                        fg=self.colors['text_primary'],
                                        wrap=tk.WORD,
                                        relief=tk.FLAT,
                                        borderwidth=0,
                                        padx=30,
                                        pady=25,
                                        insertbackground=self.colors['accent_primary'],
                                        selectbackground=self.colors['accent_primary'],
                                        selectforeground=self.colors['bg_primary'],
                                        spacing3=8)
        self.conversation_text.pack(fill=tk.BOTH, expand=True)
        
        self.conversation_text.tag_configure("user", 
                                            foreground=self.colors['accent_gold'],
                                            font=("Helvetica Neue", 13, "bold"))
        self.conversation_text.tag_configure("assistant",
                                            foreground=self.colors['text_primary'],
                                            font=("Helvetica Neue", 12, "normal"))
        self.conversation_text.tag_configure("system",
                                            foreground=self.colors['text_secondary'],
                                            font=("Helvetica Neue", 11, "italic"))
    
    def create_weather_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['glass_bg'])
        self.notebook.add(tab, text='  WEATHER  ')
        
        self.weather_text = tk.Text(tab,
                                   font=("Helvetica Neue", 13),
                                   bg=self.colors['glass_bg'],
                                   fg=self.colors['text_primary'],
                                   wrap=tk.WORD,
                                   relief=tk.FLAT,
                                   borderwidth=0,
                                   padx=30,
                                   pady=25,
                                   spacing3=5)
        self.weather_text.pack(fill=tk.BOTH, expand=True)
    
    def create_news_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['glass_bg'])
        self.notebook.add(tab, text='  NEWS  ')
        
        self.news_text = tk.Text(tab,
                                font=self.font_body,
                                bg=self.colors['glass_bg'],
                                fg=self.colors['text_primary'],
                                wrap=tk.WORD,
                                relief=tk.FLAT,
                                borderwidth=0,
                                padx=30,
                                pady=25,
                                spacing3=5)
        self.news_text.pack(fill=tk.BOTH, expand=True)
    
    def create_reminders_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['glass_bg'])
        self.notebook.add(tab, text='  REMINDERS  ')
        
        self.reminders_text = tk.Text(tab,
                                     font=self.font_body,
                                     bg=self.colors['glass_bg'],
                                     fg=self.colors['text_primary'],
                                     wrap=tk.WORD,
                                     relief=tk.FLAT,
                                     borderwidth=0,
                                     padx=30,
                                     pady=25,
                                     spacing3=5)
        self.reminders_text.pack(fill=tk.BOTH, expand=True)
    
    def update_live_transcript(self, text):
        """Update the live transcript bar with animation"""
        self.transcript_label.config(text=text if text else "Ready for your command...")
    
    def toggle_speech(self):
        self.speech_enabled = not self.speech_enabled
        if self.speech_enabled:
            self.speech_btn.config(text="🔊  Speech: ON")
            msg = "Voice output has been enabled"
            self.speak(msg)
        else:
            self.speech_btn.config(text="🔇  Speech: OFF")
            msg = "Voice output has been disabled"
        self.add_to_conversation(f"System: {msg}", "system")
    
    def get_weather_command(self):
        self.add_to_conversation("You: [Weather Request]", "user")
        self.update_live_transcript("[Weather Information Request]")
        response = f"Retrieving comprehensive weather data for {self.current_city}"
        self.add_to_conversation(f"ARIA: {response}", "assistant")
        self.speak(response)
        self.get_weather(speak=True)
    
    def get_news_command(self):
        self.add_to_conversation("You: [News Request]", "user")
        self.update_live_transcript("[Latest News Request]")
        response = "Fetching the latest news headlines from around the world"
        self.add_to_conversation(f"ARIA: {response}", "assistant")
        self.speak(response)
        self.get_news(speak=True)
    
    def update_city(self):
        city = self.city_entry.get()
        if city:
            self.current_city = city
            response = f"Location has been updated to {city}. Fetching weather information now."
            self.add_to_conversation(f"ARIA: {response}", "assistant")
            self.speak(response)
            self.get_weather(speak=True)
    
    def toggle_listening(self):
        if not self.listening:
            self.start_listening()
        else:
            self.stop_listening()
    
    def start_listening(self):
        self.listening = True
        self.pulse_active = True
        self.mic_btn.config(text="LISTENING\nNOW", 
                           bg=self.colors['listening'],
                           fg=self.colors['text_primary'])
        self.status_indicator.config(bg=self.colors['listening'])
        self.status_dot_canvas.itemconfig(self.status_dot, fill=self.colors['listening'])
        self.update_status("Listening for your command...")
        self.update_live_transcript("Listening...")
        
        response = "I'm listening"
        self.add_to_conversation(f"ARIA: {response}", "assistant")
        self.speak(response)
        
        thread = threading.Thread(target=self.listen_once)
        thread.daemon = True
        thread.start()
    
    def stop_listening(self):
        self.listening = False
        self.pulse_active = False
        self.pulse_canvas.delete("pulse")
        self.mic_btn.config(text="START\nLISTENING", 
                           bg=self.colors['accent_gold'],
                           fg=self.colors['bg_primary'])
        self.status_indicator.config(bg=self.colors['success'])
        self.status_dot_canvas.itemconfig(self.status_dot, fill=self.colors['success'])
        self.update_status("Ready")
    
    def listen_once(self):
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                try:
                    self.gui_queue.put(("status", "Processing audio..."))
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    text = self.recognizer.recognize_google(audio)
                    
                    if text:
                        self.gui_queue.put(("user_speech", text))
                        self.process_command(text)
                        
                except sr.WaitTimeoutError:
                    self.gui_queue.put(("error", "No speech detected"))
                    self.stop_listening()
                except sr.UnknownValueError:
                    self.gui_queue.put(("error", "Could not understand audio"))
                    self.stop_listening()
                except sr.RequestError:
                    self.gui_queue.put(("error", "Recognition service error"))
                    self.stop_listening()
                    
        except Exception:
            self.gui_queue.put(("error", "Microphone error"))
            self.stop_listening()
    
    def process_command(self, command):
        command_lower = command.lower()
        self.add_to_conversation(f"You: {command}", "user")
        self.update_live_transcript(command)
        
        # Extract city
        city_match = self.extract_city_from_command(command)
        if city_match:
            self.current_city = city_match
            self.city_entry.delete(0, tk.END)
            self.city_entry.insert(0, self.current_city)
        
        # Process commands
        if any(word in command_lower for word in ["weather", "temperature", "forecast", "climate"]):
            response = f"Analyzing weather conditions for {self.current_city}"
            self.add_to_conversation(f"ARIA: {response}", "assistant")
            self.speak(response)
            self.get_weather(speak=True)
            
        elif any(word in command_lower for word in ["news", "headlines", "updates"]):
            response = "Retrieving the latest news updates"
            self.add_to_conversation(f"ARIA: {response}", "assistant")
            self.speak(response)
            self.get_news(speak=True)
            
        elif any(word in command_lower for word in ["reminder", "remind"]):
            if "set" in command_lower:
                self.set_reminder(command)
            else:
                self.show_reminders()
                
        elif any(word in command_lower for word in ["hello", "hi", "hey", "greetings"]):
            response = "Hello! I'm here to assist you. What would you like to know?"
            self.add_to_conversation(f"ARIA: {response}", "assistant")
            self.speak(response)
            
        elif "time" in command_lower:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            response = f"The current time is {current_time}"
            self.add_to_conversation(f"ARIA: {response}", "assistant")
            self.speak(response)
            
        elif "date" in command_lower:
            current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            response = f"Today is {current_date}"
            self.add_to_conversation(f"ARIA: {response}", "assistant")
            self.speak(response)
            
        elif any(word in command_lower for word in ["thank", "thanks"]):
            responses = ["You're most welcome", "My pleasure to assist", "Happy to help you"]
            response = random.choice(responses)
            self.add_to_conversation(f"ARIA: {response}", "assistant")
            self.speak(response)
            
        elif any(word in command_lower for word in ["stop", "exit", "quit", "goodbye"]):
            response = "Goodbye! Have a wonderful day"
            self.add_to_conversation(f"ARIA: {response}", "assistant")
            self.speak(response)
            self.stop_listening()
            
        else:
            response = f"I understood: '{command}'. You can ask me about weather conditions, latest news, current time, date, or to set reminders."
            self.add_to_conversation(f"ARIA: {response}", "assistant")
            self.speak(response)
    
    def extract_city_from_command(self, command):
        words = command.lower().split()
        for i, word in enumerate(words):
            if word in ['in', 'for', 'at', 'of'] and i + 1 < len(words):
                next_word = words[i + 1]
                city_words = [next_word]
                for j in range(i + 2, len(words)):
                    if words[j] not in ['weather', 'temperature', 'forecast', 'climate']:
                        city_words.append(words[j])
                    else:
                        break
                return ' '.join(city_words).title()
        return None
    
    def set_reminder(self, command):
        try:
            reminder_text = command.lower().replace("set reminder", "").replace("remind me", "").replace("to", "").strip()
            
            if reminder_text:
                reminder_text = reminder_text.capitalize()
                reminders = self.load_reminders_from_file()
                reminders.append({
                    "time": datetime.datetime.now().strftime("%I:%M %p"),
                    "text": reminder_text,
                    "date": datetime.datetime.now().strftime("%Y-%m-%d")
                })
                self.save_reminders_to_file(reminders)
                
                response = f"Reminder has been set: {reminder_text}"
                self.add_to_conversation(f"ARIA: {response}", "assistant")
                self.speak(response)
                self.load_reminders()
            else:
                response = "Please specify what you'd like me to remind you about"
                self.add_to_conversation(f"ARIA: {response}", "assistant")
                self.speak(response)
        except:
            response = "I couldn't set that reminder. Please try again"
            self.add_to_conversation(f"ARIA: {response}", "assistant")
            self.speak(response)
    
    def show_reminders(self):
        reminders = self.load_reminders_from_file()
        if reminders:
            response = f"You have {len(reminders)} active reminder{'s' if len(reminders) > 1 else ''}"
        else:
            response = "You have no reminders set at the moment"
        self.add_to_conversation(f"ARIA: {response}", "assistant")
        self.speak(response)
        self.load_reminders()
    
    def get_weather(self, speak=False):
        try:
            self.update_status(f"Fetching weather data...")
            
            url = f"http://api.openweathermap.org/data/2.5/weather?q={self.current_city}&appid={self.weather_api_key}&units=metric"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get("cod") != 200:
                error_msg = f"Unable to retrieve weather data for {self.current_city}"
                self.weather_text.delete(1.0, tk.END)
                self.weather_text.insert(tk.END, error_msg)
                if speak:
                    self.add_to_conversation(f"ARIA: {error_msg}", "assistant")
                    self.speak(error_msg)
                return
            
            # Extract comprehensive weather data
            temp = round(data["main"]["temp"], 1)
            temp_min = round(data["main"]["temp_min"], 1)
            temp_max = round(data["main"]["temp_max"], 1)
            humidity = data["main"]["humidity"]
            pressure = data["main"]["pressure"]
            description = data["weather"][0]["description"]
            feels_like = round(data["main"]["feels_like"], 1)
            wind_speed = round(data["wind"]["speed"], 1)
            wind_deg = data["wind"].get("degree", 0)
            clouds = data["clouds"]["all"]
            visibility = data.get("visibility", 0) / 1000  # Convert to km
            
            # Get sunrise and sunset times
            sunrise = datetime.datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%I:%M %p")
            sunset = datetime.datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%I:%M %p")
            
            # Create comprehensive display
            weather_info = f"╔═══════════════════════════════════════════╗\n"
            weather_info += f"  COMPREHENSIVE WEATHER REPORT\n"
            weather_info += f"  {self.current_city.upper()}\n"
            weather_info += f"╚═══════════════════════════════════════════╝\n\n"
            
            weather_info += f"🌡️  TEMPERATURE\n"
            weather_info += f"   Current: {temp}°C\n"
            weather_info += f"   Feels Like: {feels_like}°C\n"
            weather_info += f"   Min/Max: {temp_min}°C / {temp_max}°C\n\n"
            
            weather_info += f"☁️  CONDITIONS\n"
            weather_info += f"   Status: {description.title()}\n"
            weather_info += f"   Cloud Coverage: {clouds}%\n"
            weather_info += f"   Visibility: {visibility:.1f} km\n\n"
            
            weather_info += f"💨  WIND & PRESSURE\n"
            weather_info += f"   Wind Speed: {wind_speed} m/s\n"
            weather_info += f"   Atmospheric Pressure: {pressure} hPa\n"
            weather_info += f"   Humidity: {humidity}%\n\n"
            
            weather_info += f"🌅  SUN SCHEDULE\n"
            weather_info += f"   Sunrise: {sunrise}\n"
            weather_info += f"   Sunset: {sunset}\n\n"
            
            weather_info += f"─────────────────────────────────────────\n"
            weather_info += f"Last Updated: {datetime.datetime.now().strftime('%I:%M %p, %B %d')}"
            
            self.weather_text.delete(1.0, tk.END)
            self.weather_text.insert(tk.END, weather_info)
            
            if speak:
                # Comprehensive spoken response
                weather_response = f"Here's the complete weather report for {self.current_city}. "
                weather_response += f"The current temperature is {temp} degrees celsius, with {description}. "
                weather_response += f"It feels like {feels_like} degrees. "
                weather_response += f"Today's temperature will range from {temp_min} to {temp_max} degrees. "
                weather_response += f"Wind speed is {wind_speed} meters per second, "
                weather_response += f"humidity is at {humidity} percent, "
                weather_response += f"and the cloud coverage is {clouds} percent. "
                weather_response += f"Visibility is {visibility:.1f} kilometers. "
                weather_response += f"The sun rose at {sunrise} and will set at {sunset}."
                
                self.add_to_conversation(f"ARIA: {weather_response}", "assistant")
                self.speak(weather_response)
            
            self.update_status("Ready")
            
        except Exception as e:
            error_msg = "Weather service is currently unavailable"
            self.weather_text.delete(1.0, tk.END)
            self.weather_text.insert(tk.END, error_msg)
            if speak:
                self.add_to_conversation(f"ARIA: {error_msg}", "assistant")
                self.speak(error_msg)
            self.update_status("Ready")
    
    def get_news(self, speak=False):
        try:
            self.update_status("Fetching latest news...")
            
            url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={self.news_api_key}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get("status") != "ok":
                error_msg = "News service is currently unavailable"
                self.news_text.delete(1.0, tk.END)
                self.news_text.insert(tk.END, error_msg)
                if speak:
                    self.add_to_conversation(f"ARIA: {error_msg}", "assistant")
                    self.speak(error_msg)
                return
            
            articles = data["articles"][:5]
            
            news_info = f"╔═══════════════════════════════════════════╗\n"
            news_info += f"  LATEST NEWS HEADLINES\n"
            news_info += f"╚═══════════════════════════════════════════╝\n\n"
            
            for i, article in enumerate(articles, 1):
                title = article.get("title", "No title").split(' - ')[0]
                source = article.get("source", {}).get("name", "Unknown")
                description = article.get("description", "")
                
                news_info += f"[{i}] {title}\n"
                news_info += f"    Source: {source}\n"
                if description and len(description) < 150:
                    news_info += f"    {description}\n"
                news_info += f"\n"
            
            news_info += f"─────────────────────────────────────────\n"
            news_info += f"Last Updated: {datetime.datetime.now().strftime('%I:%M %p, %B %d')}"
            
            self.news_text.delete(1.0, tk.END)
            self.news_text.insert(tk.END, news_info)
            
            if speak and articles:
                news_response = f"Here are the top {min(3, len(articles))} news headlines. "
                for i, article in enumerate(articles[:3], 1):
                    title = article.get("title", "").split(' - ')[0]
                    title = re.sub(r'[^\w\s,.-]', '', title)
                    if len(title) > 80:
                        title = title[:77] + "..."
                    news_response += f"Number {i}: {title}. "
                
                self.add_to_conversation(f"ARIA: {news_response}", "assistant")
                self.speak(news_response)
            
            self.update_status("Ready")
            
        except Exception:
            error_msg = "News service is currently unavailable"
            self.news_text.delete(1.0, tk.END)
            self.news_text.insert(tk.END, error_msg)
            if speak:
                self.add_to_conversation(f"ARIA: {error_msg}", "assistant")
                self.speak(error_msg)
            self.update_status("Ready")
    
    def load_reminders(self):
        reminders = self.load_reminders_from_file()
        
        reminders_text = f"╔═══════════════════════════════════════════╗\n"
        reminders_text += f"  YOUR ACTIVE REMINDERS\n"
        reminders_text += f"╚═══════════════════════════════════════════╝\n\n"
        
        if reminders:
            for i, reminder in enumerate(reminders, 1):
                reminders_text += f"[{i}] {reminder['text']}\n"
                reminders_text += f"    Set at: {reminder['time']} on {reminder['date']}\n\n"
        else:
            reminders_text += "No reminders currently set\n\n"
        
        reminders_text += f"─────────────────────────────────────────\n"
        reminders_text += f"Last Updated: {datetime.datetime.now().strftime('%I:%M %p')}"
        
        self.reminders_text.delete(1.0, tk.END)
        self.reminders_text.insert(tk.END, reminders_text)
    
    def load_reminders_from_file(self):
        try:
            with open("reminders.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_reminders_to_file(self, reminders):
        with open("reminders.json", "w") as f:
            json.dump(reminders, f, indent=2)
    
    def speak(self, text):
        if not self.speech_enabled:
            print(f"[Speech disabled] {text}")
            return
            
        def speak_thread():
            try:
                with self.tts_lock:
                    engine = pyttsx3.init()
                    engine.setProperty('rate', 165)
                    engine.setProperty('volume', 1.0)
                    voices = engine.getProperty('voices')
                    if voices:
                        engine.setProperty('voice', voices[0].id)
                    print(f"[Speaking] {text}")
                    engine.say(text)
                    engine.runAndWait()
                    engine.stop()
                    del engine
            except Exception as e:
                print(f"[TTS Error] {e}")
        
        thread = threading.Thread(target=speak_thread, daemon=True)
        thread.start()
    
    def add_to_conversation(self, text, msg_type="system"):
        if msg_type == "user":
            self.conversation_text.insert(tk.END, text + "\n", "user")
        elif msg_type == "assistant":
            self.conversation_text.insert(tk.END, text + "\n", "assistant")
        else:
            self.conversation_text.insert(tk.END, text + "\n", "system")
        self.conversation_text.insert(tk.END, "\n")
        self.conversation_text.see(tk.END)
    
    def update_status(self, text):
        self.status_label.config(text=text)
    
    def check_queue(self):
        try:
            while True:
                msg_type, data = self.gui_queue.get_nowait()
                
                if msg_type == "user_speech":
                    pass
                elif msg_type == "status":
                    self.update_status(data)
                elif msg_type == "error":
                    self.add_to_conversation(f"System: {data}", "system")
                    self.update_live_transcript(data)
                    
        except queue.Empty:
            pass
        
        self.root.after(100, self.check_queue)


def main():
    root = tk.Tk()
    app = PremiumVoiceAssistant(root)
    root.mainloop()


if __name__ == "__main__":
    main()