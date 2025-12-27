"""Convert a generic product CSV into Medusa's import template."""
from __future__ import annotations

import argparse
import csv
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, Iterable, List


def slugify(value: str) -> str:
    """Make a URL-friendly slug using alphanumeric characters."""
    normalized = (value or "").strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return slug or "product"


def parse_price(value: str | None) -> Decimal:
    """Parse a number stored as text, returning zero when parsing fails."""
    if not value:
        return Decimal(0)
    try:
        return Decimal(value)
    except InvalidOperation:
        cleaned = value.replace(",", "").strip()
        try:
            return Decimal(cleaned)
        except InvalidOperation:
            return Decimal(0)


def describe_product(product: Dict[str, str]) -> str:
    """Build a lightweight description from available attributes."""
    parts = []
    title = product.get("title")
    brand = product.get("brand")
    if title and brand:
        parts.append(f"{title} by {brand}")
    elif title:
        parts.append(title)
    if category := product.get("category"):
        parts.append(f"Category: {category}")
    if rating := product.get("rating"):
        parts.append(f"Rated {rating} stars")
    if product_url := product.get("product_url"):
        parts.append(f"Shop: {product_url}")
    return ". ".join(parts) or "Imported product from source data."


def build_medusa_row(
    product: Dict[str, str],
    defaults: Dict[str, str],
    eur_rate: Decimal,
) -> Dict[str, str]:
    raw_title = (product.get("title") or "").strip()
    brand = (product.get("brand") or "").strip()
    image_url = product.get("image_url") or ""
    product_id = (product.get("product_id") or "").strip()
    if not product_id:
        product_id = slugify(raw_title or brand)
    price_usd = parse_price(product.get("price"))

    final_title = raw_title or brand or product_id or "Imported Product"
    handle = slugify(f"{final_title}-{product_id}")
    description = describe_product(product)
    price_eur = (price_usd * eur_rate).quantize(Decimal("0.01"))
    price_usd = price_usd.quantize(Decimal("0.01"))

    row = {
        "Product Id": "",
        "Product Handle": handle,
        "Product Title": final_title,
        "Product Subtitle": brand,
        "Product Description": description,
        "Product Status": "published",
        "Product Thumbnail": image_url,
        "Product Weight": defaults["product_weight"],
        "Product Length": "",
        "Product Width": "",
        "Product Height": "",
        "Product HS Code": "",
        "Product Origin Country": "",
        "Product MID Code": "",
        "Product Material": brand,
        "Shipping Profile Id": defaults["shipping_profile"],
        "Product Sales Channel 1": defaults["sales_channel"],
        "Product Collection Id": "",
        "Product Type Id": slugify(product.get("category") or ""),
        "Product Tag 1": brand or product.get("category", ""),
        "Product Discountable": "TRUE",
        "Product External Id": product_id,
        "Variant Id": "",
        "Variant Title": final_title,
        "Variant SKU": product_id,
        "Variant Barcode": product_id,
        "Variant Allow Backorder": "FALSE",
        "Variant Manage Inventory": "TRUE",
        "Variant Weight": defaults["variant_weight"],
        "Variant Length": "",
        "Variant Width": "",
        "Variant Height": "",
        "Variant HS Code": "",
        "Variant Origin Country": "",
        "Variant MID Code": "",
        "Variant Material": brand,
        "Variant Price EUR": f"{price_eur}",
        "Variant Price USD": f"{price_usd}",
        "Variant Option 1 Name": "Variant",
        "Variant Option 1 Value": "Default",
        "Product Image 1 Url": image_url,
        "Product Image 2 Url": "",
    }
    return row


def select_products(
    products: Iterable[Dict[str, str]],
    max_total: int,
    max_per_category: int,
) -> tuple[list[Dict[str, str]], list[str]]:
    """Sample a subset of products per category until we hit the global limit."""
    if max_total <= 0 or max_per_category <= 0:
        return [], []

    grouped: Dict[str, list[Dict[str, str]]] = {}
    order: list[str] = []
    for product in products:
        raw_category = (product.get("category") or "").strip()
        category = raw_category or "Uncategorized"
        if category not in grouped:
            grouped[category] = []
            order.append(category)
        grouped[category].append(product)

    selected: list[Dict[str, str]] = []
    selected_categories: list[str] = []
    remaining = max_total
    for category in order:
        if remaining <= 0:
            break
        bucket = grouped[category]
        to_take = min(len(bucket), max_per_category, remaining)
        if not to_take:
            continue
        selected.extend(bucket[:to_take])
        selected_categories.append(category)
        remaining -= to_take

    return selected, selected_categories


