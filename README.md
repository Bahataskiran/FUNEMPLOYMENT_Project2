# OIS Course Registration Bot & Schedule Optimizer 🎓🤖

An automated course registration tool and schedule optimizer designed for the Istinye University Student Information System (OIS). The project generates conflict-free course schedules during registration periods, enrolls in sections autonomously, and provides multi-channel status alerts.

To allow safe development and testing without sending requests to the live university servers, the repository includes a local Flask mock server that replicates the actual OIS interface and workflow.

---

## Features

* **Backtracking Schedule Optimizer:** Evaluates all theoretical and laboratory section combinations using a backtracking algorithm to guarantee zero time conflicts. Supports priority criteria such as minimizing campus days (`minimum_days`) or generating compact daily blocks.
* **Structured ASCII Schedule Output:** Formats the selected conflict-free schedule into a clean, human-readable text table sorted by weekday and start time.
* **Captcha Solver:** Uses Pillow (PIL) image preprocessing filters alongside Tesseract OCR to automatically read and bypass login security codes.
* **Browser Automation:** Built with Playwright to manage user authentication, session timeouts (20-minute boundary handling), polling for registration opening, section selection, and clean logout.
* **Multi-Channel Notifications:** Alerts the user on state transitions (when registration opens and when enrollment finishes) across terminal output, desktop toast notifications, and mobile push alerts via ntfy.
* **Local Mock Server:** A Flask-based simulation of the OIS web interface (`app.py`) to safely test login flows, error recovery, captchas, and dynamic system state changes offline.

---

## Installation

### 1. Install Dependencies

Make sure Python 3.10+ is installed, then install the required packages and Playwright browser binaries:

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Install Tesseract OCR

Tesseract OCR must be installed on your system for the captcha solver to work:
* **Windows:** Download and run the [Tesseract-OCR Windows Installer](https://github.com/UB-Mannheim/tesseract/wiki) (default path: `C:\Program Files\Tesseract-OCR`).
* **Linux:** `sudo apt-get install tesseract-ocr`
* **macOS:** `brew install tesseract`

---

## Usage

The project can be run in two modes: the local mock testing environment or the live OIS environment.

### Scenario A: Testing on the Local Mock Server

1. **Start the Mock Server:**
   Run the Flask application in your terminal:
   ```bash
   python app.py
   ```
   The server starts at `http://127.0.0.1:5000` by default.

2. **Verify Environment Config:**
   Make sure the `ENV` variable inside `ois_config.py` is set to `"MOCK"`:
   ```python
   ENV = "MOCK"
   ```

3. **Subscribe to Mobile Alerts (Optional):**
   Install the **ntfy** app on your phone (available on iOS and Android, no account required) and subscribe to the topic:
   ```text
   funemployment_ois_baha_2026
   ```

4. **Run the Bot:**
   Open a new terminal window and start the bot:
   ```bash
   python bot/ois_bot.py
   ```
   The bot will launch the browser, solve the captcha, log in, and wait for the registration period to open.

5. **Simulate Registration Opening:**
   Course registration is closed by default. While the bot is polling, trigger the opening by visiting this URL in your browser:
   ```text
   http://127.0.0.1:5000/sistemi-degistir
   ```
   Once opened, the bot detects the state transition, calculates the optimal schedule, enrolls in all sections, dispatches the schedule table notification, and logs out safely.

---

### Scenario B: Running on the Live OIS System

1. Open `ois_config.py` and switch the environment to production:
   ```python
   ENV = "PRODUCTION"
   ```
2. Update the student ID and password inside the `perform_login` function in `bot/ois_bot.py` with your actual OIS credentials.
3. Start the bot:
   ```bash
   python bot/ois_bot.py
   ```

---

## Project Structure

```plaintext
├── app.py                 # Local Flask mock server replicating OIS backend
├── ois_config.py          # Environment URLs and DOM selectors (Mock vs. Production)
├── optimizer_engine.py    # Backtracking schedule generator and ASCII table formatter
├── requirements.txt       # Project dependencies
├── bot/
│   ├── ois_bot.py         # Playwright bot handling login, captcha, and enrollment
│   └── notifier.py        # Multi-channel notification dispatcher (Desktop & ntfy)
├── templates/             # HTML templates replicating the OIS frontend
│   ├── login.html
│   ├── mainmenu.html
│   └── derssecme.html
└── README.md
```

---

## Contributors (Funemployment)

* Mehmet Baha Taşkıran (2409011013) - [@Bahataskiran](https://github.com/Bahataskiran)
* Muhammet Emin Bakırcı (2409111037) - [@Eminbakircii](https://github.com/Eminbakircii)
* Yunus Çerkezoğlu (2409011003) - [@yunuscerkezoglu](https://github.com/yunuscerkezoglu)
* Mehmet Ali Saray (2509011054) - [@MehmetAliS480](https://github.com/MehmetAliS480)
* Sinan İnan (2409011034) - [@sinaninan](https://github.com/sinaninan)