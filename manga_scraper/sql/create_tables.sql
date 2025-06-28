CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- Enables UUID generation functions in PostgreSQL

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),  -- UUID as the primary key with default UUID generation
    username VARCHAR(255) UNIQUE NOT NULL,           -- 'username' must be unique and non-null
    password VARCHAR(255) NOT NULL,                  -- 'password' must be non-null
    is_admin BOOLEAN DEFAULT FALSE                   -- 'is_admin' with a default value of 'false'
);

-- Tasks table: stores scraping task metadata and status
CREATE TABLE IF NOT EXISTS tasks (
    task_id VARCHAR PRIMARY KEY,         -- Unique task identifier (UUID)
    cmd TEXT NOT NULL,                   -- Command line used to launch the task
    status VARCHAR NOT NULL DEFAULT 'running',  -- Task status: running, finished, failed, terminated
    start_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),  -- Task start timestamp with timezone
    end_time TIMESTAMPTZ,                -- Task end timestamp, null if not finished yet
    pid INTEGER,                        -- Process ID of the running task (optional)
    is_admin_only BOOLEAN DEFAULT TRUE  -- Whether only admins can manage this task
);
