# Comprehensive Viva Questions and Answers — MDTPS

Prepared for university academic viva voce examinations covering **DBMS**, **DMGT**, **ADSA**, **OOPJ**, and **Python**.

---

### Category 1: Problem Statement & System Architecture

**Q1. What core engineering problem does this project address?**  
**Answer:**  
In modern manufacturing facilities, when a quality inspection detects a defective unit, the factory often lacks automated traceability to determine which specific production batch, machine asset, shift, or process conditions produced that unit. MDTPS creates deterministic forward and backward traceability by recording foreign-key relationships along `Unit ID → Batch ID → Machine ID → Product ID → Defect ID`.

**Q2. Walk through the system architecture.**  
**Answer:**  
The user interacts through a modern web interface (HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js). The Python Flask backend exposes RESTful routes and services. The backend interfaces with:
1. **Relational Database** (MySQL/SQLite) using 3NF normalized schemas and parameterized queries.
2. **In-Memory B-Tree Index** (ADSA module) for logarithmic searching ($O(t \log_t n)$).
3. **Machine Learning Classifier** (Python `scikit-learn` Decision Tree) for telemetry risk estimation.

**Q3. How is security implemented in the system?**  
**Answer:**  
- **Password Security:** User passwords are never stored in plain text. They are hashed using Werkzeug's PBKDF2/SHA-256 implementation with unique salt.
- **SQL Injection Prevention:** All SQL queries use parameterized placeholders (`%s` for MySQL, `?` for SQLite) with bound tuple arguments; string concatenation is strictly forbidden.
- **Session Protection:** Flask secure cookie sessions protect all internal routes using a `@login_required` decorator.

---

### Category 2: DBMS (Database Management Systems)

**Q4. Explain the ER entities and cardinalities in MDTPS.**  
**Answer:**  
- `PRODUCT` (1:M) `BATCH`: One product is produced across many batches; each batch produces exactly one product.
- `MACHINE` (1:M) `BATCH`: One machine runs many batches; each batch is assigned to one primary machine.
- `BATCH` (1:M) `PRODUCTION_UNIT`: One batch contains multiple serialized units; each unit belongs to one batch.
- `PRODUCTION_UNIT` (1:0..M) `DEFECT`: A unit can have zero defects (status OK) or one/more recorded defect incidents.
- `MACHINE` (1:M) `MACHINE_MAINTENANCE`: One machine asset undergoes scheduled and corrective maintenance events over time.

**Q5. Identify the Primary Keys and Candidate Keys in the database.**  
**Answer:**  
- `product`: Primary Key is `product_id`. Candidate Key is `product_name` (`UNIQUE`).
- `machine`: Primary Key is `machine_id`.
- `batch`: Primary Key is `batch_id`. Foreign Keys: `product_id` and `machine_id`.
- `production_unit`: Primary Key is `unit_id`. Candidate Key is `serial_number` (`UNIQUE`). Foreign Key: `batch_id`.
- `defect`: Primary Key is `defect_id`. Foreign Key: `unit_id`.
- `machine_maintenance`: Primary Key is `maintenance_id`. Foreign Key: `machine_id`.

**Q6. How is the database normalized to Third Normal Form (3NF)?**  
**Answer:**  
- **1NF:** All attributes are atomic (scalar values), tables have primary keys, and no repeating groups exist.
- **2NF:** The database is in 1NF and contains no partial dependencies (all non-key attributes depend on the entire primary key).
- **3NF:** The database is in 2NF and contains no transitive functional dependencies ($X \to Y \to Z$). For example, machine location or product category is not stored redundantly in the `production_unit` table; `production_unit` only stores `batch_id`, while batch details link to product and machine tables.

**Q7. Explain the relational algebra expression for finding all defective units produced by machine M03.**  
**Answer:**  
Algebraic Expression:  
$$\sigma_{\text{machine\_id} = 'M03'}(\text{ProductionUnit} \bowtie \text{Batch} \bowtie \text{Machine}) \bowtie \text{Defect}$$  
Equivalent SQL:  
```sql
SELECT d.* 
FROM defect d
JOIN production_unit u ON d.unit_id = u.unit_id
JOIN batch b ON u.batch_id = b.batch_id
WHERE b.machine_id = 'M03';
```

**Q8. Why is the Cartesian Product ($\times$) useful, and why is it restricted to small samples?**  
**Answer:**  
The Cartesian product $R \times S$ produces all possible ordered pairs of tuples from relations $R$ and $S$. In relational theory, an inner join is conceptually a selection over a Cartesian product ($\sigma_{\text{condition}}(R \times S)$). In large databases, computing the full Cartesian product ($200 \times 30 = 6,000$ rows) is computationally wasteful, so we demonstrate it on a small $2 \times 2$ sample to prove the mathematical concept.

