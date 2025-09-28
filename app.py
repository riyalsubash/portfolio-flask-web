# app.py - Flask app rewritten to use Supabase instead of SQLAlchemy/MySQL
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
    send_file,
)
from flask_mail import Mail, Message
from functools import wraps
import cloudinary
import cloudinary.uploader
import hashlib
import os
from database import supabase  # <- your configured supabase client
from collections import defaultdict
from dotenv import load_dotenv
from io import StringIO,BytesIO
import csv
from reportlab.pdfgen import canvas

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Cloudinary (kept as before)
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("CLOUD_API"),
    api_secret=os.getenv("CLOUD_KEY")
)

# Mail (kept; ensure environment variables or set here)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(file_from_form, current_public_id, folder_name):
    if file_from_form and allowed_file(file_from_form.filename):
        try:
            upload_result = cloudinary.uploader.upload(file_from_form, folder=folder_name)
            new_public_id = upload_result["public_id"]
            if current_public_id:
                try:
                    cloudinary.uploader.destroy(current_public_id)
                except Exception:
                    pass
            return new_public_id
        except Exception as e:
            print(f"Cloudinary upload failed: {e}")
            return current_public_id
    return current_public_id


# -------------------------
# Helper wrappers for supabase queries
# -------------------------
def supa_select(table, select="*", filters=None, order=None, limit=None, count=False):
    """
    Generic select helper.
    filters: list of tuples: (op, column, value) where op in ['eq','neq','gt','lt','is','like'].
    order: tuple (column, asc_bool)
    limit: int
    count: bool -> request exact count
    """
    q = supabase.table(table).select(select, count="exact" if count else None)
    
    if filters:
        for op, col, val in filters:
            if op == "eq":
                q = q.eq(col, val)
            elif op == "neq":
                q = q.neq(col, val)
            elif op == "gt":
                q = q.gt(col, val)
            elif op == "lt":
                q = q.lt(col, val)
            elif op == "is":
                q = q.is_(col, val)
            elif op == "like":
                q = q.like(col, val)
    if order:
        col, asc = order
        # CORRECTED LINE: Use 'desc' keyword for older library versions (e.g., v1.x)
        # It's the opposite of ascending, so we use 'not asc'
        q = q.order(col, desc=not asc)
    if limit:
        q = q.limit(limit)
    
    res = q.execute()

    if hasattr(res, 'error') and res.error:
        print(f"Supabase select error on {table}: {res.error.message}")
    return res


def supa_insert(table, payload):
    res = supabase.table(table).insert(payload).execute()
    if hasattr(res, 'error') and res.error:
        print(f"Supabase insert error on {table}: {res.error.message}")
    return res


def supa_update(table, payload, filters):
    q = supabase.table(table).update(payload)
    for op, col, val in filters:
        if op == "eq":
            q = q.eq(col, val)
    res = q.execute()
    if hasattr(res, 'error') and res.error:
        print(f"Supabase update error on {table}: {res.error.message}")
    return res


def supa_delete(table, filters):
    q = supabase.table(table).delete()
    for op, col, val in filters:
        if op == "eq":
            q = q.eq(col, val)
    res = q.execute()
    if hasattr(res, 'error') and res.error:
        print(f"Supabase delete error on {table}: {res.error.message}")
    return res


# -------------------------
# Auth decorator (uses session["logged_in"] truthiness)
# -------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" not in session:
            flash("Please login to access this page.", "warning")
            return redirect(url_for("admin"))
        return f(*args, **kwargs)

    return decorated_function


