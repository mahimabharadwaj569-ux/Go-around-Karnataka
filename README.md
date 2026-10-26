# Trip Companion — Tour Together & Expense Tracker

A ready-to-run Flask + SQLite project for a Karnataka travel-planning expo demo.

## Features
- Register, login, logout, and edit profile
- Karnataka's 31 districts with landmarks, temples, attractions, and suggested stays
- Filter district information without Google Maps
- Build a 1-, 2-, 3-, or more-day itinerary based on solo, couple, family, or friends travel
- Hotel/stay directory and booking-request demo
- My bookings, trip history, goals, and expense tracker
- SQLite database is created automatically

## Run on Windows (VS Code)
1. Extract this ZIP.
2. Open the `Trip_Companion_Full_Project` folder in VS Code.
3. Open Terminal and run:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```
4. Open `http://127.0.0.1:5000` in your browser.
5. Register a new account. The database `trip_companion.db` is created automatically.

If PowerShell blocks activation, run `python -m pip install -r requirements.txt` and then `python app.py` without activating the environment.

## Demo notes
Hotel entries and booking requests are illustrative project-demo data, not live availability or verified current cleanliness ratings. Confirm real rates, safety, and availability directly before travelling. The app does not use Google Maps or require an API key.
