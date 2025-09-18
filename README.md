# Portfolio Flask Web

A Flask-based personal portfolio site with an admin dashboard, MySQL database integration, Cloudinary-powered image uploads, and email functionality using Flask-Mail.

## 📑 Table of Contents

1. Project Overview
2. Features
3. Prerequisites
4. Quick Install & Run (Development)
5. Database Setup
6. Mail & Cloudinary Setup
7. Deployment
8. Project Structure
9. Security Audit & Findings
10. Recommended .gitignore
11. FAQ & Troubleshooting
12. License

## 1. Project Overview

This project is a personal **portfolio web application** built with **Flask**.

It includes:
- Admin dashboard for managing content (projects, skills, messages).
- Database persistence with SQLAlchemy (MySQL backend).
- Cloudinary integration for media storage.
- Email sending via Flask-Mail.
- Responsive frontend with Jinja templates and Bootstrap.

## 2. Features

- 🔐 Admin authentication (session-based)
- 🗂 CRUD for projects, skills, and blog posts
- 🗄 MySQL database with SQLAlchemy ORM
- ✉️ Flask-Mail integration for contact forms
- ☁️ Cloudinary for image hosting
- 🎨 Bootstrap/Jinja templates for portfolio and admin UI

## 3. Prerequisites

- Python 3.8+
- MySQL (or a compatible DB, e.g., MariaDB)
- pip for dependency management

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

## 4. Quick Install & Run (Development)

1. Configure database and Cloudinary settings directly in `app.py` or a config file.
2. Import the provided SQL dump.
3. Start the server:

```bash
python app.py
```

## 5. Database Setup

Import the schema into MySQL:

```bash
mysql -u root -p your_db_name < portfolio.sql
```

For production, migrations with Flask-Migrate/Alembic are recommended.

## 6. Mail & Cloudinary Setup

- Update Flask-Mail settings in `app.py` with your SMTP details.
- Add Cloudinary credentials (cloud name, API key, API secret) in the config.

⚠️ Important: Never commit real credentials in a public repo.

## 7. Deployment

For production:
- Deploy via **Vercel** (already configured with `vercel.json`).
- Use a hosted MySQL database (e.g., freemysqldatabase).
- Store images on Cloudinary.
- Run with a production WSGI server like Gunicorn.

## 8. Project Structure

```
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

## 9. Security Audit & Findings

✅ No exposed API keys or secrets in repo.
⚠️ Ensure sensitive configs are never pushed to GitHub.
⚠️ Use strong SECRET_KEY in production.
⚠️ Use app passwords for mail instead of personal passwords.

## 10. FAQ & Troubleshooting

Q: App not starting?
- Check Python version & venv activation.

Q: DB connection errors?
- Verify DB credentials and MySQL server status.

Q: Static files not loading?
- Ensure `static/` folder exists and Flask is serving it.

## 11. License

MIT License
Copyright (c) 2025 Subash