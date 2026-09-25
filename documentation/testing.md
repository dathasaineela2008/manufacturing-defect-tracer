# Test Documentation & Verification Matrix — MDTPS

Automated verification results for the Manufacturing Defect Traceability and Prediction System (MDTPS).

## 1. Automated Test Suite Execution

All tests execute via pytest:
```powershell
venv\Scripts\pytest -v
```

Execution Summary:
- **Total Test Cases**: 18 Automated Pytest Unit Tests + 69 HTTP End-to-End Verification Tests
- **Status**: 100% PASSED (0 Failures, 0 Errors)
- **Environment**: Python 3.13 / Windows / SQLite & MySQL compatible

### Detailed Automated Test Results

| Test Case | Input / Operation | Expected Result | Actual Result | Status |
| --- | --- | --- | --- | --- |
| `test_login_success_and_failure` | Valid: `admin` / `Admin@123`<br>Invalid: `admin` / `wrong` | HTTP 302/200 Dashboard<br>Flash: "Invalid username or password" | Redirects to `/dashboard`<br>Flash message displayed | **PASSED** |
| `test_trace_u10025_and_invalid_unit` | Unit ID: `U10025`<br>Invalid: `U99999` | Traces Product (Industrial Pump), Batch (B2026-041), Machine (M03), Defect (Surface Crack), Severity (HIGH)<br>`RecordNotFoundError` | All lineage fields matched Section 9 format spec<br>Handled gracefully | **PASSED** |
| `test_product_creation` | ID: `P99`, Name: "Academic Test Widget" | Product stored in catalog; queryable by ID | Found in `list_products("P99")` | **PASSED** |
| `test_machine_creation_and_validation` | ID: `M99`, Status: `OPERATIONAL`<br>Invalid: Status `INVALID_STATUS` | Machine saved in registry<br>Raises `ValidationError` | `M99` queryable<br>`ValidationError` caught | **PASSED** |
| `test_batch_creation_and_validation` | ID: `B-TEST-01`, Shift: `Morning`<br>Invalid: Shift `Midnight` | Batch registered with FKs<br>Raises `ValidationError` | `B-TEST-01` queryable<br>`ValidationError` caught | **PASSED** |
| `test_production_unit_and_defect_creation` | Unit: `U99901` (status OK)<br>Defect: `D99901` (Severity HIGH) | Unit logged as OK<br>Defect logged and unit status auto-updates to `DEFECTIVE` | `U99901` created<br>Status transitioned to `DEFECTIVE` | **PASSED** |
| `test_btree_search_integration` | Search `U10025`<br>Search `U99999` | Found: record with batch & machine<br>Miss: `None` | Exact payload retrieved<br>`None` returned | **PASSED** |
| `test_database_queries` | `dashboard_stats()`, `chart_defects_by_machine()` | Non-zero counts for products, machines, batches, units, defects | Aggregated stats & chart datasets returned | **PASSED** |
| `test_prediction_output` | High risk features: M03, Overdue, 95°C, 5100 hrs | Returns `ok: True`, probability percentage, risk level (`HIGH`) | Probability ~78%, Risk Level `HIGH` | **PASSED** |
| `test_invalid_inputs_and_error_handling` | Feature: `temperature = "not-a-number"` | Returns `ok: False` with descriptive error | Friendly validation error string returned | **PASSED** |
| `test_all_application_routes` | All 15 required pages | HTTP status code 200 for all GET routes | 15/15 pages returned HTTP 200 | **PASSED** |
| `test_all_report_exports` | All 6 report kinds (`production`, `defect`, `machine`, `batch`, `traceability`, `prediction`) | Valid CSV (`text/csv`) and valid PDF (`application/pdf`) starting with `%PDF` | All 12 download streams verified | **PASSED** |
| `test_btree_web_actions` | Web POST: search, insert (`U10999`), rebuild | Search hit displayed, insert confirmed, tree rebuilt | Web flash & DOM elements confirmed | **PASSED** |
| `test_prediction_web_post` | Web POST with telemetry form data | HTTP 200 with risk badge & factors | Rendered probability and risk | **PASSED** |
| `test_btree_node_split_and_inorder` | Insert sequence into B-Tree ($t=3$) | In-order traversal produces strictly ascending sorted order | Sorted key sequence verified | **PASSED** |
| `test_btree_multi_level` | Insert 25 sequential keys | Proactive node split creates multi-level hierarchy with balanced leaves | Height $\le 3$, leaves at identical depth | **PASSED** |
| `test_relational_primitives` | Relational operations: $\sigma, \pi, \bowtie, \cup, \cap, -$ | Set semantics match relational algebra rules | Result sets match formal algebra | **PASSED** |
| `test_relational_cartesian` | Cartesian product $A \times B$ | Returns $|A| \times |B|$ combined tuples | $2 \times 2 = 4$ tuples produced | **PASSED** |

---

## 2. End-to-End HTTP Verification Script

Run the automated 69-point comprehensive script:
```powershell
venv\Scripts\python tests/verify_features_http.py
```