def write_categories_csv(categories: list[str], output_path: Path) -> None:
    """Persist the categories we sampled so they can be created in Medusa."""
    if not categories:
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Category Name", "Category Handle"])
        for category in categories:
            writer.writerow([category, slugify(category)])


def write_tags_csv(tags: list[str], output_path: Path) -> None:
    """Persist brand tags so Medusa can preload them."""
    if not tags:
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Tag Name", "Tag Handle"])
        for tag in tags:
            writer.writerow([tag, slugify(tag)])


def load_template_header(template_path: Path) -> List[str]:
    with template_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        for header in reader:
            if header:
                return header
    raise ValueError("Template file is empty or missing a header row.")


def convert(
    dataset_path: Path,
    template_path: Path,
    output_path: Path,
    shipping_profile: str,
    sales_channel: str,
    eur_rate: Decimal,
    default_weight: str,
    max_products: int,
    max_per_category: int,
    ) -> tuple[int, list[str], list[str]]:
    header = load_template_header(template_path)
    defaults = {
        "shipping_profile": shipping_profile,
        "sales_channel": sales_channel,
        "product_weight": default_weight,
        "variant_weight": default_weight,
    }

    with dataset_path.open("r", newline="", encoding="utf-8") as dataset_file, output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as output_file:
        reader = csv.DictReader(dataset_file)
        selected_products, selected_categories = select_products(
            reader, max_products, max_per_category
        )
        seen_tags: set[str] = set()
        tags: list[str] = []
        writer = csv.DictWriter(output_file, fieldnames=header)
        writer.writeheader()
        for product in selected_products:
            row = build_medusa_row(product, defaults, eur_rate)
            writer.writerow({key: row.get(key, "") for key in header})
            tag = (product.get("brand") or "").strip()
            if tag and tag not in seen_tags:
                seen_tags.add(tag)
                tags.append(tag)
            elif not tag:
                category_tag = (product.get("category") or "").strip()
                if category_tag and category_tag not in seen_tags:
                    seen_tags.add(category_tag)
                    tags.append(category_tag)
        return len(selected_products), selected_categories, tags


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a Kaggle-style product CSV into Medusa's import format"
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=Path("report/product-data/products.csv"),
        help="Source dataset that lists products from Kaggle",
    )
    parser.add_argument(
        "-t",
        "--template",
        type=Path,
        default=Path("report/product-import-template.csv"),
        help="Reference Medusa template used to ensure headers",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("report/products-medusa-import.csv"),
        help="Path where the formatted file will be written",
    )
    parser.add_argument(
        "--shipping-profile-id",
        default="default",
        help="Shipping profile id to assign every product to in Medusa",
    )
    parser.add_argument(
        "--sales-channel-id",
        default="default",
        help="Sales channel identifier that the products should belong to",
    )
    parser.add_argument(
        "--eur-rate",
        type=Decimal,
        default=Decimal("0.92"),
        help="Conversion rate from USD (dataset) to EUR (Medusa price column)",
    )
    parser.add_argument(
        "--default-weight",
        default="500",
        help="Default weight (in grams) assigned when the dataset does not provide it",
    )
    parser.add_argument(
        "--max-products",
        type=int,
        default=400,
        help="Maximum number of products Medusa will receive",
    )
    parser.add_argument(
        "--max-per-category",
        type=int,
        default=50,
        help="Upper limit of products taken from each category",
    )
    parser.add_argument(
        "--categories-output",
        type=Path,
        default=Path("report/categories-medusa.csv"),
        help="Where to write the sampled category list",
    )
    parser.add_argument(
        "--tags-output",
        type=Path,
        default=Path("report/tags-medusa.csv"),
        help="Where to write the sampled tag list",
    )

    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.categories_output.parent.mkdir(parents=True, exist_ok=True)
    args.tags_output.parent.mkdir(parents=True, exist_ok=True)

    processed = convert(
        args.input,
        args.template,
        args.output,
        args.shipping_profile_id,
        args.sales_channel_id,
        args.eur_rate,
        args.default_weight,
        args.max_products,
        args.max_per_category,
    )
    written, categories, tags = processed
    write_categories_csv(categories, args.categories_output)
    write_tags_csv(tags, args.tags_output)
    print(
        f"Wrote {written} rows to {args.output}, exported {len(categories)} categories to {args.categories_output}, and {len(tags)} tags to {args.tags_output}. Validate ids (shipping, channel) in Medusa after import."
    )


if __name__ == "__main__":
    main()
