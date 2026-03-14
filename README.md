# Ingestion Preflight Toolkit

A local, code-first data ingestion pipeline for validating, cleaning, and routing CSV file drops before they are treated as curated data.

# What it does:
* Profiles incoming CSV files in a `dropzone/`
* Routes known datasets by filename pattern
* Validates dataset-specific schema and business rules
* Quarantines invalid files with structured error reporting
* Cleans and standardizes valid files
* Writes curated outputs as partitioned Parquet
* Archives processed and unrouted source files
* Generates per-run JSON reports and a historical run index

# How to use it:
* Put CSV files into `dropzone/`
* Run the pipeline with:
  * `python -m src.cli --unknown-policy <UNKNOWN_POLICY> --output-policy <OUTPUT_POLICY>`
* Review outputs in:
  * `staging/clean/` for curated Parquet
  * `staging/quarantine/` for invalid files
  * `staging/processed/` for successfully ingested source files
  * `staging/unrouted/` for unknown datasets under `PROFILE_ONLY`
  * `reports/` for run reports and run history

# Current supported policies:
* `--unknown-policy`
  * `STRICT`: quarantine unknown datasets
  * `PROFILE_ONLY`: profile and archive unknown datasets without processing
* `--output-policy`
  * `OVERWRITE`: overwrite existing curated outputs for the same target path

# Example:
* Place a file like `users_2026-02-28.csv` in `dropzone/`
* Run:
  * `python -m src.cli --unknown-policy PROFILE_ONLY --output-policy OVERWRITE`
* Check the generated report in `reports/latest.json`