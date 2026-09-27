"""
Generates the pre-validated Excel metadata template workbook: Ingestion_metadata_load_template.xlsx
Contains all 9 official Excel tables (tbl_*) mirroring the stage.* schema in sqldb-meta-orch-dev.
"""

import openpyxl
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
# Remove default sheet
wb.remove(wb.active)

sheets_config = [
    {
        "sheet_name": "source_system",
        "table_name": "tbl_source_system",
        "headers": ["source_system_code", "source_system_name", "source_system_type", "is_active"],
        "rows": [
            ["AS400_DB2", "IBM AS400 Production DB2", "AS400", "TRUE"],
            ["SFDC", "Salesforce CRM", "REST_API", "TRUE"],
            ["FLAT_FILE", "SFTP Flat Files Landing", "File", "TRUE"]
        ]
    },
    {
        "sheet_name": "schedule",
        "table_name": "tbl_schedule",
        "headers": ["schedule_name", "frequency_type", "frequency_interval", "cron_expression", "start_datetime", "end_datetime", "timezone_name", "is_active"],
        "rows": [
            ["SCH_BATCH_TWICE_DAILY", "Daily", "1", "0 9,17 * * *", "2026-01-01 00:00:00", "", "Central European Standard Time", "TRUE"],
            ["SCH_NRT_10MIN", "Hourly", "1", "*/10 * * * *", "2026-01-01 00:00:00", "", "UTC", "TRUE"]
        ]
    },
    {
        "sheet_name": "ingestion_group",
        "table_name": "tbl_ingestion_group",
        "headers": ["group_code", "group_name", "group_description", "schedule_name", "orchestration_mode", "is_active"],
        "rows": [
            ["IG_AS400_BATCH_DIM", "AS400 Dimensions Batch Group", "Master lookup and dimension tables loaded twice daily", "SCH_BATCH_TWICE_DAILY", "Batch", "TRUE"],
            ["IG_AS400_BATCH_FACT", "AS400 Facts Batch Group", "Transactional fact ledgers loaded incrementally", "SCH_BATCH_TWICE_DAILY", "Batch", "TRUE"],
            ["IG_AS400_NRT_DIM", "AS400 NRT Dimensions", "Near real-time master entities via CDC shortcut", "SCH_NRT_10MIN", "NRT", "TRUE"],
            ["IG_AS400_NRT_FACT", "AS400 NRT Facts", "Near real-time AR/AP ledgers via CDC shortcut", "SCH_NRT_10MIN", "NRT", "TRUE"]
        ]
    },
    {
        "sheet_name": "dataset",
        "table_name": "tbl_dataset",
        "headers": ["source_system_code", "dataset_name", "dataset_description", "target_silver_table_name", "target_gold_table_name", "is_active"],
        "rows": [
            ["AS400_DB2", "F0911_General_Ledger", "JDE General Ledger transactional entries", "silver_f0911_gl_ledger", "fact_gl_ledger", "TRUE"],
            ["AS400_DB2", "F0901_Account_Master", "Chart of Accounts master definition", "silver_f0901_account_master", "dim_account", "TRUE"],
            ["AS400_DB2", "F0010_Company_Constants", "Company codes and currency definitions", "silver_f0010_company_constants", "dim_company", "TRUE"],
            ["AS400_DB2", "F03B11_AR_Ledger", "Accounts Receivable customer ledger", "silver_f03b11_ar_ledger", "fact_ar_ledger", "TRUE"],
            ["AS400_DB2", "F0411_AP_Ledger", "Accounts Payable supplier ledger", "silver_f0411_ap_ledger", "fact_ap_ledger", "TRUE"],
            ["AS400_DB2", "F1201_Asset_Master", "Fixed Asset master registry", "silver_f1201_asset_master", "dim_asset", "TRUE"]
        ]
    },
    {
        "sheet_name": "ingestion_group_dataset",
        "table_name": "tbl_ingestion_group_dataset",
        "headers": ["group_code", "dataset_name", "is_mandatory_flag", "is_active", "effective_from"],
        "rows": [
            ["IG_AS400_BATCH_DIM", "F0901_Account_Master", "TRUE", "TRUE", "2026-01-01 00:00:00"],
            ["IG_AS400_BATCH_DIM", "F0010_Company_Constants", "TRUE", "TRUE", "2026-01-01 00:00:00"],
            ["IG_AS400_BATCH_DIM", "F1201_Asset_Master", "TRUE", "TRUE", "2026-01-01 00:00:00"],
            ["IG_AS400_BATCH_FACT", "F0911_General_Ledger", "TRUE", "TRUE", "2026-01-01 00:00:00"],
            ["IG_AS400_NRT_FACT", "F03B11_AR_Ledger", "TRUE", "TRUE", "2026-01-01 00:00:00"],
            ["IG_AS400_NRT_FACT", "F0411_AP_Ledger", "TRUE", "TRUE", "2026-01-01 00:00:00"]
        ]
    },
    {
        "sheet_name": "dataset_src_to_brnz",
        "table_name": "tbl_dataset_src_to_brnz",
        "headers": [
            "dataset_name", "source_schema_name", "source_table_name", "source_query", 
            "source_container_or_path", "source_file_pattern", "source_file_path", "source_file_name",
            "column_delimiter", "row_delimiter", "destination_path", "destination_file_name_prefix",
            "destination_file_type", "bronze_schema_name", "bronze_table_name", "use_explicit_mapping",
            "key_columns", "source_watermark_column"
        ],
        "rows": [
            ["F0911_General_Ledger", "CRPOTA", "F0911", "", "", "", "", "", "", "", "bronze/as400/f0911/", "f0911_raw", "PARQUET", "bronze", "raw_f0911_gl_ledger", "FALSE", "GLKCO,GLDCT,GLDOC,GLDGJ,GLJELN", "GLUPMJ"],
            ["F0901_Account_Master", "CRPOTA", "F0901", "", "", "", "", "", "", "", "bronze/as400/f0901/", "f0901_raw", "PARQUET", "bronze", "raw_f0901_account_master", "FALSE", "GMAID", "GMUPMJ"],
            ["F0010_Company_Constants", "CRPOTA", "F0010", "", "", "", "", "", "", "", "bronze/as400/f0010/", "f0010_raw", "PARQUET", "bronze", "raw_f0010_company_constants", "FALSE", "CCCO", ""],
            ["F03B11_AR_Ledger", "CRPOTA", "F03B11", "", "", "", "", "", "", "", "bronze/as400/f03b11/", "f03b11_raw", "PARQUET", "bronze", "raw_f03b11_ar_ledger", "FALSE", "RPDOC,RPDCT,RPKCO,RPSFX", "RPUPMJ"],
            ["F0411_AP_Ledger", "CRPOTA", "F0411", "", "", "", "", "", "", "", "bronze/as400/f0411/", "f0411_raw", "PARQUET", "bronze", "raw_f0411_ap_ledger", "FALSE", "RPDOC,RPDCT,RPKCO,RPSFX", "RPUPMJ"],
            ["F1201_Asset_Master", "CRPOTA", "F1201", "", "", "", "", "", "", "", "bronze/as400/f1201/", "f1201_raw", "PARQUET", "bronze", "raw_f1201_asset_master", "FALSE", "FANUMB", "FAUPMJ"]
        ]
    },
    {
        "sheet_name": "dataset_brnz_to_silver",
        "table_name": "tbl_dataset_brnz_to_silver",
        "headers": [
            "dataset_name", "source_table_lakehouse", "source_table_schema", "source_table_name",
            "target_table_lakehouse", "target_table_schema", "target_table_name", "key_columns",
            "is_incremental", "duplication_check", "notebook_pattern"
        ],
        "rows": [
            ["F0911_General_Ledger", "lh_ips_bronze", "dbo", "raw_f0911_gl_ledger", "lh_ips_silver", "dbo", "silver_f0911_gl_ledger", "GLKCO,GLDCT,GLDOC,GLDGJ,GLJELN", "TRUE", "TRUE", "nb_silver_cleansing_dq"],
            ["F0901_Account_Master", "lh_ips_bronze", "dbo", "raw_f0901_account_master", "lh_ips_silver", "dbo", "silver_f0901_account_master", "GMAID", "FALSE", "TRUE", "nb_silver_scd2_dimensions"],
            ["F0010_Company_Constants", "lh_ips_bronze", "dbo", "raw_f0010_company_constants", "lh_ips_silver", "dbo", "silver_f0010_company_constants", "CCCO", "FALSE", "TRUE", "nb_silver_cleansing_dq"],
            ["F03B11_AR_Ledger", "lh_ips_bronze", "dbo", "raw_f03b11_ar_ledger", "lh_ips_silver", "dbo", "silver_f03b11_ar_ledger", "RPDOC,RPDCT,RPKCO,RPSFX", "TRUE", "TRUE", "nb_silver_cleansing_dq"],
            ["F0411_AP_Ledger", "lh_ips_bronze", "dbo", "raw_f0411_ap_ledger", "lh_ips_silver", "dbo", "silver_f0411_ap_ledger", "RPDOC,RPDCT,RPKCO,RPSFX", "TRUE", "TRUE", "nb_silver_cleansing_dq"],
            ["F1201_Asset_Master", "lh_ips_bronze", "dbo", "raw_f1201_asset_master", "lh_ips_silver", "dbo", "silver_f1201_asset_master", "FANUMB", "FALSE", "TRUE", "nb_silver_cleansing_dq"]
        ]
    },
    {
        "sheet_name": "dataset_silver_to_gold",
        "table_name": "tbl_dataset_silver_to_gold",
        "headers": [
            "dataset_name", "source_table_lakehouse", "target_table_name", "key_columns",
            "surrogate_key_column_name", "load_type_dim_or_fact", "load_order", "load_sp_name"
        ],
        "rows": [
            ["F0901_Account_Master", "lh_ips_silver", "dim_account", "account_id", "account_sk", "Dimension", "10", ""],
            ["F0010_Company_Constants", "lh_ips_silver", "dim_company", "company_code", "company_sk", "Dimension", "10", ""],
            ["F1201_Asset_Master", "lh_ips_silver", "dim_asset", "asset_number", "asset_sk", "Dimension", "10", ""],
            ["F0911_General_Ledger", "lh_ips_silver", "fact_gl_ledger", "company_key,doc_type,doc_number,journal_line_number", "gl_fact_sk", "Fact", "20", ""],
            ["F03B11_AR_Ledger", "lh_ips_silver", "fact_ar_ledger", "doc_number,doc_type,company_key,doc_suffix", "ar_fact_sk", "Fact", "20", ""],
            ["F0411_AP_Ledger", "lh_ips_silver", "fact_ap_ledger", "doc_number,doc_type,company_key,doc_suffix", "ap_fact_sk", "Fact", "20", ""]
        ]
    },
    {
        "sheet_name": "dataquality_rule",
        "table_name": "tbl_dataquality_rule",
        "headers": [
            "dataset_name", "rule_name", "rule_type", "rule_expression",
            "severity_code", "threshold_percent", "on_failure_action"
        ],
        "rows": [
            ["F0911_General_Ledger", "DQ_GL_ACCOUNT_NOT_NULL", "NullCheck", "account_number IS NOT NULL AND account_number != ''", "REJECT", "0.00", "Quarantine Rows"],
            ["F0911_General_Ledger", "DQ_GL_DATE_RANGE", "RangeCheck", "accounting_date >= '2000-01-01' AND accounting_date <= '2030-12-31'", "REJECT", "0.00", "Quarantine Rows"],
            ["F0911_General_Ledger", "DQ_GL_AMOUNT_NOT_NULL", "NullCheck", "amount_domestic IS NOT NULL", "WARN", "1.00", "Warn"],
            ["F0901_Account_Master", "DQ_ACC_ID_NOT_NULL", "NullCheck", "account_id IS NOT NULL", "STOP", "0.00", "Abort Pipeline"],
            ["F03B11_AR_Ledger", "DQ_AR_DOC_NOT_NULL", "NullCheck", "doc_number IS NOT NULL AND doc_number > 0", "REJECT", "0.00", "Quarantine Rows"],
            ["F0411_AP_Ledger", "DQ_AP_DOC_NOT_NULL", "NullCheck", "doc_number IS NOT NULL AND doc_number > 0", "REJECT", "0.00", "Quarantine Rows"]
        ]
    }
]