# -------------------------
# Routes (converted to Supabase)
# -------------------------
@app.route("/")
def home():
    try:
        r = supa_select("home", select="*", limit=1)
        home_rows = r.data or []
        home_data = home_rows[0] if home_rows else None

        print(r)

        r3 = supa_select("projects", select="id", filters=[("eq", "status", 1)], count=True)
        p_count = r3.count or 0

        r4 = supa_select("projects", select="*", filters=[("eq", "status", 1)], order=("id", False))
        all_projects = r4.data or []

        r_categories = supa_select("categories", select="*")
        categories = r_categories.data or []

        r_skills = supa_select("skills", select="*")
        skills = r_skills.data or []

        skills_by_category = defaultdict(list)
        for skill in skills:
            skills_by_category[skill["category_id"]].append(skill)
        
        for cat in categories:
            cat["skills"] = skills_by_category.get(cat["id"], [])
        

    except Exception as e:
        print(f"Error in home route: {e}")
        home_data = None
        categories = []
        all_projects = []
        p_count = 0

    return render_template(
        "main.html", data=home_data, count=p_count, all_projects=all_projects, categories=categories        
    )


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "logged_in" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        entered_username = request.form["username"]
        entered_password = request.form["password"]

        # hash password if stored hashed
        hashed_password = hashlib.md5(entered_password.encode()).hexdigest()

        res = supabase.table("admin").select("*").execute()
        admin_row = res.data[0] if res.data else None
        print("Admin row:", admin_row)  # debug

        if admin_row and admin_row.get("password") == hashed_password and admin_row.get("username")==entered_username:
            session["logged_in"] = admin_row.get("id")
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid Credentials. Please try again.", "danger")
            return redirect(url_for("admin"))
    return render_template("admin/admin.html")



@app.route("/dashboard")
@login_required
def dashboard():
    try:
        r1 = supa_select("contact", select="id", filters=[("eq", "seen", False)], count=True)
        not_seen = r1.count or 0

        r2 = supa_select("contact", select="id", filters=[("eq", "replied", False)], count=True)
        not_replied = r2.count or 0

        r3 = supa_select("projects", select="id", filters=[("eq", "status", 1)], count=True)
        projects = r3.count or 0

        r4 = supa_select("home", select="*", limit=1)
        admin = r4.data[0] if r4.data else None

        res = supa_select(
            "expense",
            select="*",
            filters=[("eq", "user_id", session["logged_in"])],
            order=("date", False)
        )
        expenses = res.data or []
        total = sum(e["amount"] for e in expenses)

    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
        not_seen = not_replied = projects = 0
        admin = None
        total=0

    return render_template(
        "admin/dashboard.html",
        not_seen=not_seen,
        not_replied=not_replied,
        project_count=projects,
        admin=admin,total=total,
    )


@app.route("/contacts")
@login_required
def contacts():
    try:
        r_not_seen = supa_select("contact", select="id", filters=[("eq", "seen", False)], count=True)
        not_seen = r_not_seen.count or 0

        r_not_replied = supa_select("contact", select="id", filters=[("eq", "replied", False)], count=True)
        not_replied = r_not_replied.count or 0

        r_count = supa_select("contact", select="id", count=True)
        count = r_count.count or 0

        r_msgs = supa_select("contact", select="*", order=("replied", True))
        messages_as_dicts = r_msgs.data or []
        
    except Exception as e:
        print(f"Error fetching messages: {e}")
        messages_as_dicts = []
        not_seen = not_replied = count = 0

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
    r = supa_select("contact", select="*", filters=[("eq", "id", id)], limit=1)
    msg = r.data[0] if r.data else None
    if not msg:
        flash("Contact not found.", "danger")
        return redirect(url_for("contacts"))

    if request.method == "POST":
        subject = request.form["subject"]
        body = request.form["body"]
        try:
            reply_msg = Message(
                subject=subject, sender=app.config["MAIL_USERNAME"], recipients=[msg.get("email")]
            )
            reply_msg.body = body
            mail.send(reply_msg)

            supa_update("contact", {"replied": True}, filters=[("eq", "id", id)])
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
    supa_update("contact", {"seen": True}, filters=[("eq", "id", id)])
    return jsonify({"status": "ok"})


@app.route("/devices")
@login_required
def devices():
    try:
        r = supa_select("devices", select="*")
        all_devices = r.data or []
    except Exception as e:
        print(f"Error fetching devices: {e}")
        all_devices = []
    return render_template("admin/devices.html", devices=all_devices)


