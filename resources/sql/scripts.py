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
        FOREIGN KEY (owner_id)
            REFERENCES members (user_id)
    );
"""

CREATE_TABLE_AWARDS = """
    CREATE TABLE IF NOT EXISTS awards (
        award_id TEXT PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        description TEXT NOT NULL,
        payment REAL NOT NULL
    );
"""

CREATE_TABLE_AWARD_MEMBER = """
    CREATE TABLE IF NOT EXISTS award_member (
        award_id TEXT,
        owner_id INTEGER,
        issue_date TEXT NOT NULL,
        PRIMARY KEY (award_id, owner_id),
        FOREIGN KEY (award_id)
            REFERENCES awards (award_id)
            ON DELETE CASCADE,
        FOREIGN KEY (owner_id)
            REFERENCES members (user_id)
            ON DELETE CASCADE
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

INSERT_ADDT = "INSERT INTO addt (user_id, tickets, time, description, type_) VALUES (?, ?, ?, ?, ?)"
INSERT_DELT = "INSERT INTO delt (user_id, tickets, time, description, type_) VALUES (?, ?, ?, ?, ?)"
INSERT_MEMBER = "INSERT INTO members (user_id, username, first_name, last_name, tickets) VALUES (?, ?, ?, ?, ?)"
INSERT_AWARD = "INSERT INTO awards (award_id, name, description, payment) VALUES (?, ?, ?, ?)"
INSERT_AWARD_MEMBER = "INSERT INTO award_member (award_id, owner_id) VALUES (?, ?)"
INSERT_TPAY = "INSERT INTO tpay (sender_id, receiver_id, transfer, fee, time, description) VALUES (?, ?, ?, ?, ?, ?)"

SELECT_TPAY_BY_SENDER_OR_RECEIVER = "SELECT * FROM tpay WHERE sender_id = ? OR receiver_id = ?"
SELECT_ADDT_TYPE_NOT_TPAY = "SELECT * FROM addt WHERE user_id = ? AND type_ NOT IN (?, ?)"
SELECT_DELT_TYPE_NOT_TPAY = "SELECT * FROM delt WHERE user_id = ? AND type_ NOT IN (?, ?)"
SELECT_MEMBER_BY_USER_ID = "SELECT * FROM members WHERE user_id = ?"
SELECT_MEMBER_BY_USERNAME = "SELECT * FROM members WHERE username = ?"
SELECT_AWARD = "SELECT * FROM awards WHERE award_id = ?"
SELECT_AWARDS_COUNT_BY_OWNER_ID = "SELECT COUNT(am.award_id) FROM award_member am WHERE am.owner_id = ?"
SELECT_TICKETS_COUNT = "SELECT tickets FROM members WHERE user_id = ?"
SELECT_ARTIFACTS_BY_OWNER_ID = "SELECT * FROM artifacts WHERE owner_id = ?"
SELECT_ARTIFACTS_COUNT_BY_OWNER_ID = "SELECT COUNT(a.artifact_id) FROM artifacts a WHERE a.owner_id = ?"

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

SELECT_AWARDS_BY_OWNER_ID = """
    SELECT a.*
    FROM awards a
    JOIN award_member am ON a.award_id = am.award_id
    WHERE am.owner_id = ?
"""

UPDATE_MEMBER = "UPDATE members SET username = ?, first_name = ?, last_name = ? WHERE user_id = ?"
UPDATE_TICKETS_COUNT = "UPDATE members SET tickets = ? WHERE user_id = ?"
UPDATE_TPAY_AVAILABLE = "UPDATE members SET tpay_available = ? WHERE user_id = ?"
RESET_TPAY_AVAILABLE = "UPDATE members SET tpay_available = 3"
