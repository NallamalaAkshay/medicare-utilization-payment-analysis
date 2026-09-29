from pathlib import Path
import pandas as pd

source = Path("data/Medicare_Physician_Other_Practitioners_by_Provider_and_Service_2024.csv")

columns = [
    "Rndrng_Prvdr_State_Abrvtn",
    "Rndrng_Prvdr_Type",
    "HCPCS_Cd",
    "Tot_Srvcs",
    "Avg_Mdcr_Pymt_Amt",
]

counts = {
    "total_rows": 0,
    "missing_state": 0,
    "missing_specialty": 0,
    "missing_hcpcs": 0,
    "invalid_or_missing_services": 0,
    "nonpositive_services": 0,
    "invalid_or_missing_payment": 0,
    "negative_payment": 0,
}

for chunk in pd.read_csv(source, usecols=columns, dtype=str, chunksize=100_000):
    counts["total_rows"] += len(chunk)

    for field, label in [
        ("Rndrng_Prvdr_State_Abrvtn", "missing_state"),
        ("Rndrng_Prvdr_Type", "missing_specialty"),
        ("HCPCS_Cd", "missing_hcpcs"),
    ]:
        counts[label] += chunk[field].isna().sum()

    services = pd.to_numeric(
        chunk["Tot_Srvcs"].str.replace(",", "", regex=False),
        errors="coerce",
    )
    payment = pd.to_numeric(
        chunk["Avg_Mdcr_Pymt_Amt"].str.replace(r"[$,]", "", regex=True),
        errors="coerce",
    )

    counts["invalid_or_missing_services"] += services.isna().sum()
    counts["nonpositive_services"] += (services.notna() & (services <= 0)).sum()
    counts["invalid_or_missing_payment"] += payment.isna().sum()
    counts["negative_payment"] += (payment.notna() & (payment < 0)).sum()

report = pd.DataFrame(
    [{"check": name, "rows": int(value)} for name, value in counts.items()]
)
Path("output").mkdir(exist_ok=True)
report.to_csv("output/data_quality_report_2024.csv", index=False)
print(report.to_string(index=False))