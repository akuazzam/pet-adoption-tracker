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


def create_pet(pet_id, name, breed=None):
    with driver.session() as session:
        session.run("""
            MERGE (p:Pet {id: $pet_id})
            SET p.name = $name
            """ + (", p.breed = $breed" if breed is not None else ""),
            pet_id=pet_id, name=name, breed=breed
        )

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

def get_preferred_tags(user_id):
    """
    Return a list of tag names the user has expressed a preference for.
    """
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $user_id})-[:PREFERS_TAG]->(t:Tag)
            RETURN t.name AS tag
            """,
            user_id=user_id
        )
        return [record["tag"] for record in result]

def get_interacted_pet_ids(user_id):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $user_id})-[r]->(p:Pet)
            WHERE type(r) IN ['LIKES', 'ADOPTED']
            RETURN DISTINCT p.id AS pet_id
            """,
            user_id=user_id
        )
        return [record["pet_id"] for record in result]

def get_pet_like_counts(limit=None):
    """
    Return a list of dicts {'pet_id': int, 'like_count': int},
    sorted by like_count descending. Optionally limit the number of results.
    """
    with driver.session() as session:
        if limit:
            result = session.run(
                """
                MATCH (:User)-[:LIKES]->(p:Pet)
                RETURN p.id AS pet_id, count(*) AS like_count
                ORDER BY like_count DESC
                LIMIT $limit
                """,
                limit=limit
            )
        else:
            result = session.run(
                """
                MATCH (:User)-[:LIKES]->(p:Pet)
                RETURN p.id AS pet_id, count(*) AS like_count
                ORDER BY like_count DESC
                """
            )
        return [ { 'pet_id': record['pet_id'], 'like_count': record['like_count'] } for record in result ]

def get_adopted_pet_ids(user_id):
    """
    Return all pet IDs the user has adopted.
    """
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $user_id})-[:ADOPTED]->(p:Pet)
            RETURN p.id AS pet_id
            """,
            user_id=user_id
        )
        return [record["pet_id"] for record in result]

def get_shared_like_counts(user_id: int) -> dict[int,int]:
    """
    other_user_id -> number of pets both have LIKED.
    """
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $uid})-[:LIKES]->(p:Pet)<-[:LIKES]-(o:User)
            RETURN o.id AS other_id, count(p) AS shared_count
            """,
            uid=user_id
        )
        records = list(result)   # materialize here
    return {r["other_id"]: r["shared_count"] for r in records}

def get_shared_adoption_shelter_counts(user_id: int) -> dict[int,int]:
    """
    Returns a map: other_user_id -> number of shelters both have adopted from.
    """
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $uid})-[:ADOPTED]->(:Pet)-[:LOCATED_AT]->(s:Shelter)
                  ,(o:User)-[:ADOPTED]->(:Pet)-[:LOCATED_AT]->(s)
            RETURN o.id AS other_id, count(DISTINCT s) AS shared_count
            """, uid=user_id
        )
    return {r["other_id"]: r["shared_count"] for r in result}

def get_shared_preference_tag_counts(user_id: int) -> dict[int,int]:
    """
    other_user_id -> number of tags both users prefer.
    """
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $uid})-[:PREFERS_TAG]->(t:Tag)<-[:PREFERS_TAG]-(o:User)
            RETURN o.id AS other_id, count(t) AS shared_count
            """,
            uid=user_id
        )
        records = list(result)   # materialize here
    return {r["other_id"]: r["shared_count"] for r in records}

def get_unliked_pet_ids() -> list[int]:
    """
    Return IDs of all Pet nodes with NO incoming LIKES edges.
    """
    with driver.session() as session:
        result = session.run(
            """
            MATCH (p:Pet)
            WHERE NOT ( ()-[:LIKES]->(p) )
            RETURN p.id AS pet_id
            """
        )
        records = list(result)
    return [r["pet_id"] for r in records]

def get_like_count_for_user(user_id: int) -> int:
    """
    Return the number of :LIKES edges this user has made.
    """
    with driver.session() as session:
        result = session.run(
            """
            MATCH (:User {id: $uid})-[r:LIKES]->(:Pet)
            RETURN count(r) AS like_count
            """,
            uid=user_id
        )
        record = result.single()
    return record["like_count"] if record else 0

def get_like_counts_by_breed() -> dict[str,int]:
    """
    Returns a map: breed_name -> total number of LIKES on pets of that breed,
    based on the `breed` property on Pet nodes rather than a separate label.
    """
    with driver.session() as session:
        result = session.run(
            """
            MATCH (:User)-[:LIKES]->(p:Pet)
            RETURN p.breed AS breed, count(*) AS like_count
            """
        )
        records = list(result)
    return {r["breed"]: r["like_count"] for r in records}


def get_like_counts_by_tag() -> dict[str,int]:
    """
    Returns a map: tag_name -> total number of LIKES on pets carrying that tag.
    """
    with driver.session() as session:
        result = session.run(
            """
            MATCH (:User)-[:LIKES]->(p:Pet)-[:HAS_TAG]->(t:Tag)
            RETURN t.name AS tag, count(*) AS like_count
            """
        )
        records = list(result)
    return {r["tag"]: r["like_count"] for r in records}

