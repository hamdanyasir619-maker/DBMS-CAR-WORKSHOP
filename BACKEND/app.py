"""
ProGear - Car Workshop Management System
Flask Backend with PyMySQL
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
import pymysql
import pymysql.cursors
from datetime import date

app = Flask(__name__)
app.secret_key = "progear_secret_key_2026"
CORS(app)

# ─────────────────────────────────────────────
#  Database Configuration
# ─────────────────────────────────────────────
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "Hassankhan818",
    "database": "carworkshop",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True,
}


def get_db():
    """Return a new PyMySQL connection."""
    return pymysql.connect(**DB_CONFIG)


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────
def query_all(sql, params=()):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


def query_one(sql, params=()):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()
    finally:
        conn.close()


def execute(sql, params=()):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.lastrowid
    finally:
        conn.close()


# ═══════════════════════════════════════════════
#  DASHBOARD
# ═══════════════════════════════════════════════
@app.route("/")
def dashboard():
    stats = {
        "customers": query_one("SELECT COUNT(*) AS cnt FROM CUSTOMER")["cnt"],
        "vehicles": query_one("SELECT COUNT(*) AS cnt FROM VEHICLE")["cnt"],
        "mechanics": query_one("SELECT COUNT(*) AS cnt FROM MECHANIC")["cnt"],
        "parts": query_one("SELECT COUNT(*) AS cnt FROM SPARE_PART")["cnt"],
        "jobs_pending": query_one("SELECT COUNT(*) AS cnt FROM SERVICE_JOB WHERE Status='Pending'")["cnt"],
        "jobs_in_progress": query_one("SELECT COUNT(*) AS cnt FROM SERVICE_JOB WHERE Status='In Progress'")["cnt"],
        "jobs_completed": query_one("SELECT COUNT(*) AS cnt FROM SERVICE_JOB WHERE Status='Completed'")["cnt"],
        "invoices_unpaid": query_one("SELECT COUNT(*) AS cnt FROM INVOICE WHERE PaymentStatus='Unpaid'")["cnt"],
    }
    recent_jobs = query_all(
        """
        SELECT sj.JobID, sj.Date, sj.Status, sj.LaborCost,
               v.RegNo, v.Make, v.ModelName,
               CONCAT(m.FirstName,' ',m.LastName) AS MechanicName
        FROM SERVICE_JOB sj
        JOIN VEHICLE v ON sj.VehicleID = v.VehicleID
        JOIN MECHANIC m ON sj.MechanicID = m.MechanicID
        ORDER BY sj.Date DESC
        LIMIT 5
        """
    )
    return render_template("dashboard.html", stats=stats, recent_jobs=recent_jobs)


# ═══════════════════════════════════════════════
#  CUSTOMERS
# ═══════════════════════════════════════════════
@app.route("/customers")
def customers():
    rows = query_all("SELECT * FROM CUSTOMER ORDER BY CustomerID DESC")
    return render_template("customers.html", customers=rows)


@app.route("/customers/add", methods=["GET", "POST"])
def add_customer():
    if request.method == "POST":
        f = request.form
        execute(
            """INSERT INTO CUSTOMER (FirstName,LastName,Phone,Email,Street,City,State,ZipCode)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (f["first_name"], f["last_name"], f["phone"], f["email"],
             f["street"], f["city"], f["state"], f["zip_code"]),
        )
        flash("Customer added successfully!", "success")
        return redirect(url_for("customers"))
    return render_template("customer_form.html", action="Add", customer=None)


@app.route("/customers/edit/<int:cid>", methods=["GET", "POST"])
def edit_customer(cid):
    customer = query_one("SELECT * FROM CUSTOMER WHERE CustomerID=%s", (cid,))
    if request.method == "POST":
        f = request.form
        execute(
            """UPDATE CUSTOMER SET FirstName=%s,LastName=%s,Phone=%s,Email=%s,
               Street=%s,City=%s,State=%s,ZipCode=%s WHERE CustomerID=%s""",
            (f["first_name"], f["last_name"], f["phone"], f["email"],
             f["street"], f["city"], f["state"], f["zip_code"], cid),
        )
        flash("Customer updated!", "success")
        return redirect(url_for("customers"))
    return render_template("customer_form.html", action="Edit", customer=customer)


