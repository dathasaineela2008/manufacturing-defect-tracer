"""Flask routes for every MDTPS page. Each navigation item has a real handler."""

from __future__ import annotations

from functools import wraps
from typing import Any, Dict, List

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
import io

from app import catalog
from app.btree import btree_index
from app.classifier import classifier
from app.database import DatabaseError, db
from app.dmgt import dmgt_report
from app.models import MDTPSError
from app.relational import (
    cartesian,
    difference,
    inner_join,
    intersection,
    projection,
    selection,
    stringify_rows,
    union,
)
from app.reports import rows_to_csv, rows_to_pdf
from app.traceability import traceability

bp = Blueprint("main", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)

    return wrapped


def _safe_page(template: str, **context):
    try:
        return render_template(template, **context)
    except DatabaseError as exc:
        flash(str(exc), "danger")
        return render_template(template, **{**context, "db_error": str(exc)})


@bp.app_context_processor
def inject_user():
    return {"current_user": session.get("username")}


@bp.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("main.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template("login.html")
        try:
            user = catalog.get_user(username)
        except DatabaseError as exc:
            flash(str(exc), "danger")
            return render_template("login.html")
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "danger")
            return render_template("login.html")
        session.clear()
        session["user_id"] = user["user_id"]
        session["username"] = user["username"]
        session.permanent = True
        return redirect(url_for("main.dashboard"))
    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.login"))


@bp.route("/dashboard")
@login_required
def dashboard():
    try:
        stats = traceability.dashboard_stats()
        charts = {
            "by_machine": traceability.chart_defects_by_machine(),
            "by_batch": traceability.chart_defects_by_batch(),
            "by_product": traceability.chart_defects_by_product(),
            "by_type": traceability.chart_defects_by_type(),
            "by_severity": traceability.chart_defects_by_severity(),
            "over_time": traceability.chart_defects_over_time(),
        }
        return render_template("dashboard.html", stats=stats, charts=charts)
    except DatabaseError as exc:
        flash(str(exc), "danger")
        empty = {
            "total_products": 0,
            "total_batches": 0,
            "total_machines": 0,
            "total_units": 0,
            "total_defective": 0,
            "defect_rate": 0,
        }
        return render_template("dashboard.html", stats=empty, charts={})


@bp.route("/products", methods=["GET", "POST"])
@login_required
def products():
    if request.method == "POST":
        try:
            catalog.create_product(
                request.form.get("product_id", ""),
                request.form.get("product_name", ""),
                request.form.get("product_type", ""),
                request.form.get("description", ""),
            )
            flash("Product saved.", "success")
        except MDTPSError as exc:
            flash(str(exc), "danger")
        return redirect(url_for("main.products"))
    rows = catalog.list_products(request.args.get("q", ""))
    return render_template("products.html", rows=rows, q=request.args.get("q", ""))


@bp.route("/machines", methods=["GET", "POST"])
@login_required
def machines():
    if request.method == "POST":
        try:
            catalog.create_machine(
                request.form.get("machine_id", ""),
                request.form.get("machine_name", ""),
                request.form.get("machine_type", ""),
                request.form.get("location", ""),
                request.form.get("status", ""),
                request.form.get("operating_hours", "0"),
            )
            flash("Machine saved.", "success")
        except MDTPSError as exc:
            flash(str(exc), "danger")
        return redirect(url_for("main.machines"))
    rows = catalog.list_machines(request.args.get("q", ""))
    return render_template("machines.html", rows=rows, q=request.args.get("q", ""))


@bp.route("/batches", methods=["GET", "POST"])
@login_required
def batches():
    if request.method == "POST":
        try:
            catalog.create_batch(
                request.form.get("batch_id", ""),
                request.form.get("product_id", ""),
                request.form.get("machine_id", ""),
                request.form.get("production_date", ""),
                request.form.get("quantity", ""),
                request.form.get("shift", ""),
                request.form.get("temperature_c", "0"),
                request.form.get("pressure_bar", "0"),
            )
            flash("Batch saved.", "success")
        except MDTPSError as exc:
            flash(str(exc), "danger")
        return redirect(url_for("main.batches"))
    rows = catalog.list_batches(
        request.args.get("q", ""),
        request.args.get("date_from", ""),
        request.args.get("date_to", ""),
    )
    products = catalog.list_products()
    machines = catalog.list_machines()
    return render_template(
        "batches.html",
        rows=rows,
        products=products,
        machines=machines,
        q=request.args.get("q", ""),
        date_from=request.args.get("date_from", ""),
        date_to=request.args.get("date_to", ""),
    )


