# Community Skill Exchange Desktop App

## Overview
A desktop application for communities to exchange skills, request help, and volunteer, built with Python, Flet, and SQLite.

## Features
- User registration and profile management
- Skill request and volunteer matching (greedy algorithm)
- 48-hour confirmation window for matches
- Analytics dashboard (skill trends, response rates, match stats)
- Modular MVC architecture
- Packaged as a single .exe for Windows

## Installation
1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd community_skill_exchange
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
   Or use:
   ```sh
   python setup.py install
   ```

## Running the App
- **From source:**
  ```sh
  python -m community_skill_exchange.main
  ```
- **As an .exe:**
  1. Build the executable:
     ```sh
     bash build_exe.sh
     ```
  2. Double-click `dist/community_skill_exchange.exe` to launch.

## Running Tests
- Run all tests with:
  ```sh
  pytest
  ```

## Project Structure
```
community_skill_exchange/
├── models/           # SQLAlchemy ORM models
├── controllers/      # Business logic, matching, CRUD, UI callbacks
├── views/            # Flet UI components/screens
├── analytics/        # Matplotlib visualizations
├── tests/            # Pytest test suite
├── main.py           # App entry point
├── geo_service.py    # Location/distance logic (stub)
├── database.py       # DB setup
├── ...
requirements.txt      # Dependencies
setup.py              # Install script
build_exe.sh          # PyInstaller build
README.md             # This file
```

## Notes
- No Google Maps or FastAPI (local only, Euclidean distance)
- Easily extensible for future web or mapping features
- For any issues, please open an issue or PR. 