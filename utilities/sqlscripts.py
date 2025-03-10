CREATE_TABLE_MEMBERS = """
    CREATE TABLE IF NOT EXISTS members (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        tickets_count INTEGER DEFAULT 0
    );
"""

CREATE_TABLE_ARTIFACTS = """
    CREATE TABLE IF NOT EXISTS artifacts (
        artifact_id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER,
        name TEXT,
        description TEXT,
        FOREIGN KEY (owner_id) REFERENCES members (user_id)
    );
"""

CREATE_TABLE_ADDT = """
    CREATE TABLE IF NOT EXISTS addt (
        addt_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        tickets_count INTEGER NOT NULL,
        transaction_time TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY (user_id)
            REFERENCES members (user_id)
            ON DELETE RESTRICT
    );
"""

CREATE_TABLE_DELT = """
    CREATE TABLE IF NOT EXISTS delt (
        delt_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        tickets_count INTEGER NOT NULL,
        transaction_time TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY (user_id)
            REFERENCES members (user_id)
            ON DELETE RESTRICT
    );
"""

CREATE_TABLE_RATING = """
    CREATE TABLE IF NOT EXISTS rating (
        rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
        place INTEGER NOT NULL,
        FOREIGN KEY (user_id)
            REFERENCES members (user_id)
            ON DELETE RESTRICT
    );
"""

SELECT_TOPTALL = """
    SELECT 
        m.*
    FROM 
        members m
    LEFT JOIN 
        addt a ON m.user_id = a.user_id
    LEFT JOIN 
        delt d ON m.user_id = d.user_id
    GROUP BY 
        m.user_id, m.username, m.first_name, m.last_name, m.tickets_count
    ORDER BY 
        m.tickets_count DESC, MAX(COALESCE(a.transaction_time, d.transaction_time)) DESC;
"""

SELECT_TOPT = """
    SELECT 
        m.*
    FROM 
        members m
    LEFT JOIN 
        addt a ON m.user_id = a.user_id
    LEFT JOIN 
        delt d ON m.user_id = d.user_id
    GROUP BY 
        m.user_id, m.username, m.first_name, m.last_name, m.tickets_count
    ORDER BY 
        m.tickets_count $, MAX(COALESCE(a.transaction_time, d.transaction_time)) $
    LIMIT ?;
"""

INSERT_ADDT = "INSERT INTO addt (user_id, tickets_count, transaction_time, description) VALUES (?, ?, ?, ?)"
INSERT_DELT = "INSERT INTO delt (user_id, tickets_count, transaction_time, description) VALUES (?, ?, ?, ?)"

INSERT_MEMBER = """
    INSERT INTO 
        members (user_id, username, first_name, last_name, tickets_count)
    VALUES
        (?, ?, ?, ?, ?);
"""
SELECT_MEMBER = "SELECT * FROM members WHERE user_id = ?"
DELETE_MEMBER = "DELETE FROM members WHERE user_id = ?"
UPDATE_MEMBER = "UPDATE members SET username = ?, first_name = ?, last_name = ? WHERE user_id = ?"

UPDATE_TICKETS_COUNT = "UPDATE members SET tickets_count = ? WHERE user_id = ?"
SELECT_TICKETS_COUNT = "SELECT tickets_count FROM members WHERE user_id = ?"

SELECT_ARTIFACT_NAMES = "SELECT a.name FROM artifacts a WHERE owner_id = ?"