@bp.route("/production", methods=["GET", "POST"])
@login_required
def production():
    if request.method == "POST":
        try:
            catalog.create_unit(
                request.form.get("unit_id", ""),
                request.form.get("batch_id", ""),
                request.form.get("serial_number", ""),
                request.form.get("production_time", ""),
                request.form.get("status", "OK"),
            )
            flash("Production unit saved.", "success")
        except MDTPSError as exc:
            flash(str(exc), "danger")
        return redirect(url_for("main.production"))
    rows = catalog.list_units(request.args.get("q", ""), request.args.get("status", ""))
    batches = catalog.list_batches()
    return render_template(
        "production.html",
        rows=rows,
        batches=batches,
        q=request.args.get("q", ""),
        status=request.args.get("status", ""),
    )


@bp.route("/defects", methods=["GET", "POST"])
@login_required
def defects():
    if request.method == "POST":
        try:
            catalog.create_defect(
                request.form.get("defect_id", ""),
                request.form.get("unit_id", ""),
                request.form.get("defect_type", ""),
                request.form.get("severity", ""),
                request.form.get("description", ""),
                request.form.get("detected_date", ""),
            )
            flash("Defect recorded. Unit status set to DEFECTIVE.", "success")
        except MDTPSError as exc:
            flash(str(exc), "danger")
        return redirect(url_for("main.defects"))
    rows = catalog.list_defects(request.args.get("q", ""), request.args.get("severity", ""))
    return render_template(
        "defects.html",
        rows=rows,
        q=request.args.get("q", ""),
        severity=request.args.get("severity", ""),
    )


@bp.route("/traceability", methods=["GET", "POST"])
@login_required
def trace_unit():
    result = None
    query = request.values.get("unit_id", "").strip()
    if request.method == "POST" or query:
        try:
            result = traceability.trace(query or request.form.get("unit_id", ""))
        except MDTPSError as exc:
            flash(str(exc), "danger")
        except DatabaseError as exc:
            flash(str(exc), "danger")
    return render_template("traceability.html", result=result, query=query)


@bp.route("/analysis/machines")
@login_required
def machine_analysis():
    rows = traceability.machine_analysis()
    for row in rows:
        total = int(row["total_units"] or 0)
        bad = int(row["defective_units"] or 0)
        row["defect_rate"] = round((bad / total) * 100, 2) if total else 0
    return render_template("machine_analysis.html", rows=rows)


@bp.route("/analysis/batches")
@login_required
def batch_analysis():
    rows = traceability.batch_analysis()
    for row in rows:
        total = int(row["total_units"] or 0)
        bad = int(row["defective_units"] or 0)
        row["defect_rate"] = round((bad / total) * 100, 2) if total else 0
    return render_template("batch_analysis.html", rows=rows)


@bp.route("/prediction", methods=["GET", "POST"])
@login_required
def prediction():
    prediction_result = None
    if request.method == "POST":
        features = {
            "machine_id": request.form.get("machine_id"),
            "product_id": request.form.get("product_id"),
            "temperature": request.form.get("temperature"),
            "pressure": request.form.get("pressure"),
            "operating_hours": request.form.get("operating_hours"),
            "shift": request.form.get("shift"),
            "previous_defects": request.form.get("previous_defects"),
            "maintenance_status": request.form.get("maintenance_status"),
        }
        try:
            float(features["temperature"])
            float(features["pressure"])
            float(features["operating_hours"])
            float(features["previous_defects"])
        except (TypeError, ValueError):
            flash("Temperature, pressure, operating hours, and previous defects must be numbers.", "danger")
        else:
            prediction_result = classifier.predict(features)
            if not prediction_result.get("ok"):
                flash(prediction_result.get("error", "Prediction failed."), "danger")
    products = catalog.list_products()
    machines = catalog.list_machines()
    return render_template(
        "prediction.html",
        products=products,
        machines=machines,
        result=prediction_result,
    )


@bp.route("/btree", methods=["GET", "POST"])
@login_required
def btree_demo():
    message = None
    found = None
    action = request.form.get("action") if request.method == "POST" else request.args.get("action", "display")
    key = (request.form.get("unit_id") or request.args.get("unit_id") or "").strip()
    if btree_index.tree.size == 0:
        try:
            btree_index.rebuild()
        except DatabaseError as exc:
            flash(str(exc), "danger")
    if action == "rebuild" and request.method == "POST":
        count = btree_index.rebuild()
        message = f"B-Tree rebuilt from the database ({count} unit keys)."
    elif action == "insert" and request.method == "POST":
        if not key:
            flash("Enter a Unit ID to insert.", "danger")
        else:
            btree_index.insert(key, {"unit_id": key, "status": "DEMO-INSERT", "note": "Academic insert (memory only)"})
            message = f"Inserted key {key} into the in-memory B-Tree (not written to MySQL)."
    elif action == "search" and key:
        found = btree_index.search(key)
        message = f"Found {key}." if found else f"{key} was not found in the B-Tree."
    elif action == "search" and request.method == "POST" and not key:
        flash("Enter a Unit ID to search.", "danger")
    display = btree_index.display()
    traversal = btree_index.traverse()
    structure = btree_index.structure()
    return render_template(
        "btree.html",
        display=display,
        traversal=traversal[:80],
        traversal_count=len(traversal),
        structure=structure,
        found=found,
        message=message,
        key=key,
    )


