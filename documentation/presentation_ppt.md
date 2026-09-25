# Project presentation (PPT content)

Use one slide per heading. Do not add fake statistics or company names.

## Slide 1 — Title
Manufacturing Defect Traceability and Prediction System (MDTPS)  
Academic project — fictional sample data

## Slide 2 — Problem
A manufacturer cannot trace which batch or machine produced a defective unit.

## Slide 3 — Objective
Trace Unit → Product, Batch, Machine, Date, Shift, Defect  
Demonstrate DBMS, DMGT, ADSA, OOPJ, Python

## Slide 4 — Architecture
Browser → Flask → MySQL + B-Tree + Decision Tree → Traceability engine

## Slide 5 — ER model
Product 1:M Batch M:1 Machine  
Batch 1:M ProductionUnit 1:0..M Defect  
Machine 1:M Maintenance

## Slide 6 — Relational algebra
σ defective units, ⋈ to batch and machine, π of identifiers, ∪ ∩ −, small × demo

## Slide 7 — DMGT relations
Sets P, B, M, U, D  
R_PB, R_BM, R_UD for tracing  
Same-machine equivalence on units

## Slide 8 — B-Tree (ADSA)
Unit ID index, insert/search/traverse  
O(log n) search  
Separate from MySQL’s own index

## Slide 9 — OOP
ProductionEntity → Product, Machine, Batch  
TraceabilityService, exceptions, encapsulation

## Slide 10 — Traceability demo
Input U10025  
Output product, batch, machine, date, shift, Surface Crack / HIGH

## Slide 11 — Python classifier
Decision Tree on sample CSV  
Output probability + risk  
Disclaimer: not a real-world predictor

## Slide 12 — Machine analysis
Defect rates by machine  
Association ≠ causation

## Slide 13 — Security
Hashed passwords, parameterized SQL, `.env` for credentials, sessions

## Slide 14 — Conclusion
The defective unit can be traced to a recorded product, batch, and machine.  
ML and charts are academic aids, not proof of cause.

## Slide 15 — Thank you / viva
Demo account admin / Admin@123  
Try unit U10025
