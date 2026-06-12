from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, pickle, pandas as pd, numpy as np
import os, json, io
import PyPDF2

app = Flask(__name__)
app.secret_key = "internmatch_secret_2024"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# ── Load model ────────────────────────────────────────────────────────────────
with open("models/model.pkl", "rb") as f:    model = pickle.load(f)
with open("models/label_encoder.pkl", "rb") as f: le = pickle.load(f)
with open("models/mlb.pkl", "rb") as f:      mlb = pickle.load(f)
ALL_SKILLS = list(mlb.classes_)

ROLE_SKILLS = {
    "AI/ML Engineer Intern":        ["Python","Machine Learning","TensorFlow","Pandas","NumPy"],
    "Data Science Intern":          ["Python","Pandas","Statistics","SQL","Data Visualization"],
    "Full Stack Developer Intern":  ["JavaScript","React","Node.js","HTML","CSS","MongoDB"],
    "Flutter Developer Intern":     ["Flutter","Dart","Firebase","Mobile Development"],
    "UI/UX Design Intern":          ["Figma","Adobe XD","Wireframing","Prototyping","User Research"],
    "DevOps Intern":                ["Linux","Docker","CI/CD","Jenkins","Bash"],
    "Cloud Computing Intern":       ["AWS","Azure","GCP","Terraform","Cloud Architecture"],
    "HR Operations Intern":         ["Communication","MS Office","Recruitment","HR Policies","Excel"]
}

ROLE_ROADMAP = {
    "AI/ML Engineer Intern":        ["Learn Python deeply","Study ML algorithms","Practice on Kaggle","Build 2–3 ML projects","Get TensorFlow certified"],
    "Data Science Intern":          ["Master Pandas & NumPy","Learn SQL","Study Statistics","Build visualizations","Kaggle competitions"],
    "Full Stack Developer Intern":  ["Learn HTML/CSS/JS","Master React","Learn Node.js","Build full-stack apps","Learn MongoDB"],
    "Flutter Developer Intern":     ["Learn Dart basics","Build Flutter UI","Integrate Firebase","Publish a sample app"],
    "UI/UX Design Intern":          ["Learn Figma","Study UX principles","Build a portfolio","Do usability testing"],
    "DevOps Intern":                ["Learn Linux","Docker & Kubernetes","CI/CD pipelines","Cloud basics"],
    "Cloud Computing Intern":       ["AWS fundamentals","Get AWS cert","Learn Terraform","Deploy sample apps"],
    "HR Operations Intern":         ["Communication skills","Learn HR tools","Understand labor laws","Practice recruitment"]
}

INITIAL_VACANCIES = {
    "AI/ML Engineer Intern":        5,
    "Data Science Intern":          4,
    "Full Stack Developer Intern":  6,
    "Flutter Developer Intern":     3,
    "UI/UX Design Intern":          3,
    "DevOps Intern":                3,
    "Cloud Computing Intern":       4,
    "HR Operations Intern":         2
}

