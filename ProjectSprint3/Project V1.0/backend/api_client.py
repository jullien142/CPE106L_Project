import requests

API_URL = "http://localhost:8000"

def signup(username, email, password, skill, location):
    resp = requests.post(f"{API_URL}/signup", json={"username": username, "email": email, "password": password, "skill": skill, "location": location})
    resp.raise_for_status()
    return resp.json()

def login(username, password):
    resp = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
    resp.raise_for_status()
    return resp.json()

def create_request(requester_id, skill):
    resp = requests.post(f"{API_URL}/request", params={"requester_id": requester_id, "skill": skill})
    resp.raise_for_status()
    return resp.json()

def run_matching(request_id):
    resp = requests.post(f"{API_URL}/match", params={"request_id": request_id})
    resp.raise_for_status()
    return resp.json()

def accept_match(request_id, helper_id):
    resp = requests.post(f"{API_URL}/accept", params={"request_id": request_id, "helper_id": helper_id})
    resp.raise_for_status()
    return resp.json()

def complete_session(request_id, rating=None):
    params = {"request_id": request_id}
    if rating is not None:
        params["rating"] = rating
    resp = requests.post(f"{API_URL}/complete", params=params)
    resp.raise_for_status()
    return resp.json()

def cancel(request_id):
    resp = requests.post(f"{API_URL}/cancel", params={"request_id": request_id})
    resp.raise_for_status()
    return resp.json()

def get_history(user_id):
    resp = requests.get(f"{API_URL}/history", params={"user_id": user_id})
    resp.raise_for_status()
    return resp.json()

def get_analytics():
    resp = requests.get(f"{API_URL}/analytics")
    resp.raise_for_status()
    return resp.json()

def change_skill(user_id, new_skill):
    resp = requests.post(f"{API_URL}/change_skill", json={"user_id": user_id, "new_skill": new_skill})
    resp.raise_for_status()
    return resp.json() 