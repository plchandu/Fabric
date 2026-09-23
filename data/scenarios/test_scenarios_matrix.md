# IPS BI Modernization — Test Scenarios Matrix & Data Catalog

This catalog outlines the 11 key enterprise testing scenarios covered by the generated datasets in `data/`:

| Scenario ID | Scenario Name | Target Entity / File | Key Test Records / Condition | Expected Engine Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **SC-01** | **Julian Date Boundaries** | `F0911_GL_Ledger.csv` | `GLDGJ = 124060` (Feb 29, 2024)<br/>`GLDGJ = 124366` (Dec 31, 2024 leap)<br/>`GLDGJ = 099365` (Dec 31, 1999) | Correctly parses leap day, 366th day, and C=0 1900s century boundary to Gregorian `YYYY-MM-DD`. |
| **SC-02** | **Multi-Currency & Dual Valuation** | `F0911_GL_Ledger.csv` | Doc 100016: EUR €10,000 (@ 1.085 FX)<br/>Doc 100017: JPY ¥5,000,000 (@ 0.0065 FX) | Preserves domestic `GLAA` ($) and foreign `GLACR` (€/¥). Scales JPY with 0 decimals and converts reporting USD. |
| **SC-03** | **SCD Type 2 Historical Tracking** | `F03012_Customer_Master.csv`<br/>`F0116_Address_By_Date.csv` | Cust 10001 (Credit rating B1 -> A1)<br/>Cust 10002 (Relocation Dallas -> Austin) | Creates distinct historical versions with `effective_start_date`, `effective_end_date`, and `is_current` flags. |
| **SC-04** | **Multi-Company Hierarchical Fallback** | `F03012_Customer_Master.csv`<br/>`F03B11_AR_Ledger.csv` | Customer 10008 linked to Company 00000 | Ingestion applies `F03B1.RPCO -> Company 00000` fallback without orphan lookup errors. |
| **SC-05** | **Default Member / Orphan Fact** | `F0911_GL_Ledger.csv` | Doc 100019: `GLAID = '999999.9999'` | Surrogate key lookups safely resolve to default member `row_id = -1` ('Unknown/Not Applicable'). |
| **SC-06** | **CDC Deduplication & Window Ranking** | `F0911_GL_Ledger.csv` | Doc 777001 (Duplicate row with older `04:00Z` vs newer `07:30Z` timestamp) | `row_number() over (partition by keys order by _ingested_at desc)` discards older record and preserves latest $1,250.00 amount. |
| **SC-07A** | **Data Quality Severity: STOP** | `F0911_GL_Ledger.csv` | Doc 0 (`GLDOC = 0`) | Rule 101 halts the pipeline immediately to prevent corrupt primary keys. |
| **SC-07B** | **Data Quality Severity: QUARANTINE** | `F0911_GL_Ledger.csv`<br/>`F03B11_AR_Ledger.csv` | Doc 999901 (`GLDGJ = 124400` Day 400)<br/>Doc 999904 (`GLCO = ''` Blank Co)<br/>Doc 300099 (Due Date < Inv Date) | Diverts corrupted records into `silver.{target}_quarantine` while valid records continue flowing to Silver Lakehouse. |
| **SC-07C** | **Data Quality Severity: WARNING** | `F0911_GL_Ledger.csv` | Doc 999906 (`GLAA = 0`) | Logs audit warning to `log.dq_rule_run` without halting or quarantining. |
| **SC-08** | **Fixed Assets & Depreciation** | `F1201_Asset_Master.csv`<br/>`F1202_Asset_Balances.csv` | CNC Station (#1001), Robotic Arm (#1002) | Calculates Net Book Value = Historical Cost - Accumulated Depreciation. |
| **SC-09** | **AR Aging Buckets & Credit Memos** | `F03B11_AR_Ledger.csv` | Invoices across Current, 30-60, 61-90, 90+ days, partial pay, and Credit Memo (RM) | Feeds Power BI aging matrix and DSO (Days Sales Outstanding) measures. |
| **SC-10** | **AP Vouchers & Discounts** | `F0411_AP_Ledger.csv` | Vouchers open, paid via EFT (PK), and 2% discount taken under `210NET30` | Validates cash management, discount realization, and AP liability. |
| **SC-11** | **Real-Time Hub Automated Ingestion** | `flatfile_repo_uploads/` | Valid budget vs malformed test file (`budget_targets_malformed_test.csv`) | Tests Data Activator blob triggers and error isolation for manual user uploads. |
