# Community Skill Exchange Platform

## Features
- User registration with username, password, skills (max 3), and location (Google Maps autocomplete)
- Login and authentication
- Skill selection from a predefined list
- Location stored for each user
- Request Help: users can create and manage help requests
- Open Requests: shows all open requests (except your own), **sorted by closest to farthest** (greedy algorithm)
- My Matches & History: shows all matches and requests, with clear labels and scrollable list
- Messaging: chat with matched users
- Modern, clean, and user-friendly UI (Flet)
- **Distances are NOT shown in the UI, but requests are sorted by proximity**
- Scrollable lists for both Open Requests and My Matches & History

## Setup Instructions

### Backend
1. Install Python 3.12+
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your Google Maps API key in `app/config.py` as `GOOGLE_MAPS_API_KEY`.
4. Run the backend:
   ```
   python main.py
   ```

### Frontend (Flet)
1. Install Flet:
   ```
   pip install flet
   ```
2. Run the frontend (usually also via `python main.py` or your Flet entrypoint).

## Notes
- The backend uses a greedy algorithm to sort open requests by distance, but the UI does not display the distance value.
- All lists (Open Requests, My Matches & History) are scrollable for better usability.
- User locations are used for sorting and matching, but not shown as coordinates.


- Available Users:
   Username, Password
   user1, user1
   user2, user2
   user3, user3
   user4, user4

## Contribution
Pull requests and issues are welcome! 