import psycopg2
from decimal import Decimal

SOURCE_STATEMENTS = [
    "Bank Statement Example Free .pdf",
    "Word Format Bank Statement Sample .pdf"
]
SIMULATED_NAMES = [
    "Simulated Decline 1.pdf",
    "Simulated Decline 2.pdf"
]

DB_CONN = "dbname=bank_ml_mvp user=bank_user password=your_strong_password"

def ensure_pk(cur, table, cols, constraint_name=None):
    cur.execute("""
        SELECT COUNT(*) FROM information_schema.table_constraints
        WHERE table_name=%s AND constraint_type='PRIMARY KEY';
    """, (table,))
    if cur.fetchone()[0] == 0:
        if constraint_name is None:
            constraint_name = f"{table}_pk"
        col_str = ','.join(cols)
        try:
            print(f"  [!] Adding PRIMARY KEY ({col_str}) to {table}")
            cur.execute(f"ALTER TABLE {table} ADD CONSTRAINT {constraint_name} PRIMARY KEY ({col_str});")
        except Exception as e:
            print(f"  [!] Could not add PRIMARY KEY to {table}: {e}")


def print_pk_status(cur, table):
    try:
        cur.execute("""
            SELECT constraint_name, column_name
            FROM information_schema.key_column_usage
            WHERE table_name=%s AND constraint_name LIKE '%pk%'
            ORDER BY constraint_name, ordinal_position;
        """, (table,))
        rows = cur.fetchall()
        if not rows:
            print(f"[PK] {table}: None found!")
        else:
            pk_cols = []
            for r in rows:
                if isinstance(r, tuple) and len(r) >= 2 and r[0] and r[1]:
                    pk_cols.append(f"{r[0]}({r[1]})")
                else:
                    pk_cols.append(f"Unexpected tuple: {r}")
            print(f"[PK] {table}: " + ', '.join(pk_cols))
    except Exception as e:
        print(f"[PK] {table}: Error querying PK status: {e}")
        try:
            print(f"  [PK DEBUG] Raw rows: {rows}")
        except Exception:
            pass


def generate_simulated_declines():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    ensure_pk(cur, 'monthly_summary', ['statement_name','year_month'])
    ensure_pk(cur, 'recurring_bills', ['statement_name','category'])
    ensure_pk(cur, 'outstanding_loans', ['statement_name'])
    ensure_pk(cur, 'risk_labels', ['statement_name'])
    conn.commit()
    print_pk_status(cur, 'monthly_summary')
    print_pk_status(cur, 'recurring_bills')
    print_pk_status(cur, 'outstanding_loans')
    print_pk_status(cur, 'risk_labels')

    for src, sim in zip(SOURCE_STATEMENTS, SIMULATED_NAMES):
        cur.execute("SELECT MAX(year_month) FROM monthly_summary WHERE statement_name=%s;", (src,))
        src_ym = cur.fetchone()[0]
        if src_ym is None:
            print(f"  [!] Source '{src}' has no entries in monthly_summary, skipping")
            continue
        print(f"  Using year_month = {src_ym}")

        print(f"\n⮞ Generating decline example '{sim}' from '{src}'")

        cur.execute("""
            SELECT deposits, withdrawals, fees_total, transfer_in, transfer_out
            FROM monthly_summary
            WHERE statement_name=%s AND year_month=%s
        """, (src, src_ym))
        row = cur.fetchone()
        if not row:
            print(f"  [!] Source '{src}' has no entry for {src_ym}, skipping")
            continue
        dep, wd, fees, tin, tout = row

        new_dep   = dep * Decimal('0.3')
        new_wd    = wd * Decimal('2.0')
        new_fees  = (fees * Decimal('2.0')) if fees is not None else Decimal('100.0')
        new_tin   = tin
        new_tout  = tout * Decimal('2.0')

        cur.execute("""
          INSERT INTO monthly_summary
            (statement_name, year_month, deposits, withdrawals, fees_total, transfer_in, transfer_out)
          VALUES (%s, %s, %s, %s, %s, %s, %s)
          ON CONFLICT (statement_name, year_month) DO NOTHING
        """, (sim, src_ym, new_dep, new_wd, new_fees, new_tin, new_tout))
        print(f"  • monthly_summary row inserted")

        categories = ["Rent","Payroll","Utilities","Loan","Fees"]
        for cat in categories:
            avg_amt = new_fees if cat=="Fees" else 0
            months  = 1 if cat=="Fees" else 0
            try:
                cur.execute("""
                  INSERT INTO recurring_bills(statement_name, category, avg_amount, count_months)
                  VALUES (%s,%s,%s,%s)
                  ON CONFLICT (statement_name, category) DO NOTHING
                """, (sim, cat, avg_amt, months))
            except Exception as e:
                print(f"  [!] Error inserting into recurring_bills: {e}")
        print("  • recurring_bills rows inserted")
        conn.commit()

        try:
            cur.execute("""
              INSERT INTO outstanding_loans(statement_name, total_loan_payments, loan_tx_count)
              VALUES (%s, 0, 0)
              ON CONFLICT (statement_name) DO NOTHING
            """, (sim,))
            print("  • outstanding_loans row inserted")
        except Exception as e:
            print(f"  [!] Error inserting into outstanding_loans: {e}")
        conn.commit()

        try:
            cur.execute("""
              INSERT INTO risk_labels(statement_name, approve)
              VALUES (%s, 0)
              ON CONFLICT (statement_name) DO NOTHING
            """, (sim,))
            print("  • risk_labels row inserted with approve=0")
        except Exception as e:
            print(f"  [!] Error inserting into risk_labels: {e}")
        conn.commit()

if __name__ == "__main__":
    generate_simulated_declines()
