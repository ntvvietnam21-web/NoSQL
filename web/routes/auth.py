try:
    import bcrypt
except ImportError:
    bcrypt = None
from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from database.mongodb import get_db


auth_bp = Blueprint("auth", __name__)


def verify_password(stored, supplied):
    if bcrypt and stored and isinstance(stored, str) and stored.startswith(("$2a$", "$2b$", "$2y$")) and len(stored) >= 59:
        try:
            return bcrypt.checkpw(supplied.encode("utf-8"), stored.encode("utf-8"))
        except Exception:
            pass
    return current_app.config["ALLOW_DEMO_LOGIN"] and supplied == current_app.config["DEMO_PASSWORD"]


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("jobs.home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        user = db.QL_NguoiDung.find_one({"ten_dang_nhap": username})

        if not user or not verify_password(user.get("mat_khau"), password):
            flash("Tên đăng nhập hoặc mật khẩu không chính xác.", "danger")
            return render_template("login.html", username=username)
        if user.get("trang_thai") != "hoat_dong":
            flash("Tài khoản hiện không hoạt động.", "danger")
            return render_template("login.html", username=username)

        session.clear()
        session["user_id"] = str(user["_id"])
        session["username"] = user.get("ten_dang_nhap", "")
        session["role"] = user.get("vai_tro")
        session["display_name"] = (user.get("ho_so") or {}).get("ho_ten") or user.get("ten_dang_nhap")
        flash("Đăng nhập thành công.", "success")

        if user.get("vai_tro") == "ung_vien":
            return redirect(url_for("candidate.dashboard"))
        return redirect(url_for("recruiter.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Bạn đã đăng xuất.", "info")
    return redirect(url_for("jobs.home"))
