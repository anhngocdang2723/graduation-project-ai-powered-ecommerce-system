import csv

input_file = 'report/product-data/products-medusa-import-ready.csv'
output_file = 'report/product-data/products-medusa-import-clean.csv'

def clean_csv():
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    cleaned_rows = []
    for row in rows:
        # Remove JANSPORT from Subtitle and Material
        if row.get('Product Subtitle') == 'JANSPORT':
            row['Product Subtitle'] = ''
        if row.get('Product Material') == 'JANSPORT':
            row['Product Material'] = ''
        if row.get('Variant Material') == 'JANSPORT':
            row['Variant Material'] = ''
        
        cleaned_rows.append(row)

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_rows)
    
    print(f"Saved cleaned CSV to {output_file}")

if __name__ == "__main__":
    clean_csv()
