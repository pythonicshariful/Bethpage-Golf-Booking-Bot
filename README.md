# Bethpage Golf Booking Bot

Welcome to the Bethpage Golf Booking Bot! This application fully automates the process of booking a tee time at Bethpage State Park. It handles logging into your account, finding your desired tee time, securely capturing the OTP (One-Time Password) from your email, and completing the payment.

---

## 🚀 How to Run the Application

You do not need to install Python or know how to code to use this bot. It has been packaged into a single standalone executable (`.exe`).

1. Open the project folder on your computer.
2. Navigate into the **`dist`** folder.
3. Find the file named **`BethpageBot.exe`**.
4. **Double-click** the file to launch the Graphical User Interface (GUI).
   > *Tip: You can right-click this file, select "Send to", and choose "Desktop (create shortcut)" so you can launch it easily from your desktop in the future.*

---

## 🛠️ For Developers (How to Build)

If you want to modify the code and rebuild the executable yourself, follow these steps:

### 1. Install Dependencies
```bash
pip install pyinstaller webdriver-manager selenium
```

### 2. Build the Standalone EXE
Run this command from the project root:
```bash
python -m PyInstaller --noconfirm --onefile --windowed --name "BethpageBot" --clean --collect-all selenium "gui.py"
```

---

## 📧 How to Set Up Automated OTP Retrieval (Gmail App Password)

To allow the bot to read the booking code sent to your email automatically, you **must** generate a secure "App Password" from your Google Account. **Do not use your regular Gmail password in the bot.**

Here is exactly how to generate a Gmail App Password:

### Step 1: Turn on 2-Step Verification
1. Go to your Google Account management page: [https://myaccount.google.com/](https://myaccount.google.com/)
2. On the left navigation panel, click **Security**.
3. Under the *“How you sign in to Google”* section, look for **2-Step Verification**.
4. If it says "Off", click it and follow the on-screen instructions to set it up (you'll need to link your phone number).

### Step 2: Create the App Password
1. Once 2-Step Verification is turned on, stay in the **Security** tab.
2. In the search bar at the top of your Google Account page, search for **"App passwords"** and click on the result.
   > *Note: Depending on your Google Account layout, this might also be located at the bottom of the 2-Step Verification page.*
3. You may be asked to sign into your Google account again.
4. On the App Passwords page, type a name for the app (e.g., "Golf Bot") in the text box and click **Create**.
5. A popup will appear with a **16-character password** (usually displayed in a yellow box). 

### Step 3: Add to the Bot
1. **Copy this 16-character password.**
2. Open the Bethpage Golf Booking Bot application.
3. In the **"Gmail App Password"** field, paste the 16-character code (you do not need the spaces).
4. Put your normal Gmail address in the **"Gmail/IMAP Email"** field.

---

## ⚙️ Using the Bot

Once you have your ForeUp credentials and your Gmail App Password ready, fill out the application:

### 1. Account Credentials
- **ForeUp Email Address**: The email you use to log into the Bethpage booking site.
- **ForeUp Password**: Your password for the Bethpage booking site.
- **Gmail/IMAP Email**: Your Gmail address where the OTP is sent.
- **Gmail App Password**: The 16-digit code you generated in the steps above.

### 2. Booking Settings
- **Course & Booking Class**: Select the course you want to play and your residency class (e.g., Verified NYS Resident).
- **Date & Time**: Select the specific day and a time range. The bot will search for times *between* your Start Time and End Time.
- **Players**: Number of players in your group.
- **Retry Interval (min)**: If the bot checks and no slots are available, it will wait this many minutes and try again. Select "None" if you only want it to check once.

### 3. Execution Options
- **Execution Mode**: 
  - *Immediately*: The bot will start searching as soon as you click the start button.
  - *Scheduled Time*: The bot will wait silently until the "Target Time" you set, and *then* it will start executing. (Great for times when new slots drop right at 7:00 PM).
- **Show Browser Window**: Check this box if you want to visibly watch the bot navigate the web pages. Leave it unchecked to run "Headless" (invisible background mode) for faster performance.

### 4. Payment Information
- Enter your valid credit card information. This will only be submitted on the final checkout screen to secure the tee time.

---

## 🛠️ Troubleshooting
- **OTP Fails to Fill**: Ensure that the email registered to your Bethpage account matches the Gmail account you provided the App Password for.
- **Bot gets stuck on loading**: If the website structure changes or the internet connection drops, you can close the terminal window or click the close button on the app and restart it. You can track exactly what the bot is doing in the green **Log** terminal at the bottom of the app.
