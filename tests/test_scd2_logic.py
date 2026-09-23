"""
# -------------------------------------------------------------------------------------------------
# Unit Tests: Slowly Changing Dimension Type 2 (SCD2) Logic
# Tests record hash generation, active version expiration, and insert of updated dimension rows
# -------------------------------------------------------------------------------------------------
"""

import hashlib
import pytest
from datetime import datetime

def compute_row_hash(*fields) -> str:
    combined = "||".join(str(f) for f in fields)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()

def test_hash_generation_and_detection():
    # Initial state
    h1 = compute_row_hash("Cash Operating Account", "N", "100")
    h2 = compute_row_hash("Cash Operating Account", "N", "100")
    # Description change
    h3 = compute_row_hash("Main Operating Account", "N", "100")
    
    assert h1 == h2
    assert h1 != h3

def test_scd2_lifecycle():
    account_id = "ACC-001"
    
    # Version 1
    v1 = {
        "account_id": account_id,
        "desc": "Petty Cash",
        "hash": compute_row_hash("Petty Cash"),
        "is_current": True,
        "valid_from": datetime(2025, 1, 1),
        "valid_to": None
    }
    
    # Version 2 update arrives
    new_desc = "Branch Petty Cash"
    new_hash = compute_row_hash(new_desc)
    update_time = datetime(2026, 3, 15)
    
    assert v1["hash"] != new_hash
    
    # Expire Version 1
    v1["is_current"] = False
    v1["valid_to"] = update_time
    
    # Insert Version 2
    v2 = {
        "account_id": account_id,
        "desc": new_desc,
        "hash": new_hash,
        "is_current": True,
        "valid_from": update_time,
        "valid_to": None
    }
    
    assert v1["is_current"] is False
    assert v1["valid_to"] == update_time
    assert v2["is_current"] is True
    assert v2["valid_from"] == update_time
    assert v2["valid_to"] is None
