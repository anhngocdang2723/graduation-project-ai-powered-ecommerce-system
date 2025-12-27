import csv

input_file = 'report/product-data/products-medusa-import-clean.csv'
output_file = 'report/product-data/products-medusa-import-final.csv'

def deduplicate_csv():
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    seen_handles = set()
    unique_rows = []
    
    for row in rows:
        handle = row.get('Product Handle')
        if handle and handle not in seen_handles:
            seen_handles.add(handle)
            unique_rows.append(row)
        elif not handle:
            # If no handle, maybe it's a variant row? 
            # But in this CSV structure, every row seems to be a product+variant combo.
            # If it's a multi-variant product, the handle would be the same.
            # But here we have duplicate products (same title, same SKU).
            pass

    print(f"Original rows: {len(rows)}")
    print(f"Unique rows: {len(unique_rows)}")

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique_rows)
    
    print(f"Saved deduplicated CSV to {output_file}")

if __name__ == "__main__":
    deduplicate_csv()
