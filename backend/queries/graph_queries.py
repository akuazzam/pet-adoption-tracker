from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASS"))
)

def create_user(user_id, name):
    with driver.session() as session:
        session.run("""
            MERGE (u:User {id: $user_id})
            SET u.name = $name
        """, user_id=user_id, name=name)


def create_pet(pet_id, name):
    with driver.session() as session:
        session.run("""
            MERGE (p:Pet {id: $pet_id})
            SET p.name = $name
        """, pet_id=pet_id, name=name)

def create_breed(breed_name):
    with driver.session() as session:
        session.run("""
            MERGE (:Breed {name: $breed_name})
        """, breed_name=breed_name)

def link_pet_to_breed(pet_id, breed_name):
    with driver.session() as session:
        session.run("""
            MATCH (p:Pet {id: $pet_id})
            MERGE (b:Breed {name: $breed_name})
            MERGE (p)-[:OF_BREED]->(b)
        """, pet_id=pet_id, breed_name=breed_name)

def create_shelter(shelter_id, name):
    with driver.session() as session:
        session.run("""
            MERGE (s:Shelter {id: $shelter_id})
            SET s.name = $name
        """, shelter_id=shelter_id, name=name)

def link_pet_to_shelter(pet_id, shelter_id):
    with driver.session() as session:
        session.run("""
            MATCH (p:Pet {id: $pet_id}), (s:Shelter {id: $shelter_id})
            MERGE (p)-[:LOCATED_AT]->(s)
        """, pet_id=pet_id, shelter_id=shelter_id)

def create_adopted_relationship(user_id, pet_id):
    with driver.session() as session:
        session.run("""
            MATCH (u:User {id: $user_id}), (p:Pet {id: $pet_id})
            MERGE (u)-[:ADOPTED]->(p)
        """, user_id=user_id, pet_id=pet_id)

def create_likes_edge(user_id, pet_id):
    with driver.session() as session:
        session.run("""
            MATCH (u:User {id: $user_id}), (p:Pet {id: $pet_id})
            MERGE (u)-[:LIKES]->(p)
        """, user_id=user_id, pet_id=pet_id)

def create_friend_edge(user_id1, user_id2):
    with driver.session() as session:
        session.run("""
            MATCH (u1:User {id: $user_id1}), (u2:User {id: $user_id2})
            MERGE (u1)-[:FRIEND_OF]->(u2)
            MERGE (u2)-[:FRIEND_OF]->(u1)
        """, user_id1=user_id1, user_id2=user_id2)

def create_tag(tag_name):
    with driver.session() as session:
        session.run("""
            MERGE (:Tag {name: $tag_name})
        """, tag_name=tag_name)

def link_pet_to_tag(pet_id, tag_name):
    with driver.session() as session:
        session.run("""
            MATCH (p:Pet {id: $pet_id})
            MERGE (t:Tag {name: $tag_name})
            MERGE (p)-[:HAS_TAG]->(t)
        """, pet_id=pet_id, tag_name=tag_name)

def link_user_to_preference_tag(user_id, tag_name):
    with driver.session() as session:
        session.run("""
            MATCH (u:User {id: $user_id})
            MERGE (t:Tag {name: $tag_name})
            MERGE (u)-[:PREFERS_TAG]->(t)
        """, user_id=user_id, tag_name=tag_name)

def link_breeds_as_similar(breed1, breed2):
    with driver.session() as session:
        session.run("""
            MERGE (b1:Breed {name: $breed1})
            MERGE (b2:Breed {name: $breed2})
            MERGE (b1)-[:SIMILAR_BREED]->(b2)
            MERGE (b2)-[:SIMILAR_BREED]->(b1)
        """, breed1=breed1, breed2=breed2)
