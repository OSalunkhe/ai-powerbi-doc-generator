from pbixray import PBIXRay
import sqlite3
import pandas as pd

model = PBIXRay("model.pbix")
conn = sqlite3.connect("model_data.db")

for table_name in model.tables:
    print(f"Exporting table: {table_name}")
    try:
        data = model.get_table(table_name)
        df = pd.DataFrame(data)

        if df.empty:
            print(f"  Skipped (no rows found)")
            continue

        # SQLite table names can't have spaces - keep this consistent everywhere
        safe_name = table_name.replace(" ", "_")
        df.to_sql(safe_name, conn, if_exists="replace", index=False)
        print(f"  -> {len(df)} rows written as table '{safe_name}'")
    except Exception as e:
        print(f"  Skipped {table_name}: {e}")

conn.close()
print("\nDone. Data exported to model_data.db")