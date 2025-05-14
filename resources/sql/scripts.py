""" Create Tables """
from model.types import ProductType
from resources.const import glob

CREATE_VARS = """
    CREATE TABLE IF NOT EXISTS vars (
        name TEXT PRIMARY KEY,
        value TEXT
    );
"""
CREATE_MEMBERS = """
    CREATE TABLE IF NOT EXISTS members (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        tickets REAL NOT NULL DEFAULT 0,
        tpay_available INTEGER NOT NULL DEFAULT 3 CHECK(tpay_available >= 0),
        business_account REAL NOT NULL DEFAULT 0,
        tbox_available INTEGER NOT NULL DEFAULT 1 CHECK(tbox_available >= 0)
    );
"""
CREATE_ARTIFACTS = """
    CREATE TABLE IF NOT EXISTS artifacts (
        artifact_id INTEGER PRIMARY KEY AUTOINCREMENT,
        creator_id INTEGER NOT NULL,
        owner_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        investment REAL NOT NULL DEFAULT 0,
        file_id TEXT,
        description TEXT,
        created_date TEXT NOT NULL,
        FOREIGN KEY (creator_id) REFERENCES members(user_id),
        FOREIGN KEY (owner_id) REFERENCES members(user_id)
    );
"""
CREATE_ARTIFACT_VALUE_HISTORY = """
    CREATE TABLE IF NOT EXISTS artifact_value_history (
        artifact_value_history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        artifact_id INTEGER,
        owner_id INTEGER NOT NULL,
        value REAL NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY (artifact_id) REFERENCES artifacts(artifact_id)
    );
"""
CREATE_AWARDS = """
    CREATE TABLE IF NOT EXISTS awards (
        award_id TEXT PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        description TEXT NOT NULL,
        payment REAL NOT NULL
    );
"""
CREATE_AWARD_MEMBER = """
    CREATE TABLE IF NOT EXISTS award_member (
        award_id TEXT,
        owner_id INTEGER,
        issue_date TEXT NOT NULL,
        PRIMARY KEY (award_id, owner_id),
        FOREIGN KEY (award_id) REFERENCES awards (award_id) ON DELETE CASCADE,
        FOREIGN KEY (owner_id) REFERENCES members (user_id) ON DELETE CASCADE
    );
"""
CREATE_ADDT = """
    CREATE TABLE IF NOT EXISTS addt (
        addt_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        tickets REAL NOT NULL DEFAULT 0,
        time TEXT NOT NULL,
        description TEXT,
        type_ TEXT NOT NULL DEFAULT "unknown",
        FOREIGN KEY (user_id) REFERENCES members (user_id) ON DELETE RESTRICT
    );
"""
CREATE_DELT = """
    CREATE TABLE IF NOT EXISTS delt (
        delt_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        tickets REAL NOT NULL DEFAULT 0,
        time TEXT NOT NULL,
        description TEXT,
        type_ TEXT NOT NULL DEFAULT "unknown",
        FOREIGN KEY (user_id) REFERENCES members (user_id) ON DELETE RESTRICT
    );
"""
CREATE_TPAY = """
    CREATE TABLE IF NOT EXISTS tpay (
        tpay_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        transfer REAL NOT NULL,
        fee REAL NOT NULL,
        time TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY (sender_id) REFERENCES members (user_id) ON DELETE RESTRICT,
        FOREIGN KEY (receiver_id) REFERENCES members (user_id) ON DELETE RESTRICT
    );
"""
CREATE_BUSINESS_PROFITS = """
    CREATE TABLE IF NOT EXISTS business_profits (
        business_profit_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        profit_type TEXT NOT NULL DEFAULT 'unknown',
        transfer REAL CHECK(transfer > 0),
        date TEXT NOT NULL,
        artifact_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES members (user_id) ON DELETE RESTRICT,
        FOREIGN KEY (artifact_id) REFERENCES artifacts (artifact_id) ON DELETE RESTRICT
    );
"""
CREATE_BUSINESS_WITHDRAWS = """
    CREATE TABLE IF NOT EXISTS business_withdraws (
        business_withdraw_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        transfer REAL CHECK(transfer > 0),
        date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES members (user_id) ON DELETE RESTRICT
    );
"""
CREATE_RATE_HISTORY = """
    CREATE TABLE IF NOT EXISTS rate_history (
        rate_history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        inflation REAL NOT NULL,
        fluctuation REAL NOT NULL,
        plan_date TEXT NOT NULL,
        fact_date TEXT NOT NULL
    );
"""
CREATE_SALARY_PAYOUTS = """
    CREATE TABLE IF NOT EXISTS salary_payouts (
        salary_payout_id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_date TEXT NOT NULL,
        fact_date TEXT,
        paid_out INTEGER NOT NULL DEFAULT 0
    );
"""
CREATE_EMPLOYEES = """
    CREATE TABLE IF NOT EXISTS employees (
        user_id INTEGER,
        position TEXT,
        hired_date TEXT NOT NULL,
        PRIMARY KEY (user_id, position),
        FOREIGN KEY (user_id) REFERENCES members (user_id) ON DELETE CASCADE,
        FOREIGN KEY (position) REFERENCES jobs (position) ON DELETE RESTRICT
    );
"""
CREATE_EMPLOYMENT_HISTORY = """
    CREATE TABLE IF NOT EXISTS employment_history (
        employment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        position TEXT NOT NULL,
        salary REAL NOT NULL,
        hired_date TEXT NOT NULL,
        fired_date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES members (user_id) ON DELETE RESTRICT
    );
"""
CREATE_JOBS = """
    CREATE TABLE IF NOT EXISTS jobs (
        position TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        salary REAL NOT NULL DEFAULT 0
    );
"""
CREATE_PRICES = """
    CREATE TABLE IF NOT EXISTS prices (
        product_name TEXT NOT NULL,
        product_type TEXT NOT NULL,
        price REAL NOT NULL DEFAULT 0,
        PRIMARY KEY (product_name, product_type)
    );
"""
CREATE_PRICE_HISTORY = """
    CREATE TABLE IF NOT EXISTS price_history (
        price_history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        product_type TEXT NOT NULL,
        price REAL NOT NULL DEFAULT 0,
        reset_date TEXT NOT NULL,
        FOREIGN KEY (product_name, product_type) REFERENCES parent_table(product_name, product_type)
    );
"""
CREATE_MATERIALS = """
    CREATE TABLE IF NOT EXISTS materials (
        name TEXT PRIMARY KEY,
        emoji TEXT NOT NULL
    );
"""
CREATE_MEMBER_MATERIALS = """
    CREATE TABLE IF NOT EXISTS member_materials (
        user_id INTEGER,
        material_name TEXT,
        quantity INTEGER NOT NULL CHECK(quantity >= 0),
        PRIMARY KEY (user_id, material_name),
        FOREIGN KEY (user_id) REFERENCES members(user_id),
        FOREIGN KEY (material_name) REFERENCES materials(name)
    );
"""
CREATE_MATERIAL_TRANSACTIONS = """
    CREATE TABLE IF NOT EXISTS material_transactions (
        material_transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL DEFAULT -1,
        receiver_id INTEGER NOT NULL DEFAULT -1,
        type TEXT NOT NULL DEFAULT 'unknown',
        material_name TEXT,
        quantity INTEGER NOT NULL CHECK(quantity >= 0),
        transfer REAL NOT NULL DEFAULT 0,
        tax REAL NOT NULL,
        date TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY (sender_id) REFERENCES members (user_id) ON DELETE RESTRICT,
        FOREIGN KEY (receiver_id) REFERENCES members (user_id) ON DELETE RESTRICT,
        FOREIGN KEY (material_name) REFERENCES materials(name) ON DELETE RESTRICT
    );
"""
CREATE_MATERIAL_TRANSACTION_REQUESTS = """
CREATE TABLE IF NOT EXISTS material_transaction_requests (
        material_transaction_request_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL DEFAULT -1,
        receiver_id INTEGER NOT NULL DEFAULT -1,
        type TEXT NOT NULL DEFAULT "unknown",
        material_name TEXT,
        quantity INTEGER NOT NULL CHECK(quantity >= 0),
        transfer REAL NOT NULL DEFAULT 0,
        tax REAL NOT NULL,
        date TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY (sender_id) REFERENCES members (user_id) ON DELETE RESTRICT,
        FOREIGN KEY (receiver_id) REFERENCES members (user_id) ON DELETE RESTRICT,
        FOREIGN KEY (material_name) REFERENCES materials(name) ON DELETE RESTRICT
    );
"""
CREATE_DAILY_SCHEDULES = """
    CREATE TABLE IF NOT EXISTS daily_schedules (
        daily_schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL
    );
"""
CREATE_ACTIVITY_DATA = """
    CREATE TABLE IF NOT EXISTS activity_data (
        activity_data_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        content_type TEXT NOT NULL,
        date TEXT NOT NULL,
        text_size INTEGER NOT NULL DEFAULT 0,
        is_forward INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES members(user_id)
    );
"""

