from scrapy.exceptions import DropItem


def clean_mileage(value):
    if not value:
        return None

    value = value.replace(",", "").strip()

    return int(value)


def normalize_fuel(value):
    if not value:
        return None

    return value.strip().lower()


def validate_required_fields(item):
    required_fields = ["Model", "Name", "registration"]

    for field in required_fields:
        if not item.get(field):
            raise DropItem(f"Missing required field: {field}")

    return item