@app.route("/customers/delete/<int:cid>")
def delete_customer(cid):
    execute("DELETE FROM CUSTOMER WHERE CustomerID=%s", (cid,))
    flash("Customer deleted.", "warning")
    return redirect(url_for("customers"))


# ═══════════════════════════════════════════════
#  VEHICLES
# ═══════════════════════════════════════════════
@app.route("/vehicles")
def vehicles():
    rows = query_all(
        """SELECT v.*, CONCAT(c.FirstName,' ',c.LastName) AS OwnerName
           FROM VEHICLE v JOIN CUSTOMER c ON v.CustomerID=c.CustomerID
           ORDER BY v.VehicleID DESC"""
    )
    return render_template("vehicles.html", vehicles=rows)


@app.route("/vehicles/add", methods=["GET", "POST"])
def add_vehicle():
    customers = query_all("SELECT CustomerID,FirstName,LastName FROM CUSTOMER ORDER BY FirstName")
    if request.method == "POST":
        f = request.form
        execute(
            "INSERT INTO VEHICLE (RegNo,Make,ModelName,Year,CustomerID) VALUES (%s,%s,%s,%s,%s)",
            (f["reg_no"], f["make"], f["model_name"], f["year"], f["customer_id"]),
        )
        flash("Vehicle added!", "success")
        return redirect(url_for("vehicles"))
    return render_template("vehicle_form.html", action="Add", vehicle=None, customers=customers)


@app.route("/vehicles/edit/<int:vid>", methods=["GET", "POST"])
def edit_vehicle(vid):
    vehicle = query_one("SELECT * FROM VEHICLE WHERE VehicleID=%s", (vid,))
    customers = query_all("SELECT CustomerID,FirstName,LastName FROM CUSTOMER ORDER BY FirstName")
    if request.method == "POST":
        f = request.form
        execute(
            """UPDATE VEHICLE SET RegNo=%s,Make=%s,ModelName=%s,Year=%s,CustomerID=%s
               WHERE VehicleID=%s""",
            (f["reg_no"], f["make"], f["model_name"], f["year"], f["customer_id"], vid),
        )
        flash("Vehicle updated!", "success")
        return redirect(url_for("vehicles"))
    return render_template("vehicle_form.html", action="Edit", vehicle=vehicle, customers=customers)


@app.route("/vehicles/delete/<int:vid>")
def delete_vehicle(vid):
    execute("DELETE FROM VEHICLE WHERE VehicleID=%s", (vid,))
    flash("Vehicle deleted.", "warning")
    return redirect(url_for("vehicles"))


# ═══════════════════════════════════════════════
#  MECHANICS
# ═══════════════════════════════════════════════
@app.route("/mechanics")
def mechanics():
    rows = query_all("SELECT * FROM MECHANIC ORDER BY MechanicID DESC")
    return render_template("mechanics.html", mechanics=rows)


@app.route("/mechanics/add", methods=["GET", "POST"])
def add_mechanic():
    if request.method == "POST":
        f = request.form
        execute(
            "INSERT INTO MECHANIC (FirstName,LastName,SkillLevel,Contact) VALUES (%s,%s,%s,%s)",
            (f["first_name"], f["last_name"], f["skill_level"], f["contact"]),
        )
        flash("Mechanic added!", "success")
        return redirect(url_for("mechanics"))
    return render_template("mechanic_form.html", action="Add", mechanic=None)


@app.route("/mechanics/edit/<int:mid>", methods=["GET", "POST"])
def edit_mechanic(mid):
    mechanic = query_one("SELECT * FROM MECHANIC WHERE MechanicID=%s", (mid,))
    if request.method == "POST":
        f = request.form
        execute(
            """UPDATE MECHANIC SET FirstName=%s,LastName=%s,SkillLevel=%s,Contact=%s
               WHERE MechanicID=%s""",
            (f["first_name"], f["last_name"], f["skill_level"], f["contact"], mid),
        )
        flash("Mechanic updated!", "success")
        return redirect(url_for("mechanics"))
    return render_template("mechanic_form.html", action="Edit", mechanic=mechanic)


@app.route("/mechanics/delete/<int:mid>")
def delete_mechanic(mid):
    execute("DELETE FROM MECHANIC WHERE MechanicID=%s", (mid,))
    flash("Mechanic deleted.", "warning")
    return redirect(url_for("mechanics"))


