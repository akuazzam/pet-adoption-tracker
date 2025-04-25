-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) CHECK (role IN ('adopter', 'shelter_staff')) NOT NULL
);

-- Shelters table
CREATE TABLE shelters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    phone_number VARCHAR(20),
    capacity INTEGER DEFAULT 0
);

-- Pets table
CREATE TABLE pets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INTEGER,
    type VARCHAR(50),
    breed VARCHAR(100),
    gender VARCHAR(10),
    shelter_id INTEGER REFERENCES shelters(id) ON DELETE CASCADE,
    status VARCHAR(20) CHECK (status IN ('available', 'adopted')) NOT NULL DEFAULT 'available'
);

-- Adoptions table
CREATE TABLE adoptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    pet_id INTEGER REFERENCES pets(id) ON DELETE CASCADE,
    adoption_date DATE DEFAULT CURRENT_DATE,
    success_notes TEXT
);

-- Staff table
CREATE TABLE staff (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(150),
    role VARCHAR(50),
    shelter_id INTEGER REFERENCES shelters(id) ON DELETE CASCADE
);

-- Follow-up visits table
CREATE TABLE follow_ups (
    id SERIAL PRIMARY KEY,
    adoption_id INTEGER REFERENCES adoptions(id) ON DELETE CASCADE,
    visit_date DATE,
    notes TEXT
);