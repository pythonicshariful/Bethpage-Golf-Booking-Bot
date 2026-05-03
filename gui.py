import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import sys
from datetime import datetime
from main import run_automation

class StdoutRedirector(object):
    def __init__(self, log_callback):
        self.log_callback = log_callback

    def write(self, message):
        if message == '\n':
            return
        if message.strip():
            self.log_callback(message.strip())

    def flush(self):
        pass

class GolfBookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bethpage Golf Booking Bot")
        self.root.geometry("1100x700")
        
        # --- Premium Theme Colors ---
        BG_COLOR = "#0f172a"        # Deep slate background
        CARD_BG = "#1e293b"         # Slate-800 for cards
        TEXT_COLOR = "#f8fafc"      # Off-white
        MUTED_TEXT = "#94a3b8"      # Gray
        ACCENT_COLOR = "#3b82f6"    # Vivid Blue
        ACCENT_HOVER = "#2563eb"
        ENTRY_BG = "#334155"        # Slate-700
        BORDER_COLOR = "#475569"    # Slate-600
        
        self.root.configure(bg=BG_COLOR)
        self.otp_event = threading.Event()
        self.otp_value = ""
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # --- Configure Styles ---
        self.style.configure("TLabel", background=CARD_BG, foreground=TEXT_COLOR, font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", background=BG_COLOR, foreground=ACCENT_COLOR, font=("Segoe UI", 24, "bold"))
        self.style.configure("Section.TLabel", background=CARD_BG, foreground=TEXT_COLOR, font=("Segoe UI", 12, "bold"))
        
        self.style.configure("TButton", background=ACCENT_COLOR, foreground=TEXT_COLOR, borderwidth=0, font=("Segoe UI", 11, "bold"), padding=8)
        self.style.map("TButton", background=[("active", ACCENT_HOVER)])
        
        self.style.configure("TEntry", fieldbackground=ENTRY_BG, foreground=TEXT_COLOR, borderwidth=0, padding=5)
        self.style.configure("TCombobox", fieldbackground=ENTRY_BG, background=CARD_BG, foreground=TEXT_COLOR, arrowcolor=TEXT_COLOR, borderwidth=0, padding=5)
        self.style.map("TCombobox", fieldbackground=[("readonly", ENTRY_BG)], selectbackground=[("readonly", ACCENT_COLOR)], selectforeground=[("readonly", TEXT_COLOR)])

        # --- Main Scrollable Container ---
        self.canvas = tk.Canvas(root, bg=BG_COLOR, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=BG_COLOR)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        def configure_canvas(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)
        self.canvas.bind("<Configure>", configure_canvas)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        self.main_frame = self.scrollable_frame
        
        # Redirect stdout and stderr
        sys.stdout = StdoutRedirector(self.log_message)
        sys.stderr = StdoutRedirector(self.log_message)
        
        # --- UI Builders ---
        def create_card(parent, title):
            border_frame = tk.Frame(parent, bg=BORDER_COLOR, padx=1, pady=1)
            border_frame.pack(fill="x", pady=(0, 15), padx=20)
            
            card = tk.Frame(border_frame, bg=CARD_BG, padx=25, pady=20)
            card.pack(fill="both", expand=True)
            
            title_frame = tk.Frame(card, bg=CARD_BG)
            title_frame.pack(fill="x", pady=(0, 15))
            ttk.Label(title_frame, text=title, style="Section.TLabel").pack(side="left")
            
            tk.Frame(card, bg=BORDER_COLOR, height=1).pack(fill="x", pady=(0, 15))
            
            return card
            
        def create_field(parent, label_text, widget_class=ttk.Entry, **kwargs):
            frame = tk.Frame(parent, bg=CARD_BG)
            frame.pack(fill="x", pady=(0, 12))
            ttk.Label(frame, text=label_text, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
            var = kwargs.pop('textvariable', None)
            if widget_class == ttk.Entry:
                widget = widget_class(frame, **kwargs)
            else:
                widget = widget_class(frame, textvariable=var, **kwargs)
            widget.pack(fill="x", ipady=2)
            return widget, var

        # --- Header ---
        header_frame = tk.Frame(self.main_frame, bg=BG_COLOR, pady=25)
        header_frame.pack(fill="x")
        ttk.Label(header_frame, text="Bethpage Booking Bot", style="Header.TLabel").pack()
        ttk.Label(header_frame, text="Automated Tee Time Reservation System", background=BG_COLOR, foreground=MUTED_TEXT, font=("Segoe UI", 10)).pack(pady=(5, 0))

        content_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
        content_frame.pack(fill="x", expand=True, padx=10)
        
        left_col = tk.Frame(content_frame, bg=BG_COLOR)
        left_col.pack(side="left", fill="both", expand=True, padx=5)
        
        right_col = tk.Frame(content_frame, bg=BG_COLOR)
        right_col.pack(side="left", fill="both", expand=True, padx=5)

        # --- 1. Account Credentials Card ---
        cred_card = create_card(right_col, "Account Credentials")
        
        self.email_entry, _ = create_field(cred_card, "ForeUp Email Address")
        self.pass_entry, _ = create_field(cred_card, "ForeUp Password", show="•")
        
        imap_row = tk.Frame(cred_card, bg=CARD_BG)
        imap_row.pack(fill="x")
        f1 = tk.Frame(imap_row, bg=CARD_BG); f1.pack(side="left", fill="x", expand=True, padx=(0, 8))
        f2 = tk.Frame(imap_row, bg=CARD_BG); f2.pack(side="left", fill="x", expand=True, padx=(8, 0))
        
        ttk.Label(f1, text="Gmail/IMAP Email", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
        self.imap_email_entry = ttk.Entry(f1)
        self.imap_email_entry.pack(fill="x", ipady=2)
        
        ttk.Label(f2, text="Gmail App Password", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
        self.app_pass_entry = ttk.Entry(f2, show="•")
        self.app_pass_entry.pack(fill="x", ipady=2)

        # --- 2. Booking Settings Card ---
        book_card = create_card(left_col, "Booking Settings")
        
        self.course_var = tk.StringVar(value="Bethpage Black Course")
        self.course_combo, _ = create_field(book_card, "Select Course", ttk.Combobox, textvariable=self.course_var, state="readonly", values=(
            "Bethpage Black Course",
            "Bethpage Blue Course",
            "Bethpage Green Course",
            "Bethpage Red Course",
            "Bethpage Yellow Course 9 Holes",
            "Bethpage 9 Holes Midday Front 9",
            "Bethpage Early AM 9 Holes Blue"
        ))
        
        self.booking_class_var = tk.StringVar(value="Non Resident")
        self.booking_class_combo, _ = create_field(book_card, "Booking Class", ttk.Combobox, textvariable=self.booking_class_var, state="readonly", values=(
            "Resident",
            "Verified NYS Resident - Bethpage/Sunken Meadow",
            "Non Resident",
            "Verified Access/Liberty Pass",
            "Verified Junior Resident",
            "Verified Senior Resident"
        ))
        
        date_row = tk.Frame(book_card, bg=CARD_BG)
        date_row.pack(fill="x", pady=(0, 12))
        yf = tk.Frame(date_row, bg=CARD_BG); yf.pack(side="left", fill="x", expand=True, padx=(0, 5))
        mf = tk.Frame(date_row, bg=CARD_BG); mf.pack(side="left", fill="x", expand=True, padx=5)
        df = tk.Frame(date_row, bg=CARD_BG); df.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        ttk.Label(yf, text="Year", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        self.year_combo = ttk.Combobox(yf, textvariable=self.year_var, state="readonly", values=[str(y) for y in range(2025, 2031)])
        self.year_combo.pack(fill="x", ipady=2)
        
        ttk.Label(mf, text="Month", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
        self.month_var = tk.StringVar(value=datetime.now().strftime("%B"))
        self.month_combo = ttk.Combobox(mf, textvariable=self.month_var, state="readonly", values=("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"))
        self.month_combo.pack(fill="x", ipady=2)
        
        ttk.Label(df, text="Day", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
        self.day_var = tk.StringVar(value=str(datetime.now().day))
        self.day_combo = ttk.Combobox(df, textvariable=self.day_var, state="readonly", values=[str(d) for d in range(1, 32)])
        self.day_combo.pack(fill="x", ipady=2)
        
        times_list = []
        for period in ["am", "pm"]:
            for hour in range(1, 13):
                for minute in ["00", "10", "20", "30", "40", "50"]:
                    times_list.append(f"{hour}:{minute}{period}")
                    
        time_row = tk.Frame(book_card, bg=CARD_BG)
        time_row.pack(fill="x", pady=(0, 12))
        stf = tk.Frame(time_row, bg=CARD_BG); stf.pack(side="left", fill="x", expand=True, padx=(0, 8))
        etf = tk.Frame(time_row, bg=CARD_BG); etf.pack(side="left", fill="x", expand=True, padx=(8, 0))
        
        ttk.Label(stf, text="Start Time", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
        self.start_time_var = tk.StringVar(value="9:00am")
        self.start_time_combo = ttk.Combobox(stf, textvariable=self.start_time_var, values=times_list)
        self.start_time_combo.pack(fill="x", ipady=2)
        
        ttk.Label(etf, text="End Time", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
        self.end_time_var = tk.StringVar(value="1:00pm")
        self.end_time_combo = ttk.Combobox(etf, textvariable=self.end_time_var, values=times_list)
        self.end_time_combo.pack(fill="x", ipady=2)
        
        pi_row = tk.Frame(book_card, bg=CARD_BG)
        pi_row.pack(fill="x")
        pf = tk.Frame(pi_row, bg=CARD_BG); pf.pack(side="left", fill="x", expand=True, padx=(0, 8))
        intf = tk.Frame(pi_row, bg=CARD_BG); intf.pack(side="left", fill="x", expand=True, padx=(8, 0))
        
        ttk.Label(pf, text="Players", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
        self.players_var = tk.StringVar(value="4")
        self.players_combo = ttk.Combobox(pf, textvariable=self.players_var, state="readonly", values=("1", "2", "3", "4"))
        self.players_combo.pack(fill="x", ipady=2)
        
        ttk.Label(intf, text="Retry Interval (min)", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
        self.interval_var = tk.StringVar(value="10")
        self.interval_combo = ttk.Combobox(intf, textvariable=self.interval_var, state="readonly", values=("None", "1", "2", "5", "10", "15", "30", "60"))
        self.interval_combo.pack(fill="x", ipady=2)

        # --- 3. Execution Options Card ---
        exec_card = create_card(right_col, "Execution Options")
        
        exec_row = tk.Frame(exec_card, bg=CARD_BG)
        exec_row.pack(fill="x", pady=(0, 12))
        
        modf = tk.Frame(exec_row, bg=CARD_BG)
        modf.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Label(modf, text="Execution Mode", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
        self.mode_var = tk.StringVar(value="Immediately")
        self.mode_combo = ttk.Combobox(modf, textvariable=self.mode_var, state="readonly", values=("Immediately", "Scheduled Time"))
        self.mode_combo.pack(fill="x", ipady=2)
        self.mode_combo.bind("<<ComboboxSelected>>", self.toggle_target_time)
        
        self.target_time_frame = tk.Frame(exec_row, bg=CARD_BG)
        ttk.Label(self.target_time_frame, text="Target Time", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
        self.target_time_var = tk.StringVar(value="7:00pm")
        self.target_time_combo = ttk.Combobox(self.target_time_frame, textvariable=self.target_time_var, values=times_list)
        self.target_time_combo.pack(fill="x", ipady=2)
        
        self.show_browser_var = tk.BooleanVar(value=False)
        self.show_browser_check = tk.Checkbutton(
            exec_card, text=" Show Browser Window during execution", 
            variable=self.show_browser_var, 
            bg=CARD_BG, fg=TEXT_COLOR, 
            selectcolor=ENTRY_BG, activebackground=CARD_BG, 
            activeforeground=TEXT_COLOR, font=("Segoe UI", 9),
            borderwidth=0, highlightthickness=0
        )
        self.show_browser_check.pack(anchor="w", pady=(5, 0))

        # --- 4. Payment Info Card ---
        pay_card = create_card(right_col, "Payment Information")
        pay_row = tk.Frame(pay_card, bg=CARD_BG)
        pay_row.pack(fill="x")
        
        cnf = tk.Frame(pay_row, bg=CARD_BG); cnf.pack(side="left", fill="x", expand=True, padx=(0, 5))
        expf = tk.Frame(pay_row, bg=CARD_BG); expf.pack(side="left", fill="x", expand=True, padx=5)
        cvvf = tk.Frame(pay_row, bg=CARD_BG); cvvf.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        ttk.Label(cnf, text="Card Number", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
        self.card_num_entry = ttk.Entry(cnf)
        self.card_num_entry.pack(fill="x", ipady=2)
        
        ttk.Label(expf, text="Exp (MMYY)", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
        self.card_exp_entry = ttk.Entry(expf)
        self.card_exp_entry.pack(fill="x", ipady=2)
        
        ttk.Label(cvvf, text="CVV", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
        self.card_cvv_entry = ttk.Entry(cvvf, show="•")
        self.card_cvv_entry.pack(fill="x", ipady=2)

        # --- 5. Footer Actions ---
        footer_frame = tk.Frame(self.main_frame, bg=BG_COLOR, padx=20)
        footer_frame.pack(fill="x", pady=(10, 30))
        
        footer_left = tk.Frame(footer_frame, bg=BG_COLOR)
        footer_left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        footer_right = tk.Frame(footer_frame, bg=BG_COLOR)
        footer_right.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        price_frame = tk.Frame(footer_left, bg=BG_COLOR)
        price_frame.pack(fill="x", pady=(0, 15))
        
        self.price_label = tk.Label(price_frame, text="Total Price: $0.00", bg=BG_COLOR, foreground="#22c55e", font=("Segoe UI", 16, "bold"))
        self.price_label.pack(anchor="w")
        
        btn_frame = tk.Frame(footer_left, bg=BG_COLOR)
        btn_frame.pack(fill="x", pady=(0, 15))
        
        self.submit_btn = ttk.Button(btn_frame, text="START", command=self.start_booking)
        self.submit_btn.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=8)
        
        self.stop_btn = ttk.Button(btn_frame, text="STOP", command=self.stop_booking)
        self.stop_btn.state(['disabled'])
        self.stop_btn.pack(side="left", fill="x", expand=True, padx=5, ipady=8)
        
        self.restart_btn = ttk.Button(btn_frame, text="RESTART", command=self.restart_booking)
        self.restart_btn.state(['disabled'])
        self.restart_btn.pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=8)
        
        status_frame = tk.Frame(footer_left, bg=BG_COLOR, pady=15)
        status_frame.pack(fill="x")
        tk.Label(status_frame, text="Status: ", bg=BG_COLOR, foreground=TEXT_COLOR, font=("Segoe UI", 10, "bold")).pack(side="left")
        self.status_label = tk.Label(status_frame, text="Ready to start", bg=BG_COLOR, foreground=MUTED_TEXT, font=("Segoe UI", 10, "italic"))
        self.status_label.pack(side="left")
        
        # Log Box with Border
        log_border = tk.Frame(footer_right, bg=BORDER_COLOR, padx=1, pady=1)
        log_border.pack(fill="both", expand=True)
        self.log_area = scrolledtext.ScrolledText(log_border, height=8, bg=ENTRY_BG, fg="#22c55e", font=("Consolas", 9), borderwidth=0, highlightthickness=0)
        self.log_area.pack(fill="both", expand=True, padx=1, pady=1)
        self.log_area.config(state="disabled")

        self.last_log_msg = ""
        self.is_running = False

    # --- Logic Methods ---
    def stop_booking(self):
        self.stop_requested = True
        self.log_message("Stop requested... waiting for current operation to finish.")
        self.stop_btn.state(['disabled'])
        self.restart_btn.state(['disabled'])

    def restart_booking(self):
        self.log_message("Restart requested...")
        self.stop_booking()
        threading.Thread(target=self._wait_and_restart, daemon=True).start()

    def _wait_and_restart(self):
        while getattr(self, 'is_running', False):
            time.sleep(0.5)
        self.root.after(0, self.start_booking)
    def toggle_target_time(self, event=None):
        if self.mode_var.get() == "Immediately":
            self.target_time_frame.pack_forget()
        else:
            self.target_time_frame.pack(side="left", fill="x", expand=True, padx=(8, 0))

    def submit_otp(self):
        self.otp_value = self.otp_entry.get()
        if self.otp_value:
            self.otp_event.set()
            self.otp_btn.config(state="disabled")
            self.log_message(f"OTP Submitted: {self.otp_value}")

    def request_otp(self):
        self.log_message("ACTION REQUIRED: Automatic OTP check failed. Please check your email manually.")
        return None

    def update_price(self, price_str):
        self.root.after(0, lambda: self.price_label.config(text=f"Total Price: {price_str}"))

    def log_message(self, message):
        if not message.strip():
            return
        if message == getattr(self, 'last_log_msg', ''):
            return
        self.last_log_msg = message

        def _log():
            self.log_area.config(state="normal")
            self.log_area.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
            self.log_area.see(tk.END)
            self.log_area.config(state="disabled")
        self.root.after(0, _log)

    def start_booking(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()
        course = self.course_var.get()
        booking_class = self.booking_class_var.get()
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

        self.submit_btn.state(['disabled'])
        self.stop_btn.state(['!disabled'])
        self.restart_btn.state(['!disabled'])
        self.stop_requested = False
        self.is_running = True
        
        thread = threading.Thread(target=self.run_process_loop, args=(email, password, course, booking_class, year, month, day, start_time, end_time, players, interval, card_num, card_exp, card_cvv, headless, imap_email, app_pass), daemon=True)
        thread.start()

    def run_process_loop(self, email, password, course, booking_class, year, month, day, start_time, end_time, players, interval, card_num, card_exp, card_cvv, headless, imap_email, app_pass):
        mode = self.mode_var.get()
        if mode == "Scheduled Time":
            target_time_str = self.target_time_var.get().replace(" ", "")
            try:
                now = datetime.now()
                target_time_obj = datetime.strptime(target_time_str, "%I:%M%p").replace(
                    year=now.year, month=now.month, day=now.day
                )
                
                if target_time_obj < now:
                    from datetime import timedelta
                    target_time_obj += timedelta(days=1)
                
                self.log_message(f"Waiting for scheduled time: {target_time_obj.strftime('%Y-%m-%d %I:%M%p')}")
                
                while datetime.now() < target_time_obj:
                    if getattr(self, 'stop_requested', False): break
                    diff = target_time_obj - datetime.now()
                    hours, remainder = divmod(diff.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    countdown = f"{hours:02}:{minutes:02}:{seconds:02}"
                    self.root.after(0, lambda c=countdown: self.status_label.config(text=f"Waiting... Countdown: {c}", foreground="#eab308"))
                    time.sleep(1)
                
                self.log_message("Target time reached! Starting booking...")
            except Exception as e:
                self.log_message(f"Scheduling error: {e}")

        while not getattr(self, 'stop_requested', False):
            try:
                self.root.after(0, lambda: self.status_label.config(text=f"Process Running... ({datetime.now().strftime('%H:%M:%S')})", foreground="#3b82f6"))
                success = run_automation(
                    email, password, course, year, month, day, start_time, end_time, players, 
                    booking_class=booking_class,
                    log_callback=self.log_message, 
                    otp_callback=self.request_otp,
                    price_callback=self.update_price,
                    card_info={'num': card_num, 'exp': card_exp, 'cvv': card_cvv},
                    headless=headless,
                    imap_info={'email': imap_email, 'pass': app_pass}
                )
                
                if success:
                    self.root.after(0, lambda: self.status_label.config(text="Success! Slot Booked.", foreground="#22c55e"))
                    self.log_message("SUCCESS: Booking process completed successfully.")
                    break
                
                if success is None:
                    self.root.after(0, lambda: self.status_label.config(text="Technical error! Retrying immediately...", foreground="#ef4444"))
                    self.log_message("ERROR detected. Reloading page and retrying immediately...")
                    time.sleep(2)
                    continue

                if not interval or interval.lower() == "none" or int(interval) <= 0:
                    self.root.after(0, lambda: self.status_label.config(text="No slot found (One-time run).", foreground="#ef4444"))
                    break
                
                self.root.after(0, lambda: self.status_label.config(text=f"No slot found. Retrying in {interval} min...", foreground="#94a3b8"))
                time.sleep(int(interval) * 60)
                
            except Exception as e:
                self.root.after(0, lambda msg=f"Error: {str(e)}": self.status_label.config(text=msg, foreground="#ef4444"))
                break
        
        self.is_running = False
        def _reset_buttons():
            self.submit_btn.state(['!disabled'])
            self.stop_btn.state(['disabled'])
            self.restart_btn.state(['disabled'])
        self.root.after(0, _reset_buttons)

if __name__ == "__main__":
    root = tk.Tk()
    app = GolfBookingApp(root)
    root.mainloop()
