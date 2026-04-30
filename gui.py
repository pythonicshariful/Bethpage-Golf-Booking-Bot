import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from datetime import datetime
from main import run_automation

class GolfBookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bethpage Golf Booking Bot")
        self.root.geometry("600x950")
        self.root.configure(bg="#1e1e1e")
        self.otp_event = threading.Event()
        self.otp_value = ""
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configure Styles
        self.style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Helvetica", 10))
        self.style.configure("TButton", background="#3d3d3d", foreground="#ffffff", borderwidth=0, font=("Helvetica", 10, "bold"))
        self.style.map("TButton", background=[("active", "#505050")])
        self.style.configure("TEntry", fieldbackground="#2d2d2d", foreground="#ffffff", borderwidth=0)
        self.style.configure("TCombobox", fieldbackground="#2d2d2d", foreground="#ffffff", arrowcolor="#ffffff")

        # Main Container
        self.main_frame = tk.Frame(root, bg="#1e1e1e", padx=40, pady=40)
        self.main_frame.pack(fill="both", expand=True)

        # Header
        self.header = tk.Label(self.main_frame, text="Golf Booking Bot", bg="#1e1e1e", foreground="#4cc9f0", font=("Helvetica", 20, "bold"))
        self.header.pack(pady=(0, 30))

        # Email
        self.create_label("Email Address")
        self.email_entry = self.create_entry("")

        # Password
        self.create_label("ForeUp Password")
        self.pass_entry = self.create_entry("", show="*")

        # IMAP Credentials Row
        imap_frame = tk.Frame(self.main_frame, bg="#1e1e1e")
        imap_frame.pack(fill="x", pady=(0, 15))

        # IMAP Email
        imap_email_frame = tk.Frame(imap_frame, bg="#1e1e1e")
        imap_email_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Label(imap_email_frame, text="Gmail/IMAP Email", bg="#1e1e1e", foreground="#ffffff", font=("Helvetica", 9)).pack(anchor="w")
        self.imap_email_entry = ttk.Entry(imap_email_frame)
        self.imap_email_entry.insert(0, "")
        self.imap_email_entry.pack(fill="x")

        # App Password
        app_pass_frame = tk.Frame(imap_frame, bg="#1e1e1e")
        app_pass_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))
        tk.Label(app_pass_frame, text="Gmail App Password", bg="#1e1e1e", foreground="#ffffff", font=("Helvetica", 9)).pack(anchor="w")
        self.app_pass_entry = ttk.Entry(app_pass_frame, show="*")
        self.app_pass_entry.insert(0, "")
        self.app_pass_entry.pack(fill="x")

        # Course Selection
        self.create_label("Select Course")
        self.course_var = tk.StringVar()
        self.course_combo = ttk.Combobox(self.main_frame, textvariable=self.course_var, state="readonly")
        self.course_combo['values'] = (
            "Bethpage Black Course",
            "Bethpage Blue Course",
            "Bethpage Green Course",
            "Bethpage Red Course",
            "Bethpage Yellow Course 9 Holes",
            "Bethpage 9 Holes Midday Front 9",
            "Bethpage Early AM 9 Holes Blue"
        )
        self.course_combo.set("Bethpage Black Course")
        self.course_combo.pack(fill="x", pady=(0, 15))

        # Date Row
        date_frame = tk.Frame(self.main_frame, bg="#1e1e1e")
        date_frame.pack(fill="x", pady=(0, 15))

        # Year
        year_frame = tk.Frame(date_frame, bg="#1e1e1e")
        year_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Label(year_frame, text="Year", bg="#1e1e1e", foreground="#ffffff", font=("Helvetica", 9)).pack(anchor="w")
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        self.year_combo = ttk.Combobox(year_frame, textvariable=self.year_var, state="readonly")
        self.year_combo['values'] = [str(y) for y in range(2025, 2031)]
        self.year_combo.pack(fill="x")

        # Month
        month_frame = tk.Frame(date_frame, bg="#1e1e1e")
        month_frame.pack(side="left", fill="x", expand=True, padx=5)
        tk.Label(month_frame, text="Month", bg="#1e1e1e", foreground="#ffffff", font=("Helvetica", 9)).pack(anchor="w")
        self.month_var = tk.StringVar(value=datetime.now().strftime("%B"))
        self.month_combo = ttk.Combobox(month_frame, textvariable=self.month_var, state="readonly")
        self.month_combo['values'] = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
        self.month_combo.pack(fill="x")

        # Day
        day_frame = tk.Frame(date_frame, bg="#1e1e1e")
        day_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))
        tk.Label(day_frame, text="Day", bg="#1e1e1e", foreground="#ffffff", font=("Helvetica", 9)).pack(anchor="w")
        self.day_var = tk.StringVar(value=str(datetime.now().day))
        self.day_combo = ttk.Combobox(day_frame, textvariable=self.day_var, state="readonly")
        self.day_combo['values'] = [str(d) for d in range(1, 32)]
        self.day_combo.pack(fill="x")

        # Generate Time List
        times_list = []
        for period in ["am", "pm"]:
            for hour in range(1, 13):
                for minute in ["00", "15", "30", "45"]:
                    times_list.append(f"{hour}:{minute}{period}")

        # Time Range Row
        time_frame = tk.Frame(self.main_frame, bg="#1e1e1e")
        time_frame.pack(fill="x", pady=(0, 15))

        # Start Time
        start_time_frame = tk.Frame(time_frame, bg="#1e1e1e")
        start_time_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Label(start_time_frame, text="Start Time", bg="#1e1e1e", foreground="#ffffff", font=("Helvetica", 9)).pack(anchor="w")
        self.start_time_var = tk.StringVar(value="9:00am")
        self.start_time_combo = ttk.Combobox(start_time_frame, textvariable=self.start_time_var, state="readonly")
        self.start_time_combo['values'] = times_list
        self.start_time_combo.pack(fill="x")

        # End Time
        end_time_frame = tk.Frame(time_frame, bg="#1e1e1e")
        end_time_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))
        tk.Label(end_time_frame, text="End Time", bg="#1e1e1e", foreground="#ffffff", font=("Helvetica", 9)).pack(anchor="w")
        self.end_time_var = tk.StringVar(value="1:00pm")
        self.end_time_combo = ttk.Combobox(end_time_frame, textvariable=self.end_time_var, state="readonly")
        self.end_time_combo['values'] = times_list
        self.end_time_combo.pack(fill="x")

        # Players and Interval Row
        bottom_row = tk.Frame(self.main_frame, bg="#1e1e1e")
        bottom_row.pack(fill="x", pady=(0, 15))

        # Players
        players_frame = tk.Frame(bottom_row, bg="#1e1e1e")
        players_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Label(players_frame, text="Players", bg="#1e1e1e", foreground="#ffffff", font=("Helvetica", 9)).pack(anchor="w")
        self.players_var = tk.StringVar(value="4")
        self.players_combo = ttk.Combobox(players_frame, textvariable=self.players_var, state="readonly")
        self.players_combo['values'] = ("1", "2", "3", "4")
        self.players_combo.pack(fill="x")

        # Interval
        interval_frame = tk.Frame(bottom_row, bg="#1e1e1e")
        interval_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))
        tk.Label(interval_frame, text="Retry Interval (min)", bg="#1e1e1e", foreground="#ffffff", font=("Helvetica", 9)).pack(anchor="w")
        self.interval_var = tk.StringVar(value="10")
        self.interval_combo = ttk.Combobox(interval_frame, textvariable=self.interval_var, state="readonly")
        self.interval_combo['values'] = ("None", "1", "2", "5", "10", "15", "30", "60")
        self.interval_combo.pack(fill="x")

        # Schedule Row
        schedule_frame = tk.Frame(self.main_frame, bg="#1e1e1e")
        schedule_frame.pack(fill="x", pady=(10, 15))

        # Schedule Mode
        mode_frame = tk.Frame(schedule_frame, bg="#1e1e1e")
        mode_frame.pack(side="left", 
        
        fill="x", expand=True, padx=(0, 5))
        tk.Label(mode_frame, text="Execution Mode", bg="#1e1e1e", foreground="#ffffff", font=("Helvetica", 9)).pack(anchor="w")
        self.mode_var = tk.StringVar(value="Immediately")
        self.mode_combo = ttk.Combobox(mode_frame, textvariable=self.mode_var, state="readonly")
        self.mode_combo['values'] = ("Immediately", "Scheduled Time")
        self.mode_combo.pack(fill="x")

        # Scheduled Time
        target_time_frame = tk.Frame(schedule_frame, bg="#1e1e1e")
        target_time_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))
        tk.Label(target_time_frame, text="Target Time (e.g. 7:00pm)", bg="#1e1e1e", foreground="#ffffff", font=("Helvetica", 9)).pack(anchor="w")
        self.target_time_var = tk.StringVar(value="7:00pm")
        self.target_time_combo = ttk.Combobox(target_time_frame, textvariable=self.target_time_var, state="readonly")
        self.target_time_combo['values'] = times_list
        self.target_time_combo.pack(fill="x")

        # Card Details Row
        card_frame = tk.Frame(self.main_frame, bg="#1e1e1e")
        card_frame.pack(fill="x", pady=(0, 15))

        # Card Number
        cn_frame = tk.Frame(card_frame, bg="#1e1e1e")
        cn_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Label(cn_frame, text="Card Number", bg="#1e1e1e", foreground="#ffffff", font=("Helvetica", 9)).pack(anchor="w")
        self.card_num_entry = ttk.Entry(cn_frame)
        self.card_num_entry.pack(fill="x")

        # Expiry (MMYY)
        exp_frame = tk.Frame(card_frame, bg="#1e1e1e")
        exp_frame.pack(side="left", fill="x", expand=True, padx=5)
        tk.Label(exp_frame, text="Exp (MMYY)", bg="#1e1e1e", foreground="#ffffff", font=("Helvetica", 9)).pack(anchor="w")
        self.card_exp_entry = ttk.Entry(exp_frame)
        self.card_exp_entry.pack(fill="x")

        # CVV
        cvv_frame = tk.Frame(card_frame, bg="#1e1e1e")
        cvv_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))
        tk.Label(cvv_frame, text="CVV", bg="#1e1e1e", foreground="#ffffff", font=("Helvetica", 9)).pack(anchor="w")
        self.card_cvv_entry = ttk.Entry(cvv_frame)
        self.card_cvv_entry.pack(fill="x")

        # Price Display
        self.price_label = tk.Label(self.main_frame, text="Price: $0.00", bg="#1e1e1e", foreground="#4ade80", font=("Helvetica", 12, "bold"))
        self.price_label.pack(pady=(10, 0))

        # Submit Button
        self.submit_btn = ttk.Button(self.main_frame, text="START AUTOMATION", command=self.start_booking)
        self.submit_btn.pack(fill="x", pady=(20, 0), ipady=10)

        # Options Row
        options_frame = tk.Frame(self.main_frame, bg="#1e1e1e")
        options_frame.pack(fill="x", pady=(10, 0))
        
        self.show_browser_var = tk.BooleanVar(value=False)
        self.show_browser_check = tk.Checkbutton(
            options_frame, text="Show Browser Window", 
            variable=self.show_browser_var, 
            bg="#1e1e1e", fg="#ffffff", 
            selectcolor="#2d2d2d", activebackground="#1e1e1e", 
            activeforeground="#ffffff", font=("Helvetica", 9)
        )
        self.show_browser_check.pack(side="left")


        # Status Label
        self.status_label = tk.Label(self.main_frame, text="Ready", bg="#1e1e1e", foreground="#888888", font=("Helvetica", 9))
        self.status_label.pack(pady=(10, 5))

        # Log Area
        self.log_area = scrolledtext.ScrolledText(self.main_frame, height=10, bg="#121212", fg="#4ade80", font=("Consolas", 9), borderwidth=0)
        self.log_area.pack(fill="both", expand=True, pady=(5, 0))
        self.log_area.config(state="disabled")

    def submit_otp(self):
        self.otp_value = self.otp_entry.get()
        if self.otp_value:
            self.otp_event.set()
            self.otp_btn.config(state="disabled")
            self.log_message(f"OTP Submitted: {self.otp_value}")

    def request_otp(self):
        self.log_message("ACTION REQUIRED: Automatic OTP check failed. Please check your email manually.")
        # If auto-polling fails, we'll just wait a bit longer or return None
        # Since the field is gone, we can't wait for a button. 
        # We'll return None and the main loop will retry or log.
        return None

    def update_price(self, price_str):
        self.root.after(0, lambda: self.price_label.config(text=f"Price: {price_str}"))

    def log_message(self, message):
        def _log():
            self.log_area.config(state="normal")
            self.log_area.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
            self.log_area.see(tk.END)
            self.log_area.config(state="disabled")
        self.root.after(0, _log)

    def create_label(self, text):
        lbl = ttk.Label(self.main_frame, text=text)
        lbl.pack(anchor="w", pady=(10, 5))
        return lbl

    def create_entry(self, default_text="", show=""):
        entry = ttk.Entry(self.main_frame, show=show)
        entry.insert(0, default_text)
        entry.pack(fill="x", pady=(0, 15))
        return entry

    def start_booking(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()
        course = self.course_var.get()
        year = self.year_var.get()
        month = self.month_var.get()
        day = self.day_var.get()
        start_time = self.start_time_var.get()
        end_time = self.end_time_var.get()
        players = self.players_var.get()
        interval = self.interval_var.get()
        card_num = self.card_num_entry.get()
        card_exp = self.card_exp_entry.get()
        card_cvv = self.card_cvv_entry.get()
        headless = not self.show_browser_var.get()
        imap_email = self.imap_email_entry.get()
        app_pass = self.app_pass_entry.get()

        if not all([email, password, year, month, day, start_time, end_time]):
            messagebox.showerror("Error", "Please fill in all fields")
            return

        self.submit_btn.config(state="disabled")
        self.stop_requested = False
        
        # Run automation in a separate thread
        thread = threading.Thread(target=self.run_process_loop, args=(email, password, course, year, month, day, start_time, end_time, players, interval, card_num, card_exp, card_cvv, headless, imap_email, app_pass))
        thread.start()

    def run_process_loop(self, email, password, course, year, month, day, start_time, end_time, players, interval, card_num, card_exp, card_cvv, headless, imap_email, app_pass):
        # Handle Scheduling
        mode = self.mode_var.get()
        if mode == "Scheduled Time":
            target_time_str = self.target_time_var.get()
            try:
                # Convert 7:00pm to datetime today
                now = datetime.now()
                target_time_obj = datetime.strptime(target_time_str, "%I:%M%p").replace(
                    year=now.year, month=now.month, day=now.day
                )
                
                # If time already passed today, assume tomorrow
                if target_time_obj < now:
                    from datetime import timedelta
                    target_time_obj += timedelta(days=1)
                
                self.log_message(f"Waiting for scheduled time: {target_time_obj.strftime('%Y-%m-%d %I:%M%p')}")
                
                while datetime.now() < target_time_obj:
                    if getattr(self, 'stop_requested', False): return
                    diff = target_time_obj - datetime.now()
                    hours, remainder = divmod(diff.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    countdown = f"{hours:02}:{minutes:02}:{seconds:02}"
                    self.root.after(0, lambda: self.status_label.config(text=f"Waiting... Countdown: {countdown}", foreground="#f39c12"))
                    time.sleep(1)
                
                self.log_message("Target time reached! Starting booking...")
            except Exception as e:
                self.log_message(f"Scheduling error: {e}")

        while not getattr(self, 'stop_requested', False):
            try:
                self.root.after(0, lambda: self.status_label.config(text=f"Process Running... ({datetime.now().strftime('%H:%M:%S')})", foreground="#4cc9f0"))
                success = run_automation(
                    email, password, course, year, month, day, start_time, end_time, players, 
                    log_callback=self.log_message, 
                    otp_callback=self.request_otp,
                    price_callback=self.update_price,
                    card_info={'num': card_num, 'exp': card_exp, 'cvv': card_cvv},
                    headless=headless,
                    imap_info={'email': imap_email, 'pass': app_pass}
                )
                
                if success:
                    self.root.after(0, lambda: self.status_label.config(text="Success! Slot Booked.", foreground="#4ade80"))
                    self.log_message("SUCCESS: Booking process completed successfully.")
                    break
                
                # Check if it was a technical error (usually run_automation returns False on error but we can distinguish)
                # For now, if no success, we check if it was 'No slots found' or something else
                # I'll modify run_automation to return a specific value for 'No slots' vs 'Error'
                
                if success is None: # We'll use None for technical error
                    self.root.after(0, lambda: self.status_label.config(text="Technical error! Retrying immediately...", foreground="#f87171"))
                    self.log_message("ERROR detected. Reloading page and retrying immediately...")
                    time.sleep(2) # Short pause before reload
                    continue

                if not interval or interval.lower() == "none" or int(interval) <= 0:
                    self.root.after(0, lambda: self.status_label.config(text="No slot found (One-time run).", foreground="#f87171"))
                    break
                
                self.root.after(0, lambda: self.status_label.config(text=f"No slot found. Retrying in {interval} min...", foreground="#888888"))
                time.sleep(int(interval) * 60)
                
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(text=f"Error: {str(e)}", foreground="#f87171"))
                break
        
        self.root.after(0, lambda: self.submit_btn.config(state="normal"))

if __name__ == "__main__":
    root = tk.Tk()
    app = GolfBookingApp(root)
    root.mainloop()
