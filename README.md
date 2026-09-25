# Manufacturing Defect Traceability and Prediction System (MDTPS)

**Academic project.** All manufacturing records are fictional sample data.

## 1. Project title

**Manufacturing Defect Traceability and Prediction System**  
Short name: **MDTPS — Manufacturing Defect Traceability & Prediction System**

## 2. Problem statement

A manufacturer cannot trace which batch or machine produced a defective unit.

This system traces a production unit (by Unit ID or serial number) to its **product, batch, machine, production date, shift, and defect record**, and provides academic analysis of defect patterns plus a demonstration defect-probability classifier.

## 3. Objectives

- Store production data in a normalized relational database.
- Trace a defective unit along Unit → Batch → Machine → Product.
- Demonstrate ER modelling and relational algebra (DBMS).
- Demonstrate sets and relations (DMGT).
- Demonstrate an in-memory B-Tree index (ADSA), separate from MySQL indexes.
- Implement the tracking application with OOP (OOPJ concepts in Python classes).
- Train a beginner Decision Tree classifier on sample data (Python / ML).

## 4. Features

- Login with hashed passwords
- Dashboard cards and charts
- CRUD + search for products, machines, batches, units, defects
- Defect traceability report
- Machine and batch analysis (association, not causation)
- Defect probability page (academic model)
- Interactive B-Tree demo
- Live relational-algebra demo
- CSV / PDF reports
- About page with ER, subject mapping, and DMGT relations

## 5. Technologies

| Layer | Technology |
| --- | --- |
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js |
| Backend | Python, Flask |
| Database | MySQL (college DBMS target); SQLite fallback for first-run / tests |
| ML | pandas, scikit-learn Decision Tree |
| ADSA | Custom B-Tree in `algorithms/btree.py` |

Do **not** use Streamlit. Open the app in a normal browser.

## 6. System architecture

```text
                  USER
                   |
                   ↓
          WEB FRONTEND
        HTML + CSS + JS
                   |
                   ↓
            FLASK BACKEND
                   |
       +-----------+-----------+
       |           |           |
       ↓           ↓           ↓
   DATABASE      B-TREE      ML MODEL
    MySQL        INDEX       PYTHON
       |           |           |
       +-----------+-----------+
                   |
                   ↓
          TRACEABILITY ENGINE
                   |
                   ↓
       PRODUCT → BATCH → MACHINE
                   |
                   ↓
                DEFECT
```

## 7. Database design

Normalized to 3NF:

- Product attributes stay in `product`.
- Machine attributes stay in `machine`.
- A batch references product and machine (no repeating product name on every unit).
- A unit references a batch.
- A defect references a unit.
- Maintenance references a machine.

See `database/schema.sql` and `documentation/er_diagram.md`.

## 8. Subject mapping

| Subject | Concept | Project implementation |
| --- | --- | --- |
| DBMS U1 | ER Model | Product, Batch, Machine, Defect ER model |
| DBMS U2 | Relational Algebra | Traceability queries on `/relational` |
| DMGT U2 | Relations | Product–Batch–Machine–Defect relations |
| ADSA U1 | B-Tree | Part/Unit ID indexing and search |
| OOPJ | OOP | Production tracking application classes |
| Python | Classification | Defect probability classifier |

## 9. Installation (Windows PowerShell)

Open PowerShell in this project folder.

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Copy environment settings:

```powershell
copy .env.example .env
```

## 10. Database setup

### Option A — MySQL (recommended for the DBMS viva)

1. Install MySQL Server and start the service.
2. Edit `.env`:
   - `DB_ENGINE=mysql`
   - `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE=mdtps`
3. Generate SQL (already included; regenerate if you change the script):

```powershell
python scripts\generate_sample_data.py
```

4. Seed MySQL (creates schema, sample rows, hashed admin user):

```powershell
python -m app.seed
```

You can also run `database/schema.sql` then `database/sample_data.sql` in MySQL Workbench, then still run `python -m app.seed` so the hashed demo user is created.

### Option B — SQLite (if MySQL is not installed yet)

In `.env` set:

```text
DB_ENGINE=sqlite
SQLITE_PATH=instance/mdtps.sqlite3
```

Then:

```powershell
python scripts\generate_sample_data.py
python -m app.seed
```

## 11. Train the academic classifier

```powershell
python ml\train_model.py
```

## 12. How to run

```powershell
python run.py
```

Browser:

```text
http://127.0.0.1:5000
```

## 13. Sample login (demo account only)

- Username: `admin`
- Password: `Admin@123`

This is a **local academic demonstration account**. The password is stored as a Werkzeug hash in `app_user`, not as plain text.

Suggested demo unit: **U10025**.

## 14. Screenshots

Place captured images in the `screenshots/` folder (login, dashboard, trace of U10025, B-Tree, prediction).

## 15. Tests

```powershell
pytest -q
```

## 16. Cloud Deployment (Vercel, Render, Railway)

The project includes ready-to-deploy configurations:
- [`vercel.json`](vercel.json) & [`api/index.py`](api/index.py) for **Vercel** serverless deployment.
- [`Procfile`](Procfile) for **Render** / **Railway** deployment.

See the complete step-by-step instructions in [**`documentation/deployment_guide.md`**](documentation/deployment_guide.md).

## 17. Future enhancements

- Role-based users (operator vs quality engineer)
- Photo attachments for defects
- Real sensor streams (out of scope for this academic sample)
- External authentication (college LDAP)

## 18. Academic disclaimer

This project uses **fictional** products, machines, batches, and defects. The machine-learning model is trained on generated sample data. Database joins show **recorded association**. They do not prove that a machine caused a defect. The model must not be described as a real-world predictor.

## Project layout

```text
app/            Flask backend
templates/      HTML pages
static/         CSS and JS
database/       MySQL and SQLite schema + sample SQL
algorithms/     Academic B-Tree
ml/             Dataset and training script
documentation/  ER, RA, DMGT, OOP, B-Tree, viva, report, PPT
tests/          Pytest cases
scripts/        Sample-data generator
```