def _ra_tables() -> Dict[str, List[Dict[str, Any]]]:
    units = db.query("SELECT unit_id, batch_id, serial_number, status FROM production_unit")
    batches = db.query("SELECT batch_id, product_id, machine_id, production_date, shift FROM batch")
    machines = db.query("SELECT machine_id, machine_name, status FROM machine")
    defects = db.query("SELECT defect_id, unit_id, defect_type, severity, detected_date FROM defect")
    return {"units": units, "batches": batches, "machines": machines, "defects": defects}


@bp.route("/relational")
@login_required
def relational_demo():
    tables = _ra_tables()
    units, batches, machines, defects = tables["units"], tables["batches"], tables["machines"], tables["defects"]
    defective_units = selection(units, lambda r: r["status"] == "DEFECTIVE")
    high_defects = selection(defects, lambda r: r["severity"] == "HIGH")
    unit_batch = inner_join(units, batches, "batch_id", "batch_id")
    unit_machine = inner_join(unit_batch, machines, "machine_id", "machine_id")
    date_from = request.args.get("date_from") or "2026-08-01"
    date_to = request.args.get("date_to") or "2026-12-31"
    in_range = selection(
        unit_machine,
        lambda r: str(r.get("production_date")) >= date_from and str(r.get("production_date")) <= date_to and r["status"] == "DEFECTIVE",
    )
    m03_defects = selection(unit_machine, lambda r: r.get("machine_id") == "M03")
    m03_defects = inner_join(m03_defects, defects, "unit_id", "unit_id")
    ok_ids = projection(selection(units, lambda r: r["status"] == "OK"), ["unit_id"])
    def_ids = projection(defective_units, ["unit_id"])
    all_ids = union(ok_ids, def_ids)
    both = intersection(ok_ids, def_ids)
    only_ok = difference(ok_ids, def_ids)
    tiny_u = units[:2]
    tiny_b = batches[:2]
    product_demo = cartesian(tiny_u, tiny_b)

    operations = [
        {
            "title": "Selection — defective units",
            "algebra": "σ status = 'DEFECTIVE' (ProductionUnit)",
            "sql": "SELECT * FROM production_unit WHERE status = 'DEFECTIVE';",
            "rows": stringify_rows(defective_units),
            "count": len(defective_units),
        },
        {
            "title": "Selection — high-severity defects",
            "algebra": "σ severity = 'HIGH' (Defect)",
            "sql": "SELECT * FROM defect WHERE severity = 'HIGH';",
            "rows": stringify_rows(high_defects),
            "count": len(high_defects),
        },
        {
            "title": "Join — unit to batch",
            "algebra": "ProductionUnit ⋈_batch_id Batch",
            "sql": "SELECT * FROM production_unit u JOIN batch b ON u.batch_id = b.batch_id;",
            "rows": stringify_rows(unit_batch),
            "count": len(unit_batch),
        },
        {
            "title": "Join — unit to machine",
            "algebra": "ProductionUnit ⋈ Batch ⋈ Machine",
            "sql": "SELECT u.unit_id, b.batch_id, m.machine_id, m.machine_name FROM production_unit u JOIN batch b ON u.batch_id = b.batch_id JOIN machine m ON b.machine_id = m.machine_id;",
            "rows": stringify_rows(unit_machine),
            "count": len(unit_machine),
        },
        {
            "title": "Join + selection — defects of machine M03",
            "algebra": "π (σ machine_id='M03'(ProductionUnit ⋈ Batch ⋈ Machine) ⋈ Defect)",
            "sql": "SELECT d.* FROM defect d JOIN production_unit u ON d.unit_id = u.unit_id JOIN batch b ON u.batch_id = b.batch_id WHERE b.machine_id = 'M03';",
            "rows": stringify_rows(m03_defects),
            "count": len(m03_defects),
        },
        {
            "title": "Date-range defective products",
            "algebra": f"σ production_date ≥ '{date_from}' ∧ production_date ≤ '{date_to}' ∧ status='DEFECTIVE' (U ⋈ B ⋈ M)",
            "sql": f"SELECT u.unit_id, p.product_name, b.batch_id, m.machine_id FROM production_unit u JOIN batch b ON u.batch_id = b.batch_id JOIN machine m ON b.machine_id = m.machine_id JOIN product p ON b.product_id = p.product_id WHERE u.status='DEFECTIVE' AND b.production_date BETWEEN '{date_from}' AND '{date_to}';",
            "rows": stringify_rows(in_range),
            "count": len(in_range),
        },
        {
            "title": "Projection — unit identifiers",
            "algebra": "π_unit_id (ProductionUnit)",
            "sql": "SELECT DISTINCT unit_id FROM production_unit;",
            "rows": stringify_rows(projection(units, ["unit_id"])),
            "count": len(projection(units, ["unit_id"])),
        },
        {
            "title": "Union — OK ∪ DEFECTIVE identifiers",
            "algebra": "π_unit_id(σ status='OK'(U)) ∪ π_unit_id(σ status='DEFECTIVE'(U))",
            "sql": "SELECT unit_id FROM production_unit WHERE status='OK' UNION SELECT unit_id FROM production_unit WHERE status='DEFECTIVE';",
            "rows": stringify_rows(all_ids),
            "count": len(all_ids),
        },
        {
            "title": "Intersection — OK ∩ DEFECTIVE identifiers",
            "algebra": "π_unit_id(σ status='OK'(U)) ∩ π_unit_id(σ status='DEFECTIVE'(U))",
            "sql": "SELECT unit_id FROM production_unit WHERE status='OK' INTERSECT SELECT unit_id FROM production_unit WHERE status='DEFECTIVE';",
            "rows": stringify_rows(both),
            "count": len(both),
        },
        {
            "title": "Difference — OK − DEFECTIVE identifiers",
            "algebra": "π_unit_id(σ status='OK'(U)) − π_unit_id(σ status='DEFECTIVE'(U))",
            "sql": "SELECT unit_id FROM production_unit WHERE status='OK' AND unit_id NOT IN (SELECT unit_id FROM production_unit WHERE status='DEFECTIVE');",
            "rows": stringify_rows(only_ok),
            "count": len(only_ok),
        },
        {
            "title": "Cartesian product (tiny sample of 2×2)",
            "algebra": "ProductionUnit_sample × Batch_sample",
            "sql": "SELECT * FROM production_unit LIMIT 2 CROSS JOIN (SELECT * FROM batch LIMIT 2) b;",
            "rows": stringify_rows(product_demo, limit=8),
            "count": len(product_demo),
        },
    ]
    return render_template("relational.html", operations=operations, date_from=date_from, date_to=date_to)


