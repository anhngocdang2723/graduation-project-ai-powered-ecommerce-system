import csv
import sys

csv_file = 'report/product-data/products-medusa-import-ready.csv'

def check_tags():
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        row_num = 1
        for row in reader:
            row_num += 1
            # Check Product Tag 1
            tag1 = row.get('Product Tag 1', '')
            if tag1 == 'JANSPORT':
                print(f"Row {row_num}: Product Tag 1 is JANSPORT")
            
            # Check other columns that might be confused
            for key, value in row.items():
                if value == 'JANSPORT':
                    # print(f"Row {row_num}: {key} is JANSPORT")
                    pass

            # Check if any key looks like a tag column
            for key in row.keys():
                if 'Tag' in key and row[key] == 'JANSPORT':
                     print(f"Row {row_num}: {key} is JANSPORT")

if __name__ == "__main__":
    check_tags()
