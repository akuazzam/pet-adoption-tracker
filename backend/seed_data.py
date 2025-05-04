from faker import Faker
import random
from queries.sql_queries import add_user, add_shelter, add_pet, add_adoption
from queries.mongo_db_queries import insert_pet_profile, insert_user_feedback, insert_follow_up_report
from queries.mongo_db_queries import pet_profiles
from queries.graph_queries import (
    create_user as create_user_neo4j,
    create_pet as create_pet_neo4j,
    create_shelter as create_shelter_neo4j,
    link_pet_to_shelter,
    create_adopted_relationship,
    create_tag,
    link_pet_to_tag,
    link_user_to_preference_tag,
    create_likes_edge,
    create_friend_edge
)

fake = Faker()

# Expanded tag pool
tags_pool = ["good_with_kids", "calm", "energetic", "hypoallergenic", "low_shedding", "independent", "playful"]

# Pet types and breeds
pet_types = ["dog", "cat", "rabbit", "parrot", "hamster", "fish", "turtle"]
breeds_by_type = {
    "dog": ["Golden Retriever", "Poodle", "Bulldog", "Beagle", "Shih Tzu"],
    "cat": ["Siamese", "Maine Coon", "Persian", "Ragdoll", "Bengal"],
    "rabbit": ["Lionhead", "Dutch", "Mini Lop", "Flemish Giant", "Holland Lop"],
    "parrot": ["Macaw", "Cockatiel", "Budgie", "African Grey", "Amazon"],
    "hamster": ["Syrian", "Dwarf", "Chinese", "Campbell's", "Roborovski"],
    "fish": ["Betta", "Goldfish", "Angelfish", "Guppy", "Molly"],
    "turtle": ["Red-Eared Slider", "Box Turtle", "Snapping Turtle", "Painted Turtle", "Musk Turtle"]
}

# Predefined list of 100 pet names
pet_name_pool = [
    "FluffyPaws", "TinyWhiskers", "HappyTail", "SleepyNose", "BouncyBean", "LazyBark", "SassyMeow", "ChubbyFang", "WigglyClaw", "PlayfulStripe",
    "CleverSpot", "LoyalToes", "SpeedyEars", "ZippyFur", "BraveBounce", "ShySnout", "CurlyShadow", "GoofySniff", "FurryMittens", "CuddlySpark",
    "FuzzyWhiskers", "HappyPaws", "SnugglyFur", "SpeedyTail", "TinyToes", "ShadowPaws", "FluffyEars", "ZippyBark", "ChillBean", "SpunkyNose",
    "GoofyClaw", "LoyalFur", "BouncySnout", "FierceWhiskers", "GentleEars", "BoldTail", "SoftPaws", "ShinyNose", "TinyMittens", "SnappySpot",
    "CurlyBounce", "TidyFur", "DizzyShadow", "NimbleWhiskers", "QuietPaws", "GiddyTail", "SleepyBean", "FurryClaw", "WildMeow", "ZanyBark",
    "FriendlyToes", "CuriousEars", "PeppySnout", "CozyStripe", "DashingFur", "PlayfulPaws", "SillyShadow", "JoyfulNose", "MellowMeow", "PerkyFang",
    "MuddyClaw", "DustyBean", "PatchyTail", "SniffyEars", "BravePaws", "CloudyFur", "GentleToes", "PeppyMittens", "ProudStripe", "TwitchyClaw",
    "QuirkySnout", "TidyTail", "PerkyNose", "CleverWhiskers", "CrispyBounce", "SleepyFur", "DrowsyToes", "SlinkyEars", "SoftSniff", "LushWhiskers",
    "BreezyTail", "FloppyFur", "TiredPaws", "QuietBounce", "NoisyMittens", "SassySnout", "PlayfulToes", "CozyBark", "WhiskeryShadow", "FeistyFang",
    "ZippyNose", "BouncyMittens", "CleverClaw", "LoyalStripe", "ChillEars", "FurryWhiskers", "JumpyPaws", "PurringBean", "JoyfulTail", "GiddyFur"
]
users = []
shelters = []
pets = []

