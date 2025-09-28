# Web Project

This is a Flask-based web project deployed with Vercel.  
It uses Supabase for database management and includes a student management system and an expense tracker.

## Features
- User authentication (login required)
- Expense tracker with add, edit, delete, and export options (CSV/PDF)
- Student management system (add, view, edit, delete)
- Department-based filtering and search functionality
- Modal-based forms for view/edit/add students

## Tech Stack
- **Backend:** Flask (Python)
- **Database:** Supabase (PostgreSQL)
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Deployment:** Vercel

## Project Structure
- `app.py` → Main Flask application
- `database.py` → Supabase database connection
- `requirements.txt` → Python dependencies
- `vercel.json` → Vercel deployment configuration
- `static/` → Assets (CSS, images, games, event files)
- `.env` → Environment variables (ignored in Git)

## Setup
1. Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Add your environment variables in `.env` file:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   FLASK_API_KEY=your_secret_key
   ```
3. Run the app locally:
   ```bash
   python app.py
   ```

## Notes
- Do **not** upload `.env` file (contains sensitive credentials)
- Default student image stored in `static/assets/students/`