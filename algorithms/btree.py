"""
Academic B-Tree (minimum degree t).

This module is the ADSA demonstration. It is separate from MySQL indexes.
MySQL still uses its own B+Tree internally; this class is an in-memory
teaching implementation used to index Unit ID -> production record.

Complexity (CLRS):
    Search / Insert: O(t * log_t n) which is O(log n) for a fixed t.
    A higher t (more keys per node) reduces tree height — useful for disk pages.
"""

from __future__ import annotations

from typing import Any, List, Optional, Tuple


class BTreeNode:
    """One node in the B-Tree. Internal nodes store children; leaves do not."""

    def __init__(self, leaf: bool = True) -> None:
        self.leaf = leaf
        self.keys: List[str] = []
        self.values: List[Any] = []
        self.children: List["BTreeNode"] = []

    def __repr__(self) -> str:
        return f"BTreeNode(leaf={self.leaf}, keys={self.keys})"


class BTree:
    """
    B-Tree of minimum degree t (every node except root has at least t-1 keys,
    and at most 2t-1 keys). Default t=3 so the on-screen tree stays readable.
    """

    def __init__(self, t: int = 3) -> None:
        if t < 2:
            raise ValueError("B-Tree minimum degree t must be at least 2.")
        self.t = t
        self.root = BTreeNode(leaf=True)
        self.size = 0

    # ------------------------------------------------------------------ insert
    def insert(self, key: str, value: Any = None) -> None:
        key = str(key).strip()
        if not key:
            raise ValueError("Key cannot be empty.")
        existing = self.search(key)
        if existing is not None:
            node, index = existing
            node.values[index] = value
            return

        root = self.root
        if len(root.keys) == (2 * self.t) - 1:
            new_root = BTreeNode(leaf=False)
            new_root.children.append(root)
            self._split_child(new_root, 0)
            self.root = new_root
            self._insert_non_full(new_root, key, value)
        else:
            self._insert_non_full(root, key, value)
        self.size += 1

    def _insert_non_full(self, node: BTreeNode, key: str, value: Any) -> None:
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.append("")
            node.values.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.values[i + 1] = node.values[i]
                i -= 1
            node.keys[i + 1] = key
            node.values[i + 1] = value
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == (2 * self.t) - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key, value)

    def _split_child(self, parent: BTreeNode, index: int) -> None:
        t = self.t
        full = parent.children[index]
        sibling = BTreeNode(leaf=full.leaf)

        parent.keys.insert(index, full.keys[t - 1])
        parent.values.insert(index, full.values[t - 1])
        parent.children.insert(index + 1, sibling)

        sibling.keys = full.keys[t:]
        sibling.values = full.values[t:]
        full.keys = full.keys[: t - 1]
        full.values = full.values[: t - 1]

        if not full.leaf:
            sibling.children = full.children[t:]
            full.children = full.children[:t]

    # ------------------------------------------------------------------ search
    def search(self, key: str) -> Optional[Tuple[BTreeNode, int]]:
        """Return (node, index) if key exists, else None."""
        return self._search_node(self.root, str(key).strip())

    def _search_node(self, node: BTreeNode, key: str) -> Optional[Tuple[BTreeNode, int]]:
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return node, i
        if node.leaf:
            return None
        return self._search_node(node.children[i], key)

    def get(self, key: str) -> Any:
        found = self.search(key)
        if found is None:
            return None
        node, index = found
        return node.values[index]

    # --------------------------------------------------------------- traverse
    def inorder(self) -> List[Tuple[str, Any]]:
        result: List[Tuple[str, Any]] = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node: BTreeNode, result: List[Tuple[str, Any]]) -> None:
        for i, key in enumerate(node.keys):
            if not node.leaf:
                self._inorder(node.children[i], result)
            result.append((key, node.values[i]))
        if not node.leaf and node.children:
            self._inorder(node.children[-1], result)

    def height(self) -> int:
        h = 0
        node = self.root
        while not node.leaf:
            h += 1
            node = node.children[0]
        return h

    def display_text(self) -> str:
        """Indented textual view of the tree for the academic demo page."""
        lines: List[str] = []
        self._display(self.root, 0, lines)
        header = (
            f"B-Tree  |  t={self.t}  |  keys={self.size}  |  height={self.height()}\n"
            f"(root at top; children indented)\n"
        )
        return header + "\n".join(lines)

    def _display(self, node: BTreeNode, level: int, lines: List[str]) -> None:
        indent = "    " * level
        kind = "LEAF" if node.leaf else "INTERNAL"
        lines.append(f"{indent}[{kind}] keys={node.keys}")
        if not node.leaf:
            for child in node.children:
                self._display(child, level + 1, lines)

    def to_dict(self) -> dict:
        """JSON-friendly structure for the web UI."""
        return {
            "t": self.t,
            "size": self.size,
            "height": self.height(),
            "root": self._node_dict(self.root),
        }

    def _node_dict(self, node: BTreeNode) -> dict:
        return {
            "leaf": node.leaf,
            "keys": list(node.keys),
            "children": [self._node_dict(c) for c in node.children],
        }
