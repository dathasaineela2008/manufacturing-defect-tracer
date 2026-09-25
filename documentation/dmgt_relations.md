# DMGT Unit 2 — relations in MDTPS

Only relation concepts that are used to explain traceability are included.

## Sets

```text
P = {P01, P02, …, P10}     products
B = {B2026-001, …}         batches
M = {M01, …, M10}          machines
U = {U10001, …}            production units
D = {D001, …}              defect records
```

An **ordered pair** (a, b) means “a is related to b”. A **relation** is a set of ordered pairs.

## Relations used for tracing

| Relation | Subset of | Meaning |
| --- | --- | --- |
| R_PB | P × B | Product p is manufactured as batch b |
| R_BM | B × M | Batch b was produced on machine m |
| R_UB | U × B | Unit u belongs to batch b |
| R_UD | U × D | Unit u has defect record d |

**Domain** of a relation = first components of the pairs.  
**Range** = second components.

To trace defective unit u:

1. Find unique b with (u, b) ∈ R_UB
2. Find unique m with (b, m) ∈ R_BM
3. Find unique p with (p, b) ∈ R_PB
4. Find defects d with (u, d) ∈ R_UD

R_PB, R_BM, and R_UD are **not** equivalence relations (they are not relations on a single set in the “same type” sense, and they are not reflexive on P or U).

## Equivalence relation that *is* used

On units, define:

```text
u1 R_same u2  ⇔  machine(u1) = machine(u2)
```

This is equality of an attribute, so it is:

- **Reflexive:** every unit has the same machine as itself
- **Symmetric:** if u1 and u2 share a machine, so do u2 and u1
- **Transitive:** if u1 shares with u2 and u2 shares with u3, then u1 shares with u3

Hence **R_same is an equivalence relation**. Equivalence classes group units produced on the same machine. That grouping supports machine analysis, but still does **not** prove causation.

The About page computes a readable 12-unit sample of R_same from the live database.