""" Insert """

INSERT_MEMBER = "INSERT INTO members (user_id, username, first_name, last_name, tickets) VALUES (?, ?, ?, ?, ?)"
INSERT_ARTIFACT = ("INSERT INTO artifacts (creator_id, owner_id, name, type, investment, file_id, description, "
                   "created_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
INSERT_AWARD = "INSERT INTO awards (award_id, name, description, payment) VALUES (?, ?, ?, ?)"
INSERT_AWARD_MEMBER = "INSERT INTO award_member (award_id, owner_id, issue_date) VALUES (?, ?, ?)"
INSERT_ADDT = "INSERT INTO addt (user_id, tickets, time, description, type_) VALUES (?, ?, ?, ?, ?)"
INSERT_DELT = "INSERT INTO delt (user_id, tickets, time, description, type_) VALUES (?, ?, ?, ?, ?)"
INSERT_TPAY = "INSERT INTO tpay (sender_id, receiver_id, transfer, fee, time, description) VALUES (?, ?, ?, ?, ?, ?)"
INSERT_BUSINESS_PROFIT = ("INSERT INTO business_profits (user_id, profit_type, transfer, date, artifact_id) "
                          "VALUES (?, ?, ?, ?, ?)")
INSERT_RATE_HISTORY = "INSERT INTO rate_history (inflation, fluctuation, plan_date, fact_date) VALUES (?, ?, ?, ?)"
INSERT_SALARY_PAYOUT = "INSERT INTO salary_payouts (plan_date, fact_date, paid_out) VALUES (?, ?, ?)"
INSERT_EMPLOYEE = "INSERT INTO employees (user_id, position, hired_date) VALUES (?, ?, ?)"
INSERT_EMPLOYMENT_HISTORY = ("INSERT INTO employment_history (user_id, position, salary, hired_date, fired_date) "
                             "VALUES (?, ?, ?, ?, ?)")
INSERT_JOB = "INSERT INTO jobs (position, name, salary) VALUES (?, ?, ?)"
INSERT_PRICE_HISTORY = "INSERT INTO price_history (product_name, product_type, price, reset_date) VALUES (?, ?, ?, ?)"
INSERT_OR_IGNORE_MATERIALS = "INSERT OR IGNORE INTO materials VALUES (?, ?)"
INSERT_OR_IGNORE_SQL_VARS = "INSERT OR IGNORE INTO vars VALUES (?, ?)"
INSERT_MEMBER_MATERIAL = "INSERT INTO member_materials (user_id, material_name, quantity) VALUES (?, ?, ?)"
INSERT_MATERIAL_TRANSACTION = ("INSERT INTO material_transactions (sender_id, receiver_id, type, material_name, "
                               "quantity, transfer, tax, date, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)")
INSERT_DAILY_SCHEDULE = "INSERT INTO daily_schedules (date) VALUES (?)"

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
SELECT_SUM_TICKETS = "SELECT SUM(tickets) FROM members"
SELECT_SUM_BUSINESS_ACCOUNTS = "SELECT SUM(business_account) FROM members"
SELECT_ARTIFACTS = "SELECT * FROM artifacts"
SELECT_LAST_DAILY_SCHEDULE = "SELECT * FROM daily_schedules ORDER BY date DESC LIMIT 1"
SELECT_LAST_RATE_HISTORY = "SELECT * FROM rate_history ORDER BY plan_date DESC LIMIT 1"
SELECT_LAST_SALARY_PAYOUT = "SELECT * FROM salary_payouts ORDER BY plan_date DESC LIMIT 1"
SELECT_JOBS = "SELECT * FROM jobs"
SELECT_PRICES = "SELECT * FROM prices"
SELECT_GEM_PRICES = f"SELECT * FROM prices WHERE product_type = {ProductType.gemstone}"
SELECT_MEMBER_MATERIAL = "SELECT material_name, quantity FROM member_materials WHERE user_id = ? AND material_name = ?"
SELECT_ALL_MEMBER_MATERIALS = "SELECT material_name, quantity FROM member_materials WHERE user_id = ?"
SELECT_SQL_VAR = "SELECT value FROM vars WHERE name = ?"
SELECT_GEMSTONE_PRICE = f"SELECT price FROM prices WHERE product_name = ? AND product_type = {ProductType.gemstone}"
SELECT_SOLD_ITEMS_COUNT_TODAY = (f"SELECT SUM(quantity) FROM material_transactions "
                                 f"WHERE sender_id = ? and receiver_id = {glob.NBT_ID} and date >= ?")
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
SELECT_EMPLOYEE_BY_PRIMARY_KEY = """
    SELECT e.user_id, e.position, j.salary, e.hired_date
    FROM employees e
    INNER JOIN jobs j ON e.position = j.position
    WHERE e.user_id = ? AND e.position = ?
"""
SELECT_EMPLOYEE_POSITION_NAMES = """
    SELECT j.name
    FROM employees e
    INNER JOIN jobs j ON e.position = j.position
    WHERE e.user_id = ?
"""
SELECT_EMPLOYEES = """
    SELECT e.user_id, e.position, j.salary, e.hired_date
    FROM employees e
    INNER JOIN jobs j ON e.position = j.position
"""
SELECT_DELTA_TICKETS_COUNT_AFTER_DATETIME = """
    SELECT SUM(dt) FROM (
        SELECT SUM(add_sum - delt_sum) AS dt
        FROM (
            SELECT
                DATE(time) AS date,
                SUM(tickets) AS add_sum,
                0 AS delt_sum
            FROM addt
            WHERE time >= ?
            GROUP BY DATE(time)
    
            UNION ALL
    
            SELECT
                DATE(time) AS date,
                0 AS add_sum,
                SUM(tickets) AS delt_sum
            FROM delt
            WHERE time >= ?
            GROUP BY DATE(time)
        )
        GROUP BY date
        ORDER BY date
    )
"""
SELECT_EACH_MATERIAL_COUNT = """
    SELECT material_name, SUM(quantity) as total_quantity
    FROM member_materials
    GROUP BY material_name
    ORDER BY total_quantity DESC;
"""

""" Update """

UPDATE_MEMBER_NAMES = "UPDATE members SET username = ?, first_name = ?, last_name = ? WHERE user_id = ?"
UPDATE_MEMBER_TICKETS = "UPDATE members SET tickets = ? WHERE user_id = ?"
UPDATE_MEMBER_BUSINESS_ACCOUNT = "UPDATE members SET business_account = ? WHERE user_id = ?"
SPEND_MEMBER_TPAY_AVAILABLE = "UPDATE members SET tpay_available = tpay_available - 1 WHERE user_id = ?"
SPEND_MEMBER_TBOX_AVAILABLE = "UPDATE members SET tbox_available = tbox_available - 1 WHERE user_id = ?"
RESET_MEMBER_TPAY_AVAILABLE = "UPDATE members SET tpay_available = 3"
RESET_MEMBER_TBOX_AVAILABLE = "UPDATE members SET tbox_available = 1"
ADD_MEMBER_MATERIAL = "UPDATE member_materials SET quantity = quantity + ? WHERE user_id = ? AND material_name = ?"
SPEND_MEMBER_MATERIAL = "UPDATE member_materials SET quantity = quantity - ? WHERE user_id = ? AND material_name = ?"
UPDATE_SALARY_PAYOUT = "UPDATE salary_payouts SET paid_out = ?, fact_date = ? WHERE plan_date = ?"
UPDATE_JOB_SALARY = "UPDATE jobs SET salary = ? WHERE position = ?"
RESET_PRICES = "UPDATE prices SET price = price * ?"
RESET_ARTIFACT_VALUES = "UPDATE artifacts SET investment = ROUND(investment * ?, 2)"
RESET_GEM_RATE = "UPDATE prices SET price = ? WHERE product_type = 'gemstone' AND product_name = ?"

""" Delete """

DELETE_MEMBER = "DELETE FROM members WHERE user_id = ?"
DELETE_MEMBER_MATERIAL = "DELETE FROM member_materials WHERE user_id = ? AND material_name = ?"
DELETE_PAID_MEMBER = "DELETE FROM employees WHERE user_id = ? AND position = ?"
DELETE_POSITION_CATALOGUE = "DELETE FROM jobs WHERE position = ?"
