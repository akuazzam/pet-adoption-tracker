# 🐾 Pet-Adoption Tracker 

## Overview
The **Pet-Adoption Tracker** is a multi-database application designed to simplify pet adoption processes across multiple shelters under a single organization. The system enables:

- Listing and managing pets available for adoption
- Recording user feedback and follow-up reports post-adoption
- Tracking pet health and behavior
- Enabling tag-based and social recommendations using graph networks

It integrates **three database models**:
- **Relational (PostgreSQL)**: Structured data like users, pets, adoptions
- **Document (MongoDB)**: Flexible logs like health history, behavior notes
- **Graph (Neo4j)**: Recommendations and social/user-pet-tag connections

---

## Database Models

### 1. Relational Database (PostgreSQL)
**Used for**:
- Users
- Pets
- Shelters
- Staff
- Adoptions
- Follow-ups

**Key Tables:**
- `users(id, name, email, password_hash, role)`
- `shelters(id, name, address, phone_number, capacity)`
- `pets(id, name, age, type, breed, gender, shelter_id, status)`
- `adoptions(id, user_id, pet_id, adoption_date, success_notes)`
- `staff(id, name, email, role, shelter_id)`
- `follow_ups(id, adoption_id, visit_date)`

---

###  2. Document Database (MongoDB)
**Used for**:
- Pet profiles
- User feedback
- Shelter reports
- Follow-up reports

**Collections:**
- `pet_profiles` – contains gallery, health history, behavior notes, dietary needs
- `user_feedback` – user reviews and ratings
- `shelter_reports` – daily summaries from each shelter
- `follow_up_reports` – post-adoption progress with pictures and energy levels

---

###  3. Graph Database (Neo4j)
**Used for**:
- Pet recommendations
- User preferences and friendships

**Nodes:** `User`, `Pet`, `Shelter`, `Tag`, `Breed`  
**Relationships:**
- `(:User)-[:ADOPTED]->(:Pet)`
- `(:Pet)-[:LOCATED_AT]->(:Shelter)`
- `(:Pet)-[:HAS_TAG]->(:Tag)`
- `(:User)-[:PREFERS_TAG]->(:Tag)`
- `(:User)-[:FRIEND_OF]->(:User)`
- `(:Breed)-[:SIMILAR_BREED]->(:Breed)`

---

##  Integration Examples





---

## Project Setup Instructions
## ER & Data Flow Diagrams
## Challenges
## Future Improvements / Roadmap