header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
cell_font = Font(name="Segoe UI", size=10)
thin_border = Border(
    left=Side(style='thin', color='D9D9D9'),
    right=Side(style='thin', color='D9D9D9'),
    top=Side(style='thin', color='D9D9D9'),
    bottom=Side(style='thin', color='D9D9D9')
)

for cfg in sheets_config:
    ws = wb.create_sheet(title=cfg["sheet_name"])
    ws.views.sheetView[0].showGridLines = True
    
    # Headers
    ws.append(cfg["headers"])
    for col_num in range(1, len(cfg["headers"]) + 1):
        cell = ws.cell(row=1, column=col_num)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # Rows
    for row in cfg["rows"]:
        ws.append(row)
        row_idx = ws.max_row
        for col_num in range(1, len(row) + 1):
            c = ws.cell(row=row_idx, column=col_num)
            c.font = cell_font
            c.border = thin_border
            
    # Convert range to Excel Table
    end_col_letter = get_column_letter(len(cfg["headers"]))
    max_row = max(ws.max_row, 2)
    tab_ref = f"A1:{end_col_letter}{max_row}"
    tab = Table(displayName=cfg["table_name"], ref=tab_ref)
    style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False, showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    tab.tableStyleInfo = style
    ws.add_table(tab)
    
    # Adjust column widths
    for col_cells in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col_cells)
        col_letter = get_column_letter(col_cells[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 14)

output_path = "/Users/chandu/Documents/Python_practice/Fabric/data/metadata/Ingestion_metadata_load_template.xlsx"
wb.save(output_path)
print(f"Successfully generated: {output_path}")
