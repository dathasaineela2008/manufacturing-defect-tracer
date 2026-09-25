# Academic Project Report
## Manufacturing Defect Traceability and Prediction System (MDTPS)

---

### Candidate Declaration & Certificate
*This is to certify that the project entitled **"Manufacturing Defect Traceability and Prediction System (MDTPS)"** is a bona fide record of work carried out by the student in partial fulfillment of the requirements for the degree of Bachelor of Engineering / Technology in Computer Science and Engineering.*

---

## Abstract

In discrete and continuous manufacturing environments, quality failures can lead to significant financial loss, warranty claims, and regulatory penalties. A frequent operational obstacle is that manufacturing plants record quality control failures at the end of the line, but plant operators cannot immediately identify which production batch or machine produced a specific defective item. 

The **Manufacturing Defect Traceability and Prediction System (MDTPS)** is an academic full-stack software system designed to resolve this traceability deficit while simultaneously integrating core theoretical concepts across Computer Science syllabi:
1. **Database Management Systems (DBMS):** Third Normal Form (3NF) relational modeling, integrity constraints, and live relational-algebra query demonstrations ($\sigma, \pi, \bowtie, \cup, \cap, -, \times$).
2. **Discrete Mathematics and Graph Theory (DMGT):** Formal relations ($R_{PB}, R_{BM}, R_{UD}$), domain/range calculations, and equivalence relations partitioning units by machine.
3. **Advanced Data Structures and Algorithms (ADSA):** An in-memory B-Tree ($t=3$) implementing logarithmic $O(t \log_t n)$ search and dynamic node splitting, decoupled from the underlying database's storage engine.
4. **Object-Oriented Programming with Java/Python (OOPJ):** Domain entities, encapsulation, polymorphic summaries, service layers, and structured exception handling.
5. **Python & Machine Learning:** A supervised Decision Tree classifier estimating defect probabilities and risk levels based on operational parameters.

All records, serial numbers, and production runs represent synthetic sample data designed specifically for academic rigor and demonstration.

---

## Chapter 1: Introduction

### 1.1 Problem Statement
> **Problem Statement:** A manufacturer cannot trace which batch or machine produced a defective unit.

On a factory floor producing mechanical or electrical assemblies (e.g., pumps, valves, gears, sensors), units pass through multiple processes. When an inspection station or customer identifies a defect (such as a *Surface Crack* or *Porosity*), the manufacturer needs to immediately trace:
- Which specific **Product** type it is.
- Which **Batch** it was manufactured in.
- Which **Machine** was used during processing.
- The exact **Production Date** and **Shift** (Morning, Afternoon, Night).
- Operating sensor parameters (Temperature and Pressure).
- Defect severity and machine maintenance records.

Without an integrated traceability system, identifying the root cause requires manual inspection of paper logs or disconnected spreadsheets, resulting in substantial delays and ongoing production of defective parts.

### 1.2 Objectives
The primary objectives of this system are:
1. **Traceability Engine:** Allow operators to input a Unit ID or Serial Number and immediately generate the complete provenance chain: $\text{Unit} \rightarrow \text{Batch} \rightarrow \text{Machine} \rightarrow \text{Product} \rightarrow \text{Defect}$.
2. **Academic Syllabus Integration:** Explicitly map and demonstrate practical applications of DBMS, DMGT, ADSA, OOPJ, and Python.
3. **Analytics & Risk Prediction:** Provide machine-wise and batch-wise quality statistics while using machine learning to predict defect probability under varying operational conditions.
4. **Data Integrity & Security:** Enforce 3NF normalization, candidate keys, foreign key cascades/restrictions, parameterized SQL execution, and hashed password authentication.

### 1.3 Scope and Limitations
- **Scope:** Complete tracking of products, machines, batches, serialized units, defect logs, maintenance events, and risk prediction.
- **Academic Limitation:** The predictive model and defect statistics operate on simulated historical datasets. Tracing provides **recorded association**, which must be distinguished from proven mechanical causation.

---

## Chapter 2: Literature & Theoretical Framework

### 2.1 DBMS: Relational Theory and Normalization
A relational database organizes data into relations (tables) composed of attributes (columns) and tuples (rows). To eliminate insertion, update, and deletion anomalies, the schema is normalized:
- **First Normal Form (1NF):** All attribute values are atomic; no repeating groups.
- **Second Normal Form (2NF):** Satisfies 1NF, and every non-prime attribute is fully functionally dependent on the entire primary key.
- **Third Normal Form (3NF):** Satisfies 2NF, and no non-prime attribute is transitively dependent on the primary key ($X \rightarrow Y$ implies $X$ is a superkey or $Y$ is a prime attribute).

### 2.2 DMGT: Relations, Domain, Range, and Equivalence
In discrete mathematics, a binary relation $R$ from set $A$ to set $B$ is a subset of the Cartesian product $A \times B$.
- **Domain:** $\text{dom}(R) = \{a \in A \mid \exists b \in B, (a, b) \in R\}$
- **Range:** $\text{rng}(R) = \{b \in B \mid \exists a \in A, (a, b) \in R\}$
- **Equivalence Relation:** A relation $R$ on set $A$ is an equivalence relation if and only if it is:
  1. **Reflexive:** $\forall x \in A, (x, x) \in R$
  2. **Symmetric:** $\forall x, y \in A, (x, y) \in R \implies (y, x) \in R$
  3. **Transitive:** $\forall x, y, z \in A, [(x, y) \in R \land (y, z) \in R] \implies (x, z) \in R$