# Create 5 shelters
for _ in range(5):
    shelter = add_shelter(
        name=fake.company(),
        address=fake.address(),
        phone_number=fake.phone_number(),
        capacity=random.randint(20, 50)
    )
    create_shelter_neo4j(shelter['id'], shelter['name'])
    shelters.append(shelter)

# Create 50 users
for _ in range(50):
    first_name = fake.first_name()
    last_name = fake.last_name()
    user = add_user(
        name=f"{first_name} {last_name}",
        email=fake.email(),
        password_hash="hashed_pw",
        role="adopter"
    )
    create_user_neo4j(user['id'], user['name'])
    users.append(user)
# ── Give every user 1–3 random preference tags ─────────────────────────
for user in users:
    # pick between 1 and 3 tags from your tags_pool
    pref_tags = random.sample(tags_pool, k=random.randint(1, 3))
    for tag in pref_tags:
        # make sure the tag node exists
        create_tag(tag)
        # link the user to that tag
        link_user_to_preference_tag(user['id'], tag)
        
# Create 100 pets
for i in range(100):
    shelter = random.choice(shelters)
    pet_type = random.choice(pet_types)
    breed = random.choice(breeds_by_type[pet_type])
    tag_sample = random.sample(tags_pool, k=2)

    pet = add_pet(
        name=pet_name_pool[i],
        age=random.randint(1, 10),
        type_=pet_type,
        breed=breed,
        gender=random.choice(["Male", "Female"]),
        shelter_id=shelter['id'],
        status="available"
    )
    create_pet_neo4j(pet['id'], pet['name'], pet['breed'])
    link_pet_to_shelter(pet['id'], shelter['id'])
    pets.append(pet)

    insert_pet_profile(
        pet_id=pet['id'],
        gallery=[fake.image_url(), fake.image_url()],
        tags=tag_sample,
        health_history=[{"vaccine": "Rabies", "date": "2024-01-01"}],
        behavior_notes=fake.sentence(),
        dietary_needs="Grain-free"
    )

    for tag in tag_sample:
        create_tag(tag)
        link_pet_to_tag(pet['id'], tag)

# ── Seed some LIKES ────────────────────────────────────────────────────
for user in users:
    # each user likes between 3 and 10 random pets
    liked = random.sample(pets, k=random.randint(3,10))
    for pet in liked:
        create_likes_edge(user['id'], pet['id'])

# ── Seed some FRIEND_OF edges ─────────────────────────────────────────
for user in users:
    # connect each user to 2–5 random friends
    friends = random.sample([u for u in users if u != user], k=random.randint(2,5))
    for fr in friends:
        create_friend_edge(user['id'], fr['id'])


# Create 35 adoptions
adoptions = []
for _ in range(35):
    user = random.choice(users)
    pet  = random.choice(pets)
    adoption = add_adoption(user['id'], pet['id'], success_notes="Successful match!")
    adoptions.append(adoption)
    create_adopted_relationship(user['id'], pet['id'])

    # Mongo feedback
    insert_user_feedback(user['id'], pet['id'], "Loved the pet!", random.randint(4,5))
    # Link real pet tags
    profile = pet_profiles.find_one({"pet_id": pet['id']})
    for tag in profile.get("tags", []):
        if random.random() < 0.5:
            link_user_to_preference_tag(user['id'], tag)

# ── 5) Follow-up reports ────────────────────────────────────
from datetime import timedelta
for adoption in adoptions:
    for i in range(random.randint(1,3)):
            visit = adoption['adoption_date'] + timedelta(days=7*(i+1))
            insert_follow_up_report(
            follow_up_id=f"{adoption['id']}-{i}",
            report_date=visit.isoformat(),
            pet_id=adoption['pet_id'],
            user_id=adoption['user_id'],
            review_text=random.choice([
                "Pet is thriving!","Adjusting well to home","Happy and healthy!"
            ]),
            picture=random.choice([fake.image_url(), None]),
            energy_level=random.choice(["low","medium","high"])
        )

print("✅ Expanded fake data with proper pet names successfully seeded.")
