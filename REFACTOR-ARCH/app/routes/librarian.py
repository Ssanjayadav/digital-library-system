from flask import Blueprint, render_template

librarian_bp = Blueprint("librarian", __name__, url_prefix="/librarian")


@librarian_bp.route("/dashboard")
def dashboard():
    return render_template("librarian/dashboard.html")


@librarian_bp.route("/books")
def books():
    return render_template("librarian/books.html")


@librarian_bp.route("/students")
def students():
    return render_template("librarian/students.html")


@librarian_bp.route("/issue")
def issue():
    return render_template("librarian/issue.html")


@librarian_bp.route("/return")
def return_book():
    return render_template("librarian/return.html")


@librarian_bp.route("/fines")
def fines():
    return render_template("librarian/fines.html")


@librarian_bp.route("/reports")
def reports():
    return render_template("librarian/reports.html")