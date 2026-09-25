from app.relational import difference, inner_join, intersection, projection, selection, union


def test_selection_projection_join():
    units = [
        {"unit_id": "U1", "batch_id": "B1", "status": "OK"},
        {"unit_id": "U2", "batch_id": "B1", "status": "DEFECTIVE"},
    ]
    batches = [{"batch_id": "B1", "machine_id": "M03"}]
    defective = selection(units, lambda r: r["status"] == "DEFECTIVE")
    assert len(defective) == 1
    assert defective[0]["unit_id"] == "U2"
    ids = projection(units, ["unit_id"])
    assert len(ids) == 2
    joined = inner_join(units, batches, "batch_id", "batch_id")
    assert joined[0]["machine_id"] == "M03"


def test_union_intersection_difference():
    ok = [{"unit_id": "U1"}]
    bad = [{"unit_id": "U2"}]
    both_ok = [{"unit_id": "U1"}]
    assert len(union(ok, bad)) == 2
    assert intersection(ok, both_ok) == [{"unit_id": "U1"}]
    assert difference(ok, bad) == [{"unit_id": "U1"}]
    assert intersection(ok, bad) == []