---

### Category 3: DMGT (Discrete Mathematics & Graph Theory)

**Q9. How are mathematical relations used to model traceability?**  
**Answer:**  
Let $P, B, M, U, D$ be sets representing Products, Batches, Machines, Units, and Defects:
- $R_{UB} \subseteq U \times B$: $(u, b) \in R_{UB}$ if unit $u$ was produced in batch $b$.
- $R_{BM} \subseteq B \times M$: $(b, m) \in R_{BM}$ if batch $b$ was run on machine $m$.
- $R_{BP} \subseteq B \times P$: $(b, p) \in R_{BP}$ if batch $b$ manufactures product $p$.
- $R_{UD} \subseteq U \times D$: $(u, d) \in R_{UD}$ if unit $u$ has defect record $d$.  
Traceability is the composition of these relations: given $u \in U$, we trace $u \xrightarrow{R_{UB}} b \xrightarrow{R_{BM}} m$ and $u \xrightarrow{R_{UB}} b \xrightarrow{R_{BP}} p$.

**Q10. Why are $R_{UB}$ and $R_{BM}$ NOT equivalence relations?**  
**Answer:**  
An equivalence relation must be defined on a single set ($A \times A$) and must be reflexive, symmetric, and transitive. $R_{UB} \subseteq U \times B$ is a relation between two distinct sets ($U \neq B$). A unit identifier like `U10025` is never identical to a batch identifier like `B2026-041`, so $(x, x) \notin R_{UB}$ (not reflexive).

**Q11. Define an equivalence relation that DOES exist in this project.**  
**Answer:**  
On the set of production units $U$, define relation $R_{\text{same}}$:  
$$u_1 R_{\text{same}} u_2 \iff \text{machine}(u_1) = \text{machine}(u_2)$$  
Because equality of machine assignment satisfies:
1. **Reflexive:** $\text{machine}(u_1) = \text{machine}(u_1)$ for every unit.
2. **Symmetric:** If $\text{machine}(u_1) = \text{machine}(u_2)$, then $\text{machine}(u_2) = \text{machine}(u_1)$.
3. **Transitive:** If $\text{machine}(u_1) = \text{machine}(u_2)$ and $\text{machine}(u_2) = \text{machine}(u_3)$, then $\text{machine}(u_1) = \text{machine}(u_3)$.  
Therefore, $R_{\text{same}}$ is a valid equivalence relation, and its equivalence classes partition units by their producing machine.

---

### Category 4: ADSA (Advanced Data Structures & Algorithms)

**Q12. What is a B-Tree, and what are its core properties?**  
**Answer:**  
A B-Tree of minimum degree $t \ge 2$ is a self-balancing search tree where:
1. Every node has at most $2t - 1$ keys and at most $2t$ children.
2. Every node other than the root has at least $t - 1$ keys.
3. All leaf nodes appear at the exact same depth (perfect balance).
4. Keys in each node are stored in non-decreasing sorted order.
5. In this project, $t=3$, so each internal node holds between 2 and 5 keys.

**Q13. What is the time complexity of B-Tree operations?**  
**Answer:**  
- **Search:** $O(t \log_t n)$ where $n$ is total keys. For a constant $t$, this is $O(\log n)$.
- **Insert:** $O(t \log_t n)$ using a single-pass top-down algorithm that proactively splits any full node encountered before descending.
- **Traversal:** $O(n)$ in-order traversal, visiting keys in strictly sorted ascending order.

**Q14. Why is a B-Tree preferred over a Binary Search Tree (BST/AVL) for databases?**  
**Answer:**  
In databases, records reside on secondary storage (hard drives / SSDs), where page reads (disk I/O) are orders of magnitude slower than CPU operations. A binary tree has a branching factor of 2, leading to large tree heights ($\log_2 1,000,000 \approx 20$ disk seeks). A B-Tree with a large branching factor (e.g. $t=100$) reduces tree height to $\log_{100} 1,000,000 \le 3$, needing only 3 disk reads to locate any record.

**Q15. Why did you implement a separate B-Tree if MySQL already has indexes?**  
**Answer:**  
MySQL InnoDB manages its own internal B+Trees transparently at the C/C++ engine level on disk pages. To fulfill the ADSA academic syllabus requirement, we wrote an explicit in-memory B-Tree in Python (`algorithms/btree.py`) to demonstrate node representation, splitting mechanisms, in-order traversals, and key searching independent of the database storage engine.

---

### Category 5: OOPJ (Object-Oriented Programming Concepts)

