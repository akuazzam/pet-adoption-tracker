import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from queries.sql_queries import get_available_pet_ids

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

def find_pets_by_tags(tag_list):
    result =  list(pet_profiles.find({
        "tags": {"$in": tag_list}
    }))
    return result

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

def get_all_unique_tags():
    return pet_profiles.distinct("tags")

def get_liked_tags_by_user(user_id, min_rating=4):
    feedback = user_feedback.find({"user_id": user_id, "rating": {"$gte": min_rating}})
    liked_pet_ids = [fb["pet_id"] for fb in feedback]
    if not liked_pet_ids:
        return []

    return pet_profiles.distinct("tags", {"pet_id": {"$in": liked_pet_ids}})

def add_image_to_pet_gallery(pet_id, image_url):
    return pet_profiles.update_one(
        {"pet_id": pet_id},
        {"$push": {"gallery": image_url}}
    )

def get_average_rating_for_pet(pet_id):
    pipeline = [
        {"$match": {"pet_id": pet_id}},
        {"$group": {"_id": "$pet_id", "avg_rating": {"$avg": "$rating"}}}
    ]
    result = list(user_feedback.aggregate(pipeline))
    return result[0]["avg_rating"] if result else None

def get_average_ratings_for_all_pets():
    """
    Returns a dict mapping pet_id -> average rating for every pet
    in the user_feedback collection.
    """
    pipeline = [
        {"$group": {"_id": "$pet_id", "avg_rating": {"$avg": "$rating"}}}
    ]
    result = user_feedback.aggregate(pipeline)
    return {doc["_id"]: doc["avg_rating"] for doc in result}

def get_shared_feedback_counts(user_id: int) -> dict[int,int]:
    """
    other_user_id -> number of pets both users have left feedback for
    """
    # 1. find all pet_ids this user has feedback on
    own = user_feedback.find({"user_id": user_id}, {"pet_id": 1})
    pet_ids = [doc["pet_id"] for doc in own]
    if not pet_ids:
        return {}

    # 2. group by other user where pet_id in that list
    pipeline = [
        {"$match": {
            "user_id": {"$ne": user_id},
            "pet_id":   {"$in": pet_ids}
        }},
        {"$group": {
            "_id":   "$user_id",
            "count": {"$sum": 1}
        }}
    ]
    result = user_feedback.aggregate(pipeline)
    return {doc["_id"]: doc["count"] for doc in result}

def get_reviewed_pet_ids() -> list[int]:
    """
    Return all pet_ids that appear in user_feedback (i.e. have at least one review).
    """
    return user_feedback.distinct("pet_id")

def get_feedback_count_for_user(user_id: int) -> int:
    """
    Return how many feedback docs this user has submitted.
    """
    return user_feedback.count_documents({"user_id": user_id})

def get_supply_counts_by_tag() -> dict[str,int]:
    """
    Returns a map: tag -> number of available pets carrying that tag.
    """
    avail_ids = get_available_pet_ids()
    if not avail_ids:
        return {}

    pipeline = [
        {"$match": {"pet_id": {"$in": avail_ids}}},
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}}
    ]
    result = pet_profiles.aggregate(pipeline)
    return {doc["_id"]: doc["count"] for doc in result}