@bp.route("/reports")
@login_required
def reports():
    return render_template("reports.html")


def _report_bundle(kind: str):
    if kind == "production":
        headers = ["unit_id", "serial_number", "batch_id", "product_name", "machine_id", "production_date", "status"]
        rows = catalog.list_units()
        title = "Production Report"
    elif kind == "defect":
        headers = ["defect_id", "unit_id", "defect_type", "severity", "detected_date", "batch_id"]
        rows = catalog.list_defects()
        title = "Defect Report"
    elif kind == "machine":
        headers = ["machine_id", "machine_name", "total_units", "defective_units", "defect_rate", "status"]
        rows = traceability.machine_analysis()
        for row in rows:
            total = int(row["total_units"] or 0)
            bad = int(row["defective_units"] or 0)
            row["defect_rate"] = round((bad / total) * 100, 2) if total else 0
        title = "Machine Report"
    elif kind == "batch":
        headers = ["batch_id", "product_name", "machine_id", "production_date", "quantity", "defective_units"]
        rows = traceability.batch_analysis()
        title = "Batch Report"
    elif kind == "prediction":
        headers = ["note"]
        rows = [{"note": "Run the Defect Prediction page, then export from that screen for a specific input. This file records that the academic Decision Tree lives in ml/model.pkl."}]
        title = "Prediction Report"
    else:
        headers = ["unit_id", "serial_number", "batch_id", "product_name", "machine_id", "status"]
        rows = catalog.list_units("", "DEFECTIVE")
        title = "Traceability Report (defective units)"
    return title, headers, rows


@bp.route("/reports/export/<kind>.<fmt>")
@login_required
def export_report(kind: str, fmt: str):
    allowed = {"production", "defect", "machine", "batch", "traceability", "prediction"}
    if kind not in allowed or fmt not in {"csv", "pdf"}:
        flash("Unknown report type.", "danger")
        return redirect(url_for("main.reports"))
    title, headers, rows = _report_bundle(kind)
    if fmt == "csv":
        data = rows_to_csv(headers, rows)
        return send_file(
            io.BytesIO(data.encode("utf-8")),
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"mdtps_{kind}.csv",
        )
    pdf = rows_to_pdf(title, headers, rows)
    return send_file(
        io.BytesIO(pdf),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"mdtps_{kind}.pdf",
    )


@bp.route("/about")
@login_required
def about():
    try:
        dmgt = dmgt_report()
    except DatabaseError as exc:
        dmgt = None
        flash(str(exc), "danger")
    return render_template("about.html", dmgt=dmgt)


@bp.route("/health")
def health():
    return {"status": "ok", "app": "MDTPS"}
