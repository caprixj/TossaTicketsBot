UPDATE_MEMBER_NAMES = "UPDATE members SET username = ?, first_name = ?, last_name = ? WHERE user_id = ?"
UPDATE_MEMBER_TICKETS = "UPDATE members SET tickets = ? WHERE user_id = ?"
UPDATE_MEMBER_BUSINESS_ACCOUNT = "UPDATE members SET business_account = ? WHERE user_id = ?"
UPDATE_MEMBER_ANCHOR = "UPDATE members SET anchor = ? WHERE user_id = ?"
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
