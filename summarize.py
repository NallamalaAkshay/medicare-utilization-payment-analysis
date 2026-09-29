from pathlib import Path
import pandas as pd

source = Path("data/Medicare_Physician_Other_Practitioners_by_Provider_and_Service_2024.csv")
output = Path("output/state_specialty_summary_2024.csv")
output.parent.mkdir(exist_ok=True)

columns = [
    "Rndrng_Prvdr_State_Abrvtn",
    "Rndrng_Prvdr_Type",
    "Tot_Srvcs",
    "Avg_Sbmtd_Chrg",
    "Avg_Mdcr_Alowd_Amt",
    "Avg_Mdcr_Pymt_Amt",
]

summaries = []

for chunk_number, chunk in enumerate(
    pd.read_csv(source, usecols=columns, chunksize=100_000, dtype=str),
    start=1,
):
    chunk = chunk.rename(columns={
        "Rndrng_Prvdr_State_Abrvtn": "state",
        "Rndrng_Prvdr_Type": "specialty",
        "Tot_Srvcs": "services",
        "Avg_Sbmtd_Chrg": "avg_charge",
        "Avg_Mdcr_Alowd_Amt": "avg_allowed",
        "Avg_Mdcr_Pymt_Amt": "avg_payment",
    })

    for column in ["services", "avg_charge", "avg_allowed", "avg_payment"]:
        chunk[column] = pd.to_numeric(
            chunk[column].str.replace(r"[$,]", "", regex=True),
            errors="coerce",
        )

    chunk = chunk.dropna(subset=["state", "specialty", "services"])
    chunk = chunk[chunk["services"] > 0]

    # CMS amount fields are averages per service. Weight them by service count.
    for amount in ["avg_charge", "avg_allowed", "avg_payment"]:
        chunk[f"{amount}_total"] = chunk[amount] * chunk["services"]

    summary = chunk.groupby(["state", "specialty"], as_index=False).agg(
        services=("services", "sum"),
        charge_total=("avg_charge_total", "sum"),
        allowed_total=("avg_allowed_total", "sum"),
        payment_total=("avg_payment_total", "sum"),
        source_rows=("services", "size"),
    )
    summaries.append(summary)

    if chunk_number % 10 == 0:
        print(f"Processed {chunk_number * 100_000:,} source rows...")

result = pd.concat(summaries, ignore_index=True)
result = result.groupby(["state", "specialty"], as_index=False).sum()

result["avg_charge_per_service"] = result["charge_total"] / result["services"]
result["avg_allowed_per_service"] = result["allowed_total"] / result["services"]
result["avg_payment_per_service"] = result["payment_total"] / result["services"]

result = result.drop(columns=["charge_total", "allowed_total", "payment_total"])
result = result.sort_values("services", ascending=False)
result.to_csv(output, index=False)

print(f"Done: {len(result):,} state-specialty rows saved to {output}")
print(result.head(10).to_string(index=False))