# ═══════════════════════════════════════════════
#  SERVICE JOBS
# ═══════════════════════════════════════════════
@app.route("/jobs")
def jobs():
    rows = query_all(
        """SELECT sj.JobID, sj.Date, sj.Status, sj.LaborCost,
                  v.RegNo, v.Make, v.ModelName,
                  CONCAT(m.FirstName,' ',m.LastName) AS MechanicName
           FROM SERVICE_JOB sj
           JOIN VEHICLE v ON sj.VehicleID=v.VehicleID
           JOIN MECHANIC m ON sj.MechanicID=m.MechanicID
           ORDER BY sj.JobID DESC"""
    )
    return render_template("jobs.html", jobs=rows)


@app.route("/jobs/add", methods=["GET", "POST"])
def add_job():
    vehicles = query_all("SELECT VehicleID,RegNo,Make,ModelName FROM VEHICLE ORDER BY RegNo")
    mechanics = query_all("SELECT MechanicID,FirstName,LastName,SkillLevel FROM MECHANIC ORDER BY FirstName")
    if request.method == "POST":
        f = request.form
        execute(
            """INSERT INTO SERVICE_JOB (Date,Status,LaborCost,VehicleID,MechanicID)
               VALUES (%s,%s,%s,%s,%s)""",
            (f["date"], f["status"], f["labor_cost"], f["vehicle_id"], f["mechanic_id"]),
        )
        flash("Service Job added!", "success")
        return redirect(url_for("jobs"))
    return render_template("job_form.html", action="Add", job=None,
                           vehicles=vehicles, mechanics=mechanics, today=date.today())


@app.route("/jobs/edit/<int:jid>", methods=["GET", "POST"])
def edit_job(jid):
    job = query_one("SELECT * FROM SERVICE_JOB WHERE JobID=%s", (jid,))
    vehicles = query_all("SELECT VehicleID,RegNo,Make,ModelName FROM VEHICLE ORDER BY RegNo")
    mechanics = query_all("SELECT MechanicID,FirstName,LastName,SkillLevel FROM MECHANIC ORDER BY FirstName")
    if request.method == "POST":
        f = request.form
        execute(
            """UPDATE SERVICE_JOB SET Date=%s,Status=%s,LaborCost=%s,VehicleID=%s,MechanicID=%s
               WHERE JobID=%s""",
            (f["date"], f["status"], f["labor_cost"], f["vehicle_id"], f["mechanic_id"], jid),
        )
        flash("Service Job updated!", "success")
        return redirect(url_for("jobs"))
    return render_template("job_form.html", action="Edit", job=job,
                           vehicles=vehicles, mechanics=mechanics, today=date.today())


@app.route("/jobs/delete/<int:jid>")
def delete_job(jid):
    execute("DELETE FROM SERVICE_JOB WHERE JobID=%s", (jid,))
    flash("Job deleted.", "warning")
    return redirect(url_for("jobs"))


# ═══════════════════════════════════════════════
#  SPARE PARTS
# ═══════════════════════════════════════════════
@app.route("/parts")
def parts():
    rows = query_all("SELECT * FROM SPARE_PART ORDER BY PartID DESC")
    return render_template("parts.html", parts=rows)


@app.route("/parts/add", methods=["GET", "POST"])
def add_part():
    if request.method == "POST":
        f = request.form
        execute(
            "INSERT INTO SPARE_PART (Name,Quantity,UnitPrice) VALUES (%s,%s,%s)",
            (f["name"], f["quantity"], f["unit_price"]),
        )
        flash("Part added!", "success")
        return redirect(url_for("parts"))
    return render_template("part_form.html", action="Add", part=None)


@app.route("/parts/edit/<int:pid>", methods=["GET", "POST"])
def edit_part(pid):
    part = query_one("SELECT * FROM SPARE_PART WHERE PartID=%s", (pid,))
    if request.method == "POST":
        f = request.form
        execute(
            "UPDATE SPARE_PART SET Name=%s,Quantity=%s,UnitPrice=%s WHERE PartID=%s",
            (f["name"], f["quantity"], f["unit_price"], pid),
        )
        flash("Part updated!", "success")
        return redirect(url_for("parts"))
    return render_template("part_form.html", action="Edit", part=part)


