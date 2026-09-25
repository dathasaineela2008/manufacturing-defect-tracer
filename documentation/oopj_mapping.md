# OOPJ mapping (implemented in Python classes)

The college OOPJ outcomes are demonstrated by the domain model, not by empty “proof of concept” classes.

| Concept | Where it appears |
| --- | --- |
| Class / object | `Product`, `Machine`, `Batch`, `ProductionUnit`, `Defect` |
| Encapsulation | IDs stored as `self._id` with `@property` accessors |
| Constructor | `__init__` on every domain class; `from_row` factory |
| Abstraction | `ProductionEntity.summary()` is abstract |
| Inheritance | `Product`, `Machine`, `Batch` extend `ProductionEntity` because they share id + name |
| Polymorphism | `summary()` returns a different sentence per subclass |
| Methods | `Machine.needs_maintenance()`, `ProductionUnit.is_defective()`, `TraceabilityService.trace()` |
| Access control | Leading-underscore attributes; public properties |
| Exception handling | `ValidationError`, `RecordNotFoundError`, `DuplicateRecordError`, `DatabaseError` |

Inheritance is **not** applied to `Defect` or `ProductionUnit` because they are not “named production entities” in the same way. Forcing a shared parent would be artificial.

Supporting classes:

- `TraceabilityService` — Unit → Product/Batch/Machine/Defect
- `DatabaseManager` — connections and parameterized SQL
- `BTreeIndex` — academic index facade
- `DefectAnalyzer` — loads the Decision Tree and returns probability/risk
