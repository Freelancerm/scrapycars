from scrapy.exceptions import DropItem


def clean_mileage(value):
    if value is None:
        return 0

    if isinstance(value, int):
        return value

    if isinstance(value, str):
        value = value.replace(",", "").replace(" miles", "").strip()
        try:
            return int(value)
        except ValueError:
            return 0

    return 0


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