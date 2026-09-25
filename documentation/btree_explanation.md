# ADSA — B-Tree unit index

## Why a B-Tree?

A production database may store hundreds of thousands of unit IDs. A B-Tree keeps keys sorted inside nodes that can hold many keys (minimum degree **t**). Height grows slowly, so search is logarithmic.

For minimum degree t:

- Each node except the root has at least t−1 keys and at most 2t−1 keys
- Search / insert: **O(t log_t n)** which is **O(log n)** for fixed t

This is the same family of ideas used inside disk-based databases. **MySQL already uses a B+Tree for indexes.** This project still implements its own tree so the ADSA concept is visible.

## What is indexed?

```text
Part / Unit ID  →  production record (batch, machine, status)
```

Implementation file: `algorithms/btree.py`  
Application wrapper: `app/btree.py`  
UI: `/btree`

The tree is rebuilt from `production_unit` when the demo page loads. Inserts on that page are **in-memory only** so students can see split/search without confusing them with SQL INSERT.

## Operations demonstrated

- Create empty tree (t = 3)
- Insert unit keys from the database
- Search a Unit ID such as U10025
- Inorder traversal
- Text display of internal vs leaf nodes

## How this differs from MySQL indexing

| Academic B-Tree | MySQL index |
| --- | --- |
| Python objects in RAM | Pages on disk, B+Tree |
| Visible on `/btree` | Hidden inside the storage engine |
| Teaching search/insert | Speeding up `WHERE unit_id = …` |

Both can exist in the same project without contradiction.
