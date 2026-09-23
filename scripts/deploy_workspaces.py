#!/usr/bin/env python3
"""
# -------------------------------------------------------------------------------------------------
# Script: deploy_workspaces.py
# Description: Automated deployment of Microsoft Fabric Medallion Workspaces & Lakehouses
#              using the Microsoft Fabric REST API (https://api.fabric.microsoft.com/v1).
# -------------------------------------------------------------------------------------------------
"""

import os
import sys
import json
import requests

FABRIC_API_BASE = "https://api.fabric.microsoft.com/v1"

def get_fabric_token():
    token = os.environ.get("FABRIC_TOKEN")
    if not token:
        print("ERROR: FABRIC_TOKEN environment variable is not set.", file=sys.stderr)
        print("Run: export FABRIC_TOKEN=$(az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv)", file=sys.stderr)
        sys.exit(1)
    return token

def create_workspace(token: str, display_name: str) -> str:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    # Check if already exists
    res = requests.get(f"{FABRIC_API_BASE}/workspaces", headers=headers)
    if res.status_code == 200:
        for ws in res.json().get("value", []):
            if ws.get("displayName") == display_name:
                print(f"[EXISTS] Workspace '{display_name}' already exists with ID: {ws['id']}")
                return ws["id"]
                
    payload = {"displayName": display_name}
    res = requests.post(f"{FABRIC_API_BASE}/workspaces", headers=headers, json=payload)
    if res.status_code in [200, 201]:
        ws_id = res.json().get("id")
        print(f"[CREATED] Workspace '{display_name}' created successfully with ID: {ws_id}")
        return ws_id
    else:
        print(f"[ERROR] Failed to create workspace '{display_name}': {res.status_code} - {res.text}", file=sys.stderr)
        return None

def create_lakehouse(token: str, workspace_id: str, display_name: str, description: str = "") -> str:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "displayName": display_name,
        "description": description
    }
    res = requests.post(f"{FABRIC_API_BASE}/workspaces/{workspace_id}/lakehouses", headers=headers, json=payload)
    if res.status_code in [200, 201]:
        lh_id = res.json().get("id")
        print(f"  [CREATED] Lakehouse '{display_name}' created in workspace {workspace_id}")
        return lh_id
    else:
        print(f"  [ERROR] Failed to create Lakehouse '{display_name}': {res.status_code} - {res.text}", file=sys.stderr)
        return None

def main():
    print("==================================================================")
    print(" Microsoft Fabric Medallion Architecture Auto-Provisioning       ")
    print(" Target Region: South India (Chennai) / Central India (Pune)     ")
    print("==================================================================")
    
    token = get_fabric_token()
    
    workspaces = [
        {"name": "ws_ips_erp_bronze", "lakehouse": "lh_ips_bronze", "desc": "Raw AS400 DB2 ERP Ingestion Landing"},
        {"name": "ws_ips_erp_silver", "lakehouse": "lh_ips_silver", "desc": "Cleansed & SCD2 Conformed Delta Tables"},
        {"name": "ws_ips_erp_gold", "lakehouse": "lh_ips_gold", "desc": "Star Schema Mart & Power BI Direct Lake"}
    ]
    
    created_map = {}
    for item in workspaces:
        ws_id = create_workspace(token, item["name"])
        if ws_id:
            created_map[item["name"]] = ws_id
            create_lakehouse(token, ws_id, item["lakehouse"], item["desc"])
            
    print("\n[SUMMARY] Workspace GUIDs for configuration:")
    for name, guid in created_map.items():
        print(f"export {name.upper()}_ID=\"{guid}\"")

if __name__ == "__main__":
    main()
