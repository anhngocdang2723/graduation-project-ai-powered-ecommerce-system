# Medusa CSV import helpers

The scripts in this folder help you push `report/*.csv` fixtures into the running Medusa backend before you import products.

## Prerequisites

- Python 3.11+ (or whatever the workspace uses).
- `requests` installed into your active environment: `pip install requests`.
- A valid Medusa admin token. You can either generate one through the admin UI (`Settings -> API Keys`) or re-use an existing JWT stored in `MEDUSA_ADMIN_TOKEN`.

## Available entry point

`python medusa_csv_import.py` exposes two subcommands:

### 1. categories

```
python medusa_csv_import.py categories --file report/categories-medusa.csv --admin-token <token>
```

Reads the CSV that `product_csv_to_medusa_import.py` exports (headers: `Category Name`, `Category Handle`) and posts each row to `/admin/product-categories`. Names/handles already present in the store are skipped.

### 2. tags

```
python medusa_csv_import.py tags --file report/tags-medusa.csv --admin-token <token>
```

Same as above but hits `/admin/product-tags` using headers `Tag Name` and `Tag Handle`.

### Common options

- `--base-url`: override the admin URL (defaults to `http://localhost:9000`).
- `--dry-run`: just prints what would be created without calling the API.

## Typical workflow

1. Run `python tools/product_csv_to_medusa_import.py` to generate trimmed `products-medusa-import-*.csv`, `categories-medusa.csv`, `tags-medusa.csv`.
2. Use the helper script above to create categories and tags in the Medusa admin.
3. Import `products-medusa-import-*.csv` via the Medusa admin UI (`Products -> Import products`).

If you want to automate the product import too, you could extend the script to talk to `/admin/products/imports`, but that path already exists via the web UI.
