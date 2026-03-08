# Ingestion Preflight Toolkit 

Local ingestion preflight pipeline:
- profile incoming files
- validate schema/rules
- clean + standardize
- quarantine bad files
- write clean outputs as Parquet
- emit a JSON run report

## Quickstart (v1)
1) Put CSV files in `dropzone/` 
2) Run: `python -m src.run`
3) Outputs:
- `staging/clean`
- `staging/clean/`
- `reports/`