from datetime import datetime
from bson import ObjectId


def to_object_id(value):
    try:
        return ObjectId(str(value))
    except Exception:
        return None


def format_salary(value):
    if value in (None, ""):
        return "Thỏa thuận"
    try:
        return f"{int(value):,}".replace(",", ".") + " đ"
    except Exception:
        return str(value)


def parse_int(value, default=0):
    try:
        return int(str(value).replace(".", "").replace(",", "").strip())
    except Exception:
        return default


def now_utc():
    return datetime.utcnow()
