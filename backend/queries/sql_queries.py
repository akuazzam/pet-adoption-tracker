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
