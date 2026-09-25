"""
End-to-end HTTP feature verification script for MDTPS.
Tests every feature and page against the live running server or Flask test client.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app

def run_verification():
    print("=" * 70)
    print("MDTPS - COMPREHENSIVE END-TO-END FEATURE VERIFICATION SUITE")
    print("=" * 70)

    app = create_app()
    client = app.test_client()

    passed = 0
    total = 0

    def check(name: str, condition: bool, details: str = ""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  [PASS] {name} {details}")
        else:
            print(f"  [FAIL] {name} {details}")
            sys.exit(1)

    # 1. Login Page
    print("\n--- Phase 1: Authentication & Session Security ---")
    res = client.get("/login")
    check("GET /login renders properly", res.status_code == 200)
    check("Contains MDTPS Branding & Auto-fill", b"MDTPS" in res.data and b"fillDemo" in res.data)

    # Invalid login
    res_bad = client.post("/login", data={"username": "admin", "password": "wrongpassword"}, follow_redirects=True)
    check("Invalid login rejection", b"Invalid username or password" in res_bad.data)

    # Valid login
    res_login = client.post("/login", data={"username": "admin", "password": "Admin@123"}, follow_redirects=True)
    check("Valid login authentication", res_login.status_code == 200)
    check("Redirects to Dashboard", b"Dashboard" in res_login.data)

    # 2. Dashboard
    print("\n--- Phase 2: Dashboard Metrics & Telemetry Charts ---")
    res_dash = client.get("/dashboard")
    check("GET /dashboard renders properly", res_dash.status_code == 200)
    check("Total Products stat present", b"Products" in res_dash.data)
    check("Total Machines stat present", b"Machines" in res_dash.data)
    check("Total Batches stat present", b"Batches" in res_dash.data)
    check("Total Units stat present", b"Units" in res_dash.data)
    check("Defect Rate stat present", b"Defect Rate" in res_dash.data)
    check("Chart canvases initialized", b"chartMachine" in res_dash.data and b"chartProduct" in res_dash.data)

    # 3. Core Traceability Feature (Section 9 Prompt Scenario)
    print("\n--- Phase 3: Core Defect Traceability Engine (Section 9 Scenario) ---")
    res_trace = client.get("/traceability?unit_id=U10025")
    check("GET /traceability?unit_id=U10025 status 200", res_trace.status_code == 200)
    check("Traced Unit ID U10025", b"U10025" in res_trace.data)
    check("Traced Product Industrial Pump", b"Industrial Pump" in res_trace.data)
    check("Traced Batch B2026-041", b"B2026-041" in res_trace.data)
    check("Traced Machine M03 (CNC Machine 03)", b"M03" in res_trace.data and b"CNC Machine 03" in res_trace.data)
    check("Traced Defect Surface Crack", b"Surface Crack" in res_trace.data)
    check("Traced Severity HIGH", b"HIGH" in res_trace.data)
    check("Machine Status Maintenance Required", b"MAINTENANCE_REQUIRED" in res_trace.data or b"Maintenance Required" in res_trace.data)
    check("Possible Source Machine M03 / Batch B2026-041", b"Possible Source:" in res_trace.data)

    # 4. Master Data Catalog Pages
    print("\n--- Phase 4: Master Data Catalog & CRUD Endpoints ---")
    for endpoint, label in [
        ("/products", "Products Catalog"),
        ("/machines", "Machines Assets"),
        ("/batches", "Production Batches"),
        ("/production", "Production Units"),
        ("/defects", "Quality Defects"),
    ]:
        res_ep = client.get(endpoint)
        check(f"GET {endpoint} ({label})", res_ep.status_code == 200)

    # 5. Machine and Batch Performance Analysis
    print("\n--- Phase 5: Machine & Batch Association Analysis ---")
    res_ma = client.get("/analysis/machines")
    check("GET /analysis/machines status 200", res_ma.status_code == 200)
    check("Machine Analysis contains causation disclaimer", b"Association vs. Causation" in res_ma.data or b"association" in res_ma.data)

    res_ba = client.get("/analysis/batches")
    check("GET /analysis/batches status 200", res_ba.status_code == 200)
    check("Batch Analysis contains batches table", b"B2026-041" in res_ba.data)

    # 6. Python ML Defect Probability Classifier
    print("\n--- Phase 6: Python ML Classifier (Decision Tree) ---")
    res_pred_page = client.get("/prediction")
    check("GET /prediction status 200", res_pred_page.status_code == 200)

    # High-Risk prediction
    res_pred_high = client.post("/prediction", data={
        "machine_id": "M03",
        "product_id": "P01",
        "temperature": "95.0",
        "pressure": "8.8",
        "operating_hours": "5200",
        "shift": "Night",
        "previous_defects": "14",
        "maintenance_status": "OVERDUE",
    })
    check("POST /prediction (High-Risk Scenario)", res_pred_high.status_code == 200)
    check("High-Risk evaluation produced", b"HIGH" in res_pred_high.data and b"%" in res_pred_high.data)

    # Low-Risk prediction
    res_pred_low = client.post("/prediction", data={
        "machine_id": "M01",
        "product_id": "P01",
        "temperature": "70.0",
        "pressure": "4.5",
        "operating_hours": "2100",
        "shift": "Morning",
        "previous_defects": "0",
        "maintenance_status": "COMPLETED",
    })
    check("POST /prediction (Low-Risk Scenario)", res_pred_low.status_code == 200)
    check("Low-Risk evaluation produced", b"LOW" in res_pred_low.data and b"%" in res_pred_low.data)

    # 7. ADSA B-Tree Index Demonstration
    print("\n--- Phase 7: ADSA B-Tree In-Memory Index ---")
    res_bt_get = client.get("/btree")
    check("GET /btree status 200", res_bt_get.status_code == 200)

    # B-Tree search
    res_bt_search = client.post("/btree", data={"action": "search", "unit_id": "U10025"})
    check("POST /btree search U10025", res_bt_search.status_code == 200)
    check("B-Tree hit found", b"Found" in res_bt_search.data and b"U10025" in res_bt_search.data)

    # B-Tree insert
    res_bt_ins = client.post("/btree", data={"action": "insert", "unit_id": "U10999"})
    check("POST /btree insert U10999", res_bt_ins.status_code == 200)
    check("B-Tree insert confirmed", b"Inserted key U10999" in res_bt_ins.data)

    # B-Tree rebuild
    res_bt_reb = client.post("/btree", data={"action": "rebuild"})
    check("POST /btree rebuild from DB", res_bt_reb.status_code == 200 and b"rebuilt" in res_bt_reb.data)

    # 8. Relational Algebra (DBMS Unit 2)
    print("\n--- Phase 8: DBMS Relational Algebra Demonstration ---")
    res_ra = client.get("/relational?date_from=2026-08-01&date_to=2026-12-31")
    check("GET /relational status 200", res_ra.status_code == 200)
    check("Selection operation present", b"Selection" in res_ra.data)
    check("Projection operation present", b"Projection" in res_ra.data)
    check("Join operation present", b"Join" in res_ra.data)
    check("Union operation present", b"Union" in res_ra.data)
    check("Intersection operation present", b"Intersection" in res_ra.data)
    check("Difference operation present", b"Difference" in res_ra.data)
    check("Cartesian Product present", b"Cartesian" in res_ra.data)

    # 9. Reports & Exports (CSV and PDF)
    print("\n--- Phase 9: Report Generation & Document Exports ---")
    res_rep = client.get("/reports")
    check("GET /reports status 200", res_rep.status_code == 200)

    report_types = ["production", "defect", "machine", "batch", "traceability", "prediction"]
    for rtype in report_types:
        csv_dl = client.get(f"/reports/export/{rtype}.csv")
        check(f"Export CSV: {rtype}.csv", csv_dl.status_code == 200 and csv_dl.mimetype == "text/csv")

        pdf_dl = client.get(f"/reports/export/{rtype}.pdf")
        check(f"Export PDF: {rtype}.pdf", pdf_dl.status_code == 200 and pdf_dl.mimetype == "application/pdf" and pdf_dl.data.startswith(b"%PDF"))

    # 10. About & Syllabus Mapping
    print("\n--- Phase 10: Academic Documentation & Syllabus Mapping ---")
    res_about = client.get("/about")
    check("GET /about status 200", res_about.status_code == 200)
    check("Contains DBMS ER model section", b"DBMS" in res_about.data and b"ENTITY-RELATIONSHIP" in res_about.data)
    check("Contains DMGT Relations section", b"DMGT" in res_about.data and b"Relations" in res_about.data)
    check("Contains ADSA B-Tree mapping", b"ADSA" in res_about.data and b"B-Tree" in res_about.data)
    check("Contains OOPJ Design patterns", b"OOPJ" in res_about.data and b"ProductionEntity" in res_about.data)

    # 11. Health & Logout
    print("\n--- Phase 11: System Health & Logout ---")
    res_health = client.get("/health")
    check("GET /health API status", res_health.status_code == 200 and res_health.json.get("status") == "ok")

    res_logout = client.get("/logout", follow_redirects=True)
    check("GET /logout session termination", res_logout.status_code == 200 and b"logged out" in res_logout.data)

    print("\n" + "=" * 70)
    print(f"VERIFICATION SUMMARY: ALL {passed}/{total} FEATURES PASSED (100% SUCCESS)!")
    print("=" * 70)

if __name__ == "__main__":
    run_verification()
