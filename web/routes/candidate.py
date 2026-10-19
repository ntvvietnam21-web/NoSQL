from datetime import datetime
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from database.mongodb import get_db
from services.redis_service import (
    favorite_count,
    get_favorite_ids,
    get_recent_searches,
)
from utils.decorators import role_required
from utils.helpers import to_object_id


candidate_bp = Blueprint("candidate", __name__, url_prefix="/candidate")


@candidate_bp.route("/dashboard")
@role_required("ung_vien")
def dashboard():
    db = get_db()
    uid = to_object_id(session["user_id"])
    applications = db.QL_UngTuyen.count_documents({"ma_ung_vien": uid})
    approved = db.QL_UngTuyen.count_documents({"ma_ung_vien": uid, "trang_thai": "da_duyet"})
    favorites = favorite_count(session["user_id"])
    recommended = list(db.QL_ViecLam.find({"trang_thai": "dang_tuyen"}).sort("ngay_dang", -1).limit(5))
    return render_template("candidate/dashboard.html", applications=applications, approved=approved, favorites=favorites, recommended=recommended)


@candidate_bp.route("/profile", methods=["GET", "POST"])
@role_required("ung_vien")
def profile():
    db = get_db()
    uid = to_object_id(session["user_id"])
    user = db.QL_NguoiDung.find_one({"_id": uid})
    if not user:
        abort(404)

    if request.method == "POST":
        skills = [x.strip() for x in request.form.get("ky_nang", "").split(",") if x.strip()]
        update = {
            "ho_so.ho_ten": request.form.get("ho_ten", "").strip(),
            "ho_so.nganh_nghe": request.form.get("nganh_nghe", "").strip(),
            "ho_so.hoc_van": request.form.get("hoc_van", "").strip(),
            "ho_so.kinh_nghiem": request.form.get("kinh_nghiem", "").strip(),
            "ho_so.chi_tiet_ho_so.ky_nang": skills,
            "ho_so.chi_tiet_ho_so.github": request.form.get("github", "").strip(),
            "ho_so.ngay_cap_nhat": datetime.utcnow(),
        }
        db.QL_NguoiDung.update_one({"_id": uid}, {"$set": update})
        session["display_name"] = update["ho_so.ho_ten"] or session.get("username")
        flash("Cập nhật hồ sơ thành công.", "success")
        return redirect(url_for("candidate.profile"))

    return render_template("candidate/profile.html", user=user)


@candidate_bp.route("/applications")
@role_required("ung_vien")
def applications():
    db = get_db()
    uid = to_object_id(session["user_id"])
    pipeline = [
        {"$match": {"ma_ung_vien": uid}},
        {"$lookup": {"from": "QL_ViecLam", "localField": "ma_viec_lam", "foreignField": "_id", "as": "viec_lam"}},
        {"$unwind": "$viec_lam"},
        {"$sort": {"ngay_ung_tuyen": -1}},
    ]
    items = list(db.QL_UngTuyen.aggregate(pipeline))
    return render_template("candidate/applications.html", items=items)


@candidate_bp.route("/favorites")
@role_required("ung_vien")
def favorites():
    db = get_db()
    ids = [to_object_id(x) for x in get_favorite_ids(session["user_id"])]
    ids = [x for x in ids if x]
    jobs = list(db.QL_ViecLam.find({"_id": {"$in": ids}})) if ids else []
    for job in jobs:
        job["_id_str"] = str(job["_id"])
    return render_template("candidate/favorites.html", jobs=jobs)


@candidate_bp.route("/history")
@role_required("ung_vien")
def history():
    searches = get_recent_searches(session["user_id"])
    return render_template("candidate/history.html", searches=searches)
