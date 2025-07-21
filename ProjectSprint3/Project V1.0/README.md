# Community Skill-Sharing App

A simple desktop and API platform for community skill exchange.

## Features
- User sign up, login, and skill selection
- Create and manage help requests
- Volunteer matching and session management
- Ratings, analytics, and history
- Plain, light, and simple UI (Flet)

## Requirements
- Python 3.10+
- `pip install -r requirements.txt`

## Setup
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Seed the database (optional, for demo/testing):
   ```sh
   python -m backend.db_seed
   ```
3. Start the backend API:
   ```sh
   uvicorn backend.main:app --reload
   ```
4. Start the desktop app:
   ```sh
   python -m backend.desktop_app
   ```

## Usage
- Sign up or log in as a user
- Create requests, view offers, accept/ignore, and manage sessions
- Use the dashboard to view your skill, requests, and history

## Notes
- No Google Maps API key required (uses placeholder distances)
- To reset data, delete `skillshare.db` and re-seed 