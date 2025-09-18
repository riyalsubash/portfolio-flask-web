from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from functools import wraps
import cloudinary
import hashlib

app = Flask(__name__)

app.secret_key = "PLACE YOUR SECRET KEY HERE"

db_user = "DB_USERNAME"
db_password = "DB_PASSWORD"
db_host = "DB_SERVER"
db_port = "DB_PORT"
db_name = "DB_NAME"

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["MAIL_SERVER"] = "YOUR_MAIL_SERVER"
app.config["MAIL_PORT"] = 587 #YOUR_MAIL_PORT
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "YOUR EMAIL"
app.config["MAIL_PASSWORD"] = "YOUR APP PASSWORD"

cloudinary.config( 
  cloud_name = "YOUR CLOUD NAME", 
  api_key = "YOUR API KEY", 
  api_secret = "YOUR API SECRET",
  secure = True
)

db = SQLAlchemy(app)
mail = Mail(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" not in session:
            flash("Please login to access this page.", "warning")
            return redirect(url_for("admin"))
        return f(*args, **kwargs)

    return decorated_function

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file_from_form, current_public_id, folder_name):
    if file_from_form and allowed_file(file_from_form.filename):
        try:
            upload_result = cloudinary.uploader.upload(
                file_from_form, 
                folder=folder_name
            )
            new_public_id = upload_result['public_id']
            
            if current_public_id:
                cloudinary.uploader.destroy(current_public_id)
            
            return new_public_id
        except Exception as e:
            print(f"Cloudinary upload failed: {e}")
            return current_public_id
        
    return current_public_id

class Home(db.Model):
    __tablename__ = "home"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))
    title = db.Column(db.String(10))
    role = db.Column(db.String(20))
    about = db.Column(db.Text)
    phone = db.Column(db.String(12))
    insta = db.Column(db.String(20))
    github = db.Column(db.String(20))
    linkedin = db.Column(db.String(20))
    main = db.Column(db.Text)
    firstImage = db.Column(db.String(100), nullable=True)
    secondImage = db.Column(db.String(100), nullable=True)


class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)


class Contact(db.Model):
    __tablename__ = "contact"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    message = db.Column(db.Text)
    seen = db.Column(db.Boolean, default=False)
    replied = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "message": self.message,
            "seen": self.seen,
            "replied": self.replied,
        }


class Projects(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)
    link = db.Column(db.String(255), nullable=True)
    github = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Integer, default=0)
    tech_stack = db.Column(db.String(255), nullable=True)

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    skills = db.relationship("Skill", backref="category", lazy=True)

class Skill(db.Model):
    __tablename__ = "skills"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)


@app.route("/")
def home():
    try:
        home_data = Home.query.first()
        categories = Category.query.all()
        p_count = (
            db.session.query(db.func.count())
            .select_from(Projects)
            .filter_by(status=1)
            .scalar()
        )
        all_projects = Projects.query.filter_by(status=1).all()
        # 

    except Exception as e:
        print(f"Database error: {e}")
        home_data = []
        categories=[]
        all_projects = []
        p_count = 0
        # 

    return render_template(
        "main.html", data=home_data, count=p_count, all_projects=all_projects,categories=categories)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "logged_in" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        entered_username = request.form["username"]
        entered_password = request.form["password"]
        result = hashlib.md5(entered_password.encode()).hexdigest()
        user = Admin.query.filter_by(username=entered_username).first()
        if user and user.password == result:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid Credentials. Please try again.", "danger")
            return redirect(url_for("admin"))
    return render_template("admin/admin.html")


@app.route("/dashboard")
@login_required
def dashboard():
    try:
        not_seen = Contact.query.filter_by(seen=False).count()
        not_replied = Contact.query.filter_by(replied=False).count()
        projects = Projects.query.filter_by(status=1).count()
        admin = Home.query.first()
    except Exception as e:
        print(f"Error fetching contacts: {e}")
        total_contacts = 0
    return render_template(
        "admin/dashboard.html",
        not_seen=not_seen,
        not_replied=not_replied,
        project_count=projects,
        admin=admin,
    )


@app.route("/contacts")
@login_required
def contacts():
    try:
        not_seen = Contact.query.filter_by(seen=False).count()
        not_replied = Contact.query.filter_by(replied=False).count()
        count = Contact.query.count()

        all_messages_objects = Contact.query.order_by(
            Contact.replied.asc(), Contact.id.desc()
        ).all()

        messages_as_dicts = [message.to_dict() for message in all_messages_objects]

    except Exception as e:
        print(f"Error fetching messages: {e}")
        messages_as_dicts = []
        not_seen, not_replied, count = 0, 0, 0

    return render_template(
        "admin/contact.html",
        not_seen=not_seen,
        not_replied=not_replied,
        count=count,
        messages=messages_as_dicts, 
    )


@app.route("/reply/<int:id>", methods=["GET", "POST"])
@login_required
def reply(id):
    msg = Contact.query.get_or_404(id)
    if request.method == "POST":
        subject = request.form["subject"]
        body = request.form["body"]
        try:
            reply_msg = Message(
                subject=subject,
                sender=app.config["MAIL_USERNAME"],
                recipients=[msg.email],
            )
            reply_msg.body = body
            mail.send(reply_msg)

            msg.replied = True
            db.session.commit()

            flash("Reply sent successfully!", "success")
            return redirect(url_for("contacts"))
        except Exception as e:
            print(f"Reply sending failed: {e}")
            flash("Failed to send reply.", "danger")
            return redirect(url_for("contacts"))
    return render_template("admin/reply.html", contact=msg)