@app.route("/toggle/<int:device_id>", methods=["POST"])
@login_required
def toggle_status(device_id):
    r = supa_select("devices", select="*", filters=[("eq", "id", device_id)], limit=1)
    device = r.data[0] if r.data else None
    if device:
        new_status = 1 if device.get("status", 0) == 0 else 0
        supa_update("devices", {"status": new_status}, filters=[("eq", "id", device_id)])
        return jsonify({"success": True, "device_id": device_id, "status": new_status})
    return jsonify({"success": False, "error": "Device not found"}), 404


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    # session["logged_in"] stores the admin id
    admin_id = session.get("logged_in")

    # Fetch the admin row from Supabase
    r = supa_select("admin", select="*", filters=[("eq", "id", admin_id)], limit=1)
    admin = r.data[0] if r.data else None

    if request.method == "POST":
        # Get form values
        username = request.form.get("username")
        password = request.form.get("password")  # plain text

        payload = {"username": username}
        if password:
            payload["password"] = password

        # Update the admin row in Supabase
        supa_update("admin", payload, filters=[("eq", "id", admin_id)])
        flash("Settings updated successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("admin/settings.html", current_admin=admin)


@app.route("/edit_home", methods=["GET", "POST"])
@login_required
def edit_home():
    res = supa_select("home", select="*", limit=1)
    home_data = res.data[0] if res and res.data else None

    if request.method == "POST":
        # ADD THIS LINE TO DEBUG
        print("--- FORM DATA RECEIVED:", request.form)
        # Collect all the text data from the form into a dictionary (payload)
        payload = {
            "name": request.form.get("name"),
            "title": request.form.get("title"),
            "role": request.form.get("role"),
            "about": request.form.get("about"),
            "phone": request.form.get("phone"),
            "insta": request.form.get("insta"),
            "github": request.form.get("github"),
            "linkedin": request.form.get("linkedin"),
            "main": request.form.get("main"),
        }

        # Get the current image IDs to pass to the save_image function
        # This allows it to delete the old image from Cloudinary upon successful upload
        current_first_image = home_data.get("firstimage") if home_data else None
        current_second_image = home_data.get("secondimage") if home_data else None

        # Process file uploads using your existing helper function
        new_first_image_id = save_image(
            request.files.get('firstimage'), 
            current_first_image,
            'home'
        )
        new_second_image_id = save_image(
            request.files.get('secondimage'), 
            current_second_image,
            'home'
        )

        # Only add the image IDs to the payload if a new file was uploaded
        if new_first_image_id:
            payload['firstimage'] = new_first_image_id
        if new_second_image_id:
            payload['secondimage'] = new_second_image_id

        # If home_data exists, UPDATE the row. Otherwise, INSERT a new row.
        if home_data:
            supa_update("home", payload, filters=[("eq", "id", home_data.get("id"))])
        else:
            supa_insert("home", payload)

        flash("Home content updated successfully!", "success")
        return redirect(url_for("dashboard"))

    # For a GET request, just show the page with the fetched data
    return render_template("admin/edit_home.html", home_data=home_data)

@app.route("/projects")
@login_required
def list_projects():
    r = supa_select("projects", select="*")
    projects = r.data or []
    return render_template("projects/projects_list.html", projects=projects)


@app.route("/projects/add", methods=["GET", "POST"])
@login_required
def add_project():
    if request.method == "POST":
        image_public_id = save_image(request.files.get("image"), None, "projects")
        payload = {
            "title": request.form["title"],
            "description": request.form.get("desc") or request.form.get("description"),
            "image": image_public_id,
            "link": request.form.get("link"),
            "github": request.form.get("github"),
            "status": int(request.form.get("status", 1)),
            "tech_stack": request.form.get("tech_stack"),
        }

        supa_insert("projects", payload)
        flash("Project added successfully!", "success")
        return redirect(url_for("list_projects"))
    return render_template("projects/add_project.html")


@app.route("/projects/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_project(id):
    r = supa_select("projects", select="*", filters=[("eq", "id", id)], limit=1)
    project = r.data[0] if r.data else None
    if not project:
        flash("Project not found.", "danger")
        return redirect(url_for("list_projects"))
    
    if request.method == "POST":
        new_image = save_image(request.files.get("image"), project.get("image"), "projects")
        payload = {
            "title": request.form["title"],
            "description": request.form.get("desc") or request.form.get("description"),
            "link": request.form.get("link"),
            "github": request.form.get("github"),
            "status": int(request.form.get("status", 0)),
            "tech_stack": request.form.get("tech_stack"),
        }
        if new_image:
            payload["image"] = new_image

        supa_update("projects", payload, filters=[("eq", "id", id)])
        flash("Project updated successfully!", "info")
        return redirect(url_for("list_projects"))
    return render_template("projects/edit_project.html", project=project)


@app.route("/projects/delete/<int:id>", methods=["POST"])
@login_required
def delete_project(id):
    supa_update("projects", {"status": 0}, filters=[("eq", "id", id)])
    flash("Project deleted (set inactive)!", "warning")
    return redirect(url_for("list_projects"))


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("admin"))


@app.route("/api/status")
def api_status():
    try:
        r = supa_select("devices", select="*")
        devices_list = [{"id": d.get("id"), "status": d.get("status")} for d in (r.data or [])]
        return jsonify(devices_list)
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({"error": "Could not fetch device status"}), 500


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
            payload = {"name": name, "email": email_from, "message": message_body, "seen": False, "replied": False}
            supa_insert("contact", payload)
            flash("Message saved successfully!", "success")
        except Exception as e:
            print(f"DB insert failed: {e}")
            flash("Failed to save message. Please try again later.", "danger")

        return redirect(url_for("home", _anchor="contact"))


# -------------------------------
# Skills & Categories (CRUD)
# -------------------------------
@app.route("/skills/add", methods=["GET", "POST"])
@login_required
def add_skill():
    r_cats = supa_select("categories", select="*")
    categories = r_cats.data or []
    if request.method == "POST":
        name = request.form["name"]
        category_id = int(request.form["category_id"])
        payload = {"name": name, "category_id": category_id}
        supa_insert("skills", payload)
        flash("Skill Added Successfully ✅", "success")
        return redirect(url_for("view_skills"))
    return render_template("skills/add_skill.html", categories=categories)


@app.route("/skills")
@login_required
def view_skills():
    r = supa_select("skills", select="*, categories(name)") 
    skills = r.data or []
    # print(skills)
    return render_template("skills/view_skills.html", skills=skills)


@app.route("/skills/edit/<int:skill_id>", methods=["GET", "POST"])
@login_required
def edit_skill(skill_id):
    r_skill = supa_select("skills", select="*", filters=[("eq", "id", skill_id)], limit=1)
    skill = r_skill.data[0] if r_skill.data else None
    if not skill:
        flash("Skill not found.", "danger")
        return redirect(url_for("view_skills"))

    r_cats = supa_select("categories", select="*")
    categories = r_cats.data or []

    if request.method == "POST":
        name = request.form["name"]
        category_id = int(request.form["category_id"])
        supa_update("skills", {"name": name, "category_id": category_id}, filters=[("eq", "id", skill_id)])
        flash("Skill Updated Successfully ✏️", "success")
        return redirect(url_for("view_skills"))

    return render_template("skills/edit_skill.html", skill=skill, categories=categories)


@app.route("/skills/delete/<int:skill_id>")
@login_required
def delete_skill(skill_id):
    supa_delete("skills", filters=[("eq", "id", skill_id)])
    flash("Skill Deleted Successfully 🗑️", "danger")
    return redirect(url_for("view_skills"))

@app.route("/students")
@login_required
def view_students():
    search_term = request.args.get('search', '').strip()
    sort_by = request.args.get('sort', 'roll_no_asc')

    filters = None
    order = None

    if search_term:
        filters = [('ilike', 'name', f'%{search_term}%')]

    if sort_by:
        if '_' in sort_by:
            column, direction = sort_by.rsplit('_', 1)
            if column in ['name', 'roll_no'] and direction in ['asc', 'desc']:
                is_ascending = (direction == 'asc')
                order = (column, is_ascending)

    try:
        res = supa_select("students", select="*", filters=filters, order=order)
        students = res.data or []
    except Exception as e:
        print(f"Error fetching students: {e}")
        students = []
        flash("Could not fetch student records.", "danger")
        
    return render_template("students/view_students.html", students=students, search_term=search_term, sort_by=sort_by)



@app.route("/students/add", methods=["GET", "POST"])
@login_required
def add_student():
    """Handles adding a new student to the database."""
    if request.method == "POST":
        name = request.form.get("name")
        roll_no = request.form.get("roll_no")

        # Validation: Name and Roll No are mandatory
        if not name or not roll_no:
            flash("Name and Roll No are required fields.", "danger")
            # Redirect back to the form with the data the user already entered
            return render_template("students/add_edit_student.html", student=request.form)

        # Handle image upload
        image_public_id = save_image(request.files.get("image"), None, "students")

        # Prepare data payload for Supabase
        payload = {
            "name": name,
            "roll_no": roll_no,
            "email": request.form.get("email"),
            "image": image_public_id,
            "dob": request.form.get("dob") or None, # Handle empty date
            "dpt": request.form.get("dpt"),
            "ph_no": request.form.get("ph_no"),
            "f_name": request.form.get("f_name"),
            "m_name": request.form.get("m_name"),
            "f_phno": request.form.get("f_phno"),
            "m_phno": request.form.get("m_phno"),
            "aadhaar_no": request.form.get("aadhaar_no"),
            "address": request.form.get("address")
        }

        supa_insert("students", payload)
        flash("Student added successfully! ✅", "success")
        return redirect(url_for("view_students"))

    # For a GET request, show the empty form
    return render_template("students/add_edit_student.html", student=None)


@app.route("/students/edit/<int:student_id>", methods=["GET", "POST"])
@login_required
def edit_student(student_id):
    """Handles editing an existing student's details."""
    # Fetch the student to edit
    res = supa_select("students", select="*", filters=[("eq", "id", student_id)], limit=1)
    student = res.data[0] if res.data else None

    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("view_students"))
        
    # --- CHANGE 1: Clean data for display ---
    # Create a version of the student data where None is replaced with an empty string.
    # This prevents the word "None" from appearing in the form fields.
    student_for_display = {key: "" if value is None else value for key, value in student.items()}

    if request.method == "POST":
        name = request.form.get("name")
        roll_no = request.form.get("roll_no")

        if not name or not roll_no:
            flash("Name and Roll No are required fields.", "danger")
            # Pass the cleaned student data back to pre-fill the form on error
            return render_template("students/add_edit_student.html", student=student_for_display)

        # Handle image update (pass current image ID to delete it from Cloudinary)
        new_image_id = save_image(
            request.files.get("image"), 
            student.get("image"), # Use original data to get current image ID
            "students"
        )
        
        # --- CHANGE 2: Build payload without None values ---
        # Use request.form.get("key", "") to provide an empty string as a default
        # if the form field is missing or empty. This prevents sending None/null to the database.
        payload = {
            "name": name,
            "roll_no": roll_no,
            "email": request.form.get("email", ""),
            "dob": request.form.get("dob", ""),
            "dpt": request.form.get("dpt", ""),
            "ph_no": request.form.get("ph_no", ""),
            "f_name": request.form.get("f_name", ""),
            "m_name": request.form.get("m_name", ""),
            "f_phno": request.form.get("f_phno", ""),
            "m_phno": request.form.get("m_phno", ""),
            "aadhaar_no": request.form.get("aadhaar_no", ""),
            "address": request.form.get("address", "")
        }
        
        # Only add the image to the payload if a new one was uploaded
        if new_image_id:
            payload["image"] = new_image_id

        supa_update("students", payload, filters=[("eq", "id", student_id)])
        flash("Student details updated successfully! ✏️", "success")
        return redirect(url_for("view_students"))

    # For a GET request, show the form pre-filled with the cleaned student data
    return render_template("students/add_edit_student.html", student=student_for_display)



