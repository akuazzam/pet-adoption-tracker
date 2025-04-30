# backend/functions/core_create.py

from queries.sql_queries import (
    add_user,
    add_pet,
    add_shelter,
    add_adoption
)

from queries.graph_queries import (
    create_user as create_user_neo4j,
    create_pet as create_pet_neo4j,
    create_shelter as create_shelter_neo4j,
    create_breed,
    link_pet_to_breed,
    link_pet_to_shelter,
    link_pet_to_tag,
    create_adopted_relationship,
    link_user_to_preference_tag
)

from queries.mongo_db_queries import (
    insert_pet_profile,
    insert_user_feedback,
    get_liked_tags_by_user
)


def create_user(name, email, password_hash, role):
    """Create user in both PostgreSQL and Neo4j."""
    user = add_user(name, email, password_hash, role)  # PostgreSQL
    create_user_neo4j(user['id'], name)                # Neo4j
    return user


def create_pet(name, age, type_, breed, gender, shelter_id, status="available",
               tags=None, gallery=None, behavior_notes=None, dietary_needs=None, health_history=None):
    """Create pet in PostgreSQL, MongoDB, and Neo4j."""
    pet = add_pet(name, age, type_, breed, gender, shelter_id, status)
    create_pet_neo4j(pet['id'], name)
    
    if breed:
        create_breed(breed)
        link_pet_to_breed(pet['id'], breed)
    if shelter_id:
        link_pet_to_shelter(pet['id'], shelter_id)
    if tags:
        for tag in tags:
            link_pet_to_tag(pet['id'], tag)
    
    insert_pet_profile(
        pet_id=pet['id'],
        gallery=gallery or [],
        tags=tags or [],
        health_history=health_history or [],
        behavior_notes=behavior_notes or "",
        dietary_needs=dietary_needs or ""
    )
    return pet

def create_shelter(name, address, phone_number, capacity):
    """Create shelter in PostgreSQL and Neo4j."""
    shelter = add_shelter(name, address, phone_number, capacity)  # SQL
    create_shelter_neo4j(shelter['id'], name)                     # Graph
    return shelter


def create_adoption(user_id, pet_id, success_notes=None):
    adoption = add_adoption(user_id, pet_id, success_notes)
    create_adopted_relationship(user_id, pet_id)
    
    # Sync tag preferences to Neo4j from MongoDB
    tags = get_liked_tags_by_user(user_id)
    for tag in tags:
        link_user_to_preference_tag(user_id, tag)
    
    return adoption