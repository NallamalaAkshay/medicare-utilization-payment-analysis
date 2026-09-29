import sqlite3
import pandas as pd

df = pd.read_csv("output/state_specialty_summary_2024.csv")
conn = sqlite3.connect("output/medicare_2024.db")
df.to_sql("state_specialty", conn, if_exists="replace", index=False)

queries = {
    "top_specialties": """
        SELECT specialty, SUM(services) AS total_services
        FROM state_specialty
        GROUP BY specialty
        ORDER BY total_services DESC
        LIMIT 10
    """,
    "new_york_specialties": """
        SELECT specialty, services,
               ROUND(avg_payment_per_service, 2) AS avg_payment
        FROM state_specialty
        WHERE state = 'NY'
        ORDER BY services DESC
        LIMIT 10
    """,
}

for name, query in queries.items():
    result = pd.read_sql_query(query, conn)
    result.to_csv(f"output/{name}.csv", index=False)
    print(f"\n{name}\n{result.to_string(index=False)}")

conn.close()