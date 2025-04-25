# backend/functions/core_create.py

from queries.sql_queries import (
    insert_user_sql,
    insert_pet_sql,
    insert_shelter_sql,
    insert_adoption_sql
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


def create_user(user_id, name, email, password_hash, role):
    """Create user in both PostgreSQL and Neo4j."""
    insert_user_sql(user_id, name, email, password_hash, role)  # PostgreSQL
    create_user_neo4j(user_id, name)                            # Neo4j


def create_pet(pet_id, name, breed, gender, age, type_, shelter_id, status):
    """Create pet in PostgreSQL and sync it with Neo4j."""
    insert_pet_sql(pet_id, name, breed, gender, age, type_, shelter_id, status)  # SQL
    create_pet_neo4j(pet_id, name)                                               # Graph
    if breed:
        create_breed(breed)
        link_pet_to_breed(pet_id, breed)
    if shelter_id:
        link_pet_to_shelter(pet_id, shelter_id)


def create_shelter(shelter_id, name, address, phone_number, capacity):
    """Create shelter in PostgreSQL and Neo4j."""
    insert_shelter_sql(shelter_id, name, address, phone_number, capacity)  # SQL
    create_shelter_neo4j(shelter_id, name)                                  # Graph


def create_adoption(adoption_id, user_id, pet_id, adoption_date, success_notes):
    """Create adoption record and corresponding Neo4j edge."""
    insert_adoption_sql(adoption_id, user_id, pet_id, adoption_date, success_notes)  # SQL
    create_adopted_relationship(user_id, pet_id)                                     # Graph