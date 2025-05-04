# backend/queries/sql_queries.py

import psycopg2
from psycopg2.extras import RealDictCursor
import os

from dotenv import load_dotenv

load_dotenv() 



DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")



def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        cursor_factory=RealDictCursor
    )

# ---------- USERS ----------
def add_user(name, email, password_hash, role):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (name, email, password_hash, role)
                VALUES (%s, %s, %s, %s)
                RETURNING *;
            """, (name, email, password_hash, role))
            return cur.fetchone()

# ---------- SHELTERS ----------
def add_shelter(name, address, phone_number, capacity):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO shelters (name, address, phone_number, capacity)
                VALUES (%s, %s, %s, %s)
                RETURNING *;
            """, (name, address, phone_number, capacity))
            return cur.fetchone()

# ---------- PETS ----------
def add_pet(name, age, type_, breed, gender, shelter_id, status="available"):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO pets (name, age, type, breed, gender, shelter_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING *;
            """, (name, age, type_, breed, gender, shelter_id, status))
            return cur.fetchone()

# ---------- ADOPTIONS ----------
def add_adoption(user_id, pet_id, success_notes=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO adoptions (user_id, pet_id, success_notes)
                VALUES (%s, %s, %s)
                RETURNING *;
            """, (user_id, pet_id, success_notes))
            return cur.fetchone()

# ---------- STAFF ----------
def add_staff(name, email, role, shelter_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO staff (name, email, role, shelter_id)
                VALUES (%s, %s, %s, %s)
                RETURNING *;
            """, (name, email, role, shelter_id))
            return cur.fetchone()

# ---------- FOLLOW UPS ----------
def add_follow_up(adoption_id, visit_date, notes=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO follow_ups (adoption_id, visit_date, notes)
                VALUES (%s, %s, %s)
                RETURNING *;
            """, (adoption_id, visit_date, notes))
            return cur.fetchone()

# ---------- Raw Queries --------

def get_pets_by_ids(pet_ids):
    """
    Fetch basic pet details for the given list of pet IDs,
    but only those still marked 'available'.
    Returns a list of dicts.
    """
    if not pet_ids:
        return []

    query = """
        SELECT id, name, type, breed, gender, status
        FROM pets
        WHERE id = ANY(%s)
          AND status = 'available';
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (pet_ids,))
            return cur.fetchall()
    
def get_user_by_id(user_id):
    """
    Fetch a single user record by its ID.
    Returns a dict with keys: id, name, email, password_hash, role.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT name
                FROM users
                WHERE id = %s;
            """, (user_id,))
            return cur.fetchone()

def get_available_pet_ids():
    """
    Fetch all pet IDs where status is 'available'.
    Returns a list of integers.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id
                  FROM pets
                 WHERE status = 'available';
            """)
            rows = cur.fetchall()
            # Each row is a dict like {'id': 42}, so extract the values:
            return [row['id'] for row in rows]
        
def get_shared_adoption_counts(user_id: int) -> dict[int,int]:
    """
    other_user_id -> number of pets both users have ADOPTED
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT a2.user_id   AS other_id,
                       COUNT(*)      AS shared_count
                  FROM adoptions a1
                  JOIN adoptions a2
                    ON a1.pet_id = a2.pet_id
                 WHERE a1.user_id = %s
                   AND a2.user_id <> %s
              GROUP BY a2.user_id;
            """, (user_id, user_id))
            rows = cur.fetchall()
    return {r["other_id"]: r["shared_count"] for r in rows}

def get_adoption_count_for_user(user_id: int) -> int:
    """
    Return how many adoptions this user has made.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) AS cnt FROM adoptions WHERE user_id = %s",
                (user_id,)
            )
            row = cur.fetchone()
    return row["cnt"] if row else 0

def get_available_pets_count_by_breed() -> dict[str,int]:
    """
    Returns a map: breed -> number of pets currently available in SQL.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT breed, COUNT(*) AS supply_count
                  FROM pets
                 WHERE status = 'available'
                 GROUP BY breed;
            """)
            rows = cur.fetchall()
    return {r["breed"]: r["supply_count"] for r in rows}