@app.route("/students/delete/<int:student_id>", methods=["POST"])
@login_required
def delete_student(student_id):
    """Handles deleting a student."""
    # Optional: You might want to delete the Cloudinary image as well, but that's more complex.
    # For now, we just delete the database record.
    supa_delete("students", filters=[("eq", "id", student_id)])
    flash("Student record deleted successfully. 🗑️", "warning")
    return redirect(url_for("view_students"))

@app.route("/students/view/<int:student_id>")
@login_required
def get_student_details(student_id):
    """API endpoint to get a single student's details as JSON."""
    try:
        res = supa_select("students", select="*", filters=[("eq", "id", student_id)], limit=1)
        student = res.data[0] if res.data else None
        if student:
            return jsonify(student) # Converts Python dict to JSON
        else:
            return jsonify({"error": "Student not found"}), 404
    except Exception as e:
        print(f"API Error fetching student {student_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
@app.route("/expenses")
@login_required
def expenses():
    res = supa_select(
        "expense",
        select="*",
        filters=[("eq", "user_id", session["logged_in"])],
        order=("date", False)
    )
    expenses = res.data or []
    total = sum(e["amount"] for e in expenses)
    return render_template("expenses.html", expenses=expenses, total=total)

# --- ADD EXPENSE ---
@app.route("/expenses/add", methods=["POST"])
@login_required
def add_expense():
    payload = {
        "title": request.form["title"],
        "amount": float(request.form["amount"]),
        "category": request.form["category"],
        "date": request.form["date"],
        "notes": request.form.get("notes",""),
        "user_id": session["logged_in"]
    }
    supa_insert("expense", payload)
    flash("Expense added successfully!", "success")
    return redirect(url_for("expenses"))

# --- EDIT EXPENSE ---
@app.route("/expenses/edit/<int:id>", methods=["POST"])
@login_required
def edit_expense(id):
    res = supa_select(
        "expense",
        filters=[("eq", "id", id), ("eq", "user_id", session["logged_in"])],
        limit=1
    )
    expense = res.data[0] if res.data else None
    if not expense:
        flash("Expense not found.", "danger")
        return redirect(url_for("expenses"))

    payload = {
        "title": request.form["title"],
        "amount": float(request.form["amount"]),
        "category": request.form["category"],
        "date": request.form["date"],
        "notes": request.form.get("notes","")
    }
    supa_update("expense", payload, filters=[("eq", "id", id)])
    flash("Expense updated successfully!", "success")
    return redirect(url_for("expenses"))

# --- DELETE EXPENSE ---
@app.route("/expenses/delete/<int:id>", methods=["POST"])
@login_required
def delete_expense(id):
    supa_delete(
        "expense",
        filters=[("eq", "id", id), ("eq", "user_id", session["logged_in"])]
    )
    flash("Expense deleted successfully!", "warning")
    return redirect(url_for("expenses"))

# --- EXPORT CSV ---
@app.route("/expenses/export/csv")
@login_required
def export_csv():
    res = supa_select("expense", select="*")
    expenses = res.data or []

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(["Title", "Amount", "Category", "Date"])
    for e in expenses:
        cw.writerow([e["title"], e["amount"], e["category"], e["date"]])

    # Encode to bytes for send_file
    output = BytesIO()
    output.write(si.getvalue().encode("utf-8"))
    output.seek(0)

    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name="expenses.csv"
    )

# --- EXPORT PDF ---
@app.route("/expenses/export/pdf")
@login_required
def export_pdf():
    res = supa_select(
        "expense",
        select="*",
        filters=[("eq", "user_id", session["logged_in"])]
    )
    expenses = res.data or []

    buffer = BytesIO()  # <-- use BytesIO for binary data
    p = canvas.Canvas(buffer)
    y = 800
    for e in expenses:
        p.drawString(
            50, y,
            f'{e["date"]} | {e["title"]} | {e["category"]} | ₹{e["amount"]}'
        )
        y -= 20
        if y < 50:
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="expenses.pdf",
        mimetype="application/pdf"
    )

# Error handler
@app.errorhandler(404)
def not_found(e):
    return render_template("default/404.html")


if __name__ == "__main__":
    app.run(debug=True)