# ── Database ──────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, department TEXT, cgpa REAL,
        skills TEXT, projects INTEGER, certifications INTEGER,
        area_of_interest TEXT, preferred_tech TEXT, experience_level INTEGER,
        recommended_role TEXT, secondary_role TEXT,
        score REAL, score_label TEXT,
        missing_skills TEXT, roadmap TEXT,
        status TEXT DEFAULT 'Pending',
        resume_text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS vacancies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT UNIQUE,
        total INTEGER,
        available INTEGER
    )""")
    for role, count in INITIAL_VACANCIES.items():
        c.execute("INSERT OR IGNORE INTO vacancies (role, total, available) VALUES (?,?,?)",
                  (role, count, count))
    conn.commit()
    conn.close()

init_db()

# ── Helpers ───────────────────────────────────────────────────────────────────
def encode_candidate(skills_list, cgpa, projects, certifications, exp_level):
    skills_bin = mlb.transform([skills_list])
    X_skills = pd.DataFrame(skills_bin, columns=mlb.classes_)
    X_num = pd.DataFrame([[cgpa, projects, certifications, exp_level]],
                         columns=["cgpa","projects","certifications","experience_level"])
    return pd.concat([X_num, X_skills], axis=1)

def calculate_score(cgpa, projects, certifications, exp_level, skills_list, role):
    role_skills = ROLE_SKILLS.get(role, [])
    matched     = sum(1 for s in skills_list if s in role_skills)
    skill_score = (matched / max(len(role_skills),1)) * 40
    cgpa_score  = ((cgpa - 5.5) / 4.5) * 25
    proj_score  = min(projects/5,1) * 20
    cert_score  = min(certifications/3,1) * 10
    exp_score   = (exp_level/2) * 5
    total = round(min(skill_score+cgpa_score+proj_score+cert_score+exp_score, 100), 2)
    label = "Excellent Candidate" if total>=75 else ("Good Candidate" if total>=50 else "Needs Improvement")
    return total, label

def extract_skills_from_text(text):
    found = []
    text_lower = text.lower()
    for skill in ALL_SKILLS:
        if skill.lower() in text_lower:
            found.append(skill)
    return found

def extract_text_from_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except:
        return ""

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/analyze")
def index():
    return render_template("index.html", all_skills=ALL_SKILLS)

@app.route("/extract_resume", methods=["POST"])
def extract_resume():
    file = request.files.get("resume")
    if not file:
        return json.dumps({"name":"","department":"","cgpa":"","skills":[],"text":""})

    text = extract_text_from_pdf(file)
    skills = extract_skills_from_text(text)

    # ── Extract Name ──────────────────────────────────────────────────────
    name = ""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines[:8]:
        words = line.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
            skip = ["university","college","institute","department","resume","curriculum"]
            if not any(s in line.lower() for s in skip):
                name = line
                break

    # ── Extract CGPA ──────────────────────────────────────────────────────
    import re
    cgpa = ""
    cgpa_patterns = [
        r'cgpa[:\s]+(\d+\.?\d*)',
        r'gpa[:\s]+(\d+\.?\d*)',
        r'(\d\.\d{1,2})\s*/\s*10',
        r'(\d\.\d{1,2})\s*cgpa',
    ]
    for pattern in cgpa_patterns:
        match = re.search(pattern, text.lower())
        if match:
            val = float(match.group(1))
            if 0 < val <= 10:
                cgpa = str(val)
                break

    # ── Extract Department ────────────────────────────────────────────────
    department = ""
    dept_keywords = {
        "computer science": "Computer Science",
        "information technology": "Information Technology",
        "electronics": "Electronics & Communication",
        "electrical": "Electrical Engineering",
        "mechanical": "Mechanical Engineering",
        "civil": "Civil Engineering",
        "data science": "Data Science",
        "artificial intelligence": "Artificial Intelligence",
        "software engineering": "Software Engineering",
        "business administration": "Business Administration",
        "mba": "MBA",
    }
    text_lower = text.lower()
    for key, value in dept_keywords.items():
        if key in text_lower:
            department = value
            break

    return json.dumps({
        "name": name,
        "department": department,
        "cgpa": cgpa,
        "skills": skills,
        "text": text[:500]
    })

@app.route("/predict", methods=["POST"])
def predict():
    name           = request.form.get("name")
    department     = request.form.get("department")
    cgpa           = float(request.form.get("cgpa", 0))
    skills_raw     = request.form.getlist("skills")
    projects       = int(request.form.get("projects", 0))
    certifications = int(request.form.get("certifications", 0))
    area           = request.form.get("area_of_interest")
    preferred      = request.form.get("preferred_tech")
    exp_level      = int(request.form.get("experience_level", 0))
    resume_text    = request.form.get("resume_text", "")

    skills_list = [s.strip() for s in skills_raw if s.strip()]
    X = encode_candidate(skills_list, cgpa, projects, certifications, exp_level)
    proba = model.predict_proba(X)[0]
    top2  = np.argsort(proba)[::-1][:2]
    recommended_role = le.inverse_transform([top2[0]])[0]
    secondary_role   = le.inverse_transform([top2[1]])[0]

    score, score_label = calculate_score(cgpa, projects, certifications, exp_level, skills_list, recommended_role)
    missing = [s for s in ROLE_SKILLS.get(recommended_role,[]) if s not in skills_list]
    roadmap = ROLE_ROADMAP.get(recommended_role, [])

    conn = sqlite3.connect("database.db")
    cur = conn.execute("""
        INSERT INTO candidates
        (name,department,cgpa,skills,projects,certifications,area_of_interest,
         preferred_tech,experience_level,recommended_role,secondary_role,
         score,score_label,missing_skills,roadmap,resume_text)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (name,department,cgpa,", ".join(skills_list),projects,certifications,
          area,preferred,exp_level,recommended_role,secondary_role,
          score,score_label,", ".join(missing),json.dumps(roadmap),resume_text))
    conn.commit()
    cid = cur.lastrowid
    conn.close()

    return render_template("result.html",
        id=cid, name=name, department=department, cgpa=cgpa,
        skills=skills_list, projects=projects, certifications=certifications,
        recommended_role=recommended_role, secondary_role=secondary_role,
        score=score, score_label=score_label, missing=missing, roadmap=roadmap
    )