**Q16. How is Abstraction implemented in the codebase?**  
**Answer:**  
In `app/models.py`, `ProductionEntity` is declared as an Abstract Base Class (`abc.ABC`). It defines the common identity of all tracked manufacturing objects and mandates that every subclass implement the abstract method `@abstractmethod def summary(self) -> str`.

**Q17. How is Inheritance used, and why is it not applied to Defect?**  
**Answer:**  
`Product`, `Machine`, and `Batch` inherit from `ProductionEntity` because they share an identity (an entity ID and display name) and represent core manufacturing physical/logical assets. `Defect`, on the other hand, is a quality incident log (an event), not a manufactured entity. Applying inheritance to `Defect` would violate the "Is-A" design principle.

**Q18. How is Polymorphism demonstrated?**  
**Answer:**  
Each subclass (`Product`, `Machine`, `Batch`) overrides the polymorphic `summary()` method:
- `Product.summary()` returns `Product P01: Industrial Pump (Hydraulics)`
- `Machine.summary()` returns `Machine M03: CNC Machine 03 [MAINTENANCE_REQUIRED]`
- `Batch.summary()` returns `Batch B2026-041 | product P01 | machine M03 | 2026-09-18 | Night`  
Client code can iterate over any collection of `ProductionEntity` instances and invoke `.summary()` without knowing the concrete class.

**Q19. How is Encapsulation maintained?**  
**Answer:**  
Internal entity identifiers are encapsulated with private attribute prefixes (e.g. `self._id`, `self._unit_id`) and exposed via read-only Python `@property` decorators (`entity_id`, `unit_id`). Modifying IDs directly is disallowed, preventing corrupted state. Custom domain exceptions (`RecordNotFoundError`, `ValidationError`, `DuplicateRecordError`) provide clean error boundaries.

---

### Category 6: Python & Machine Learning

**Q20. What algorithm is used for the defect classifier, and why?**  
**Answer:**  
We chose a **Decision Tree Classifier** (`sklearn.tree.DecisionTreeClassifier`, `max_depth=5`) because:
1. It is beginner-friendly, interpretable, and produces transparent decision paths.
2. It handles both categorical and continuous manufacturing variables (temperature, pressure, operating hours, previous defect history, maintenance status).
3. It natively provides probabilistic class predictions (`predict_proba()`), allowing the system to output risk tiers (HIGH $\ge 70\%$, MEDIUM $40-69\%$, LOW $< 40\%$).

**Q21. What features are fed into the classifier?**  
**Answer:**  
Eight telemetry features:
1. `machine_code` (Numerical asset identifier)
2. `product_code` (Numerical product category)
3. `temperature` (Chamber operating temperature in °C)
4. `pressure` (Pressure in bar)
5. `operating_hours` (Machine runtime hours)
6. `shift_code` (Morning=0, Afternoon=1, Night=2)
7. `previous_defects` (Historical defects logged on asset)
8. `maintenance_overdue` (Binary flag: 1 if OVERDUE or MAINTENANCE_REQUIRED, 0 otherwise)

**Q22. Does the model prove that a machine caused a defect?**  
**Answer:**  
**No.** This is a critical distinction emphasized throughout the project: **correlation/association is not causation**. The model estimates statistical probability based on historical training correlations. Actual mechanical failure requires metallurgical or mechanical root-cause analysis.

---

### Category 7: Final Demonstration Walkthrough

**Q23. How do you demonstrate the system in 3 minutes during an evaluation?**  
**Answer:**  
1. **Login:** Open `http://127.0.0.1:5000/login`, click "Auto-fill", and click "Sign In".
2. **Dashboard:** Point out total metrics (10 Products, 10 Machines, 30 Batches, 200 Units, 50 Defects, 25% Defect Rate) and real-time Chart.js charts.
3. **Traceability:** Click the quick sample chip for `U10025`. Show the animated interactive pipeline: `Unit U10025 → Industrial Pump (P01) → Batch B2026-041 → CNC Machine 03 (M03) → Surface Crack (HIGH)`. Show the Section 9 terminal format box and machine maintenance alert.
4. **ADSA B-Tree:** Click "ADSA B-Tree Index Search" button; show instant search hit card and ASCII level tree hierarchy.
5. **Relational Algebra:** Navigate to `/relational` to show the $\sigma, \pi, \bowtie, \cup, \cap, -$ queries with equivalent SQL queries.
6. **Machine Learning:** Navigate to `/prediction`, click "High-Risk Scenario", and execute inference showing Defect Probability ~78%, HIGH Risk badge, and driving factors.
7. **Export Report:** Go to `/reports`, click "PDF Document" for Traceability Report, and open the generated PDF document.
