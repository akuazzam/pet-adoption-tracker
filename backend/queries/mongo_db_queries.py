import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Read from .env
mongo_uri = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client["pet_tracker"]

# Access collections
pet_profiles = db.pet_profiles
user_feedback = db.user_feedback
shelter_reports = db.shelter_reports
follow_up_reports = db.follow_up_reports

if __name__ == "__main__":
    try:
        # Test the connection
        db.command('ping')
        print("Successfully connected to MongoDB!")
        
        # Print database info
        print("\nAvailable collections:", db.list_collection_names())
        
    except Exception as e:
        print("Failed to connect to MongoDB:", e)


#functions to insert data into the database

def insert_pet_profile(pet_id, gallery, tags, health_history, behavior_notes, dietary_needs):
    doc = {
        "pet_id": pet_id,
        "gallery": gallery,
        "tags": tags,
        "healthHistory": health_history,
        "behaviorNotes": behavior_notes,
        "dietaryNeeds": dietary_needs
    }
    return pet_profiles.insert_one(doc)

def find_pets_by_tag(tag):
    return list(pet_profiles.find({"tags": tag}))

def insert_user_feedback(user_id, pet_id, review_text, rating):
    doc = {
        "user_id": user_id,
        "pet_id": pet_id,
        "reviewText": review_text,
        "rating": rating,
        "timestamp": datetime.utcnow().isoformat()
    }
    return user_feedback.insert_one(doc)

def get_feedback_for_pet(pet_id):
    return list(user_feedback.find({"pet_id": pet_id}))

def insert_shelter_report(shelter_id, date, occupancy, notes, intake, adoptions):
    doc = {
        "shelter_id": shelter_id,
        "date": date,
        "occupancy": occupancy,
        "notes": notes,
        "intake": intake,
        "adoptions": adoptions
    }
    return shelter_reports.insert_one(doc)

def get_shelter_reports(shelter_id):
    return list(shelter_reports.find({"shelter_id": shelter_id}))

def insert_follow_up_report(follow_up_id, report_date, pet_id, user_id, review_text, picture, energy_level):
    doc = {
        "follow_up_id": follow_up_id,
        "report_date": report_date,
        "pet_id": pet_id,
        "user_id": user_id,
        "reviewText": review_text,
        "picture": picture,
        "energy_level": energy_level
    }
    return follow_up_reports.insert_one(doc)

def get_follow_ups_for_pet(pet_id):
    return list(follow_up_reports.find({"pet_id": pet_id}))

