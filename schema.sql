-- Drop existing tables to reset
DROP TABLE IF EXISTS calendar_events;
DROP TABLE IF EXISTS interviews;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS users;

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL
);

-- Jobs table with display_id
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    display_id INTEGER NOT NULL,
    company VARCHAR(100) NOT NULL,
    position VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'applied',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, display_id)
);

-- Interviews table with display_id
CREATE TABLE interviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    display_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    job_display_id INTEGER NOT NULL,
    date VARCHAR(10) NOT NULL,
    time VARCHAR(5) NOT NULL,
    details TEXT,
    UNIQUE(user_id, display_id),
    FOREIGN KEY (user_id, job_display_id) REFERENCES jobs(user_id, display_id)
);

-- Calendar events table with display_id
CREATE TABLE calendar_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    display_id INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL,
    date VARCHAR(10) NOT NULL,
    time VARCHAR(5) NOT NULL,
    details TEXT,
    UNIQUE(user_id, display_id)
);