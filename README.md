# Pet Adoption Tracker

A demonstration of a multi-database pet adoption platform that uses PostgreSQL, MongoDB, and Neo4j for data storage and cross-database analytics. This project includes data‑seeding scripts, reusable business‑logic functions, and example function calls.

---

## 🛠️ Prerequisites

* Docker & Docker Compose
* Python 3.10+
* pip
* (Optional) A running MongoDB instance if you prefer not to use a hosted cluster

---

## ⚙️ Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/akuazzam/pet-adoption-tracker
   ```

2. **Start PostgreSQL & Neo4j**

   ```bash
   # launches only db and neo4j services in detached mode
   docker-compose up build
   ```

   * Postgres will be available on **localhost:5433**
   * Neo4j Bolt endpoint on **localhost:7687**

3. **Create the SQL schema**

   The `db/init.sql` script is automatically executed by Postgres on first startup via the Docker volume mount.

4. **Install Python dependencies**

   ```bash
   pip install --no-cache-dir -r requirements.txt
   ```


5. **Configure environment variables**

   The seeding script and business‑logic code read DB connections from environment variables. Create a `.env` file in the project root or export directly:

   ```bash
   export DB_HOST=localhost
   export DB_PORT=5433
   export DB_NAME=cs440
   export DB_USER=postgres
   export DB_PASSWORD=450720



   # Neo4j
   export NEO4J_URI=bolt://localhost:7687
   export NEO4J_USER=neo4j
   export NEO4J_PASSWORD=testpass
   ```

---

## 🚀 Seeding the Database

After Postgres and Neo4j are up and environment variables are set, run:

```bash
python backend/seed_data.py
```

This will:

* Create shelters, users, pets in Postgres & Neo4j
* Insert profiles and feedback in MongoDB
* Establish likes, friendships, and adoptions across databases

---

## 📂 Folder Structure

A quick overview of the project layout:

```
.
├── backend/                 # application code and database scripts
│   ├── db/                  # SQL schema & init scripts (loaded by Postgres)
│   │   └── init.sql
│   ├── function_/           # high-level business-logic functions
│   │   ├── business_functions.py
│   │   └── core_functions.py
│   ├── queries/             # raw data-access: SQL, MongoDB, Neo4j queries
│   │   ├── sql_queries.py
│   │   ├── mongo_db_queries.py
│   │   └── graph_queries.py
│   ├── app.py               # example runner (`run_example_calls()`)
│   ├── seed_data.py         # one-off data-seeding script
│   └── test_sql_queries.py  # unit tests for SQL queries
│
├── docker/                  # Dockerfiles or helper scripts (optional)
├── .env                     # environment-variable overrides
├── docker-compose.yml       # orchestrates Postgres, Neo4j, etc.
├── requirements.txt         # Python dependencies
└── README.md                # project documentation (this file)
```

## 📚 Business Logic Module

The six high-level operations—top recommendations, most adoptable ranking, cross‐database user connections, low‐engagement reporting, user engagement reporting, and pet demand forecasting—are implemented in `backend/function_/business_functions.py` and are exercised in the example runner `backend/app.py`.

All cross‑database analytics live in `queries/business_functions.py`.  Key functions:

1. `get_top_recommended_pets_for_user(user_id, top_n)`
2. `get_most_adoptable_pet_profiles(top_n)`
3. `get_top_crossdb_user_connections(user_id, top_n)`
4. `get_low_engagement_pets_report()`
5. `get_user_engagement_report(user_id)`
6. `forecast_pet_demand_by_breed_or_tag()`

Use these directly in your own scripts or integrate into a web framework of your choice.

---

## 📦 Running Example Function Calls

All six high‑level business functions are exercised in `app.py` via a simple `run_example_calls()` entry point.

```bash
python app.py
```

You should see output similar to:

```
Top Recommended Pets for user 1: [...]
Most Adoptable Pets (top 5): [...]
Top 5 Cross-DB Connections for user 1: [...]
Low Engagement Pets: [...]
Engagement Report for user 1: {...}
Forecast Pet Demand by Breed and Tag: {...}
```

Feel free to adjust the `user_id` and `top_n` parameters at the top of `run_example_calls()`.

---


## 📖 Next Steps

* Integrate into a Flask/FastAPI service
* Add automated tests for the business functions
* Dockerize the seeding and example runner in a dedicated container

---



