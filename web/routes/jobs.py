from datetime import datetime
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from database.mongodb import get_db
from services.redis_service import (
    add_recent_search,
    cache_job_summary,
    get_cached_job,
    get_job_summary,
    increment_job_view,
    is_favorite,
    set_cached_job,
    add_favorite,
    remove_favorite,
)
from utils.helpers import to_object_id
from utils.decorators import role_required


jobs_bp = Blueprint("jobs", __name__)


def _decorate_jobs(jobs):
    result = []
    for job in jobs:
        job_id = str(job["_id"])
        summary = get_job_summary(job_id)
        if not summary:
            summary = cache_job_summary(job)
        job["_id_str"] = job_id
        job["summary_cache"] = summary
        result.append(job)
    return result


@jobs_bp.route("/")
def home():
    db = get_db()
    jobs = list(db.QL_ViecLam.find({"trang_thai": "dang_tuyen"}).sort("ngay_dang", -1).limit(6))
    return render_template("index.html", jobs=_decorate_jobs(jobs))


@jobs_bp.route("/jobs")
@jobs_bp.route("/jobs/search")
def list_jobs():
    db = get_db()
    keyword = request.args.get("q", "").strip()
    location = request.args.get("location", "").strip()
    industry = request.args.get("industry", "").strip()

    query = {"trang_thai": "dang_tuyen"}
    if keyword:
        query["$or"] = [
            {"tieu_de": {"$regex": keyword, "$options": "i"}},
            {"nganh_nghe": {"$regex": keyword, "$options": "i"}},
            {"chi_tiet_nganh.cong_nghe_chinh": {"$regex": keyword, "$options": "i"}},
            {"cong_ty.ten_cong_ty": {"$regex": keyword, "$options": "i"}},
        ]
        if session.get("role") == "ung_vien" and session.get("user_id"):
            add_recent_search(session["user_id"], keyword)
    if location:
        query["dia_diem"] = {"$regex": location, "$options": "i"}
    if industry:
        query["nganh_nghe"] = industry

    page = max(int(request.args.get("page", 1) or 1), 1)
    per_page = 12
    total = db.QL_ViecLam.count_documents(query)
    cursor = db.QL_ViecLam.find(query).sort("ngay_dang", -1).skip((page - 1) * per_page).limit(per_page)
    jobs = _decorate_jobs(list(cursor))
    industries = db.QL_ViecLam.distinct("nganh_nghe", {"trang_thai": "dang_tuyen"})
    pages = max((total + per_page - 1) // per_page, 1)

    return render_template(
        "jobs/list.html",
        jobs=jobs,
        keyword=keyword,
        location=location,
        industry=industry,
        industries=sorted(i for i in industries if i),
        page=page,
        pages=pages,
        total=total,
    )


@jobs_bp.route("/jobs/<job_id>")
def detail(job_id):
    oid = to_object_id(job_id)
    if not oid:
        abort(404)

    db = get_db()
    cached = get_cached_job(job_id)
    source = "Redis"
    if cached:
        job = cached
        job["_id_str"] = job_id
    else:
        source = "MongoDB"
        job = db.QL_ViecLam.find_one({"_id": oid})
        if not job:
            abort(404)
        set_cached_job(job)
        job["_id_str"] = job_id

    views = increment_job_view(job_id)
    favorite = False
    applied = False
    if session.get("role") == "ung_vien" and session.get("user_id"):
        favorite = is_favorite(session["user_id"], job_id)
        user_oid = to_object_id(session["user_id"])
        applied = bool(db.QL_UngTuyen.find_one({"ma_viec_lam": oid, "ma_ung_vien": user_oid}))

    return render_template("jobs/detail.html", job=job, views=views, cache_source=source, favorite=favorite, applied=applied)


@jobs_bp.post("/jobs/<job_id>/apply")
@role_required("ung_vien")
def apply_job(job_id):
    db = get_db()
    jid = to_object_id(job_id)
    uid = to_object_id(session["user_id"])
    if not jid or not db.QL_ViecLam.find_one({"_id": jid, "trang_thai": "dang_tuyen"}):
        abort(404)
    if db.QL_UngTuyen.find_one({"ma_viec_lam": jid, "ma_ung_vien": uid}):
        flash("Bạn đã ứng tuyển công việc này trước đó.", "warning")
    else:
        db.QL_UngTuyen.insert_one({
            "ma_viec_lam": jid,
            "ma_ung_vien": uid,
            "ngay_ung_tuyen": datetime.utcnow(),
            "trang_thai": "cho_duyet",
            "ghi_chu": "",
        })
        flash("Ứng tuyển thành công.", "success")
    return redirect(url_for("jobs.detail", job_id=job_id))


@jobs_bp.post("/jobs/<job_id>/favorite")
@role_required("ung_vien")
def toggle_favorite(job_id):
    db = get_db()
    jid = to_object_id(job_id)
    if not jid or not db.QL_ViecLam.find_one({"_id": jid}):
        abort(404)
    if is_favorite(session["user_id"], job_id):
        remove_favorite(session["user_id"], job_id)
        flash("Đã bỏ khỏi danh sách yêu thích.", "info")
    else:
        add_favorite(session["user_id"], job_id)
        flash("Đã lưu việc làm yêu thích.", "success")
    return redirect(request.referrer or url_for("jobs.detail", job_id=job_id))
