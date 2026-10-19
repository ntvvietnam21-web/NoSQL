from datetime import datetime
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from database.mongodb import get_db
from services.redis_service import invalidate_job
from utils.decorators import role_required
from utils.helpers import parse_int, to_object_id


recruiter_bp = Blueprint("recruiter", __name__, url_prefix="/recruiter")


def _owned_job(db, job_id):
    jid = to_object_id(job_id)
    uid = to_object_id(session["user_id"])
    if not jid or not uid:
        return None
    return db.QL_ViecLam.find_one({"_id": jid, "cong_ty.ma_nha_tuyen_dung": uid})


@recruiter_bp.route("/dashboard")
@role_required("nha_tuyen_dung")
def dashboard():
    db = get_db()
    uid = to_object_id(session["user_id"])
    job_ids = [x["_id"] for x in db.QL_ViecLam.find({"cong_ty.ma_nha_tuyen_dung": uid}, {"_id": 1})]
    total_jobs = len(job_ids)
    total_applicants = db.QL_UngTuyen.count_documents({"ma_viec_lam": {"$in": job_ids}}) if job_ids else 0
    pending = db.QL_UngTuyen.count_documents({"ma_viec_lam": {"$in": job_ids}, "trang_thai": "cho_duyet"}) if job_ids else 0
    approved = db.QL_UngTuyen.count_documents({"ma_viec_lam": {"$in": job_ids}, "trang_thai": "da_duyet"}) if job_ids else 0

    recent = []
    if job_ids:
        pipeline = [
            {"$match": {"ma_viec_lam": {"$in": job_ids}}},
            {"$lookup": {"from": "QL_NguoiDung", "localField": "ma_ung_vien", "foreignField": "_id", "as": "ung_vien"}},
            {"$unwind": "$ung_vien"},
            {"$lookup": {"from": "QL_ViecLam", "localField": "ma_viec_lam", "foreignField": "_id", "as": "viec_lam"}},
            {"$unwind": "$viec_lam"},
            {"$sort": {"ngay_ung_tuyen": -1}},
            {"$limit": 5},
        ]
        recent = list(db.QL_UngTuyen.aggregate(pipeline))

    return render_template("recruiter/dashboard.html", total_jobs=total_jobs, total_applicants=total_applicants, pending=pending, approved=approved, recent=recent)


@recruiter_bp.route("/jobs")
@role_required("nha_tuyen_dung")
def jobs():
    db = get_db()
    uid = to_object_id(session["user_id"])
    items = list(db.QL_ViecLam.find({"cong_ty.ma_nha_tuyen_dung": uid}).sort("ngay_dang", -1))
    return render_template("recruiter/jobs.html", jobs=items)


def _build_job_from_form(existing=None):
    existing = existing or {}
    company_old = existing.get("cong_ty", {}) or {}
    address_old = company_old.get("dia_chi", {}) or {}
    contact_old = company_old.get("lien_he", {}) or {}
    tech = [x.strip() for x in request.form.get("cong_nghe", "").split(",") if x.strip()]
    detail = dict(existing.get("chi_tiet_nganh", {}) or {})
    detail["kinh_nghiem_nam"] = parse_int(request.form.get("kinh_nghiem"), 0)
    if tech:
        detail["cong_nghe_chinh"] = tech
    else:
        detail.pop("cong_nghe_chinh", None)
    work_type = request.form.get("hinh_thuc_lam_viec", "").strip()
    if work_type:
        detail["hinh_thuc_lam_viec"] = work_type

    return {
        "cong_ty": {
            "ten_cong_ty": request.form.get("ten_cong_ty", "").strip(),
            "quy_mo": request.form.get("quy_mo", company_old.get("quy_mo", "")).strip(),
            "dia_chi": {
                "thanh_pho": request.form.get("thanh_pho", request.form.get("dia_diem", "")).strip(),
                "quan_huyen": request.form.get("quan_huyen", address_old.get("quan_huyen", "")).strip(),
                "chi_tiet": request.form.get("dia_chi_chi_tiet", address_old.get("chi_tiet", "")).strip(),
            },
            "lien_he": {
                "email": request.form.get("email_lien_he", contact_old.get("email", "")).strip(),
                "so_dien_thoai": request.form.get("so_dien_thoai", contact_old.get("so_dien_thoai", "")).strip(),
            },
            "mo_ta": request.form.get("mo_ta_cong_ty", company_old.get("mo_ta", "")).strip(),
            "ma_nha_tuyen_dung": to_object_id(session["user_id"]),
        },
        "tieu_de": request.form.get("tieu_de", "").strip(),
        "nganh_nghe": request.form.get("nganh_nghe", "").strip(),
        "muc_luong": {
            "toi_thieu": parse_int(request.form.get("luong_toi_thieu")),
            "toi_da": parse_int(request.form.get("luong_toi_da")),
            "don_vi": "VND",
        },
        "dia_diem": request.form.get("dia_diem", "").strip(),
        "chi_tiet_nganh": detail,
        "trang_thai": request.form.get("trang_thai", "dang_tuyen"),
    }


