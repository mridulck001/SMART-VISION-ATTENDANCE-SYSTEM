import os
import io
import threading
import sqlite3
import datetime
import json
import logging
from functools import wraps
from flask import Flask, render_template, request, jsonify, send_file, abort, redirect, url_for, session

# Import your custom model helpers
# NOTE: Ensure model.py exists and has these functions!
from model import train_model_background, extract_embedding_for_image, MODEL_PATH, load_model_if_exists, predict_with_model

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "attendance.db")
DATASET_DIR = os.path.join(APP_DIR, "dataset")
os.makedirs(DATASET_DIR, exist_ok=True)
TRAIN_STATUS_FILE = os.path.join(APP_DIR, "train_status.json")

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")
logging.basicConfig(level=logging.INFO)

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    roll TEXT,
                    class TEXT,
                    section TEXT,
                    reg_no TEXT,
                    created_at TEXT
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    name TEXT,
                    timestamp TEXT
                )""")
    conn.commit()
    conn.close()

init_db()

def write_train_status(status_dict):
    try:
        with open(TRAIN_STATUS_FILE, "w") as f:
            json.dump(status_dict, f)
    except Exception as e:
        print(f"Error writing status: {e}")

def read_train_status():
    if not os.path.exists(TRAIN_STATUS_FILE):
        return {"running": False, "progress": 0, "message": "Not trained"}
    try:
        with open(TRAIN_STATUS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"running": False, "progress": 0, "message": "Error reading status"}

write_train_status({"running": False, "progress": 0, "message": "No training yet."})


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            api_paths = {"/upload_face", "/train_model", "/train_status", "/attendance_stats", "/add_student"}
            if request.path in api_paths or request.method != "GET" or request.accept_mimetypes.best == "application/json" or request.is_json:
                return jsonify({"error": "admin login required"}), 401
            return redirect(url_for("admin_login", next=request.path))
        return view_func(*args, **kwargs)

    return wrapped

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin", methods=["GET"])
@admin_required
def admin_dashboard():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM students")
    student_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM attendance")
    attendance_count = c.fetchone()[0]
    c.execute("SELECT name, timestamp FROM attendance ORDER BY timestamp DESC LIMIT 5")
    recent_attendance = c.fetchall()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        student_count=student_count,
        attendance_count=attendance_count,
        recent_attendance=recent_attendance,
        train_status=read_train_status(),
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    next_url = request.args.get("next") or request.form.get("next") or url_for("admin_dashboard")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(next_url)

        error = "Invalid admin credentials."

    return render_template("admin_login.html", error=error, next_url=next_url, default_username=ADMIN_USERNAME)


@app.route("/admin/logout", methods=["GET"])
def admin_logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/attendance_stats")
@admin_required
def attendance_stats():
    try:
        import pandas as pd
    except ImportError:
        return jsonify({"error": "Pandas not installed"}), 500
        
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT timestamp FROM attendance", conn)
    finally:
        conn.close()
        
    if df.empty:
        from datetime import date, timedelta
        days = [(date.today() - timedelta(days=i)).strftime("%d-%b") for i in range(29, -1, -1)]
        return jsonify({"dates": days, "counts": [0]*30})
        
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    last_30 = [ (datetime.date.today() - datetime.timedelta(days=i)) for i in range(29, -1, -1) ]
    counts = [ int(df[df['date'] == d].shape[0]) for d in last_30 ]
    dates = [ d.strftime("%d-%b") for d in last_30 ]
    return jsonify({"dates": dates, "counts": counts})

@app.route("/add_student", methods=["GET", "POST"])
@admin_required
def add_student():
    if request.method == "GET":
        return render_template("add_student.html")
    
    data = request.form
    name = data.get("name","").strip()
    if not name:
        return jsonify({"error":"name required"}), 400
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.datetime.utcnow().isoformat()
    c.execute("INSERT INTO students (name, roll, class, section, reg_no, created_at) VALUES (?, ?, ?, ?, ?, ?)",
              (name, data.get("roll",""), data.get("class",""), data.get("sec",""), data.get("reg_no",""), now))
    sid = c.lastrowid
    conn.commit()
    conn.close()
    
    os.makedirs(os.path.join(DATASET_DIR, str(sid)), exist_ok=True)
    return jsonify({"student_id": sid})

@app.route("/upload_face", methods=["POST"])
@admin_required
def upload_face():
    student_id = request.form.get("student_id")
    if not student_id:
        return jsonify({"error":"student_id required"}), 400
        
    # FIX: Check both 'images[]' and 'images'
    files = request.files.getlist("images[]") or request.files.getlist("images")
    
    saved = 0
    folder = os.path.join(DATASET_DIR, student_id)
    os.makedirs(folder, exist_ok=True)
    
    for f in files:
        try:
            if f.filename == '': continue
            fname = f"{datetime.datetime.utcnow().timestamp():.6f}_{saved}.jpg"
            path = os.path.join(folder, fname)
            f.save(path)
            saved += 1
        except Exception as e:
            app.logger.error("save error: %s", e)
            
    return jsonify({"saved": saved})

# Wrapper to handle thread crashes
def training_worker(dataset_dir):
    try:
        def update_progress(p, m):
            write_train_status({"running": True, "progress": p, "message": m})
            
        train_model_background(dataset_dir, update_progress)
        write_train_status({"running": False, "progress": 100, "message": "Training complete!"})
    except Exception as e:
        app.logger.error(f"Training crashed: {e}")
        write_train_status({"running": False, "progress": 0, "message": f"Failed: {str(e)}"})

@app.route("/train_model", methods=["GET"])
@admin_required
def train_model_route():
    status = read_train_status()
    if status.get("running"):
        return jsonify({"status":"already_running"}), 202
        
    write_train_status({"running": True, "progress": 0, "message": "Starting training..."})
    
    t = threading.Thread(target=training_worker, args=(DATASET_DIR,))
    t.daemon = True
    t.start()
    
    return jsonify({"status":"started"}), 202

@app.route("/train_status", methods=["GET"])
@admin_required
def train_status():
    return jsonify(read_train_status())

@app.route("/mark_attendance", methods=["GET"])
def mark_attendance_page():
    return render_template("mark_attendance.html")

@app.route("/recognize_face", methods=["POST"])
def recognize_face():
    if "image" not in request.files:
        return jsonify({"recognized": False, "error":"no image"}), 400
        
    img_file = request.files["image"]
    try:
        emb = extract_embedding_for_image(img_file.stream)
        if emb is None:
            return jsonify({"recognized": False, "error":"no face detected"}), 200
            
        clf = load_model_if_exists()
        if clf is None:
            return jsonify({"recognized": False, "error":"model not trained"}), 200
            
        pred_label, conf = predict_with_model(clf, emb)
        
        if conf < 0.5:
            return jsonify({"recognized": False, "confidence": float(conf)}), 200
            
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name FROM students WHERE id=?", (int(pred_label),))
        row = c.fetchone()
        name = row[0] if row else "Unknown"
        
        # Only mark attendance if not marked in last 60 seconds (Optional improvement)
        ts = datetime.datetime.utcnow().isoformat()
        c.execute("INSERT INTO attendance (student_id, name, timestamp) VALUES (?, ?, ?)", (int(pred_label), name, ts))
        conn.commit()
        conn.close()
        
        return jsonify({"recognized": True, "student_id": int(pred_label), "name": name, "confidence": float(conf)}), 200
    except Exception as e:
        app.logger.exception("recognize error")
        return jsonify({"recognized": False, "error": str(e)}), 500

# ... rest of your routes (attendance_record, download_csv, students) remain same ...

# -------- Attendance records & filters --------
@app.route("/attendance_record", methods=["GET"])
@admin_required
def attendance_record():
    period = request.args.get("period", "all")  # all, daily, weekly, monthly
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    q = "SELECT id, student_id, name, timestamp FROM attendance"
    params = ()
    
    if period == "daily":
        today = datetime.date.today().isoformat()
        q += " WHERE date(timestamp) = ?"
        params = (today,)
    elif period == "weekly":
        start = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
        q += " WHERE date(timestamp) >= ?"
        params = (start,)
    elif period == "monthly":
        start = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
        q += " WHERE date(timestamp) >= ?"
        params = (start,)
        
    q += " ORDER BY timestamp DESC LIMIT 5000"
    c.execute(q, params)
    rows = c.fetchall()
    conn.close()
    
    return render_template("attendance_record.html", records=rows, period=period)

# -------- CSV download --------
@app.route("/download_csv", methods=["GET"])
@admin_required
def download_csv():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, student_id, name, timestamp FROM attendance ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    
    output = io.StringIO()
    output.write("id,student_id,name,timestamp\n")
    for r in rows:
        output.write(f'{r[0]},{r[1]},{r[2]},{r[3]}\n')
        
    mem = io.BytesIO()
    mem.write(output.getvalue().encode("utf-8"))
    mem.seek(0)
    
    return send_file(mem, as_attachment=True, download_name="attendance.csv", mimetype="text/csv")

# -------- Students API for listing/editing --------
@app.route("/students", methods=["GET"])
def students_list():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, roll, class, section, reg_no, created_at FROM students ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    
    data = [ {"id":r[0],"name":r[1],"roll":r[2],"class":r[3],"section":r[4],"reg_no":r[5],"created_at":r[6]} for r in rows ]
    return jsonify({"students": data})

@app.route("/students/<int:sid>", methods=["DELETE"])
def delete_student(sid):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id=?", (sid,))
    c.execute("DELETE FROM attendance WHERE student_id=?", (sid,))
    conn.commit()
    conn.close()
    
    # also delete dataset folder
    folder = os.path.join(DATASET_DIR, str(sid))
    if os.path.isdir(folder):
        import shutil
        shutil.rmtree(folder, ignore_errors=True)
        
    return jsonify({"deleted": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=False)