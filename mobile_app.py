from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, text
import os

app = FastAPI()

# Connect to your existing Neon PostgreSQL database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://your_neon_connection_string_here")
engine = create_engine(DATABASE_URL)

# Expanded HTML template matching your professional portal requirements
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JUC Staff Portal</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f6f9; margin: 0; padding: 20px; }
        .card { background: white; padding: 25px; border-radius: 12px; max-width: 600px; margin: auto; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h2 { color: #1e3a8a; text-align: center; margin-bottom: 20px; }
        label { font-weight: bold; display: block; margin-top: 15px; color: #374151; }
        input, textarea, select { width: 100%; padding: 12px; margin-top: 5px; border: 1px solid #d1d5db; border-radius: 8px; box-sizing: border-box; font-size: 16px; background-color: #fff; }
        button { width: 100%; background-color: #2563eb; color: white; padding: 14px; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; margin-top: 25px; cursor: pointer; }
        button:hover { background-color: #1d4ed8; }
        button:active { background-color: #1e40af; }
        .success { background: #d1fae5; color: #065f46; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 15px; font-weight: 500; }
        .error { background: #fee2e2; color: #991b1b; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 15px; font-weight: 500; }
    </style>
</head>
<body>
    <div class="card">
        <h2>JUC Staff & M&E Portal</h2>
        
        {% if success %}
            <div class="success">Report submitted successfully!</div>
        {% elif error %}
            <div class="error">{{ error_msg }}</div>
        {% endif %}
        
        <form method="POST" action="/">
            <label>Full Name</label>
            <input type="text" name="name" required placeholder="Enter your full name">
            
            <label>Department / Unit</label>
            <select name="department" required>
                <option value="" disabled selected>Select your department</option>
                <option value="Monitoring and Evaluation">Monitoring and Evaluation (M&E)</option>
                <option value="Youth Empowerment">Youth Empowerment</option>
                <option value="Administration">Administration</option>
                <option value="Programs">Programs</option>
                <option value="Management">Management</option>
            </select>
            
            <label>Reporting Period / Date</label>
            <input type="date" name="report_date" required>
            
            <label>Activity Report / Notes</label>
            <textarea name="report" rows="5" required placeholder="Describe your weekly activities, outcomes, and notes..."></textarea>
            
            <button type="submit">Submit Weekly Report</button>
        </form>
    </div>
</body>
</html>
"""

from jinja2 import Template

@app.get("/", response_class=HTMLResponse)
def read_form(success: bool = False, error: bool = False):
    t = Template(HTML_TEMPLATE)
    return t.render(success=success, error=error, error_msg="")

@app.post("/", response_class=HTMLResponse)
def handle_form(
    name: str = Form(...), 
    department: str = Form(...), 
    report_date: str = Form(...), 
    report: str = Form(...)
):
    try:
        # Save securely into your Neon PostgreSQL database table
        with engine.begin() as conn:
            query = text('''
                INSERT INTO your_table_name (name, department, report_date, report) 
                VALUES (:name, :dept, :date, :rep)
            ''')
            conn.execute(query, {
                "name": name, 
                "dept": department, 
                "date": report_date, 
                "rep": report
            })
            
        t = Template(HTML_TEMPLATE)
        return t.render(success=True, error=False, error_msg="")
    except Exception as e:
        t = Template(HTML_TEMPLATE)
        return t.render(success=False, error=True, error_msg=f"Database Error: {str(e)}")