Results:
```text
======================================================================
MDTPS - COMPREHENSIVE END-TO-END FEATURE VERIFICATION SUITE
======================================================================
--- Phase 1: Authentication & Session Security ---
  [PASS] GET /login renders properly 
  [PASS] Contains MDTPS Branding & Auto-fill 
  [PASS] Invalid login rejection 
  [PASS] Valid login authentication 
  [PASS] Redirects to Dashboard 

--- Phase 2: Dashboard Metrics & Telemetry Charts ---
  [PASS] GET /dashboard renders properly 
  [PASS] Total Products stat present 
  [PASS] Total Machines stat present 
  [PASS] Total Batches stat present 
  [PASS] Total Units stat present 
  [PASS] Defect Rate stat present 
  [PASS] Chart canvases initialized 

--- Phase 3: Core Defect Traceability Engine (Section 9 Scenario) ---
  [PASS] GET /traceability?unit_id=U10025 status 200 
  [PASS] Traced Unit ID U10025 
  [PASS] Traced Product Industrial Pump 
  [PASS] Traced Batch B2026-041 
  [PASS] Traced Machine M03 (CNC Machine 03) 
  [PASS] Traced Defect Surface Crack 
  [PASS] Traced Severity HIGH 
  [PASS] Machine Status Maintenance Required 
  [PASS] Possible Source Machine M03 / Batch B2026-041 

--- Phase 4: Master Data Catalog & CRUD Endpoints ---
  [PASS] GET /products (Products Catalog) 
  [PASS] GET /machines (Machines Assets) 
  [PASS] GET /batches (Production Batches) 
  [PASS] GET /production (Production Units) 
  [PASS] GET /defects (Quality Defects) 

--- Phase 5: Machine & Batch Association Analysis ---
  [PASS] GET /analysis/machines status 200 
  [PASS] Machine Analysis contains causation disclaimer 
  [PASS] GET /analysis/batches status 200 
  [PASS] Batch Analysis contains batches table 

--- Phase 6: Python ML Classifier (Decision Tree) ---
  [PASS] GET /prediction status 200 
  [PASS] POST /prediction (High-Risk Scenario) 
  [PASS] High-Risk evaluation produced 
  [PASS] POST /prediction (Low-Risk Scenario) 
  [PASS] Low-Risk evaluation produced 

--- Phase 7: ADSA B-Tree In-Memory Index ---
  [PASS] GET /btree status 200 
  [PASS] POST /btree search U10025 
  [PASS] B-Tree hit found 
  [PASS] POST /btree insert U10999 
  [PASS] B-Tree insert confirmed 
  [PASS] POST /btree rebuild from DB 

--- Phase 8: DBMS Relational Algebra Demonstration ---
  [PASS] GET /relational status 200 
  [PASS] Selection operation present 
  [PASS] Projection operation present 
  [PASS] Join operation present 
  [PASS] Union operation present 
  [PASS] Intersection operation present 
  [PASS] Difference operation present 
  [PASS] Cartesian Product present 

--- Phase 9: Report Generation & Document Exports ---
  [PASS] GET /reports status 200 
  [PASS] Export CSV: production.csv 
  [PASS] Export PDF: production.pdf 
  [PASS] Export CSV: defect.csv 
  [PASS] Export PDF: defect.pdf 
  [PASS] Export CSV: machine.csv 
  [PASS] Export PDF: machine.pdf 
  [PASS] Export CSV: batch.csv 
  [PASS] Export PDF: batch.pdf 
  [PASS] Export CSV: traceability.csv 
  [PASS] Export PDF: traceability.pdf 
  [PASS] Export CSV: prediction.csv 
  [PASS] Export PDF: prediction.pdf 

--- Phase 10: Academic Documentation & Syllabus Mapping ---
  [PASS] GET /about status 200 
  [PASS] Contains DBMS ER model section 
  [PASS] Contains DMGT Relations section 
  [PASS] Contains ADSA B-Tree mapping 
  [PASS] Contains OOPJ Design patterns 

--- Phase 11: System Health & Logout ---
  [PASS] GET /health API status 
  [PASS] GET /logout session termination 

======================================================================
VERIFICATION SUMMARY: ALL 69/69 FEATURES PASSED (100% SUCCESS)!
======================================================================
```

---

## 3. Manual College Viva Checklist

| Step | Action | Expected Output | Status |
| --- | --- | --- | --- |
| 1 | Navigate to `http://127.0.0.1:5000/login` | Login screen with auto-fill button | Verified |
| 2 | Click "Auto-fill", then click "Sign In" | Redirected to `/dashboard` | Verified |
| 3 | View Dashboard stat cards | Products=10, Batches=30, Machines=10, Units=200, Defects=50, Rate=25% | Verified |
| 4 | Search `U10025` on Dashboard hero bar | Directs to `/traceability?unit_id=U10025` | Verified |
| 5 | Inspect Traceability Pipeline & Output Box | Visual pipeline displays: Unit U10025 → Industrial Pump → B2026-041 → CNC Machine 03 (M03) → Surface Crack (HIGH). Terminal box formatted per Section 9. | Verified |
| 6 | Click "ADSA B-Tree Index Search" button | Opens `/btree?action=search&unit_id=U10025`, displays B-Tree hit card | Verified |
| 7 | Navigate to `/relational` | Mathematical $\sigma, \pi, \bowtie, \cup, \cap, -$ queries with equivalent SQL boxes | Verified |
| 8 | Navigate to `/analysis/machines` | Displays defect rate bars and "Association vs Causation" notice | Verified |
| 9 | Navigate to `/prediction` | Click "High-Risk Scenario" preset → Defect Probability ~78%, HIGH Risk | Verified |
| 10 | Navigate to `/reports` | Click "PDF Document" on Traceability Report → downloads `mdtps_traceability.pdf` | Verified |
| 11 | Navigate to `/about` | Syllabus mapping table, ER diagram, DMGT properties, and OOPJ architecture | Verified |
| 12 | Sign out | Session cleared, redirected to `/login` | Verified |
