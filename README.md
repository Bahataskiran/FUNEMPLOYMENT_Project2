# OIS Course Registration Bot & Schedule Optimizer

An automated course registration tool and schedule optimizer designed for the Istinye University Student Information System (OIS). The project generates conflict-free course schedules during registration periods and handles the enrollment process autonomously.

To allow safe development and testing without sending requests to the live university servers, the repository includes a local Flask mock server that replicates the actual OIS interface and workflow.

## Features

* **Local Mock Server:** A Flask-based simulation of the OIS web interface (`app.py`) to test login flows, captcha handling, and course selection offline.
* **Captcha Solver:** Uses Pillow (PIL) image preprocessing filters alongside Tesseract OCR to automatically read and bypass login security codes.
* **Browser Automation:** Built with Playwright to handle user authentication, poll the registration page until the system opens, enroll in the selected sections, and log out safely.
* **Backtracking Schedule Optimizer:** Evaluates all theoretical and laboratory section combinations to guarantee zero time conflicts. Supports custom sorting criteria such as minimizing campus days (`minimum_days`) or creating compact daily schedules.

## Installation

### 1. Install Dependencies

Make sure Python 3.10+ is installed, then install the required packages and Playwright browser binaries:

```bash
pip install -r requirements.txt
playwright install chromium                            2. Install Tesseract OCRTesseract OCR must be installed on your system for the captcha solver to work:Windows: Download and run the Tesseract-OCR Windows Installer (default path: C:\Program Files\Tesseract-OCR).Linux: sudo apt-get install tesseract-ocrmacOS: brew install tesseractUsageThe project can be run in two modes: the local mock testing environment or the live OIS environment.Scenario A: Testing on the Local Mock ServerStart the Mock Server:
Run the Flask application in your terminal:Bashpython app.py
Check the Environment Config:
Make sure the ENV variable inside ois_config.py is set to "MOCK":PythonENV = "MOCK"
Set Optimization Criteria (Optional):
Pass your preferred scheduling priority as a parameter to the build_optimal_schedule function in ois_bot.py.Run the Bot:
Open a new terminal window and start the bot:Bashpython ois_bot.py
The bot will launch a browser, solve the captcha, log in, and wait for the course registration period to open.Simulate Registration Opening:
Course registration is closed by default. You can open the system by changing the following flag to True in app.py (or by visiting the /sistemi-degistir route in your browser)[cite: 7]:   PythonSISTEM_ACIK_MI = False
Once opened, the bot detects the change, computes the conflict-free schedule, selects the courses, and logs out.Scenario B: Running on the Live OIS SystemOpen ois_config.py and switch the environment to production:PythonENV = "PRODUCTION"
Update the student ID and password fields inside the perform_login function in ois_bot.py with your actual OIS credentials.Start the bot:Bashpython ois_bot.py
Project StructurePlaintext├── app.py                 # Local Flask mock server for testing
├── ois_bot.py             # Playwright bot handling login, captcha, and enrollment
├── ois_config.py          # Environment URLs and DOM selectors (Mock vs. Production)
├── optimizer_engine.py    # Backtracking schedule generator and clash detector
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates replicating the OIS frontend
│   ├── login.html
│   ├── mainmenu.html
│   └── derssecme.html
└── README.md
ContributorsMehmet Baha Taşkıran (2409011013) - @Bahataskiran
Muhammet Emin Bakırcı (2409111037) - @Eminbakircii
Yunus Çerkezoğlu (2409011003) - @yunuscerkezoglu
Mehmet Ali Saray (2509011054) - @MehmetAliS480
Sinan İnan (2409011034) - @sinaninan