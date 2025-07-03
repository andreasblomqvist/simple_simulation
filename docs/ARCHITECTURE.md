# SimpleSim Architecture Documentation

## 1. System Overview

SimpleSim is a simulation platform for modeling organizational growth, financials, and workforce scenarios. The system is composed of the following main components:

- **Frontend (UI):** Executive-friendly React interface for scenario creation, lever adjustment, and results visualization.
- **Backend API:** FastAPI-based service that exposes endpoints for scenario management, simulation execution, and data export.
- **Adapter/Service Layer:** (Proposed) Middle layer that translates scenario runner payloads into the simulation engine's expected format and vice versa.
- **Simulation Engine:** Core Python engine that performs deterministic, monthly simulations and calculates all KPIs and financial metrics.
- **Data Storage:** JSON files for configuration, scenario definitions, and results; Excel for imports/exports.

### High-Level Architecture Diagram

```
Frontend (React UI)
    |
    v
Backend API (FastAPI)
    |
    v
[Adapter/Service Layer]
    |
    v
Simulation Engine (Python)
    |
    v
Data Storage (JSON, Excel)
```

---

## 2. Current Solution

### Data Flow
1. **User interacts with the Scenario Runner UI** to create or modify a scenario (set name, description, time range, office scope, and adjust levers for recruitment, churn, progression).
2. **Frontend sends a scenario payload** to the backend API (currently, this may be a custom or partial mapping to the engine's lever plan format).
3. **Backend API receives the payload** and either:
   - Translates it into the simulation engine's lever plan format (if logic exists in the router), or
   - Passes it directly to the simulation engine (if already in the correct format).
4. **Simulation Engine runs the scenario** using the provided parameters, applies all business logic, and returns results (KPIs, journey distribution, financials, etc.).
5. **Backend returns results to the frontend** for display and comparison.

### Where Business Logic Resides
- **All core calculations** (KPI, financials, journey, etc.) are performed in the simulation engine.
- **Some data transformation** may currently occur in the backend router, but this is not centralized or standardized.

---

## 3. Scenario Runner Integration: Adapter/Service Layer

### Motivation
- Decouple the frontend scenario runner from the simulation engine's internal data structures.
- Centralize all data transformation, validation, and business rules for scenario execution.
- Allow the simulation engine to remain stable and focused on calculations, while supporting evolving UI needs.

### Responsibilities
- **Translate scenario runner payloads** (name, description, time range, office scope, lever values) into the simulation engine's lever plan format.
- **Validate inputs** (lever ranges, time ranges, office scope, etc.).
- **Call the simulation engine** with the transformed payload.
- **Return results** to the frontend, reformatting only for structure (never recalculating KPIs or business metrics).
- **Persist scenario definitions and results** (as needed).

### Example Data Transformation
- **Input (from UI):**
  ```json
  {
    "name": "Aggressive Growth",
    "description": "Test high recruitment, low churn",
    "time_range": {"start_year": 2025, "end_year": 2027},
    "office_scope": ["Stockholm", "Berlin"],
    "levers": {
      "recruitment": {"A": 1.2, "AC": 1.1},
      "churn": {"A": 0.9, "AC": 1.0},
      "progression": {"A": 1.0, "AC": 1.0}
    }
  }
  ```
- **Output (to Engine):**
  ```json
  {
    "offices": {
      "Stockholm": {
        "Consultant": {
          "A": {
            "recruitment_1": 24.0,  // baseline * 1.2
            ...
            "churn_1": 1.8,         // baseline * 0.9
            ...
          }
        }
      },
      ...
    }
  }
  ```

### What the Adapter Does **NOT** Do
- Does **not** recalculate KPIs, totals, or business metrics.
- Does **not** patch or fix results from the engine.
- Does **not** duplicate business logic from the engine.

---

## 4. Risks and Mitigation

### Risks
- **Transformation Bugs:** Incorrect mapping of lever values or office/level names can lead to simulation errors.
- **Result Mismatches:** If the adapter recalculates or post-processes results, discrepancies can arise.
- **Logging/Debugging Complexity:** More layers can make it harder to trace bugs.

### Mitigation Strategies
- **Keep the adapter thin:** Only translate data structures, never recalculate business logic.
- **Single source of truth:** All calculations remain in the simulation engine.
- **Automated integration tests:** Run scenarios through both the adapter and direct engine calls, compare results.
- **Comprehensive logging:** Log all inputs/outputs at each layer for traceability.
- **Schema validation:** Use Pydantic models to validate all data in/out.

---

## 5. Best Practices

- **Centralize all business logic in the simulation engine.**
- **Keep the adapter/service layer as thin as possible.**
- **Write integration tests** to ensure adapter and engine results match.
- **Document all data mappings and transformations.**
- **Log all scenario inputs and outputs for traceability.**
- **Version adapter logic** if/when the engine's input/output format changes.

---

## 6. Future Considerations

- **Refactor the engine** to accept scenario runner payloads directly if/when the UI and engine are tightly coupled.
- **Support versioned scenario formats** for backward compatibility.
- **Expand adapter responsibilities** only if absolutely necessary (e.g., for new business rules that cannot live in the engine).

---

## 7. Appendix: Example Adapter Service Skeleton

```python
# backend/src/services/scenario_service.py
from typing import Dict, Any

class ScenarioService:
    def run_scenario(self, scenario_payload: Dict[str, Any]) -> Dict[str, Any]:
        lever_plan = self._transform_to_lever_plan(scenario_payload)
        results = self._call_simulation_engine(lever_plan)
        return self._format_results(results)

    def _transform_to_lever_plan(self, scenario_payload: Dict[str, Any]) -> Dict:
        # Transform UI payload to engine lever plan
        pass

    def _call_simulation_engine(self, lever_plan: Dict) -> Dict:
        # Call the simulation engine with lever plan
        pass

    def _format_results(self, results: Dict) -> Dict:
        # Reformat results for frontend (no recalculation)
        pass
```

---

This document should be updated as the system evolves. All contributors should reference this as the single source of architectural truth for SimpleSim. 