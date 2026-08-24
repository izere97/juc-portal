from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, text
import os
from jinja2 import Template

app = FastAPI()

# Connect to your Neon PostgreSQL database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://your_neon_connection_string_here")
engine = create_engine(DATABASE_URL)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JUC Staff & M&E Portal</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f6f9; margin: 0; padding: 20px; color: #333; }
        .container { max-width: 900px; margin: auto; }
        .card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 25px; }
        h2, h3 { color: #1e3a8a; margin-top: 0; text-align: center; }
        label { font-weight: bold; display: block; margin-top: 15px; color: #374151; }
        input, textarea, select { width: 100%; padding: 12px; margin-top: 5px; border: 1px solid #d1d5db; border-radius: 8px; box-sizing: border-box; font-size: 16px; background-color: #fff; }
        button { width: 100%; background-color: #2563eb; color: white; padding: 14px; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; margin-top: 25px; cursor: pointer; }
        button:hover { background-color: #1d4ed8; }
        .success { background: #d1fae5; color: #065f46; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 15px; font-weight: 500; }
        .error { background: #fee2e2; color: #991b1b; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 15px; font-weight: 500; }
        
        /* Table styling for mobile and desktop */
        .table-responsive { overflow-x: auto; margin-top: 15px; }
        table { width: 100%; border-collapse: collapse; font-size: 14px; text-align: left; }
        th, td { padding: 12px; border: 1px solid #e5e7eb; }
        th { background-color: #f3f4f6; color: #374151; }
        tr:nth-child(even) { background-color: #f9fafb; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Form Section -->
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
                <textarea name="report" rows="4" required placeholder="Describe your weekly activities, outcomes, and notes..."></textarea>
                
                <button type="submit">Submit Weekly Report</button>
            </form>
        </div>

        <!-- Reports View Section (Matches Streamlit Data View) -->
        <div class="card">
            <h3>Submitted Reports History</h3>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Department</th>
                            <th>Date</th>
                            <th>Report</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% if reports %}
                            {% for row in reports %}
                            <tr>
                                <td>{{ row.name }}</td>
                                <td>{{ row.department }}</td>
                                <td>{{ row.report_date }}</td>
                                <td>{{ row.report }}</td>
                            </tr>
                            {% endfor %}
                        {% else %}
                            <tr>
                                <td colspan="4" style="text-align: center; color: #6b7280;">No reports submitted yet.</td>
                            </tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def read_form(success: bool = False, error: bool = False):
    reports = []
    try:
        with engine.begin() as conn:
            # Fetch existing reports from your table (replace 'your_table_name' with your actual table name)
            result = conn.execute(text("SELECT name, department, report_date, report FROM your_table_name ORDER BY report_date DESC"))
            reports = [dict(row._mapping) for row in result]
    except Exception:
        pass # Handle table creation/missing table gracefully if needed

    t = Template(HTML_TEMPLATE)
    return t.render(success=success, error=error, error_msg="", reports=reports)

@app.post("/", response_class=HTMLResponse)
def handle_form(
    name: str = Form(...), 
    department: str = Form(...), 
    report_date: str = Form(...), 
    report: str = Form(...)
):
    reports = []
    try:
        with engine.begin() as conn:
            # Insert new report
            insert_query = text('''
                INSERT INTO your_table_name (name, department, report_date, report) 
                VALUES (:name, :dept, :date, :rep)
            ''')
            conn.execute(insert_query, {"name": name, "dept": department, "date": report_date, "rep": report})
            
            # Fetch updated reports list
            result = conn.execute(text("SELECT name, department, report_date, report FROM your_table_name ORDER BY report_date DESC"))
            reports = [dict(row._mapping) for row in result]
            
        t = Template(HTML_TEMPLATE)
        return t.render(success=True, error=False, error_msg="", reports=reports)
    except Exception as e:
        try:
            with engine.begin() as conn:
                result = conn.execute(text("SELECT name, department, report_date, report FROM your_table_name ORDER BY report_date DESC"))
                reports = [dict(row._mapping) for row in result]
        except:
            pass
            
        t = Template(HTML_TEMPLATE)
        return t.render(success=False, error=True, error_msg=f"Database Error: {str(e)}", reports=reports)
