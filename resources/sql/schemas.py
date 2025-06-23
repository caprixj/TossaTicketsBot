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
        tbox_available INTEGER NOT NULL DEFAULT 1 CHECK(tbox_available >= 0),
        anchor INTEGER
    );
"""
CREATE_DEL_MEMBERS = """
    CREATE TABLE IF NOT EXISTS del_members (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        anchor INTEGER
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
# CREATE_ARTIFACT_VALUE_HISTORY = """
#     CREATE TABLE IF NOT EXISTS artifact_value_history (
#         artifact_value_history_id INTEGER PRIMARY KEY AUTOINCREMENT,
#         artifact_id INTEGER,
#         owner_id INTEGER NOT NULL,
#         value REAL NOT NULL,
#         date TEXT NOT NULL,
#         FOREIGN KEY (artifact_id) REFERENCES artifacts(artifact_id)
#     );
# """
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
CREATE_TICKET_TXNS = """
    CREATE TABLE IF NOT EXISTS ticket_txns (
        ticket_txn_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        transfer REAL NOT NULL,
        type TEXT NOT NULL DEFAULT 'unknown',
        time TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY (sender_id) REFERENCES members (user_id) ON DELETE RESTRICT,
        FOREIGN KEY (receiver_id) REFERENCES members (user_id) ON DELETE RESTRICT
    );
"""
CREATE_TAX_TXNS = """
    CREATE TABLE IF NOT EXISTS tax_txns (
        tax_txn_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_txn_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        type TEXT NOT NULL DEFAULT 'unknown',
        time TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES members (user_id) ON DELETE RESTRICT,
        FOREIGN KEY (ticket_txn_id) REFERENCES ticket_txns (ticket_txn_id) ON DELETE RESTRICT
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
