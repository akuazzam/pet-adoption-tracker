"""
High-Level Business Logic for Pet-Adoption Tracker.
This module orchestrates cross-database queries using the raw data-access
functions defined in the `queries/` folder.
"""
from queries.graph_queries import (
    get_preferred_tags as _get_preferred_tags,
    get_interacted_pet_ids as _get_interacted_pet_ids,
    get_pet_like_counts,
    get_adopted_pet_ids,
    get_shared_like_counts,
    get_unliked_pet_ids,
    get_shared_preference_tag_counts,
    get_like_count_for_user,
    get_like_counts_by_breed,
    get_like_counts_by_tag
)
from queries.mongo_db_queries import (
    find_pets_by_tags,
    get_average_rating_for_pet,
    get_average_ratings_for_all_pets, 
    pet_profiles,
    get_shared_feedback_counts,
    get_reviewed_pet_ids,
    get_feedback_count_for_user,
    get_supply_counts_by_tag
)
                                      
from queries.sql_queries import (
    get_pets_by_ids,
    get_user_by_id,
    get_available_pet_ids,
    get_shared_adoption_counts,
    get_adoption_count_for_user,
    get_available_pets_count_by_breed
) 
import os

def get_top_recommended_pets_for_user(user_id, top_n = 5):
    """
    Recommend up to `top_n` available pets for a given user based on their
    preferred tags and excluding pets they already liked or adopted.
    Workflow:
      1. Fetch user's preferred tags from Neo4j.
      2. Fetch pet IDs user has already interacted with (LIKES or ADOPTED).
      3. Query MongoDB for pets matching those tags (raw profile lookup).
      4. Score and sort pets by tag overlap (in Python).
      5. Fetch final pet details from PostgreSQL for those top IDs.
    """
    user = get_user_by_id(user_id)
    if not user:
        return None
    # 1. Tags the user prefers
    preferred_tags = _get_preferred_tags(user_id)
    # 2. Pet IDs the user has liked or adopted already
    excluded_ids = _get_interacted_pet_ids(user_id)
    
    adopted_ids = set(get_adopted_pet_ids(user_id))

    matching_profiles = find_pets_by_tags(preferred_tags)

    # 4. Score by overlap, exclude seen pets
    scored = []
    for profile in matching_profiles:
        pid = profile['pet_id']
        if pid in adopted_ids:
            continue
        overlap = len(set(profile.get('tags', [])) & set(preferred_tags))
        scored.append((overlap, pid))
    scored.sort(key=lambda x: -x[0])
    top_ids = [pid for _, pid in scored[:top_n]]

    # 5. Get full pet details from SQL
    return get_pets_by_ids(top_ids)



def get_most_adoptable_pet_profiles(top_n):
    """
    Rank and return up to top_n pets that are most "attractive" based on:
      - Number of likes (Neo4j)
      - High average feedback rating (MongoDB)
      - Currently available (PostgreSQL)
    """
    # 1. Get all available pet IDs
    available_ids = get_available_pet_ids()

    # 2. Get like counts and average ratings
    like_counts = {d['pet_id']: d['like_count'] for d in get_pet_like_counts()}
    avg_ratings = get_average_ratings_for_all_pets()

    # 3. Compute a simple composite score: like_count + avg_rating
    scores = []
    for pid in available_ids:
        score = like_counts.get(pid, 0) + avg_ratings.get(pid, 0)
        scores.append((score, pid))

    # 4. Sort and pick top_n
    scores.sort(key=lambda x: -x[0])
    top_ids = [pid for _, pid in scores[:top_n]]

    # 5. Fetch full pet details
    return get_pets_by_ids(top_ids)

def get_top_crossdb_user_connections(user_id, top_n):
    # 0. validate user
    base = get_user_by_id(user_id)
    if not base:
        return None

    # 1. pull all four similarity maps
    likes_map     = get_shared_like_counts(user_id)
    tag_pref_map  = get_shared_preference_tag_counts(user_id)
    adopted_map   = get_shared_adoption_counts(user_id)
    feedback_map  = get_shared_feedback_counts(user_id)

    # 2. aggregate into a single score
    scores = {}
    for similarity_map in (likes_map, tag_pref_map, adopted_map, feedback_map):
        for other_id, cnt in similarity_map.items():
            scores[other_id] = scores.get(other_id, 0) + cnt

    if not scores:
        return []

    # 3. rank and pick top_n
    top_ids = sorted(scores, key=lambda uid: -scores[uid])[:top_n]

    # 4. fetch their user records
    return [get_user_by_id(uid) for uid in top_ids]

def get_low_engagement_pets_report():
    """
    Find all pets that:
      • have NO LIKES (Neo4j),
      • have NO reviews (MongoDB),
      • have been available > `days` days (PostgreSQL).
    Returns a list of full pet records (dicts) from SQL.
    """
    # 1. Pets nobody's liked
    unliked = set(get_unliked_pet_ids())

    # 2. Pets with no user_feedback
    reviewed = set(get_reviewed_pet_ids())

    # 3. Pets still available and older than `days`
    available = set(get_available_pet_ids())

    # 4. Intersection: unliked ∩ old_available ∖ reviewed
    low_ids = sorted(unliked & available  - reviewed)
    if not low_ids:
        return []

    # 5. Fetch detailed rows from SQL
    return get_pets_by_ids(low_ids)

def get_user_engagement_report(user_id: int) -> dict | None:
    """
    Return a summary of this user’s engagement:
      - number of pets they’ve liked
      - number of feedback posts they’ve made
      - number of adoptions they’ve completed

    Returns None if the user doesn’t exist.
    """
    user = get_user_by_id(user_id)
    if not user:
        return None

    return {
        "user_id":    user_id,
        "name":       user["name"],
        "likes":      get_like_count_for_user(user_id),
        "feedbacks":  get_feedback_count_for_user(user_id),
        "adoptions":  get_adoption_count_for_user(user_id),
    }

def forecast_pet_demand_by_breed_or_tag() -> dict:
    """
    Predict demand vs. supply for each breed and each tag:
      • demand = total LIKES (graph)
      • supply = available pets (SQL for breeds, Mongo for tags)
    Returns:
    {
      "by_breed": { breed: {demand: int, supply: int, ratio: float}, … },
      "by_tag":   {  tag: {demand: int, supply: int, ratio: float}, … }
    }
    """
    # --- demand side ---
    likes_breed = get_like_counts_by_breed()
    likes_tag   = get_like_counts_by_tag()

    # --- supply side ---
    supply_breed = get_available_pets_count_by_breed()
    supply_tag   = get_supply_counts_by_tag()

    # --- merge into a forecast report ---
    report = {"by_breed": {}, "by_tag": {}}

    # breeds
    all_breeds = set(likes_breed) | set(supply_breed)
    for breed in all_breeds:
        d = likes_breed.get(breed, 0)
        s = supply_breed.get(breed, 0)
        ratio = (d / s) if s else None
        report["by_breed"][breed] = {"demand": d, "supply": s, "ratio": ratio}

    # tags
    all_tags = set(likes_tag) | set(supply_tag)
    for tag in all_tags:
        d = likes_tag.get(tag, 0)
        s = supply_tag.get(tag, 0)
        ratio = (d / s) if s else None
        report["by_tag"][tag] = {"demand": d, "supply": s, "ratio": ratio}

    return report