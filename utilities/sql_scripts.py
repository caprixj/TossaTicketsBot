CREATE_TABLE_MEMBERS = """
    CREATE TABLE IF NOT EXISTS members (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        tickets REAL NOT NULL DEFAULT 0,
        tpay_available INTEGER NOT NULL DEFAULT 3
    );
"""

CREATE_TABLE_ARTIFACTS = """
    CREATE TABLE IF NOT EXISTS artifacts (
        artifact_id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER,
        name TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY (owner_id) REFERENCES members (user_id)
    );
"""

CREATE_TABLE_ADDT = """
    CREATE TABLE IF NOT EXISTS addt (
        addt_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        tickets REAL NOT NULL DEFAULT 0,
        time TEXT NOT NULL,
        description TEXT,
        type_ TEXT NOT NULL DEFAULT "unknown",
        FOREIGN KEY (user_id)
            REFERENCES members (user_id)
            ON DELETE RESTRICT
    );
"""

CREATE_TABLE_DELT = """
    CREATE TABLE IF NOT EXISTS delt (
        delt_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        tickets REAL NOT NULL DEFAULT 0,
        time TEXT NOT NULL,
        description TEXT,
        type_ TEXT NOT NULL DEFAULT "unknown",
        FOREIGN KEY (user_id)
            REFERENCES members (user_id)
            ON DELETE RESTRICT
    );
"""

CREATE_TABLE_TPAY = """
    CREATE TABLE IF NOT EXISTS tpay (
        tpay_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        transfer REAL NOT NULL,
        fee REAL NOT NULL,
        time TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY (sender_id)
            REFERENCES members (user_id)
            ON DELETE RESTRICT,
        FOREIGN KEY (receiver_id)
            REFERENCES members (user_id)
            ON DELETE RESTRICT
    );
"""

SELECT_TOPTALL = """
    SELECT m.*
    FROM members m
    LEFT JOIN addt a ON m.user_id = a.user_id
    LEFT JOIN delt d ON m.user_id = d.user_id
    GROUP BY m.user_id, m.username, m.first_name, m.last_name, m.tickets
    ORDER BY m.tickets DESC, MAX(COALESCE(a.time, d.time)) DESC;
"""

SELECT_TOPT = """
    SELECT m.*
    FROM members m
    LEFT JOIN addt a ON m.user_id = a.user_id
    LEFT JOIN delt d ON m.user_id = d.user_id
    GROUP BY m.user_id, m.username, m.first_name, m.last_name, m.tickets
    ORDER BY m.tickets $, MAX(COALESCE(a.time, d.time)) $
    LIMIT ?;
"""

INSERT_ADDT = "INSERT INTO addt (user_id, tickets, time, description, type_) VALUES (?, ?, ?, ?, ?)"
INSERT_DELT = "INSERT INTO delt (user_id, tickets, time, description, type_) VALUES (?, ?, ?, ?, ?)"
INSERT_MEMBER = "INSERT INTO members (user_id, username, first_name, last_name, tickets) VALUES (?, ?, ?, ?, ?)"
INSERT_TPAY = """
    INSERT INTO tpay (sender_id, receiver_id, transfer, fee, time, description)
    VALUES (?, ?, ?, ?, ?, ?);
"""

SELECT_MEMBER_BY_USER_ID = "SELECT * FROM members WHERE user_id = ?"
SELECT_MEMBER_BY_USERNAME = "SELECT * FROM members WHERE username = ?"
DELETE_MEMBER = "DELETE FROM members WHERE user_id = ?"
UPDATE_MEMBER = "UPDATE members SET username = ?, first_name = ?, last_name = ? WHERE user_id = ?"

SELECT_TICKETS_COUNT = "SELECT tickets FROM members WHERE user_id = ?"
UPDATE_TICKETS_COUNT = "UPDATE members SET tickets = ? WHERE user_id = ?"

UPDATE_TPAY_AVAILABLE = "UPDATE members SET tpay_available = ? WHERE user_id = ?"

SELECT_ARTIFACT_NAMES = "SELECT a.name FROM artifacts a WHERE owner_id = ?"

RESET_TPAY_AVAILABLE = "UPDATE members SET tpay_available = 3"