@app.route("/parts/delete/<int:pid>")
def delete_part(pid):
    execute("DELETE FROM SPARE_PART WHERE PartID=%s", (pid,))
    flash("Part deleted.", "warning")
    return redirect(url_for("parts"))


# ═══════════════════════════════════════════════
#  INVOICES
# ═══════════════════════════════════════════════
@app.route("/invoices")
def invoices():
    rows = query_all(
        """SELECT i.InvoiceID, i.Date, i.PaymentStatus, i.PaymentMethod,
                  i.JobID, sj.LaborCost,
                  v.RegNo, v.Make, v.ModelName,
                  COALESCE(SUM(sp_part.UnitPrice * sp.QuantityUsed), 0) AS PartsCost
           FROM INVOICE i
           JOIN SERVICE_JOB sj ON i.JobID=sj.JobID
           JOIN VEHICLE v ON sj.VehicleID=v.VehicleID
           LEFT JOIN SERVICE_PARTS sp ON sj.JobID=sp.JobID
           LEFT JOIN SPARE_PART sp_part ON sp.PartID=sp_part.PartID
           GROUP BY i.InvoiceID
           ORDER BY i.InvoiceID DESC"""
    )
    return render_template("invoices.html", invoices=rows)


@app.route("/invoices/add", methods=["GET", "POST"])
def add_invoice():
    jobs = query_all(
        """SELECT sj.JobID,sj.Date,sj.Status,v.RegNo
           FROM SERVICE_JOB sj JOIN VEHICLE v ON sj.VehicleID=v.VehicleID
           ORDER BY sj.JobID DESC"""
    )
    if request.method == "POST":
        f = request.form
        execute(
            "INSERT INTO INVOICE (Date,PaymentStatus,PaymentMethod,JobID) VALUES (%s,%s,%s,%s)",
            (f["date"], f["payment_status"], f["payment_method"], f["job_id"]),
        )
        flash("Invoice created!", "success")
        return redirect(url_for("invoices"))
    return render_template("invoice_form.html", action="Add", invoice=None,
                           jobs=jobs, today=date.today())


@app.route("/invoices/edit/<int:iid>", methods=["GET", "POST"])
def edit_invoice(iid):
    invoice = query_one("SELECT * FROM INVOICE WHERE InvoiceID=%s", (iid,))
    jobs = query_all(
        """SELECT sj.JobID,sj.Date,sj.Status,v.RegNo
           FROM SERVICE_JOB sj JOIN VEHICLE v ON sj.VehicleID=v.VehicleID
           ORDER BY sj.JobID DESC"""
    )
    if request.method == "POST":
        f = request.form
        execute(
            """UPDATE INVOICE SET Date=%s,PaymentStatus=%s,PaymentMethod=%s,JobID=%s
               WHERE InvoiceID=%s""",
            (f["date"], f["payment_status"], f["payment_method"], f["job_id"], iid),
        )
        flash("Invoice updated!", "success")
        return redirect(url_for("invoices"))
    return render_template("invoice_form.html", action="Edit", invoice=invoice,
                           jobs=jobs, today=date.today())


@app.route("/invoices/delete/<int:iid>")
def delete_invoice(iid):
    execute("DELETE FROM INVOICE WHERE InvoiceID=%s", (iid,))
    flash("Invoice deleted.", "warning")
    return redirect(url_for("invoices"))


# ═══════════════════════════════════════════════
#  JSON API  (for AJAX / future use)
# ═══════════════════════════════════════════════
@app.route("/api/stats")
def api_stats():
    stats = {
        "customers": query_one("SELECT COUNT(*) AS cnt FROM CUSTOMER")["cnt"],
        "vehicles": query_one("SELECT COUNT(*) AS cnt FROM VEHICLE")["cnt"],
        "mechanics": query_one("SELECT COUNT(*) AS cnt FROM MECHANIC")["cnt"],
        "parts": query_one("SELECT COUNT(*) AS cnt FROM SPARE_PART")["cnt"],
        "jobs": query_one("SELECT COUNT(*) AS cnt FROM SERVICE_JOB")["cnt"],
        "invoices": query_one("SELECT COUNT(*) AS cnt FROM INVOICE")["cnt"],
    }
    return jsonify(stats)


# ─────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)
