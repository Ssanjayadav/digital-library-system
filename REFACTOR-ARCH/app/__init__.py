from flask import Flask
from flask import request



def build_menu(role):
    if role == "student":
        return [
            {"name": "Dashboard", "endpoint": "student.dashboard"},
            {"name": "Issued Books", "endpoint": "student.issued"},
            {"name": "Reading History", "endpoint": "student.history"},
            {"name": "Reserved Books", "endpoint": "student.reservations"},
            {"name": "Fines", "endpoint": "student.fines"},
            {"name": "Profile", "endpoint": "student.profile"},
        ]

    if role == "librarian":
        return [
            {"name": "Dashboard", "endpoint": "librarian.dashboard"},
            {"name": "Manage Books", "endpoint": "librarian.books"},
            {"name": "Students", "endpoint": "librarian.students"},
            {"name": "Issue Book", "endpoint": "librarian.issue"},
            {"name": "Return Book", "endpoint": "librarian.return_book"},
            {"name": "Fines", "endpoint": "librarian.fines"},
            {"name": "Reports", "endpoint": "librarian.reports"},
        ]

    return []




def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    app.secret_key = "dev-secret-key"

    from .routes.student import student_bp
    from .routes.librarian import librarian_bp
    from .routes.auth import auth_bp


    app.register_blueprint(student_bp)
    app.register_blueprint(librarian_bp)
    app.register_blueprint(auth_bp)

    from flask import request

    @app.context_processor
    def inject_global_data():

       endpoint = request.endpoint or ""  

       role = ""
       page_title = ""
   
       if "." in endpoint:
           module, page = endpoint.split(".")
   
           role = module.capitalize()
           page_title = page.replace("_", " ").title()
       breadcrumb = ""
       if "." in endpoint:
   
           module, page = endpoint.split(".")
           breadcrumb = f"{module.capitalize()} > {page.replace('_',' ').title()}"
       menu = build_menu(role.lower())
   
    # Temporary demo profile image
       profile_image = "https://i.pravatar.cc/150?img=3"
       return dict(
           active=endpoint,
   
           breadcrumb=breadcrumb,
           menu=menu,
           role=role,
           page_title=page_title, 
           profile_image=profile_image
       )
    

    return app
