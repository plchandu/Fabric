#!/usr/bin/env python3
"""
# -------------------------------------------------------------------------------------------------
# Deployment Script: validate_repo.py
# Purpose: Pre-deployment static audit gate for Microsoft Fabric CI/CD.
# Checks:
#   1. Format Enforcement: Rejects forbidden .ipynb files in src/notebooks/ (enforces .py).
#   2. Anti-Hardcoding Audit: Detects hardcoded secrets, connection passwords, SAS tokens, API keys.
#   3. Parameter Schema Consistency: Validates parameter-*.yml configs across DEV, UAT, and PROD.
#   4. Syntax Validation: Ensures all Python scripts compile cleanly without syntax errors.
# Exit Code: 0 on success, 1 on audit failure.
# -------------------------------------------------------------------------------------------------
"""

import os
import sys
import re
import yaml
import py_compile
from pathlib import Path

# Base repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Regex patterns for anti-hardcoding secret detection
FORBIDDEN_PATTERNS = [
    (r"(?i)password\s*=\s*['\"][^'\"]{4,}['\"]", "Hardcoded plain-text password detected"),
    (r"(?i)client_secret\s*=\s*['\"][a-zA-Z0-9_\-~.]{8,}['\"]", "Hardcoded Azure Client Secret detected"),
    (r"\bAccountKey=[a-zA-Z0-9+/=]{40,}\b", "Hardcoded Azure Storage Account Key detected"),
    (r"\bSharedAccessSignature=\?sv=[^\s'\"]+\b", "Hardcoded Azure Storage SAS token detected"),
    (r"\bDefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[^;]+", "Hardcoded Azure Storage Connection String detected"),
    (r"(?i)bearer\s+[a-zA-Z0-9_\-\.]{50,}", "Hardcoded OAuth Bearer Token detected"),
]

# Allowed file extensions to scan for secrets
SCAN_EXTENSIONS = {".py", ".json", ".yml", ".yaml", ".sql", ".tmdl"}

# Directories to exclude from secret scans
EXCLUDE_DIRS = {".git", ".pytest_cache", ".vscode", "__pycache__", "venv", ".venv", "images"}


def check_forbidden_notebook_formats(repo_root: Path) -> list:
    """Enforces Tenet 10: PySpark notebooks must be serialized as .py, never .ipynb."""
    errors = []
    notebooks_dir = repo_root / "src" / "notebooks"
    if notebooks_dir.exists():
        for path in notebooks_dir.rglob("*.ipynb"):
            errors.append(
                f"[FORMAT VIOLATION] Forbidden Jupyter Notebook found: '{path.relative_to(repo_root)}'. "
                "PySpark notebooks must be serialized as '.py' files with '# %%' cell comments."
            )
    return errors


def check_anti_hardcoding(repo_root: Path) -> list:
    """Scans all code and config files for embedded secrets and connection credentials."""
    errors = []
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() not in SCAN_EXTENSIONS:
                continue

            # Skip checking the validator itself
            if file == "validate_repo.py":
                continue

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, start=1):
                        for pattern, description in FORBIDDEN_PATTERNS:
                            if re.search(pattern, line):
                                # Permit variable assignment from os.environ or sys.argv
                                if "os.environ" in line or "os.getenv" in line or "secrets." in line:
                                    continue
                                rel_path = file_path.relative_to(repo_root)
                                errors.append(
                                    f"[SECURITY VIOLATION] {description} in {rel_path}:{line_num}\n"
                                    f"  --> Line content: {line.strip()[:80]}..."
                                )
            except Exception as e:
                errors.append(f"[IO ERROR] Failed to read {file_path.relative_to(repo_root)}: {str(e)}")
    return errors


def check_parameter_configs(repo_root: Path) -> list:
    """Validates that parameter-dev, uat, and prod yml files exist and have consistent structures."""
    errors = []
    config_dir = repo_root / "deployment" / "config"
    required_envs = ["dev", "uat", "prod"]
    expected_top_keys = {"environment", "workspace", "lakehouses", "sql_databases", "key_vault", "gateway", "variable_library"}

    for env in required_envs:
        cfg_file = config_dir / f"parameter-{env}.yml"
        if not cfg_file.exists():
            errors.append(f"[CONFIG MISSING] Required environment config missing: {cfg_file.relative_to(repo_root)}")
            continue

        try:
            with open(cfg_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if not isinstance(data, dict):
                    errors.append(f"[CONFIG ERROR] {cfg_file.name} is not a valid YAML dictionary mapping.")
                    continue

                missing_keys = expected_top_keys - set(data.keys())
                if missing_keys:
                    errors.append(f"[CONFIG MISMATCH] {cfg_file.name} is missing expected top-level keys: {missing_keys}")
        except Exception as e:
            errors.append(f"[YAML ERROR] Failed to parse {cfg_file.name}: {str(e)}")

    return errors


def check_python_syntax(repo_root: Path) -> list:
    """Ensures all Python files compile cleanly without syntax errors."""
    errors = []
    scan_folders = [repo_root / "src", repo_root / "deployment", repo_root / "tests"]
    for folder in scan_folders:
        if not folder.exists():
            continue
        for py_file in folder.rglob("*.py"):
            try:
                py_compile.compile(str(py_file), doraise=True)
            except py_compile.PyCompileError as e:
                errors.append(f"[SYNTAX ERROR] Failed to compile {py_file.relative_to(repo_root)}: {str(e)}")
    return errors


def main():
    print("=" * 80)
    print("  MICROSOFT FABRIC CI/CD PRE-DEPLOYMENT AUDIT GATE (validate_repo.py)")
    print(f"  Repository Root: {REPO_ROOT}")
    print("=" * 80)

    all_errors = []

    print("[Step 1/4] Checking notebook serialization format...")
    format_errors = check_forbidden_notebook_formats(REPO_ROOT)
    all_errors.extend(format_errors)
    print(f"  --> Format Errors: {len(format_errors)}")

    print("[Step 2/4] Scanning for hardcoded credentials & secrets...")
    security_errors = check_anti_hardcoding(REPO_ROOT)
    all_errors.extend(security_errors)
    print(f"  --> Security / Secret Errors: {len(security_errors)}")

    print("[Step 3/4] Validating environment parameter configurations...")
    config_errors = check_parameter_configs(REPO_ROOT)
    all_errors.extend(config_errors)
    print(f"  --> Configuration Errors: {len(config_errors)}")

    print("[Step 4/4] Checking Python syntax compilation...")
    syntax_errors = check_python_syntax(REPO_ROOT)
    all_errors.extend(syntax_errors)
    print(f"  --> Syntax Errors: {len(syntax_errors)}")

    print("-" * 80)
    if all_errors:
        print(f"FAILED: Pre-deployment audit identified {len(all_errors)} blocking issue(s):\n")
        for i, err in enumerate(all_errors, start=1):
            print(f"{i}. {err}\n")
        print("Please resolve all violations before merging or deploying to production.")
        sys.exit(1)
    else:
        print("SUCCESS: All pre-deployment audits passed successfully! Ready for deployment.")
        sys.exit(0)


if __name__ == "__main__":
    main()
