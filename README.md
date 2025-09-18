# Portfolio Flask Web

A Flask-based personal portfolio site with admin functionality, SQLAlchemy models, Cloudinary image uploads, and email functionality (Flask-Mail).

---

## Table of Contents
1. Project Overview  
2. Features  
3. Prerequisites  
4. Quick Install & Run (Development)  
5. Environment Variables  
6. Database Setup  
7. Mail & Cloudinary Setup  
8. Deployment  
9. Project Structure  
10. Security Audit & Findings  
11. Recommended .gitignore  
12. FAQ & Troubleshooting  
13. License  

---

## 1. Project Overview
This project is a portfolio web application built using **Flask**. It includes:
- Admin dashboard for managing content (projects, skills, blog posts).
- Database persistence with SQLAlchemy.
- File/image uploads with Cloudinary.
- Email sending with Flask-Mail.
- Modern templating for portfolio and admin UI.

---

## 2. Features
- 🔐 Admin login with session-based authentication  
- 🗂 CRUD for portfolio items and blog posts  
- 🗄 SQLAlchemy ORM with MySQL (via PyMySQL)  
- ✉️ Email functionality (Flask-Mail)  
- ☁️ Cloudinary integration for image storage  
- 🎨 Bootstrap/Jinja templates  

---

## 3. Prerequisites
- Python 3.8+  
- MySQL or compatible DB  
- `pip` for dependency management  

Create a virtual environment and install requirements:
```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

---

## 4. Quick Install & Run (Development)
1. Create a `.env` file (see below).  
2. Initialize your database.  
3. Run the app:
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

---

## 5. Environment Variables
Create a `.env` file (never commit real credentials):

```env
SECRET_KEY="replace-with-a-strong-secret"

DB_USERNAME="your_db_user"
DB_PASSWORD="your_db_password"
DB_SERVER="localhost"
DB_PORT="3306"
DB_NAME="your_db_name"

MAIL_SERVER="smtp.example.com"
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME="your-email@example.com"
MAIL_PASSWORD="your-mail-app-password"

CLOUDINARY_CLOUD_NAME="your-cloud-name"
CLOUDINARY_API_KEY="your-api-key"
CLOUDINARY_API_SECRET="your-api-secret"
```

---

## 6. Database Setup
To import schema/dump:
```bash
mysql -u root -p your_db_name < portfolio.sql
```
For production, use Alembic/Flask-Migrate migrations.

---

## 7. Mail & Cloudinary Setup
- Configure email with `MAIL_*` vars.  
- Configure Cloudinary with `CLOUDINARY_*` vars.  
⚠️ Never commit secrets.

---

## 8. Deployment
For production:
- Use Gunicorn or uWSGI behind Nginx.  
- Configure `.env` variables securely.  
- Run DB migrations before first deploy.  

---

## 9. Project Structure
```markdown
📂 portfolio-flask-web-unzipped
📂 portfolio-flask-web
    📄 app.py
    📄 portfolio.sql
    📄 requirements.txt
    📄 vercel.json
    📂 static
        📂 css
            📄 admin.css
            📄 dashboard.css
            📂 home
                📄 style.css
            📂 skills
                📄 style.css
        📂 js
            📂 home
                📄 script.js
    📂 templates
        📄 main.html
        📂 admin
            📄 admin.html
            📄 contact.html
            📄 dashboard.html
            📄 edit_home.html
            📄 reply.html
            📄 settings.html
        📂 default
            📄 404.html
        📂 projects
            📄 add_project.html
            📄 edit_project.html
            📄 projects_list.html
        📂 skills
            📄 add_skill.html
            📄 edit_skill.html
            📄 view_skills.html
```

---

## 10. Security Audit & Findings
✅ No exposed API keys or secrets in repo (all are `.env`).  
⚠️ Ensure `.env`, `__pycache__/`, and `*.db` are in `.gitignore`.  
⚠️ Use strong `SECRET_KEY` in production.  
⚠️ Use app passwords for mail (not personal passwords).  

---

## 11. Recommended .gitignore
```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
*.db
*.sqlite3

# Virtual environment
.venv/

# Env files
.env
.env.*

# Logs
*.log
```

---

## 12. FAQ & Troubleshooting
**Q: App not starting?**  
- Check Python version & venv activation.  

**Q: DB connection errors?**  
- Verify `.env` DB settings & MySQL server running.  

**Q: Static files not loading?**  
- Ensure `static/` folder exists and Flask is serving.  

---

## 13. License
MIT License  
Copyright (c) 2025 SUBASH
