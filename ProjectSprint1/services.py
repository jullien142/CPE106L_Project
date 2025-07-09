from typing import Any
from models import Location
import math
import random

class GeoService:
    @staticmethod
    def calculate_distance(loc1: Location, loc2: Location) -> float:
        # Euclidean distance for now
        dx = loc1.x - loc2.x
        dy = loc1.y - loc2.y
        return math.sqrt(dx*dx + dy*dy)

class DatabaseService:
    @staticmethod
    def save_user(user: Any):
        print(f"[DB] Saving user: {user.name}")

    @staticmethod
    def load_requests():
        print("[DB] Loading requests...")
        return []

    @staticmethod
    def save_request(request: Any):
        print(f"[DB] Saving request for: {request.requester.name}")

class VisualizationService:
    @staticmethod
    def generate_metrics(users, matches, requests):
        print(f"[Viz] Users: {len(users)}, Matches: {len(matches)}, Requests: {len(requests)}") 