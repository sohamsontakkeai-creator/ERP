"""
Main Flask application entry point
"""

from flask import Flask, send_from_directory, make_response
from flask_cors import CORS
from flask_mail import Mail
from flask_session import Session
from flask_jwt_extended import JWTManager
from config import config
from models import db
from routes import register_blueprints
from utils.migration_manager import init_migrations
import os

# Initialize extensions
mail = Mail()
jwt = JWTManager()  # ✅ Proper JWT initialization


def create_app(config_name=None):
    """
    Flask application factory
    """
    app = Flask(__name__)

    # Load configuration
    config_name = config_name or os.getenv("FLASK_CONFIG", "default")
    app.config.from_object(config[config_name])
    # Load frontend URL from environment (for password reset links)
    app.config['FRONTEND_BASE_URL'] = os.getenv('FRONTEND_BASE_URL', 'http://localhost:5173')

    # Initialize core extensions
    db.init_app(app)
    mail.init_app(app)
    Session(app)
    jwt.init_app(app)  # ✅ Attach JWT manager

    # Upload folder setup
    app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "backend", "uploads")

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        """Serve uploaded files"""
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    # Register blueprints (all API routes)
    register_blueprints(app)

    # ✅ Enable CORS with all required custom headers
    CORS(
        app,
        origins=[
            "https://erp-ct75.vercel.app/auth",
            "https://*.vercel.app",  # allows preview URLs
            "http://localhost:5173",  # for local testing
        ],
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "x-user-department",
            "x-user-email",
            "x-user-name",
        ],
    )

    # ✅ Handle OPTIONS (preflight) requests manually (safety net)
    @app.route("/<path:path>", methods=["OPTIONS"])
    def handle_options(path):
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = "https://erp-ct75.vercel.app"
        response.headers[
            "Access-Control-Allow-Headers"
        ] = "Content-Type,Authorization,x-user-department,x-user-email,x-user-name"
        response.headers[
            "Access-Control-Allow-Methods"
        ] = "GET,POST,PUT,DELETE,OPTIONS"
        return response, 200

    # ✅ Always attach CORS headers after each response
    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "https://erp-latest.vercel.app"
        response.headers[
            "Access-Control-Allow-Headers"
        ] = "Content-Type,Authorization,x-user-department,x-user-email,x-user-name"
        response.headers[
            "Access-Control-Allow-Methods"
        ] = "GET,POST,PUT,DELETE,OPTIONS"
        return response

    # ✅ Initialize database only if not in testing mode
    if not app.config.get("TESTING", False):
        initialize_database(app)

    return app


def initialize_database(app):
    """Run migrations, create tables, and seed defaults"""
    with app.app_context():
        try:
            print("\n🔧 Running custom migrations...")
            init_migrations(app, db)

            # Create all models’ tables
            db.create_all()
            print("✅ Database tables created successfully!")

            # Ensure column exists in purchase_order table
            from sqlalchemy import text

            result = db.session.execute(
                text(
                    """
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'purchase_order' 
                AND COLUMN_NAME = 'original_requirements'
            """
                )
            )

            if not result.fetchone():
                print("🔄 Adding missing 'original_requirements' column...")
                db.session.execute(
                    text("ALTER TABLE purchase_order ADD COLUMN original_requirements TEXT")
                )
                db.session.commit()
                print("✅ Column added successfully!")
            else:
                print("ℹ️ 'original_requirements' column already exists")

            # ✅ Ensure admin user exists
            from models import User

            admin_created = User.create_admin_user()
            if admin_created:
                print("✅ Admin user created successfully!")
            else:
                print("ℹ️ Admin user already exists")

        except Exception as e:
            print(f"❌ Error setting up database: {e}")
            raise


# Run Flask app (Render/Railway will use gunicorn in production)
if __name__ == "__main__":
    app = create_app()
    app.run(
        debug=app.config.get("DEBUG", True),
        host="0.0.0.0",
        port=5000,
    )
