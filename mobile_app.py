from fastapi import FastAPI, Form, Request, Query
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, text
import os
from jinja2 import Template

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://your_neon_connection_string_here")
engine = create_engine(DATABASE_URL)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JUC Multi-Portal</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f6f9; margin: 0; padding: 15px; color: #333; }
        .container { max-width: 900px; margin: auto; }
        
        /* Navigation Tabs */
        .nav-tabs { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; background: white; padding: 10px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .nav-tabs a { padding: 10px 14px; text-decoration: none; color: #4b5563; background: #f3f4f6; border-radius: 8px; font-weight: 600; font-size: 14px; flex-grow: 1; text-align: center; }
        .nav-tabs a.active { background: #2563eb; color: white; }

        .card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 25px; }
        h2, h3 { color: #1e3a8a; margin-top: 0; text-align: center; }
        label { font-weight: bold; display: block; margin-top: 15px; color: #374151; }
        input, textarea, select { width: 100%; padding: 12px; margin-top: 5px; border: 1px solid #d1d5db; border-radius: 8px; box-sizing: border-box; font-size: 16px; background-color: #fff; }
        button { width: 100%; background-color: #2563eb; color: white; padding: 14px; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; margin-top: 25px; cursor: pointer; }
        button:hover { background-color: #1d4ed8; }
        .success { background: #d1fae5; color: #065f46; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 15px; font-weight: 500; }
        
        .table-responsive { overflow-x: auto; margin-top: 15px; }
        table { width: 100%; border-collapse: collapse; font-size: 14px; text-align: left; }
        th, td { padding: 12px; border: 1px solid #e5e7eb; }
        th { background-color: #f3f4f6; color: #374151; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Navigation Menu -->
        <div class="nav-tabs">
            <a href="/?tab=weekly" class="{% if tab == 'weekly' %}active{% endif %}">Weekly Report</a>
            <a href="/?tab=strategic" class="{% if tab == 'strategic' %}active{% endif %}">Strategic Pillar</a>
            <a href="/?tab=bubble" class="{% if tab == 'bubble' %}active{% endif %}">Bubble Dashboard</a>
            <a href="/?tab=admin" class="{% if tab == 'admin' %}active{% endif %}">Admin</a>
            <a href="/?tab=ngororero" class="{% if tab == 'ngororero' %}active{% endif %}">Ngororero</a>
            <a href="/?tab=youth" class="{% if tab == 'youth' %}active{% endif %}">Youth Program</a>
        </div>

        {% if success %}
            <div class="success">Record saved successfully!</div>
        {% endif %}

        <!-- TAB 1: WEEKLY REPORT -->
        {% if tab == 'weekly' %}
        <div class="card">
            <h2>Weekly Report Portal</h2>
            <form method="POST" action="/submit?tab=weekly">
                <label>Full Name</label>
                <input type="text" name="name" required placeholder="Enter your full name">
                <label>Department</label>
                <input type="text" name="department" required placeholder="Enter department">
                <label>Report Date</label>
                <input type="date" name="report_date" required>
                <label>Weekly Activity Notes</label>
                <textarea name="report" rows="4" required placeholder="Describe weekly progress..."></textarea>
                <button type="submit">Submit Weekly Report</button>
            </form>
        </div>

        <!-- TAB 2: STRATEGIC PILLAR REPORT -->
        {% elif tab == 'strategic' %}
        <div class="card">
            <h2>Strategic Pillar Report</h2>
            <form method="POST" action="/submit?tab=strategic">
                <label>Pillar Name / Focus Area</label>
                <input type="text" name="pillar" required placeholder="e.g., Pillar 1: Education">
                <label>Strategic Indicator / Milestone</label>
                <input type="text" name="indicator" required placeholder="Enter milestone description">
                <label>Progress Details</label>
                <textarea name="report" rows="4" required placeholder="Enter strategic outcomes..."></textarea>
                <button type="submit">Submit Strategic Report</button>
            </form>
        </div>

        <!-- TAB 3: BUBBLE DASHBOARD -->
        {% elif tab == 'bubble' %}
        <div class="card">
            <h2>Bubble Dashboard View</h2>
            <p style="text-align: center; color: #6b7280;">Embedded analytics views or custom metrics cards go here.</p>
            <!-- You can embed external dashboard frames or summary metrics here -->
        </div>

        <!-- TAB 4: ADMIN PANEL -->
        {% elif tab == 'admin' %}
        <div class="card">
            <h2>Admin Management Panel</h2>
            <p>System controls, user access logs, and management settings.</p>
        </div>

        <!-- TAB 5: NGORORERO PROGRAM -->
        {% elif tab == 'ngororero' %}
        <div class="card">
            <h2>Ngororero Program Portal</h2>
            <form method="POST" action="/submit?tab=ngororero">
                <label>Officer Name</label>
                <input type="text" name="name" required placeholder="Enter name">
                <label>Activity / Field Notes</label>
                <textarea name="report" rows="4" required placeholder="Enter Ngororero activities..."></textarea>
                <button type="submit">Submit Ngororero Report</button>
            </form>
        </div>

        <!-- TAB 6: YOUTH PROGRAM -->
        {% elif tab == 'youth' %}
        <div class="card">
            <h2>Youth Empowerment Program</h2>
            <form method="POST" action="/submit?tab=youth">
                <label>Facilitator Name</label>
                <input type="text" name="name" required placeholder="Enter name">
                <label>Youth Program Update</label>
                <textarea name="report" rows="4" required placeholder="Enter youth program details..."></textarea>
                <button type="submit">Submit Youth Report</button>
            </form>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def read_root(tab: str = "weekly", success: bool = False):
    t = Template(HTML_TEMPLATE)
    return t.render(tab=tab, success=success)

@app.post("/submit", response_class=HTMLResponse)
def handle_submit(tab: str = Query("weekly"), name: str = Form(None), department: str = Form(None), report_date: str = Form(None), pillar: str = Form(None), indicator: str = Form(None), report: str = Form(...)):
    # Save inputs into your database based on active tab context
    try:
        with engine.begin() as conn:
            query = text('''
                INSERT INTO your_table_name (tab_category, name, department, report_date, report) 
                VALUES (:tab, :name, :dept, :date, :rep)
            ''')
            conn.execute(query, {
                "tab": tab, 
                "name": name or "N/A", 
                "dept": department or pillar or "N/A", 
                "date": report_date or "2026-01-01", 
                "rep": report
            })
    except Exception as e:
        print("DB Error:", e)

    t = Template(HTML_TEMPLATE)
    return t.render(tab=tab, success=True)
