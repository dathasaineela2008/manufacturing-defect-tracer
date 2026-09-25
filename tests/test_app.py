"""Comprehensive automated test suite for MDTPS."""

from app import create_app
from app.catalog import create_product, list_products
from app.classifier import DefectAnalyzer
from app.models import DuplicateRecordError, RecordNotFoundError
from app.traceability import TraceabilityService


def test_login_success_and_failure():
    app = create_app()
    client = app.test_client()
    bad = client.post("/login", data={"username": "admin", "password": "wrong"}, follow_redirects=True)
    assert b"Invalid username or password" in bad.data
    ok = client.post("/login", data={"username": "admin", "password": "Admin@123"}, follow_redirects=True)
    assert ok.status_code == 200
    assert b"Dashboard" in ok.data


def test_trace_u10025_and_invalid_unit():
    svc = TraceabilityService()
    result = svc.trace("U10025")
    assert result["unit"]["unit_id"] == "U10025"
    assert result["unit"]["batch_id"] == "B2026-041"
    assert result["unit"]["machine_id"] == "M03"
    assert result["unit"]["product_name"] == "Conveyor Roller" or "Industrial Pump" in result["unit"]["product_name"] or result["unit"]["product_name"]
    assert result["primary_defect"] is not None
    assert result["primary_defect"]["defect_type"]

    # Also test tracing via serial number
    serial = result["unit"]["serial_number"]
    by_serial = svc.trace(serial)
    assert by_serial["unit"]["unit_id"] == "U10025"

    try:
        svc.trace("U99999")
        assert False, "expected missing unit"
    except RecordNotFoundError:
        pass


def test_product_creation():
    try:
        create_product("P99", "Academic Test Widget", "Test", "Created by pytest")
    except DuplicateRecordError:
        pass
    names = [row["product_id"] for row in list_products("P99")]
    assert "P99" in names


def test_machine_creation_and_validation():
    from app.catalog import create_machine, list_machines
    from app.models import ValidationError
    try:
        create_machine("M99", "CNC Lathe Test", "CNC", "Bay 9", "OPERATIONAL", "100")
    except DuplicateRecordError:
        pass
    machines = [row["machine_id"] for row in list_machines("M99")]
    assert "M99" in machines

    # Invalid status should raise ValidationError
    try:
        create_machine("M98", "Invalid Machine", "CNC", "Bay 9", "INVALID_STATUS", "0")
        assert False, "expected ValidationError on invalid status"
    except ValidationError:
        pass


def test_batch_creation_and_validation():
    from app.catalog import create_batch, list_batches
    from app.models import ValidationError
    try:
        create_batch("B-TEST-01", "P01", "M01", "2026-09-01", "50", "Morning", "75.5", "6.2")
    except DuplicateRecordError:
        pass
    batches = [row["batch_id"] for row in list_batches("B-TEST-01")]
    assert "B-TEST-01" in batches

    # Invalid shift should raise ValidationError
    try:
        create_batch("B-TEST-BAD", "P01", "M01", "2026-09-01", "50", "Midnight", "75.5", "6.2")
        assert False, "expected ValidationError on invalid shift"
    except ValidationError:
        pass


def test_production_unit_and_defect_creation():
    from app.catalog import create_unit, list_units, create_defect, list_defects
    # Create valid unit
    try:
        create_unit("U99901", "B2026-001", "SN-99901-TEST", "2026-09-01 10:00:00", "OK")
    except DuplicateRecordError:
        pass
    units = [row["unit_id"] for row in list_units("U99901")]
    assert "U99901" in units

    # Create defect on this unit, which should flip its status to DEFECTIVE
    try:
        create_defect("D99901", "U99901", "Surface Flaw", "HIGH", "Pytest defect", "2026-09-02")
    except DuplicateRecordError:
        pass
    defects = [row["defect_id"] for row in list_defects("D99901")]
    assert "D99901" in defects
    updated_unit = list_units("U99901")[0]
    assert updated_unit["status"] == "DEFECTIVE"


def test_btree_search_integration():
    from app.btree import btree_index
    btree_index.rebuild()
    result = btree_index.search("U10025")
    assert result is not None
    assert result["unit_id"] == "U10025"
    assert "batch_id" in result
    assert "machine_id" in result

    # Test not found
    missing = btree_index.search("U99999")
    assert missing is None


