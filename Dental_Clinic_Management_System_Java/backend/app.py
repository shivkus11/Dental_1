import os, sqlite3, secrets, hashlib, hmac, json
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from flask import Flask, request, jsonify, session, send_from_directory, abort
from werkzeug.utils import secure_filename

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "dental_clinic.db"
UPLOAD_DIR = ROOT / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "pdf"}
TREATMENTS = [
    "X-rays", "Implants", "Tooth extraction", "Caries filling", "Missing teeth",
    "Bridges", "Crowns", "Removable partial dentures (RPD)",
    "Periodontitis treatment", "Scaling"
]
app = Flask(__name__, static_folder="web", static_url_path="")
app.secret_key = os.environ.get("DENTAL_SECRET_KEY", "dev-only-change-this-secret")
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
                  MAX_CONTENT_LENGTH=8 * 1024 * 1024)

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con

def hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 240_000)
    return salt.hex() + ":" + digest.hex()

def verify_password(password, stored):
    try:
        salt_hex, digest_hex = stored.split(":", 1)
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 240_000)
        return hmac.compare_digest(candidate.hex(), digest_hex)
    except Exception:
        return False

def init_db():
    with connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(
          id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
          role TEXT NOT NULL DEFAULT 'dentist', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS patients(
          id INTEGER PRIMARY KEY, patient_code TEXT UNIQUE NOT NULL, full_name TEXT NOT NULL,
          dob TEXT, gender TEXT, phone TEXT, email TEXT, address TEXT, emergency_contact TEXT,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS medical_history(
          id INTEGER PRIMARY KEY, patient_id INTEGER NOT NULL UNIQUE REFERENCES patients(id) ON DELETE CASCADE,
          conditions TEXT DEFAULT '', allergies TEXT DEFAULT '', medications TEXT DEFAULT '',
          surgeries TEXT DEFAULT '', notes TEXT DEFAULT '', updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS treatments(
          id INTEGER PRIMARY KEY, patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
          category TEXT NOT NULL, tooth_number TEXT DEFAULT '', treatment_date TEXT DEFAULT '',
          description TEXT DEFAULT '', cost REAL DEFAULT 0, status TEXT DEFAULT 'Planned',
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS dental_charts(
          id INTEGER PRIMARY KEY, patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
          chart_type TEXT NOT NULL, chart_date TEXT NOT NULL, tooth_status_json TEXT NOT NULL,
          notes TEXT DEFAULT '', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS dental_images(
          id INTEGER PRIMARY KEY, patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
          filename TEXT NOT NULL, original_name TEXT NOT NULL, category TEXT DEFAULT 'General',
          caption TEXT DEFAULT '', uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS appointments(
          id INTEGER PRIMARY KEY, patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
          appointment_at TEXT NOT NULL, reason TEXT DEFAULT '', doctor TEXT DEFAULT '',
          status TEXT NOT NULL DEFAULT 'Scheduled', reminder_sent INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS followups(
          id INTEGER PRIMARY KEY, patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
          treatment_id INTEGER REFERENCES treatments(id) ON DELETE SET NULL,
          due_date TEXT NOT NULL, notes TEXT DEFAULT '', status TEXT NOT NULL DEFAULT 'Pending',
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """)
        row = c.execute("SELECT id FROM users WHERE username='admin'").fetchone()
        if not row:
            c.execute("INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",
                      ("admin", hash_password("ChangeMe123!"), "admin"))

def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Authentication required"}), 401
        return fn(*args, **kwargs)
    return wrapped

def rowdict(row):
    return dict(row) if row else None

def body():
    return request.get_json(silent=True) or {}

def required(data, keys):
    missing = [k for k in keys if not str(data.get(k, "")).strip()]
    if missing:
        return "Required field(s): " + ", ".join(missing)
    return None

@app.get("/")
def home():
    return app.send_static_file("index.html")

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "Dental Clinic Management API"})

@app.post("/api/login")
def login():
    data = body()
    err = required(data, ["username", "password"])
    if err: return jsonify({"error": err}), 400
    with connect() as c:
        user = c.execute("SELECT * FROM users WHERE username=?", (data["username"].strip(),)).fetchone()
    if not user or not verify_password(data["password"], user["password_hash"]):
        return jsonify({"error": "Invalid username or password"}), 401
    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["role"] = user["role"]
    return jsonify({"id": user["id"], "username": user["username"], "role": user["role"]})

@app.post("/api/logout")
@login_required
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

@app.get("/api/me")
@login_required
def me():
    return jsonify({"username": session.get("username"), "role": session.get("role")})

@app.get("/api/dashboard")
@login_required
def dashboard():
    with connect() as c:
        return jsonify({
            "patients": c.execute("SELECT COUNT(*) n FROM patients").fetchone()["n"],
            "appointments": c.execute("SELECT COUNT(*) n FROM appointments WHERE status='Scheduled'").fetchone()["n"],
            "followups": c.execute("SELECT COUNT(*) n FROM followups WHERE status='Pending'").fetchone()["n"],
            "treatments": c.execute("SELECT COUNT(*) n FROM treatments").fetchone()["n"]
        })

@app.get("/api/patients")
@login_required
def list_patients():
    q = request.args.get("q", "").strip()
    with connect() as c:
        rows = c.execute("""SELECT * FROM patients
          WHERE (?='' OR full_name LIKE ? OR patient_code LIKE ? OR phone LIKE ?)
          ORDER BY full_name LIMIT 250""", (q, f"%{q}%", f"%{q}%", f"%{q}%")).fetchall()
    return jsonify([rowdict(r) for r in rows])

@app.post("/api/patients")
@login_required
def create_patient():
    d = body()
    err = required(d, ["full_name"])
    if err: return jsonify({"error": err}), 400
    code = "DENT-" + secrets.token_hex(4).upper()
    with connect() as c:
        cur = c.execute("""INSERT INTO patients(patient_code,full_name,dob,gender,phone,email,address,emergency_contact)
          VALUES(?,?,?,?,?,?,?,?)""", (code, d["full_name"].strip(), d.get("dob",""), d.get("gender",""),
          d.get("phone",""), d.get("email",""), d.get("address",""), d.get("emergency_contact","")))
        pid = cur.lastrowid
        c.execute("INSERT INTO medical_history(patient_id) VALUES(?)", (pid,))
        row = c.execute("SELECT * FROM patients WHERE id=?", (pid,)).fetchone()
    return jsonify(rowdict(row)), 201

@app.get("/api/patients/<int:pid>")
@login_required
def patient_detail(pid):
    with connect() as c:
        p = c.execute("SELECT * FROM patients WHERE id=?", (pid,)).fetchone()
        if not p: return jsonify({"error":"Patient not found"}), 404
        mh = c.execute("SELECT * FROM medical_history WHERE patient_id=?", (pid,)).fetchone()
        ts = c.execute("SELECT * FROM treatments WHERE patient_id=? ORDER BY id DESC", (pid,)).fetchall()
        ap = c.execute("SELECT * FROM appointments WHERE patient_id=? ORDER BY appointment_at DESC", (pid,)).fetchall()
        fu = c.execute("SELECT * FROM followups WHERE patient_id=? ORDER BY due_date DESC", (pid,)).fetchall()
        imgs = c.execute("SELECT * FROM dental_images WHERE patient_id=? ORDER BY id DESC", (pid,)).fetchall()
        charts = c.execute("SELECT * FROM dental_charts WHERE patient_id=? ORDER BY id DESC", (pid,)).fetchall()
    return jsonify({"patient":rowdict(p), "medical_history":rowdict(mh), "treatments":[rowdict(x) for x in ts],
                    "appointments":[rowdict(x) for x in ap], "followups":[rowdict(x) for x in fu],
                    "images":[rowdict(x) for x in imgs], "charts":[rowdict(x) for x in charts]})

@app.put("/api/patients/<int:pid>/medical-history")
@login_required
def save_medical_history(pid):
    d = body()
    with connect() as c:
        if not c.execute("SELECT id FROM patients WHERE id=?", (pid,)).fetchone():
            return jsonify({"error":"Patient not found"}), 404
        c.execute("""INSERT INTO medical_history(patient_id,conditions,allergies,medications,surgeries,notes,updated_at)
          VALUES(?,?,?,?,?,?,CURRENT_TIMESTAMP)
          ON CONFLICT(patient_id) DO UPDATE SET conditions=excluded.conditions, allergies=excluded.allergies,
          medications=excluded.medications, surgeries=excluded.surgeries, notes=excluded.notes, updated_at=CURRENT_TIMESTAMP""",
          (pid,d.get("conditions",""),d.get("allergies",""),d.get("medications",""),d.get("surgeries",""),d.get("notes","")))
        row = c.execute("SELECT * FROM medical_history WHERE patient_id=?", (pid,)).fetchone()
    return jsonify(rowdict(row))

@app.get("/api/treatments/categories")
@login_required
def treatment_categories():
    return jsonify(TREATMENTS)

@app.post("/api/treatments")
@login_required
def add_treatment():
    d=body()
    err=required(d,["patient_id","category"])
    if err: return jsonify({"error":err}),400
    if d["category"] not in TREATMENTS: return jsonify({"error":"Invalid treatment category"}),400
    try: pid=int(d["patient_id"]); cost=float(d.get("cost") or 0)
    except (ValueError,TypeError): return jsonify({"error":"Invalid patient ID or cost"}),400
    with connect() as c:
        if not c.execute("SELECT id FROM patients WHERE id=?", (pid,)).fetchone(): return jsonify({"error":"Patient not found"}),404
        cur=c.execute("""INSERT INTO treatments(patient_id,category,tooth_number,treatment_date,description,cost,status)
          VALUES(?,?,?,?,?,?,?)""",(pid,d["category"],d.get("tooth_number",""),d.get("treatment_date",""),
          d.get("description",""),cost,d.get("status","Planned")))
        row=c.execute("SELECT * FROM treatments WHERE id=?",(cur.lastrowid,)).fetchone()
    return jsonify(rowdict(row)),201

@app.post("/api/charts")
@login_required
def save_chart():
    d=body()
    err=required(d,["patient_id","chart_date","tooth_status"])
    if err: return jsonify({"error":err}),400
    try: pid=int(d["patient_id"])
    except (ValueError,TypeError): return jsonify({"error":"Invalid patient ID"}),400
    with connect() as c:
        p=c.execute("SELECT dob FROM patients WHERE id=?", (pid,)).fetchone()
        if not p: return jsonify({"error":"Patient not found"}),404
        chart_type=d.get("chart_type","adult")
        if chart_type=="child":
            if not p["dob"]: return jsonify({"error":"Patient date of birth is required for child chart validation"}),400
            try:
                born=datetime.strptime(p["dob"],"%Y-%m-%d").date()
                today=datetime.now().date()
                age=today.year-born.year-((today.month,today.day)<(born.month,born.day))
            except ValueError: return jsonify({"error":"Date of birth must use YYYY-MM-DD"}),400
            if not 6 <= age <= 12: return jsonify({"error":"Child chart is only available for ages 6 to 12"}),400
        cur=c.execute("INSERT INTO dental_charts(patient_id,chart_type,chart_date,tooth_status_json,notes) VALUES(?,?,?,?,?)",
          (pid,chart_type,d["chart_date"],json.dumps(d["tooth_status"]),d.get("notes","")))
        row=c.execute("SELECT * FROM dental_charts WHERE id=?",(cur.lastrowid,)).fetchone()
    return jsonify(rowdict(row)),201

@app.post("/api/images")
@login_required
def upload_image():
    patient_id=request.form.get("patient_id","")
    if not patient_id.isdigit(): return jsonify({"error":"Valid patient_id is required"}),400
    file=request.files.get("file")
    if not file or not file.filename: return jsonify({"error":"Select a file"}),400
    original=secure_filename(file.filename)
    ext=original.rsplit(".",1)[-1].lower() if "." in original else ""
    if ext not in ALLOWED_EXTENSIONS: return jsonify({"error":"Allowed formats: png, jpg, jpeg, webp, pdf"}),400
    with connect() as c:
        if not c.execute("SELECT id FROM patients WHERE id=?", (int(patient_id),)).fetchone(): return jsonify({"error":"Patient not found"}),404
        filename=secrets.token_hex(16)+"."+ext
        file.save(UPLOAD_DIR/filename)
        cur=c.execute("INSERT INTO dental_images(patient_id,filename,original_name,category,caption) VALUES(?,?,?,?,?)",
          (int(patient_id),filename,original,request.form.get("category","General"),request.form.get("caption","")))
        row=c.execute("SELECT * FROM dental_images WHERE id=?",(cur.lastrowid,)).fetchone()
    return jsonify({**rowdict(row),"url":f"/api/images/{row['id']}/file"}),201

@app.get("/api/images/<int:image_id>/file")
@login_required
def get_image(image_id):
    with connect() as c:
        row=c.execute("SELECT filename FROM dental_images WHERE id=?",(image_id,)).fetchone()
    if not row or not (UPLOAD_DIR/row["filename"]).exists(): abort(404)
    return send_from_directory(UPLOAD_DIR,row["filename"],as_attachment=False)

@app.get("/api/appointments")
@login_required
def list_appointments():
    with connect() as c:
        rows=c.execute("""SELECT a.*,p.full_name,p.patient_code,p.phone FROM appointments a
          JOIN patients p ON p.id=a.patient_id ORDER BY appointment_at LIMIT 500""").fetchall()
    return jsonify([rowdict(r) for r in rows])

@app.post("/api/appointments")
@login_required
def create_appointment():
    d=body()
    err=required(d,["patient_id","appointment_at"])
    if err:return jsonify({"error":err}),400
    try: pid=int(d["patient_id"])
    except (ValueError,TypeError):return jsonify({"error":"Invalid patient ID"}),400
    with connect() as c:
        if not c.execute("SELECT id FROM patients WHERE id=?",(pid,)).fetchone():return jsonify({"error":"Patient not found"}),404
        cur=c.execute("INSERT INTO appointments(patient_id,appointment_at,reason,doctor) VALUES(?,?,?,?)",
          (pid,d["appointment_at"],d.get("reason",""),d.get("doctor","")))
        row=c.execute("SELECT * FROM appointments WHERE id=?",(cur.lastrowid,)).fetchone()
    return jsonify(rowdict(row)),201

@app.patch("/api/appointments/<int:aid>")
@login_required
def update_appointment(aid):
    d=body()
    allowed={"appointment_at","reason","doctor","status","reminder_sent"}
    changes={k:v for k,v in d.items() if k in allowed}
    if not changes:return jsonify({"error":"No valid fields supplied"}),400
    if "status" in changes and changes["status"] not in ("Scheduled","Completed","Cancelled"):
        return jsonify({"error":"Invalid status"}),400
    sql=", ".join(f"{k}=?" for k in changes)
    with connect() as c:
        cur=c.execute(f"UPDATE appointments SET {sql} WHERE id=?",(*changes.values(),aid))
        if cur.rowcount==0:return jsonify({"error":"Appointment not found"}),404
        row=c.execute("SELECT * FROM appointments WHERE id=?",(aid,)).fetchone()
    return jsonify(rowdict(row))

@app.get("/api/reminders")
@login_required
def reminders():
    now=datetime.now().strftime("%Y-%m-%dT%H:%M")
    until=(datetime.now()+timedelta(days=7)).strftime("%Y-%m-%dT%H:%M")
    with connect() as c:
        rows=c.execute("""SELECT a.*,p.full_name,p.phone,p.email FROM appointments a JOIN patients p ON p.id=a.patient_id
          WHERE a.status='Scheduled' AND a.reminder_sent=0 AND a.appointment_at BETWEEN ? AND ?
          ORDER BY a.appointment_at""",(now,until)).fetchall()
    return jsonify({"delivery":"queue_only; configure an SMS/email provider for delivery",
                    "items":[rowdict(r) for r in rows]})

@app.get("/api/followups")
@login_required
def list_followups():
    with connect() as c:
        rows=c.execute("""SELECT f.*,p.full_name,p.patient_code FROM followups f JOIN patients p ON p.id=f.patient_id
          ORDER BY due_date LIMIT 500""").fetchall()
    return jsonify([rowdict(r) for r in rows])

@app.post("/api/followups")
@login_required
def add_followup():
    d=body()
    err=required(d,["patient_id","due_date"])
    if err:return jsonify({"error":err}),400
    try:pid=int(d["patient_id"])
    except (ValueError,TypeError):return jsonify({"error":"Invalid patient ID"}),400
    with connect() as c:
        if not c.execute("SELECT id FROM patients WHERE id=?",(pid,)).fetchone():return jsonify({"error":"Patient not found"}),404
        cur=c.execute("INSERT INTO followups(patient_id,treatment_id,due_date,notes) VALUES(?,?,?,?)",
          (pid,d.get("treatment_id") or None,d["due_date"],d.get("notes","")))
        row=c.execute("SELECT * FROM followups WHERE id=?",(cur.lastrowid,)).fetchone()
    return jsonify(rowdict(row)),201

@app.patch("/api/followups/<int:fid>")
@login_required
def update_followup(fid):
    d=body()
    if d.get("status") not in ("Pending","Completed","Cancelled"):
        return jsonify({"error":"status must be Pending, Completed, or Cancelled"}),400
    with connect() as c:
        cur=c.execute("UPDATE followups SET status=? WHERE id=?",(d["status"],fid))
        if cur.rowcount==0:return jsonify({"error":"Follow-up not found"}),404
        row=c.execute("SELECT * FROM followups WHERE id=?",(fid,)).fetchone()
    return jsonify(rowdict(row))

@app.errorhandler(413)
def too_large(_):
    return jsonify({"error":"File too large; maximum size is 8 MB"}),413

init_db()
if __name__ == "__main__":
    # Development server only; do not expose this directly to the public internet.
    app.run(host="0.0.0.0", port=5000, debug=False)
