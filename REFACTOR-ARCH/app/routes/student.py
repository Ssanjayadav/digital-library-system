from flask import Blueprint, render_template

student_bp = Blueprint("student", __name__, url_prefix="/student")

def student_menu():
    return [
        {"name": "Dashboard", "endpoint": "student.dashboard"},
        {"name": "Issued Books", "endpoint": "student.issued"},
        {"name": "Reading History", "endpoint": "student.history"},
        {"name": "Reserved Books", "endpoint": "student.reservations"},
        {"name": "Fines", "endpoint": "student.fines"},
        {"name": "Profile", "endpoint": "student.profile"},
    ]

@student_bp.route("/dashboard")
def dashboard():
    return render_template(
        "student/dashboard.html",
              
    )

@student_bp.route("/issued")
def issued():
    return render_template(
        "student/issued.html",
        
    )

@student_bp.route("/history")
def history():
    return render_template(
        "student/history.html",
         
    )

@student_bp.route("/reservations")
def reservations():
    return render_template(
        "student/reservations.html",
        
    )

@student_bp.route("/fines")
def fines():
    return render_template(
        "student/fines.html",
             )

@student_bp.route("/profile")
def profile():
    return render_template(
        "student/profile.html",
            
    )