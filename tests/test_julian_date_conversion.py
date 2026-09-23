"""
# -------------------------------------------------------------------------------------------------
# Unit Tests: Julian Date Conversion
# Verifies enterprise boundary handling for JD Edwards CYYDDD format across leap years and centuries
# -------------------------------------------------------------------------------------------------
"""

import pytest
from datetime import date, timedelta

def julian_to_gregorian(julian_int: int) -> date:
    """
    Python reference implementation of the PySpark CYYDDD conversion logic.
    """
    if julian_int is None or julian_int <= 0:
        return None
        
    century_digit = julian_int // 100000
    year_two_digit = (julian_int % 100000) // 1000
    day_of_year = julian_int % 1000
    
    full_year = 1900 + (century_digit * 100) + year_two_digit
    
    # 1st Jan of the calculated year + (day_of_year - 1)
    base_date = date(full_year, 1, 1)
    return base_date + timedelta(days=day_of_year - 1)

def test_millennium_boundary():
    # 099365 -> 1999-12-31
    assert julian_to_gregorian(99365) == date(1999, 12, 31)
    # 100001 -> 2000-01-01 (Y2K Boundary)
    assert julian_to_gregorian(100001) == date(2000, 1, 1)

def test_leap_year_handling():
    # 2024 is a leap year (366 days)
    # 124060 -> 2024-02-29
    assert julian_to_gregorian(124060) == date(2024, 2, 29)
    # 124061 -> 2024-03-01
    assert julian_to_gregorian(124061) == date(2024, 3, 1)

def test_current_year_2026():
    # 126001 -> 2026-01-01
    assert julian_to_gregorian(126001) == date(2026, 1, 1)
    # 126266 -> 2026-09-23
    assert julian_to_gregorian(126266) == date(2026, 9, 23)

def test_null_and_zero_inputs():
    assert julian_to_gregorian(0) is None
    assert julian_to_gregorian(-1) is None
    assert julian_to_gregorian(None) is None
