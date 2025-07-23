from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DATABASE_URL = f"sqlite:///{BASE_DIR}/community_skills.db"

# Security
SECRET_KEY = "your-secret-key-here"  # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Google Maps API
GOOGLE_MAPS_API_KEY = "AIzaSyD5g6qxHvknc__zPkH5xqUZ6h2dcJ32rVI"

# Available Skills
AVAILABLE_SKILLS = [
    "Mathematics Tutoring",
    "Physics Tutoring",
    "Chemistry Tutoring",
    "Programming",
    "Web Development",
    "Mobile App Development",
    "Plumbing",
    "Electrical Work",
    "Carpentry",
    "Painting",
    "Gardening",
    "Music Lessons",
    "Language Teaching",
    "Cooking Classes",
    "Fitness Training",
    "Photography",
    "Graphic Design",
    "Writing & Editing",
    "Financial Planning",
    "Car Mechanics"
]

# Maximum skills per user
MAX_SKILLS = 3 