def test_database_queries():
    from app.traceability import traceability
    stats = traceability.dashboard_stats()
    assert stats["total_products"] > 0
    assert stats["total_machines"] > 0
    assert stats["total_batches"] > 0
    assert stats["total_units"] > 0
    assert stats["total_defective"] > 0
    assert 0 <= stats["defect_rate"] <= 100

    m_chart = traceability.chart_defects_by_machine()
    assert len(m_chart) > 0


def test_prediction_output():
    analyzer = DefectAnalyzer()
    result = analyzer.predict(
        {
            "machine_id": "M03",
            "product_id": "P01",
            "temperature": 95,
            "pressure": 9,
            "operating_hours": 5100,
            "shift": "Night",
            "previous_defects": 12,
            "maintenance_status": "OVERDUE",
        }
    )
    assert result["ok"] is True
    assert "probability" in result
    assert result["risk_level"] in {"LOW", "MEDIUM", "HIGH"}


def test_invalid_inputs_and_error_handling():
    analyzer = DefectAnalyzer()
    bad_pred = analyzer.predict(
        {
            "machine_id": "M03",
            "product_id": "P01",
            "temperature": "not-a-number",
            "pressure": 9,
            "operating_hours": 5100,
            "shift": "Night",
            "previous_defects": 12,
            "maintenance_status": "OVERDUE",
        }
    )
    assert bad_pred["ok"] is False
    assert "error" in bad_pred


def test_all_application_routes():
    app = create_app()
    client = app.test_client()
    login_resp = client.post('/login', data={'username': 'admin', 'password': 'Admin@123'}, follow_redirects=True)
    assert login_resp.status_code == 200

    routes = [
        '/dashboard',
        '/products',
        '/machines',
        '/batches',
        '/production',
        '/defects',
        '/traceability?unit_id=U10025',
        '/analysis/machines',
        '/analysis/batches',
        '/prediction',
        '/btree?action=display',
        '/relational',
        '/reports',
        '/about',
        '/health',
    ]
    for r in routes:
        res = client.get(r)
        assert res.status_code == 200, f"Route {r} failed with status {res.status_code}"


def test_all_report_exports():
    app = create_app()
    client = app.test_client()
    client.post('/login', data={'username': 'admin', 'password': 'Admin@123'}, follow_redirects=True)

    report_types = ["production", "defect", "machine", "batch", "traceability", "prediction"]
    for kind in report_types:
        # Test CSV export
        csv_res = client.get(f'/reports/export/{kind}.csv')
        assert csv_res.status_code == 200, f"CSV export for {kind} failed"
        assert csv_res.mimetype == "text/csv"
        assert len(csv_res.data) > 0

        # Test PDF export
        pdf_res = client.get(f'/reports/export/{kind}.pdf')
        assert pdf_res.status_code == 200, f"PDF export for {kind} failed"
        assert pdf_res.mimetype == "application/pdf"
        assert pdf_res.data.startswith(b"%PDF")


def test_btree_web_actions():
    app = create_app()
    client = app.test_client()
    client.post('/login', data={'username': 'admin', 'password': 'Admin@123'}, follow_redirects=True)

    # Search existing
    res = client.post('/btree', data={'action': 'search', 'unit_id': 'U10025'})
    assert res.status_code == 200
    assert b"Found" in res.data

    # Insert new key
    ins = client.post('/btree', data={'action': 'insert', 'unit_id': 'U10999'})
    assert ins.status_code == 200
    assert b"Inserted key U10999" in ins.data

    # Rebuild from DB
    reb = client.post('/btree', data={'action': 'rebuild'})
    assert reb.status_code == 200
    assert b"rebuilt" in reb.data


def test_prediction_web_post():
    app = create_app()
    client = app.test_client()
    client.post('/login', data={'username': 'admin', 'password': 'Admin@123'}, follow_redirects=True)

    # Predict high risk
    res = client.post('/prediction', data={
        'machine_id': 'M03',
        'product_id': 'P05',
        'temperature': '95',
        'pressure': '8.8',
        'operating_hours': '5200',
        'shift': 'Night',
        'previous_defects': '14',
        'maintenance_status': 'OVERDUE'
    })
    assert res.status_code == 200
    assert b"RISK" in res.data
