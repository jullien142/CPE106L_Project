from community_skill_exchange.models import Skill
from community_skill_exchange.database import SessionLocal

skills = [
    "Cooking", "Cleaning", "Gardening", "Driving", "Teaching", "Tutoring", 
    "Repair", "Painting", "Photography", "Music", "Writing", "Translation",
    "Childcare", "Elderly Care", "Pet Care", "Computer Help", "Math", "Science",
    "Language Learning", "Fitness Training", "Yoga", "Meditation", "Art", "Crafting",
    "Sewing", "Knitting", "Woodworking", "Plumbing", "Electrical Work", "Carpentry",
    "Car Maintenance", "Bike Repair", "Hair Styling", "Makeup", "Massage", "Therapy",
    "Legal Advice", "Financial Planning", "Tax Help", "Resume Writing", "Interview Prep",
    "Event Planning", "Catering", "Baking", "Interior Design", "Landscaping",
    "House Sitting", "Pet Sitting", "Dog Walking", "Plant Care", "Aquarium Care"
]

session = SessionLocal()
for name in skills:
    if not session.query(Skill).filter_by(name=name).first():
        session.add(Skill(name=name))
session.commit()
session.close()
print("General skills added to the database.") 