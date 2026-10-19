import json
from datetime import datetime
from bson import ObjectId
from flask import current_app
from database.redis_db import get_redis


def _json_default(value):
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Không thể chuyển {type(value)} sang JSON")


def _safe(call, default=None):
    try:
        return call()
    except Exception:
        return default


# STRING: cache chi tiết việc làm dưới dạng JSON
def get_cached_job(job_id):
    r = get_redis()
    raw = _safe(lambda: r.get(f"job:{job_id}"))
    return json.loads(raw) if raw else None


def set_cached_job(job):
    r = get_redis()
    job_id = str(job["_id"])
    payload = json.dumps(job, ensure_ascii=False, default=_json_default)
    _safe(lambda: r.set(f"job:{job_id}", payload, ex=current_app.config["CACHE_TTL"]))


# STRING/INTEGER: bộ đếm lượt xem
def increment_job_view(job_id):
    r = get_redis()
    value = _safe(lambda: r.incr(f"job:view:{job_id}"), 0)
    return int(value or 0)


def get_job_view(job_id):
    r = get_redis()
    value = _safe(lambda: r.get(f"job:view:{job_id}"), "0")
    return int(value or 0)


# HASH: cache tóm tắt việc làm
def cache_job_summary(job):
    r = get_redis()
    job_id = str(job["_id"])
    company = job.get("cong_ty", {}) or {}
    salary = job.get("muc_luong", {}) or {}
    mapping = {
        "tieu_de": str(job.get("tieu_de", "")),
        "nganh_nghe": str(job.get("nganh_nghe", "")),
        "dia_diem": str(job.get("dia_diem", "")),
        "ten_cong_ty": str(company.get("ten_cong_ty", "")),
        "luong_toi_thieu": str(salary.get("toi_thieu", "")),
        "luong_toi_da": str(salary.get("toi_da", "")),
        "trang_thai": str(job.get("trang_thai", "")),
    }
    key = f"job:info:{job_id}"
    _safe(lambda: r.hset(key, mapping=mapping))
    _safe(lambda: r.expire(key, current_app.config["CACHE_TTL"]))
    return mapping


def get_job_summary(job_id):
    r = get_redis()
    return _safe(lambda: r.hgetall(f"job:info:{job_id}"), {}) or {}


# LIST: 5 từ khóa tìm kiếm gần nhất
def add_recent_search(user_id, keyword):
    if not keyword:
        return
    r = get_redis()
    key = f"search:recent:{user_id}"
    _safe(lambda: r.lpush(key, keyword))
    _safe(lambda: r.ltrim(key, 0, 4))


def get_recent_searches(user_id):
    r = get_redis()
    return _safe(lambda: r.lrange(f"search:recent:{user_id}", 0, 4), []) or []


# SET: danh sách việc làm yêu thích
def add_favorite(user_id, job_id):
    r = get_redis()
    return _safe(lambda: r.sadd(f"favorite:jobs:{user_id}", str(job_id)), 0)


def remove_favorite(user_id, job_id):
    r = get_redis()
    return _safe(lambda: r.srem(f"favorite:jobs:{user_id}", str(job_id)), 0)


def is_favorite(user_id, job_id):
    r = get_redis()
    return bool(_safe(lambda: r.sismember(f"favorite:jobs:{user_id}", str(job_id)), 0))


def get_favorite_ids(user_id):
    r = get_redis()
    return list(_safe(lambda: r.smembers(f"favorite:jobs:{user_id}"), set()) or set())


def favorite_count(user_id):
    r = get_redis()
    return int(_safe(lambda: r.scard(f"favorite:jobs:{user_id}"), 0) or 0)


def invalidate_job(job_id):
    r = get_redis()
    _safe(lambda: r.delete(f"job:{job_id}", f"job:info:{job_id}"))
