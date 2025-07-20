from community_skill_exchange.controllers import create_user

dummies = [
    {"username": "alice", "password": "alice123", "skills": "Cooking", "availability": "2024-06-10:2024-06-15", "location": "Metro City"},
    {"username": "bob", "password": "bob123", "skills": "Teaching", "availability": "2024-06-11:2024-06-20", "location": "Metro City"},
    {"username": "carol", "password": "carol123", "skills": "Gardening", "availability": "2024-06-12:2024-06-18", "location": "Uptown"},
    {"username": "dave", "password": "dave123", "skills": "Computer Help", "availability": "2024-06-13:2024-06-25", "location": "Downtown"},
    {"username": "eve", "password": "eve123", "skills": "Pet Care", "availability": "2024-06-14:2024-06-30", "location": "Suburb"},
    {"username": "frank", "password": "frank123", "skills": "Driving", "availability": "2024-06-15:2024-06-22", "location": "Downtown"},
    {"username": "grace", "password": "grace123", "skills": "Cleaning", "availability": "2024-06-16:2024-06-28", "location": "Metro City"},
    {"username": "henry", "password": "henry123", "skills": "Repair", "availability": "2024-06-17:2024-06-24", "location": "Uptown"},
]

for d in dummies:
    user, error = create_user(d["username"], d["password"], d["skills"], d["availability"], d["location"])
    if user:
        print(f"Created user: {d['username']} - {d['skills']}")
    else:
        print(f"Failed to create user {d['username']}: {error}") 