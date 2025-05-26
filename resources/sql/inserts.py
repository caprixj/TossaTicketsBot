INSERT_MEMBER = ("INSERT INTO members (user_id, username, first_name, last_name, tickets, anchor) "
                 "VALUES (?, ?, ?, ?, ?, ?)")
INSERT_DEL_MEMBER = "INSERT INTO del_members (user_id, username, first_name, last_name, anchor) VALUES (?, ?, ?, ?, ?)"
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
