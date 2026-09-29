from pathlib import Path
import pandas as pd

source = Path("data/Medicare_Physician_Other_Practitioners_by_Provider_and_Service_2024.csv")
output = Path("output/office_visit_99213_by_state_2024.csv")

columns = [
    "Rndrng_Prvdr_State_Abrvtn",
    "Rndrng_Prvdr_Type",
    "HCPCS_Cd",
    "Place_Of_Srvc",
    "Tot_Srvcs",
    "Avg_Mdcr_Pymt_Amt",
]

parts = []
rows_read = 0
rows_selected = 0

for chunk in pd.read_csv(source, usecols=columns, dtype=str, chunksize=100_000):
    rows_read += len(chunk)

    chunk = chunk[
        (chunk["HCPCS_Cd"] == "99213")
        & (chunk["Rndrng_Prvdr_Type"] == "Internal Medicine")
        & (chunk["Place_Of_Srvc"] == "O")
    ].copy()

    chunk["services"] = pd.to_numeric(
        chunk["Tot_Srvcs"].str.replace(",", "", regex=False),
        errors="coerce",
    )
    chunk["payment"] = pd.to_numeric(
        chunk["Avg_Mdcr_Pymt_Amt"].str.replace(r"[$,]", "", regex=True),
        errors="coerce",
    )

    chunk = chunk.dropna(
        subset=["Rndrng_Prvdr_State_Abrvtn", "services", "payment"]
    )
    chunk = chunk[(chunk["services"] > 0) & (chunk["payment"] >= 0)]
    rows_selected += len(chunk)

    chunk["estimated_payment_total"] = chunk["services"] * chunk["payment"]

    part = chunk.groupby(
        "Rndrng_Prvdr_State_Abrvtn", as_index=False
    ).agg(
        services=("services", "sum"),
        estimated_payment_total=("estimated_payment_total", "sum"),
        provider_service_rows=("services", "size"),
    )
    parts.append(part)

result = pd.concat(parts, ignore_index=True)
result = result.groupby(
    "Rndrng_Prvdr_State_Abrvtn", as_index=False
).sum()

result["avg_medicare_payment_per_service"] = (
    result["estimated_payment_total"] / result["services"]
)
result = result.rename(
    columns={"Rndrng_Prvdr_State_Abrvtn": "state"}
)
result = result.drop(columns="estimated_payment_total")
result = result.sort_values("services", ascending=False)
result.to_csv(output, index=False)

print(f"Source rows read: {rows_read:,}")
print(f"Valid rows selected: {rows_selected:,}")
print(f"States/areas in output: {len(result):,}")
print(result.head(10).to_string(index=False))
print(f"Saved: {output}")