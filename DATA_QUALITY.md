# Data Quality Checks

Dataset: CMS Medicare Physician & Other Practitioners — by Provider and Service, 2024

The Python quality check scanned all 9,781,673 source rows in chunks.

| Check | Rows flagged |
| --- | ---: |
| Missing state | 0 |
| Missing specialty | 0 |
| Missing HCPCS code | 0 |
| Invalid or missing service count | 0 |
| Nonpositive service count | 0 |
| Invalid or missing average Medicare payment | 0 |
| Negative average Medicare payment | 0 |

No rows were flagged by these checks. These results confirm completeness and
basic numeric validity for the fields tested; they do not establish that every
record is unique or that the source data is free of reporting limitations.