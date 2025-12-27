import csv
import requests
import sys
import json

BASE_URL = "http://localhost:9000"
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY3Rvcl9pZCI6InVzZXJfMDFLQ0JIOU5LNFZOV1AzVDAzMUtHQ0VWMFMiLCJhY3Rvcl90eXBlIjoidXNlciIsImF1dGhfaWRlbnRpdHlfaWQiOiJhdXRoaWRfMDFLQ0JIOU5RUTkzNEVNR1RaMzdTODIxRkoiLCJhcHBfbWV0YWRhdGEiOnsidXNlcl9pZCI6InVzZXJfMDFLQ0JIOU5LNFZOV1AzVDAzMUtHQ0VWMFMifSwidXNlcl9tZXRhZGF0YSI6e30sImlhdCI6MTc2NTYzODkxNSwiZXhwIjoxNzY1NzI1MzE1fQ.czxdeobiXTKYXiS2QRsmsfwtOiF3Q-rJqPUTDDLW68Y"

HEADERS = {
    "Authorization": f"Bearer {ADMIN_TOKEN}",
    "Content-Type": "application/json"
}

def fetch_all(endpoint):
    items = []
    offset = 0
    limit = 100
    while True:
        response = requests.get(f"{BASE_URL}/admin/{endpoint}?limit={limit}&offset={offset}", headers=HEADERS)
        if response.status_code != 200:
            print(f"Error fetching {endpoint}: {response.text}")
            break
        data = response.json()
        batch = data.get(endpoint.replace("-", "_"), []) # e.g. product-tags -> product_tags
        if not batch:
            break
        items.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
    return items

def main():
    print("Fetching tags...")
    tags = fetch_all("product-tags")
    tag_map = {t["value"]: t["id"] for t in tags}
    print(f"Found {len(tag_map)} tags.")

    print("Fetching product types...")
    types = fetch_all("product-types")
    type_map = {t["value"]: t["id"] for t in types}
    print(f"Found {len(type_map)} types.")
    
    print("Fetching sales channels...")
    scs = fetch_all("sales-channels")
    sc_map = {sc["name"]: sc["id"] for sc in scs}
    # Add default handle mapping if needed
    for sc in scs:
        if sc.get("name") == "Default Sales Channel":
             sc_map["default"] = sc["id"]
    print(f"Found {len(sc_map)} sales channels.")

    input_file = "report/product-data/products-medusa-import-slim.csv"
    output_file = "report/product-data/products-medusa-import-ready.csv"

    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if fieldnames is None:
            print("Error: CSV file has no headers")
            return
        rows = list(reader)

    updated_rows = []
    for row in rows:
        # Map Tag
        tag_val = row.get("Product Tag 1")
        if tag_val and tag_val in tag_map:
            row["Product Tag 1"] = tag_map[tag_val]
        
        # Map Type
        # The CSV has 'new-season' as Type ID, but maybe that's the value?
        # Let's check if we have a type with value 'new-season'
        type_val = row.get("Product Type Id")
        if type_val:
             # Try to find by value
             if type_val in type_map:
                 row["Product Type Id"] = type_map[type_val]
             # If not found, maybe create it? Or maybe it's already an ID?
             # For now let's assume it's a value we need to map.
        
        # Map Sales Channel
        sc_val = row.get("Product Sales Channel 1")
        if sc_val and sc_val in sc_map:
            row["Product Sales Channel 1"] = sc_map[sc_val]

        updated_rows.append(row)

    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)
    
    print(f"Saved updated CSV to {output_file}")

if __name__ == "__main__":
    main()