@app.route("/mark_seen/<int:id>", methods=["POST"])
@login_required
def mark_seen(id):
    msg = Contact.query.get_or_404(id)
    if not msg.seen:
        msg.seen = True
        db.session.commit()
    return jsonify({"status": "ok"})


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    admin = Admin.query.get(session["logged_in"])
    if request.method == "POST":
        admin.username = request.form["username"]
        password = request.form["password"]

        if password:
            result = hashlib.md5(password.encode()).hexdigest()
            admin.password = result

        db.session.commit()
        flash("Settings updated successfully!", "success")
        return redirect(url_for("logout"))

    return render_template("admin/settings.html", current_admin=admin)


@app.route("/edit_home", methods=["GET", "POST"])
@login_required
def edit_home():
    home = Home.query.first()
    if not home:
        home = Home()
        db.session.add(home)
        db.session.commit()

    if request.method == "POST":
        home.name = request.form.get("name")
        home.title = request.form.get("title")
        home.role = request.form.get("role")
        home.about = request.form.get("about")
        home.phone = request.form.get("phone")
        home.insta = request.form.get("insta")
        home.github = request.form.get("github")
        home.linkedin = request.form.get("linkedin")
        home.main = request.form.get("main")

        home.firstImage = save_image(
            request.files.get('firstImage'), 
            home.firstImage,
            'home'
        )
        home.secondImage = save_image(
            request.files.get('secondImage'), 
            home.secondImage,
            'home'
        )

        db.session.commit()
        flash("Home content updated successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("admin/edit_home.html", home_data=home)


@app.route("/projects")
@login_required
def list_projects():
    projects = Projects.query.all()
    return render_template("projects/projects_list.html", projects=projects)


@app.route("/projects/add", methods=["GET", "POST"])
@login_required
def add_project():
    if request.method == "POST":
        image_public_id = save_image(
            request.files.get('image'),
            None,
            'projects'
        )

        new_project = Projects(
            title=request.form["title"],
            desc=request.form.get("desc"),
            image=image_public_id, 
            link=request.form.get("link"),
            github=request.form.get("github"),
            status=int(request.form.get("status", 1)),
            tech_stack=request.form.get("tech_stack"),
        )
        
        db.session.add(new_project)
        db.session.commit()
        
        flash("Project added successfully!", "success")
        return redirect(url_for("list_projects"))
        
    return render_template("projects/add_project.html")


@app.route("/projects/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_project(id):
    project = Projects.query.get_or_404(id)
    if request.method == "POST":
        project.image = save_image(
            request.files.get('image'),
            project.image,
            'projects'
        )

        project.title = request.form["title"]
        project.desc = request.form.get("desc")
        project.link = request.form.get("link")
        project.github = request.form.get("github")
        project.status = int(request.form.get("status", 0))
        project.tech_stack = request.form.get("tech_stack")

        db.session.commit()
        flash("Project updated successfully!", "info")
        return redirect(url_for("list_projects"))
        
    return render_template("projects/edit_project.html", project=project)


@app.route("/projects/delete/<int:id>", methods=["POST"])
@login_required
def delete_project(id):
    project = Projects.query.get_or_404(id)
    project.status = 0
    db.session.commit()
    flash("Project deleted (set inactive)!", "warning")
    return redirect(url_for("list_projects"))


@app.errorhandler(404)
def not_found(e):
    return render_template("default/404.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("admin"))
    
@app.route("/send_mail", methods=["POST"])
def send_mail():
    if request.method == "POST":
        name = request.form.get("name")
        email_from = request.form.get("email")
        message_body = request.form.get("message")

        if not all([name, email_from, message_body]):
            flash("Please fill all the fields.", "danger")
            return redirect(url_for("home", _anchor="contact"))

        try:
            contact = Contact(
                name=name, email=email_from, message=message_body
            )
            db.session.add(contact)
            db.session.commit()
            flash("Message saved successfully!", "success")
        except Exception as e:
            db.session.rollback()
            print(f"DB insert failed: {e}")
            flash("Failed to save message. Please try again later.", "danger")

        return redirect(url_for("home", _anchor="contact"))
    
# -------------------------------
# Add Skill
# -------------------------------
@app.route("/skills/add", methods=["GET", "POST"])
@login_required
def add_skill():
    categories = Category.query.all()
    if request.method == "POST":
        name = request.form["name"]
        category_id = request.form["category_id"]

        new_skill = Skill(name=name, category_id=category_id)
        db.session.add(new_skill)
        db.session.commit()
        flash("Skill Added Successfully ✅", "success")
        return redirect(url_for("view_skills"))

    return render_template("skills/add_skill.html", categories=categories)


# -------------------------------
# View All Skills
# -------------------------------
@app.route("/skills")
@login_required
def view_skills():
    skills = Skill.query.all()
    return render_template("skills/view_skills.html", skills=skills)


# -------------------------------
# Edit Skill
# -------------------------------
@app.route("/skills/edit/<int:skill_id>", methods=["GET", "POST"])
@login_required
def edit_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    categories = Category.query.all()

    if request.method == "POST":
        skill.name = request.form["name"]
        skill.category_id = request.form["category_id"]
        db.session.commit()
        flash("Skill Updated Successfully ✏️", "success")
        return redirect(url_for("view_skills"))

    return render_template("skills/edit_skill.html", skill=skill, categories=categories)


# -------------------------------
# Delete Skill
# -------------------------------
@app.route("/skills/delete/<int:skill_id>")
@login_required
def delete_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    db.session.delete(skill)
    db.session.commit()
    flash("Skill Deleted Successfully 🗑️", "danger")
    return redirect(url_for("view_skills"))



if __name__ == "__main__":
    app.run(debug=True)