### 2.3 ADSA: B-Tree Indexing Principles
A B-Tree of minimum degree $t \ge 2$ is a self-balancing search tree designed to optimize block-based storage:
1. Every node has at most $2t - 1$ keys.
2. Every internal node (except root) has at least $t - 1$ keys.
3. Every internal node has $\text{number of keys} + 1$ children.
4. All leaves appear at the exact same depth.
5. Search and insertion operate in $O(t \log_t n)$ time.

### 2.4 Supervised Learning: Decision Trees
A Decision Tree recursively partitions feature space into homogenous subsets using information criteria (e.g., Gini impurity or Shannon entropy). It provides high interpretability, enabling factory engineers to identify which threshold (e.g., operating hours $> 4000$ or temperature $> 90^\circ\text{C}$) drives defect probability.

---

## Chapter 3: System Architecture and Design

### 3.1 Architectural Diagram
```text
[ Browser Client: HTML5 / Bootstrap 5 / Chart.js ]
                        |
                        ↓ HTTP / REST
         [ Flask Web Framework: app/routes.py ]
                        |
       +----------------+----------------+
       |                |                |
       ↓                ↓                ↓
[ DatabaseManager ] [ BTreeIndex ] [ DefectAnalyzer ]
(MySQL / SQLite)    (Memory B-Tree)(Decision Tree)
       |                |                |
       +----------------+----------------+
                        |
                        ↓
            [ TraceabilityService ]
                        |
      Unit → Batch → Machine → Product → Defect
```

### 3.2 Database Schema Specification
The schema comprises 7 interconnected tables:
1. `app_user`: System login credentials with Werkzeug PBKDF2/scrypt hashes.
2. `product`: Master catalog of products (`product_id` PK, `product_name` UNIQUE).
3. `machine`: Shop-floor equipment (`machine_id` PK, `status`, `operating_hours`).
4. `batch`: Production runs (`batch_id` PK, `product_id` FK, `machine_id` FK, `quantity`, `shift`, `temperature_c`, `pressure_bar`).
5. `production_unit`: Serialized parts (`unit_id` PK, `batch_id` FK, `serial_number` UNIQUE candidate key, `status`).
6. `defect`: Quality events (`defect_id` PK, `unit_id` FK, `defect_type`, `severity`, `detected_date`).
7. `machine_maintenance`: Equipment service records (`maintenance_id` PK, `machine_id` FK, `status`).

---

## Chapter 4: Implementation Details

### 4.1 Traceability Service (`app/traceability.py`)
The traceability engine executes parameterized SQL to connect units to batches, machines, and defect logs. It also generates aggregation metrics for the dashboard cards and charts:
- Total Products, Batches, Machines, Units, and Defective Units.
- Calculated Defect Rate: $\text{Defect Rate} = \left(\frac{\text{Defective Units}}{\text{Total Units}}\right) \times 100\%$.
- Machine-wise defect frequency and batch failure distributions.

### 4.2 In-Memory B-Tree Index (`algorithms/btree.py`)
The B-Tree is implemented with minimum degree $t=3$. When inserting into a full node ($2t - 1 = 5$ keys), the median key is pushed to the parent, and the remaining keys are split into two sibling nodes. Traversal is performed inorder to produce a sorted list of Unit IDs.

### 4.3 Defect Probability Classifier (`ml/train_model.py` & `app/classifier.py`)
Features are normalized and encoded into a vector:
$$\mathbf{x} = [\text{machine\_code}, \text{product\_code}, \text{temp}, \text{pressure}, \text{hours}, \text{shift\_code}, \text{prev\_defects}, \text{maint\_overdue}]$$
The trained Decision Tree calculates class probabilities:
$$P(\text{Defect} = 1 \mid \mathbf{x}) = \frac{N_{\text{defective}}}{N_{\text{total in leaf}}}$$
Based on this probability:
- $\ge 70\%$: **HIGH RISK**
- $40\% - 69.9\%$: **MEDIUM RISK**
- $< 40\%$: **LOW RISK**

---

## Chapter 5: Verification & Test Results

### 5.1 Automated Test Execution
Automated tests are executed using `pytest` across 15 test scenarios:
- **Authentication:** Valid credentials (`admin` / `Admin@123`) redirect to dashboard; invalid credentials trigger friendly errors.
- **Traceability:** Unit `U10025` resolves correctly to Product *Industrial Pump*, Batch *B2026-003*, Machine *CNC Lathe 03*, and Defect *Surface Crack*.
- **CRUD Operations:** Catalog creation and integrity validation across products, machines, batches, units, and defects.
- **B-Tree Operations:** Insertion of out-of-order keys results in balanced trees with sorted inorder sequences.
- **Relational Algebra:** Selections, projections, joins, unions, intersections, and differences return mathematically verified sets.
- **Result:** **15 passed in 4.43 seconds**.

---

## Chapter 6: Conclusion & Future Scope

### 6.1 Conclusion
The **Manufacturing Defect Traceability and Prediction System (MDTPS)** successfully solves the defect provenance problem by enabling sub-second tracing of any defective unit to its machine, batch, product, and operational parameters. Furthermore, it serves as a unified pedagogical platform demonstrating DBMS normalization, relational algebra, discrete mathematical relations, B-Tree data structures, object-oriented design, and machine learning classification.

### 6.2 Future Enhancements
- Integration with real-time IoT sensors (MQTT/OPC-UA) for streaming telemetry.
- Barcode and QR-code scanner support for shop-floor tablets.
- Automated maintenance work-order generation when defect rates exceed predefined statistical process control (SPC) limits.