@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("database.db")
    rows = conn.execute("SELECT * FROM candidates ORDER BY created_at DESC").fetchall()
    conn.close()
    total = len(rows)
    if total == 0:
        return render_template("dashboard.html", total=0, rows=[],
                               role_data="{}", score_data="{}", avg_score=0)
    role_data  = {}
    score_dist = {"Excellent Candidate":0,"Good Candidate":0,"Needs Improvement":0}
    scores = []
    for r in rows:
        role_data[r[10]]  = role_data.get(r[10],0)+1
        score_dist[r[13]] = score_dist.get(r[13],0)+1
        scores.append(r[12])
    avg_score = round(sum(scores)/len(scores),1)
    return render_template("dashboard.html", total=total, rows=rows,
    role_data=json.dumps(role_data),
    score_data=json.dumps(score_dist), avg_score=avg_score,
    roles_covered=len(role_data))

# ── Availability ──────────────────────────────────────────────────────────────
@app.route("/availability")
def availability():
    conn = sqlite3.connect("database.db")
    rows = conn.execute("SELECT role, total, available FROM vacancies").fetchall()
    conn.close()
    return render_template("availability.html", vacancies=rows)

# ── Admin ─────────────────────────────────────────────────────────────────────
@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"]==ADMIN_USERNAME and request.form["password"]==ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin"))
        flash("Invalid credentials")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    search = request.args.get("search","")
    conn = sqlite3.connect("database.db")
    if search:
        rows = conn.execute(
            "SELECT * FROM candidates WHERE name LIKE ? OR department LIKE ? ORDER BY created_at DESC",
            (f"%{search}%",f"%{search}%")).fetchall()
    else:
        rows = conn.execute("SELECT * FROM candidates ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template("admin.html", rows=rows, search=search)

@app.route("/admin/candidate/<int:cid>")
def candidate_report(cid):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    conn = sqlite3.connect("database.db")
    r = conn.execute("SELECT * FROM candidates WHERE id=?", (cid,)).fetchone()
    vac = conn.execute("SELECT available FROM vacancies WHERE role=?", (r[10],)).fetchone()
    conn.close()
    if not r:
        return "Not found", 404
    roadmap = json.loads(r[15]) if r[15] else []
    available = vac[0] if vac else 0
    return render_template("candidate_report.html", r=r, roadmap=roadmap, available=available)

@app.route("/admin/action/<int:cid>/<action>", methods=["POST"])
def candidate_action(cid, action):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    conn = sqlite3.connect("database.db")
    candidate = conn.execute("SELECT recommended_role, status FROM candidates WHERE id=?", (cid,)).fetchone()
    if candidate:
        role, current_status = candidate
        if action == "accept" and current_status != "Accepted":
            vac = conn.execute("SELECT available FROM vacancies WHERE role=?", (role,)).fetchone()
            if vac and vac[0] > 0:
                conn.execute("UPDATE candidates SET status=? WHERE id=?", ("Accepted", cid))
                conn.execute("UPDATE vacancies SET available=available-1 WHERE role=?", (role,))
            else:
                conn.execute("UPDATE candidates SET status=? WHERE id=?", ("Accepted - No Vacancy", cid))
        elif action == "reject":
            if current_status == "Accepted":
                conn.execute("UPDATE vacancies SET available=available+1 WHERE role=?", (role,))
            conn.execute("UPDATE candidates SET status=? WHERE id=?", ("Rejected", cid))
        conn.commit()
    conn.close()
    return redirect(url_for("candidate_report", cid=cid))

@app.route("/admin/delete/<int:cid>", methods=["POST"])
def delete(cid):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    conn = sqlite3.connect("database.db")
    r = conn.execute("SELECT recommended_role, status FROM candidates WHERE id=?", (cid,)).fetchone()
    if r and r[1] == "Accepted":
        conn.execute("UPDATE vacancies SET available=available+1 WHERE role=?", (r[0],))
    conn.execute("DELETE FROM candidates WHERE id=?", (cid,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)