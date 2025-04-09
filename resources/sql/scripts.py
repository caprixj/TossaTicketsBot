""" Create Tables """

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

CREATE_TABLE_PRICE_HISTORY = """
    CREATE TABLE IF NOT EXISTS price_history (
        price_history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        inflation REAL NOT NULL,
        fluctuation REAL NOT NULL,
        plan_date TEXT NOT NULL,
        fact_date TEXT NOT NULL
    );
"""

CREATE_TABLE_SALARY_PAYOUTS = """
    CREATE TABLE IF NOT EXISTS salary_payouts (
        salary_payout_id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_date TEXT NOT NULL,
        fact_date TEXT,
        paid_out INTEGER NOT NULL DEFAULT 0
    );
"""

CREATE_TABLE_PAID_MEMBERS = """
    CREATE TABLE IF NOT EXISTS paid_members (
        user_id INTEGER,
        position TEXT,
        hired_date TEXT NOT NULL,
        PRIMARY KEY (user_id, position),
        FOREIGN KEY (user_id)
            REFERENCES members (user_id)
            ON DELETE RESTRICT,
        FOREIGN KEY (position)
            REFERENCES salary_catalogue (position)
            ON DELETE RESTRICT
    );
"""

CREATE_TABLE_PAID_MEMBER_HISTORY = """
    CREATE TABLE IF NOT EXISTS paid_member_history (
        paid_member_history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        position TEXT NOT NULL,
        salary REAL NOT NULL,
        hired_date TEXT NOT NULL,
        fired_date TEXT NOT NULL,
        FOREIGN KEY (user_id)
            REFERENCES members (user_id)
            ON DELETE RESTRICT
    );
"""

CREATE_SALARY_CATALOGUE = """
    CREATE TABLE IF NOT EXISTS salary_catalogue (
        position TEXT PRIMARY KEY,
        salary REAL NOT NULL DEFAULT 0
    );
"""

""" Insert """

INSERT_ADDT = "INSERT INTO addt (user_id, tickets, time, description, type_) VALUES (?, ?, ?, ?, ?)"
INSERT_DELT = "INSERT INTO delt (user_id, tickets, time, description, type_) VALUES (?, ?, ?, ?, ?)"
INSERT_MEMBER = "INSERT INTO members (user_id, username, first_name, last_name, tickets) VALUES (?, ?, ?, ?, ?)"
INSERT_AWARD = "INSERT INTO awards (award_id, name, description, payment) VALUES (?, ?, ?, ?)"
INSERT_AWARD_MEMBER = "INSERT INTO award_member (award_id, owner_id) VALUES (?, ?)"
INSERT_TPAY = "INSERT INTO tpay (sender_id, receiver_id, transfer, fee, time, description) VALUES (?, ?, ?, ?, ?, ?)"
INSERT_PRICE_HISTORY = "INSERT INTO price_history (inflation, fluctuation, plan_date, fact_date) VALUES (?, ?, ?, ?)"
INSERT_SALARY_PAYOUT = "INSERT INTO salary_payouts (plan_date, fact_date, paid_out) VALUES (?, ?, ?)"
INSERT_PAID_MEMBER = "INSERT INTO paid_members (user_id, position, hired_date) VALUES (?, ?, ?)"
INSERT_PAID_MEMBER_HISTORY = ("INSERT INTO paid_member_history (user_id, position, salary, hired_date, fired_date) "
                              "VALUES (?, ?, ?, ?, ?)")

""" Select """

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
SELECT_TOTAL_TICKETS_COUNT = "SELECT SUM(tickets) FROM members"
SELECT_PRICE_HISTORY = "SELECT * FROM price_history ORDER BY plan_date DESC LIMIT 1"
SELECT_SALARY_PAYOUT = "SELECT * FROM salary_payouts ORDER BY plan_date DESC LIMIT 1"
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
    LIMIT ?
"""
SELECT_AWARD_RECORDS_BY_OWNER_ID = """
    SELECT a.*, am.issue_date
    FROM awards a
    JOIN award_member am ON a.award_id = am.award_id
    WHERE am.owner_id = ?
    ORDER BY am.issue_date ASC
"""
SELECT_PAID_MEMBER_BY_PRIMARY_KEY = """
    SELECT pm.user_id, pm.position, sc.salary, pm.hired_date
    FROM paid_members pm
    INNER JOIN salary_catalogue sc ON pm.position = sc.position
    WHERE pm.user_id = ? AND pm.position = ?
"""
SELECT_PAID_MEMBERS_BY_USER_ID = """
    SELECT pm.user_id, pm.position, sc.salary, pm.hired_date
    FROM paid_members pm
    INNER JOIN salary_catalogue sc ON pm.position = sc.position
    WHERE pm.user_id = ?
"""
SELECT_PAID_MEMBERS = """
    SELECT pm.user_id, pm.position, sc.salary, pm.hired_date
    FROM paid_members pm
    INNER JOIN salary_catalogue sc ON pm.position = sc.position
"""

""" Update """

UPDATE_MEMBER = "UPDATE members SET username = ?, first_name = ?, last_name = ? WHERE user_id = ?"
UPDATE_TICKETS_COUNT = "UPDATE members SET tickets = ? WHERE user_id = ?"
UPDATE_TPAY_AVAILABLE = "UPDATE members SET tpay_available = ? WHERE user_id = ?"
RESET_TPAY_AVAILABLE = "UPDATE members SET tpay_available = 3"
UPDATE_SALARY_PAYOUT = "UPDATE salary_payouts SET paid_out = ?, fact_date = ? WHERE plan_date = ?"

""" Delete """

DELETE_PAID_MEMBER = "DELETE FROM paid_members WHERE user_id = ? AND position = ?"
