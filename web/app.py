from flask import Flask, render_template
from config import Config
from database.mongodb import init_mongo
from database.redis_db import init_redis
from routes.auth import auth_bp
from routes.jobs import jobs_bp
from routes.candidate import candidate_bp
from routes.recruiter import recruiter_bp
from utils.helpers import format_salary


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_mongo(app)
    init_redis(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(candidate_bp)
    app.register_blueprint(recruiter_bp)

    app.jinja_env.filters["salary"] = format_salary

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("errors/404.html"), 404

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=True)
