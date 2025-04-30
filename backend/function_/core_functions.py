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
    create_adopted_relationship
)


def create_user(name, email, password_hash, role):
    """Create user in both PostgreSQL and Neo4j."""
    user = add_user(name, email, password_hash, role)  # PostgreSQL
    create_user_neo4j(user['id'], name)                # Neo4j
    return user


def create_pet(name, age, type_, breed, gender, shelter_id, status="available"):
    """Create pet in PostgreSQL and sync it with Neo4j."""
    pet = add_pet(name, age, type_, breed, gender, shelter_id, status)  # SQL
    create_pet_neo4j(pet['id'], name)                                   # Graph
    if breed:
        create_breed(breed)
        link_pet_to_breed(pet['id'], breed)
    if shelter_id:
        link_pet_to_shelter(pet['id'], shelter_id)
    return pet


def create_shelter(name, address, phone_number, capacity):
    """Create shelter in PostgreSQL and Neo4j."""
    shelter = add_shelter(name, address, phone_number, capacity)  # SQL
    create_shelter_neo4j(shelter['id'], name)                     # Graph
    return shelter


def create_adoption(user_id, pet_id, success_notes=None):
    """Create adoption record and corresponding Neo4j edge."""
    adoption = add_adoption(user_id, pet_id, success_notes)       # SQL
    create_adopted_relationship(user_id, pet_id)                  # Graph
    return adoption