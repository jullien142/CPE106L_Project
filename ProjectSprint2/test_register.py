from community_skill_exchange.controllers import create_user

user, error = create_user(
    username="testuser",
    password="testpass",
    skills="Python,SQL",
    availability="2024-06-01",
    location="Test City"
)

if user:
    print("Registration successful!")
else:
    print(f"Registration failed: {error}") 