from flask import Flask
from routes.auth import auth_bp
from routes.attendance import attendance_bp
from routes.sessions import sessions_bp
from routes.announcements import announcements_bp
from routes.materials import materials_bp
from routes.substitution_routes import substitution_bp
from routes.fcm_routes import fcm_bp
from routes.students import students_bp

app = Flask(__name__)

app.register_blueprint(auth_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(sessions_bp)
app.register_blueprint(announcements_bp)
app.register_blueprint(materials_bp)
app.register_blueprint(substitution_bp)
app.register_blueprint(fcm_bp)
app.register_blueprint(students_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)