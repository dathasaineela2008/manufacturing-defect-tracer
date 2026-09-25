from algorithms.btree import BTree


def test_insert_search_and_missing_key():
    tree = BTree(t=3)
    for key in ["U10010", "U10003", "U10025", "U10001", "U10040"]:
        tree.insert(key, {"unit_id": key})
    found = tree.search("U10025")
    assert found is not None
    node, index = found
    assert node.keys[index] == "U10025"
    assert tree.get("U10025")["unit_id"] == "U10025"
    assert tree.search("U99999") is None


def test_inorder_sorted_and_display():
    tree = BTree(t=3)
    keys = ["C", "A", "B", "E", "D", "G", "F"]
    for key in keys:
        tree.insert(key, key)
    ordered = [k for k, _ in tree.inorder()]
    assert ordered == sorted(keys)
    text = tree.display_text()
    assert "B-Tree" in text
    assert tree.size == 7
