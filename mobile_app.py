from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, text
import os

app = FastAPI()

# Connect to your existing Neon database using your environment variable / secret URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://your_neon_connection_string_here")
engine = create_engine(DATABASE_URL)

# Simple embedded HTML template optimized for mobile screens
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JUC Mobile Portal</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f6f9; margin: 0; padding: 20px; }
        .card { background: white; padding: 20px; border-radius: 12px; max-width: 500px; margin: auto; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h2 { color: #1e3a8a; text-align: center; margin-bottom: 20px; }
        label { font-weight: bold; display: block; margin-top: 15px; color: #374151; }
        input, textarea, select { width: 100%; padding: 12px; margin-top: 5px; border: 1px solid #d1d5db; border-radius: 8px; box-sizing: border-box; font-size: 16px; }
        button { width: 100%; background-color: #2563eb; color: white; padding: 14px; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; margin-top: 25px; cursor: pointer; }
        button:active { background-color: #1d4ed8; }
        .success { background: #d1fae5; color: #065f46; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>JUC Staff Portal</h2>
        {% if success %}
            <div class="success">Report submitted successfully!</div>
        {% endif %}
        <form method="POST" action="/">
            <label>Full Name</label>
            <input type="text" name="name" required placeholder="Enter your name">
            
            <label>Department</label>
            <input type="text" name="department" required placeholder="Enter your department">
            
            <label>Activity Report / Notes</label>
            <textarea name="report" rows="4" required placeholder="Describe your activity..."></textarea>
            
            <button type="submit">Submit Report</button>
        </form>
    </div>
</body>
</html>
"""

from jinja2 import Template

@app.get("/", response_class=HTMLResponse)
def read_form(success: bool = False):
    t = Template(HTML_TEMPLATE)
    return t.render(success=success)

@app.post("/", response_class=HTMLResponse)
def handle_form(name: str = Form(...), department: str = Form(...), report: str = Form(...)):
    # Save directly to your Neon PostgreSQL database table
    with engine.begin() as conn:
        query = text('INSERT INTO your_table_name (name, department, report) VALUES (:name, :dept, :rep)')
        conn.execute(query, {"name": name, "dept": department, "rep": report})
        
    t = Template(HTML_TEMPLATE)
    return t.render(success=True)
