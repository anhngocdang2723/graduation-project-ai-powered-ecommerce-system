"""Helper to load CSV fixtures into Medusa admin resources."""
from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path
from typing import Iterable, Sequence

import requests


def slugify(value: str) -> str:
    normalized = (value or "").strip().lower()
    return "-".join(filter(None, normalized.replace(" ", "-").split("-"))) or "item"


def ensure_token(token: str | None) -> str:
    if token:
        return token
    env = os.getenv("MEDUSA_ADMIN_TOKEN")
    if env:
        return env
    raise SystemExit("Missing Medusa admin token. Pass --admin-token or set MEDUSA_ADMIN_TOKEN.")


def read_rows(path: Path) -> Iterable[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            yield {k.strip(): (v or "").strip() for k, v in row.items()}


def fetch_existing_handles(session: requests.Session, url: str, key: str) -> set[str]:
    response = session.get(url)
    response.raise_for_status()
    payload = response.json()
    return {item["handle"] for item in payload.get(key, []) if item.get("handle")}


def create_categories(
    session: requests.Session, base_url: str, csv_path: Path, dry_run: bool
) -> None:
    endpoint = f"{base_url.rstrip('/')}/admin/product-categories"
    existing = fetch_existing_handles(session, endpoint, "product_categories")
    added = 0
    for row in read_rows(csv_path):
        name = row.get("Category Name") or row.get("name") or row.get("Name")
        handle = row.get("Category Handle") or row.get("handle")
        if not name:
            print("Skipping category row without a name.")
            continue
        handle = handle or slugify(name)
        if handle in existing:
            continue
        if dry_run:
            print(f"Would create category {name} ({handle})")
            added += 1
            continue
        payload = {"name": name, "handle": handle, "is_active": True}
        response = session.post(endpoint, json=payload)
        response.raise_for_status()
        existing.add(handle)
        added += 1
        print(f"Created category {name} ({handle})")
    print(f"Categories processed: {len(existing)} (created {added} new entries)")


def create_tags(session: requests.Session, base_url: str, csv_path: Path, dry_run: bool) -> None:
    endpoint = f"{base_url.rstrip('/')}/admin/product-tags"
    existing = fetch_existing_handles(session, endpoint, "product_tags")
    added = 0
    for row in read_rows(csv_path):
        name = row.get("Tag Name") or row.get("name") or row.get("Name") or row.get("Product Tag 1")
        handle = row.get("Tag Handle") or row.get("handle")
        if not name:
            print("Skipping tag row without a name.")
            continue
        handle = handle or slugify(name)
        if handle in existing:
            continue
        if dry_run:
            print(f"Would create tag {name} ({handle})")
            added += 1
            continue
        payload = {"value": name}
        # payload = {"value": name, "handle": handle, "is_active": True}
        response = session.post(endpoint, json=payload)
        if response.status_code == 400:
             print(f"Failed to create tag {name} ({handle}): {response.text}")
             continue
        response.raise_for_status()
        existing.add(handle)
        added += 1
        print(f"Created tag {name} ({handle})")
    print(f"Tags processed: {len(existing)} (created {added} new entries)")


def create_product_types(session: requests.Session, base_url: str, csv_path: Path, dry_run: bool) -> None:
    endpoint = f"{base_url.rstrip('/')}/admin/product-types"
    existing = fetch_existing_handles(session, endpoint, "product_types") # Note: types don't always have handles in v2, but let's check
    # Actually product types in v2 have 'value' and 'id'. They might not have handles.
    # Let's fetch all values.
    
    # Helper to fetch values since fetch_existing_handles assumes 'handle'
    response = session.get(endpoint, params={"limit": 1000})
    response.raise_for_status()
    existing_values = {item["value"] for item in response.json().get("product_types", [])}

    added = 0
    for row in read_rows(csv_path):
        # In the CSV, we have 'Product Type Id' which holds the value like 'new-season'
        val = row.get("Product Type Id")
        if not val:
            continue
        
        if val in existing_values:
            continue

        if dry_run:
            print(f"Would create type {val}")
            added += 1
            continue

        payload = {"value": val}
        response = session.post(endpoint, json=payload)
        if response.status_code == 400:
             print(f"Failed to create type {val}: {response.text}")
             continue
        response.raise_for_status()
        existing_values.add(val)
        added += 1
        print(f"Created type {val}")
    print(f"Types processed: {len(existing_values)} (created {added} new entries)")

def main() -> None:
    parser = argparse.ArgumentParser(description="Load Medusa categories/tags from CSV files")
    parser.add_argument("--base-url", default="http://localhost:9000", help="Medusa admin base URL")
    parser.add_argument(
        "--admin-token",
        help="Admin API token (falls back to MEDUSA_ADMIN_TOKEN)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Don't actually call the API")

    subparsers = parser.add_subparsers(dest="command", required=True)
    cat_parser = subparsers.add_parser("categories", help="Import categories")
    cat_parser.add_argument("file", type=Path, help="CSV with Category Name/Category Handle columns")
    tag_parser = subparsers.add_parser("tags", help="Import tags")
    tag_parser.add_argument("file", type=Path, help="CSV with Tag Name/Tag Handle columns")
    type_parser = subparsers.add_parser("types", help="Import product types")
    type_parser.add_argument("file", type=Path, help="CSV with Product Type Id column")

    args = parser.parse_args()
    token = ensure_token(args.admin_token)
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}"})

    if args.command == "categories":
        create_categories(session, args.base_url, args.file, args.dry_run)
    elif args.command == "tags":
        create_tags(session, args.base_url, args.file, args.dry_run)
    elif args.command == "types":
        create_product_types(session, args.base_url, args.file, args.dry_run)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
