from datetime import datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo
import sqlite3

from resources import glob

SOURCE_TZ = ZoneInfo("Europe/Kyiv")
SRC_FMT = "%Y-%m-%d %H:%M:%S"      # current format in your DB
DST_FMT = "%Y-%m-%dT%H:%M:%SZ"     # ISO-8601 Z (UTC)

# Table -> list of datetime TEXT columns to convert
TARGETS = {
    "artifacts": ["created_date"],
    "award_member": ["issue_date"],
    "ticket_txns": ["time"],
    "tax_txns": ["time"],
    "business_profits": ["date"],
    "business_withdraws": ["date"],
    "rate_history": ["plan_date", "fact_date"],
    "salary_payouts": ["plan_date", "fact_date"],
    "employees": ["hired_date"],
    "employment_history": ["hired_date", "fired_date"],
    "price_history": ["reset_date"],
    "mat_txns": ["date"],
    "mat_txn_invoices": ["date"],
    "daily_schedules": ["date"],
    "activity_data": ["date"],
}

def convert_local_to_utc_iso(s: str) -> Optional[str]:
    if s is None:
        return None
    s = s.strip()
    if not s:
        return s
    # parse old local time
    local = datetime.strptime(s, SRC_FMT).replace(tzinfo=SOURCE_TZ)
    # convert to UTC and format ISO8601 with Z
    return local.astimezone(timezone.utc).strftime(DST_FMT)

def utc_migrate():
    con = sqlite3.connect(glob.rms.db_file_path)
    con.execute("PRAGMA foreign_keys = ON;")

    try:
        # BEGIN a transaction (IMMEDIATE prevents writers race)
        con.execute("BEGIN IMMEDIATE;")

        for table, cols in TARGETS.items():
            # fetch rowid + all targeted cols (rowid exists unless WITHOUT ROWID was used; your schema doesn't use that)
            select_cols = ", ".join(cols)
            cur = con.execute(f"SELECT rowid, {select_cols} FROM {table};")
            rows = cur.fetchall()

            for row in rows:
                rowid = row[0]
                old_vals = row[1:]
                new_vals = [convert_local_to_utc_iso(v) for v in old_vals]

                # build SET clause only for changed/non-null values to avoid useless writes (optional)
                set_parts = []
                params = []
                for col, old_v, new_v in zip(cols, old_vals, new_vals):
                    # allow NULL fact_date, etc.
                    if new_v is None:
                        continue
                    if old_v == new_v:
                        continue
                    set_parts.append(f"{col} = ?")
                    params.append(new_v)

                if set_parts:
                    params.append(rowid)
                    con.execute(f"UPDATE {table} SET {', '.join(set_parts)} WHERE rowid = ?;", params)

        # Optional: sanity check a few rows programmatically here

        con.execute("COMMIT;")
        print("Migration committed successfully.")
    except Exception as e:
        con.execute("ROLLBACK;")
        raise
    finally:
        con.close()
