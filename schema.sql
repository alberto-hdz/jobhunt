CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(100) NOT NULL
);

CREATE TABLE jobs (
    user_id INTEGER REFERENCES users(id),
    job_id INTEGER NOT NULL,
    company VARCHAR(100) NOT NULL,
    job_title VARCHAR(100) NOT NULL,
    job_description TEXT,
    role VARCHAR(100) NOT NULL,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, job_id)
);

CREATE TABLE interviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    date_time TIMESTAMP NOT NULL,
    prep_tips TEXT,
    CONSTRAINT fk_jobs FOREIGN KEY (user_id, job_id) REFERENCES jobs(user_id, job_id)
);