@recruiter_bp.route("/jobs/create", methods=["GET", "POST"])
@role_required("nha_tuyen_dung")
def create_job():
    if request.method == "POST":
        db = get_db()
        doc = _build_job_from_form()
        doc["ngay_dang"] = datetime.utcnow()
        if not doc["tieu_de"] or not doc["nganh_nghe"] or not doc["dia_diem"] or not doc["cong_ty"]["ten_cong_ty"]:
            flash("Vui lòng nhập đầy đủ tiêu đề, ngành nghề, địa điểm và tên công ty.", "danger")
            return render_template("recruiter/create_job.html", form=request.form)
        result = db.QL_ViecLam.insert_one(doc)
        flash("Đăng tin tuyển dụng thành công.", "success")
        return redirect(url_for("recruiter.jobs"))
    return render_template("recruiter/create_job.html")


@recruiter_bp.route("/jobs/<job_id>/edit", methods=["GET", "POST"])
@role_required("nha_tuyen_dung")
def edit_job(job_id):
    db = get_db()
    job = _owned_job(db, job_id)
    if not job:
        abort(404)
    if request.method == "POST":
        doc = _build_job_from_form(job)
        db.QL_ViecLam.update_one({"_id": job["_id"]}, {"$set": doc})
        invalidate_job(job_id)
        flash("Cập nhật việc làm thành công.", "success")
        return redirect(url_for("recruiter.jobs"))
    return render_template("recruiter/edit_job.html", job=job)


@recruiter_bp.route("/jobs/<job_id>/applicants")
@role_required("nha_tuyen_dung")
def applicants(job_id):
    db = get_db()
    job = _owned_job(db, job_id)
    if not job:
        abort(404)
    pipeline = [
        {"$match": {"ma_viec_lam": job["_id"]}},
        {"$lookup": {"from": "QL_NguoiDung", "localField": "ma_ung_vien", "foreignField": "_id", "as": "ung_vien"}},
        {"$unwind": "$ung_vien"},
        {"$sort": {"ngay_ung_tuyen": -1}},
    ]
    items = list(db.QL_UngTuyen.aggregate(pipeline))
    return render_template("recruiter/applicants.html", job=job, items=items)


@recruiter_bp.post("/applications/<application_id>/status")
@role_required("nha_tuyen_dung")
def application_status(application_id):
    db = get_db()
    aid = to_object_id(application_id)
    if not aid:
        abort(404)
    application = db.QL_UngTuyen.find_one({"_id": aid})
    if not application:
        abort(404)
    job = _owned_job(db, str(application["ma_viec_lam"]))
    if not job:
        abort(403)

    status = request.form.get("status")
    if status not in {"cho_duyet", "da_duyet", "tu_choi"}:
        flash("Trạng thái không hợp lệ.", "danger")
    else:
        note = "Đã gửi lịch phỏng vấn" if status == "da_duyet" else ("Chưa đạt yêu cầu" if status == "tu_choi" else "")
        db.QL_UngTuyen.update_one({"_id": aid}, {"$set": {"trang_thai": status, "ghi_chu": note}})
        flash("Đã cập nhật trạng thái hồ sơ.", "success")
    return redirect(url_for("recruiter.applicants", job_id=str(application["ma_viec_lam"])))
