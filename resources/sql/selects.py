SELECT_ADDTS_BY_USER_ID = "SELECT * FROM ticket_txns WHERE receiver_id = ? AND type = ?"
SELECT_DELTS_BY_USER_ID = "SELECT * FROM ticket_txns WHERE sender_id = ? AND type = ?"
SELECT_MSELLS_BY_USER_ID = "SELECT * FROM ticket_txns WHERE receiver_id = ? AND type = ?"
SELECT_NON_TPAY_TAXES_BY_USER_ID = "SELECT * FROM tax_txns WHERE type != 'single_tpay' AND user_id = ?"
SELECT_MEMBER_BY_USER_ID = "SELECT * FROM members WHERE user_id = ?"
SELECT_MEMBER_BY_USERNAME = "SELECT * FROM members WHERE username = ?"
SELECT_DEL_MEMBER_BY_USER_ID = "SELECT * FROM del_members WHERE user_id = ?"
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
SELECT_GEM_RATES = "SELECT * FROM prices WHERE product_type = 'gemstone'"
SELECT_MEMBER_MATERIAL = "SELECT material_name, quantity FROM member_materials WHERE user_id = ? AND material_name = ?"
SELECT_MEMBER_MATERIALS_BY_USER_ID = "SELECT material_name, quantity FROM member_materials WHERE user_id = ?"
SELECT_ALL_MEMBER_MATERIALS = "SELECT * FROM member_materials"
SELECT_SQL_VAR = "SELECT value FROM vars WHERE name = ?"
SELECT_GEMSTONE_PRICE = "SELECT price FROM prices WHERE product_name = ? AND product_type = 'gemstone'"
SELECT_SOLD_ITEMS_COUNT_TODAY = (f"SELECT SUM(quantity) FROM material_transactions "
                                 f"WHERE sender_id = ? and receiver_id = -1 and date >= ?")
SELECT_TPAYS_AND_TAXATION_BY_USER_ID = """
    SELECT tic.*, COALESCE(SUM(txs.amount), 0.0) AS total_tax
    FROM ticket_txns tic
    LEFT JOIN tax_txns txs ON txs.ticket_txn_id = tic.ticket_txn_id
    WHERE (tic.sender_id = ? AND tic.receiver_id != -1) OR (tic.sender_id != -1 AND tic.receiver_id = ?)
    GROUP BY tic.ticket_txn_id;
"""
SELECT_TOPT = """
    WITH last_activity AS (
        SELECT user_id, MAX(time) AS last_activity
        FROM (
            SELECT sender_id AS user_id, time
            FROM ticket_txns
            WHERE sender_id = {user_id}
            
            UNION ALL
            
            SELECT receiver_id AS user_id, time
            FROM ticket_txns
            WHERE receiver_id = {user_id}
        )
        GROUP BY user_id
    )
    SELECT m.*
    FROM members AS m
    LEFT JOIN last_activity AS la ON la.user_id = m.user_id
    ORDER BY m.tickets {order}, la.last_activity {order}
    {limit_clause};
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
# SELECT_DELTA_TICKETS_COUNT_AFTER_DATETIME = """
#     SELECT SUM(dt) FROM (
#         SELECT SUM(add_sum - delt_sum) AS dt
#         FROM (
#             SELECT
#                 DATE(time) AS date,
#                 SUM(tickets) AS add_sum,
#                 0 AS delt_sum
#             FROM addt
#             WHERE time >= ?
#             GROUP BY DATE(time)
#
#             UNION ALL
#
#             SELECT
#                 DATE(time) AS date,
#                 0 AS add_sum,
#                 SUM(tickets) AS delt_sum
#             FROM delt
#             WHERE time >= ?
#             GROUP BY DATE(time)
#         )
#         GROUP BY date
#         ORDER BY date
#     )
# """
SELECT_EACH_MATERIAL_COUNT = """
    SELECT material_name, SUM(quantity) as total_quantity
    FROM member_materials
    GROUP BY material_name
    ORDER BY total_quantity DESC;
"""
