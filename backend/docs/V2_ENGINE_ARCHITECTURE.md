# SimpleSim V2 Engine Architecture Documentation

## Overview

The SimpleSim V2 Engine represents a complete rewrite of the simulation engine with a **time-first** processing approach, individual event tracking, and enhanced business plan integration. This document outlines the core architecture, business rules, and data structures that define the V2 engine.

## Architecture Principles

### 1. Time-First Processing
- **Monthly simulation loops**: Process all offices for each month before moving to the next
- **Deterministic execution**: Same seed produces identical results across runs
- **Sequential workforce operations**: Churn → Progression → Recruitment for each month

### 2. Individual Event Tracking
- **PersonEvent objects**: Track every workforce change (HIRED, CHURNED, PROMOTED)
- **Event details**: Include role, level, office, date, and reason for each event
- **Comprehensive audit trail**: Full visibility into simulation decisions

### 3. Enhanced Business Plan Integration
- **Monthly targets**: Revenue, costs, recruitment, and churn targets per month
- **Role-specific data**: Separate targets for each role and level combination
- **Scenario levers**: Apply multipliers to business plan targets
- **KPI calculation**: Real-time calculation of 22+ metrics per month

## Core Components

### SimulationEngineV2
**Location**: `backend/src/services/simulation_engine_v2.py`

The main simulation engine coordinates monthly processing across all offices.

```python
def run_scenario(self, scenario: ScenarioRequest) -> SimulationResults:
    """Execute time-first simulation with monthly processing"""
    
    # For each month in time range
    for year, month in month_iterator:
        # Process all offices for this month
        for office_id in scenario.office_ids:
            monthly_events = self._process_office_month(
                office_state, year, month, current_date, scenario.levers
            )
            
            # Calculate monthly KPIs
            monthly_kpis = self.kpi_calculator.calculate_monthly_kpis(
                office_state, monthly_events, business_targets
            )
            
            # Store results
            monthly_results[month_key] = {
                'events': monthly_events,
                'kpis': monthly_kpis,
                'workforce_snapshot': office_state.get_workforce_snapshot()
            }
```

**Key Features**:
- Time-first processing ensures consistent cross-office simulation
- Preserves office states between months for accurate progression tracking
- Integrates KPI calculation within the simulation loop
- Handles both leveled and flat role structures

### WorkforceManagerV2
**Location**: `backend/src/services/workforce_manager_v2.py`

Handles individual workforce operations with CAT matrix integration.

```python
def process_churn(self, office_state, churn_targets, current_date):
    """Process monthly churn with individual person selection"""
    
def process_progression(self, office_state, cat_matrices, current_date):
    """Process promotions using CAT probability matrices"""
    
def process_recruitment(self, office_state, recruitment_targets, current_date):
    """Hire new people based on monthly targets"""
```

**Business Rules**:
- **CAT Matrix Integration**: Uses Career Advancement Timeline for promotion probabilities
- **Level-Specific Progression**: Different progression months per level (A/AC: [1,4,7,10], C/SrC: [1,7], M+: [1])
- **Tenure-Based Categories**: Maps tenure to CAT categories (CAT0, CAT6, CAT12, CAT18, CAT24, CAT30+)

### BusinessPlanProcessorV2
**Location**: `backend/src/services/business_plan_processor_v2.py`

Processes monthly business plan targets with scenario lever application.

```python
def get_monthly_targets(self, office_id, year, month):
    """Get business plan targets for specific month"""
    
def apply_scenario_levers(self, targets, levers):
    """Apply recruitment/churn/progression multipliers"""
```

**Enhanced Structure** (Planned):
```python
class EnhancedMonthlyPlan:
    # Existing fields
    recruitment: Dict[str, Dict[str, int]]
    churn: Dict[str, Dict[str, int]]
    revenue: float
    costs: float
    
    # NEW: Baseline workforce data
    baseline_fte: Dict[str, Dict[str, int]]  # Current workforce by role/level
    
    # NEW: Utilization and financial details
    utilization_targets: Dict[str, float]  # By role
    price_per_hour: Dict[str, float]      # Billable rates by level
    salary_costs: Dict[str, Dict[str, float]]  # By role/level
    operating_costs: float                # Non-salary costs
```

## Business Rules and Role Definitions

### Role-Specific Business Model

Based on actual SimpleSim business requirements:

```python
ROLE_DEFINITIONS = {
    'Consultant': {
        'billable': True,
        'generates_revenue': True,          # Only role that generates revenue
        'has_levels': True,
        'levels': ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P'],
        'progression_enabled': True,
        'revenue_model': 'billable_hours'
    },
    'Sales': {
        'billable': False,
        'generates_revenue': False,         # Support role - no direct revenue
        'has_levels': True,
        'levels': ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P'],
        'progression_enabled': True,
        'revenue_model': 'support_role'
    },
    'Recruitment': {
        'billable': False,
        'generates_revenue': False,         # Support role - no direct revenue
        'has_levels': True,
        'levels': ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P'],
        'progression_enabled': True,
        'revenue_model': 'support_role'
    },
    'Operations': {
        'billable': False,
        'generates_revenue': False,         # Support role - no direct revenue
        'has_levels': False,
        'levels': ['Operations'],           # Single flat level
        'progression_enabled': False,
        'revenue_model': 'support_role'
    }
}
```

### Net Sales Calculation

Revenue is generated exclusively by Consultant billable hours:

```python
def calculate_net_sales(consultant_workforce, utilization_target, price_per_hour, working_hours_per_month=160):
    """
    Net Sales = Sum across all consultant levels of:
    (Number of Consultants at Level) × 
    (Utilization Rate) × 
    (Price per Hour for Level) × 
    (Working Hours per Month)
    """
    
    total_revenue = 0
    
    for level, consultants in consultant_workforce.items():
        active_consultants = len([c for c in consultants if c.is_active])
        level_utilization = utilization_target  # Can be level-specific
        level_price = price_per_hour[level]
        
        level_revenue = (
            active_consultants * 
            level_utilization * 
            level_price * 
            working_hours_per_month
        )
        
        total_revenue += level_revenue
    
    return total_revenue
```

## Data Structures

### Core Simulation Objects

#### Person
```python
@dataclass
class Person:
    id: str
    current_role: str
    current_level: str
    current_office: str
    hire_date: date
    current_level_start: date
    events: List[PersonEvent]
    is_active: bool = True
    
    def get_level_tenure_months(self, current_date: date = None) -> int:
        """Calculate months in current level for CAT matrix lookup"""
```

#### PersonEvent
```python
@dataclass
class PersonEvent:
    event_id: str
    person_id: str
    event_type: PersonEventType  # HIRED, CHURNED, PROMOTED
    event_date: date
    details: Dict[str, Any]  # Role, level, office, reason, etc.
```

#### OfficeState
```python
@dataclass
class OfficeState:
    name: str
    workforce: Dict[str, Dict[str, List[Person]]]  # role -> level -> people
    business_plan: BusinessPlan
    snapshot: PopulationSnapshot
    cat_matrices: Dict[str, CATMatrix]
    economic_parameters: Optional[EconomicParameters]
    
    def get_total_workforce(self) -> int:
        """Count all active employees across all roles/levels"""
```

### Monthly Results Structure

```python
monthly_results = {
    "2024-07": {
        "events": List[PersonEvent],
        "kpis": {
            # Workforce KPIs
            "total_headcount": int,
            "total_recruitment": int,
            "total_churn": int,
            "net_recruitment": int,
            
            # Role-specific KPIs
            "role_specific_workforce": {
                "Consultant": {
                    "total_headcount": int,
                    "headcount_by_level": {"A": int, "AC": int, ...},
                    "billable_headcount": int,
                    "progression_eligible": bool
                },
                "Sales": {...},
                "Recruitment": {...},
                "Operations": {...}
            },
            
            # Financial KPIs
            "net_sales": float,
            "total_costs": float,
            "gross_profit": float,
            "ebitda": float,
            
            # Role-specific financial
            "role_specific_financial": {
                "Consultant": {
                    "revenue": float,    # Gets ALL office revenue
                    "costs": float,      # Proportional salary costs
                    "profit": float,
                    "generates_revenue": True
                },
                "Sales": {
                    "revenue": 0,        # No direct revenue
                    "costs": float,      # Pure cost center
                    "profit": float,     # Always negative
                    "generates_revenue": False
                },
                # ... other roles
            }
        },
        "workforce_snapshot": Dict[str, Dict[str, int]]  # role -> level -> count
    }
}
```

## CAT Matrix System

The Career Advancement Timeline (CAT) matrix defines promotion probabilities based on tenure in current level.

### CAT Categories
- **CAT0**: 0 months tenure
- **CAT6**: 6+ months tenure
- **CAT12**: 12+ months tenure
- **CAT18**: 18+ months tenure
- **CAT24**: 24+ months tenure
- **CAT30**: 30+ months tenure
- **CAT30+**: 30+ months tenure (same as CAT30)

### Level-Specific Progression Months
Different roles have different progression evaluation months:

```python
LEVEL_SPECIFIC_PROGRESSION_MONTHS = {
    "A": [1, 4, 7, 10],      # Junior levels: quarterly evaluation
    "AC": [1, 4, 7, 10],     # Junior levels: quarterly evaluation
    "C": [1, 7],             # Mid levels: bi-annual evaluation
    "SrC": [1, 7],           # Mid levels: bi-annual evaluation
    "AM": [1],               # Senior levels: annual evaluation only
    "M": [1],                # Senior levels: annual evaluation only
    "SrM": [1],              # Senior levels: annual evaluation only
    "Pi": [1],               # Senior levels: annual evaluation only
    "P": [1]                 # Senior levels: annual evaluation only
}
```

### CAT Matrix Usage
```python
def calculate_promotion_probability(person: Person, current_date: date) -> float:
    tenure_months = person.get_level_tenure_months(current_date)
    cat_category = get_cat_category(tenure_months)  # e.g., "CAT12"
    
    cat_matrix = self.cat_matrices[person.current_role]
    level_probabilities = cat_matrix.progression_probabilities[person.current_level]
    
    return level_probabilities.get(cat_category, 0.0)
```

## Enhanced Business Plan Integration

### Current Structure Limitations
The current business plan structure lacks baseline workforce data and detailed financial parameters needed for accurate KPI calculation.

### Planned Enhancements

#### 1. Baseline FTE Integration
```python
# Option A: Duplicate in business plan (chosen approach)
monthly_plan = {
    "baseline_fte": {
        "Consultant": {"A": 5, "AC": 8, "C": 6, "SrC": 3, "M": 1},
        "Sales": {"A": 3, "AC": 2, "C": 1},
        "Recruitment": {"A": 1, "AC": 1, "C": 1},
        "Operations": {"Operations": 2}
    },
    "recruitment": {...},  # Existing
    "churn": {...},        # Existing
    "revenue": float,      # Existing
    "costs": float         # Existing
}

# Option B: Fetch from office snapshot (alternative)
# Pros: Single source of truth
# Cons: Requires snapshot loading, more complex data flow
```

#### 2. Utilization-Based Revenue Calculation
```python
monthly_plan = {
    "utilization_targets": {
        "Consultant": 0.85,  # 85% billable utilization
        "Sales": 0.0,        # Non-billable
        "Recruitment": 0.0,  # Non-billable
        "Operations": 0.0    # Non-billable
    },
    "price_per_hour": {
        "A": 150, "AC": 200, "C": 250, 
        "SrC": 300, "AM": 350, "M": 400,
        "SrM": 450, "Pi": 500, "P": 600
    },
    "working_hours_per_month": 160  # Standard full-time
}
```

#### 3. Detailed Cost Breakdown
```python
monthly_plan = {
    "salary_costs": {
        "Consultant": {"A": 5000, "AC": 6000, "C": 7500, ...},
        "Sales": {"A": 4000, "AC": 5000, "C": 6000, ...},
        "Recruitment": {"A": 4500, "AC": 5500, "C": 6500, ...},
        "Operations": {"Operations": 4000}
    },
    "operating_costs": 50000,  # Office rent, utilities, equipment, etc.
    "total_costs": float       # Calculated: salary_costs + operating_costs
}
```

## KPI Calculation Integration

### Monthly KPI Processing
KPIs are calculated within the simulation loop for each month:

```python
def _process_office_month(self, office_state, year, month, current_date, levers):
    # 1. Execute workforce operations
    monthly_events = []
    monthly_events.extend(self.workforce_manager.process_churn(...))
    monthly_events.extend(self.workforce_manager.process_progression(...))
    monthly_events.extend(self.workforce_manager.process_recruitment(...))
    
    # 2. Calculate KPIs immediately
    business_targets = self.business_processor.get_monthly_targets(office_id, year, month)
    monthly_kpis = self.kpi_calculator.calculate_monthly_kpis(
        office_state, monthly_events, business_targets
    )
    
    # 3. Store comprehensive results
    return monthly_events, monthly_kpis
```

### KPI Categories

#### Workforce KPIs (7 metrics)
- Total headcount, recruitment, churn, net recruitment
- Headcount by role, promotion count, churn rate

#### Financial KPIs (8 metrics)
- Net sales, total costs, gross profit, EBITDA
- Revenue per FTE, cost per FTE, profit margin, utilization rate

#### Role-Specific KPIs (4 roles × 6 metrics = 24 metrics)
- Per-role headcount, events, revenue attribution, cost allocation
- Billable vs non-billable distinction
- Revenue-generating vs support role classification

#### Monthly Totals: 39+ metrics per month

## Testing and Verification

### Comprehensive Test Suite
**Location**: `backend/tests/v2/`

#### Key Tests
1. **`test_comprehensive_monthly_results.py`**: Full monthly simulation with all systems
2. **`test_monthly_kpis.py`**: 22-metric KPI calculation verification
3. **`test_role_specific_kpis.py`**: Role-specific business rule validation
4. **`final-simulation-test.spec.ts`**: End-to-end UI workflow testing

#### Test Data Structure
```
backend/tests/v2/test_data/
├── business_plans.json          # 24-month business plan data
├── cat_matrices_correct.json    # CAT progression probabilities  
├── population_snapshots.json    # Initial workforce state
└── corrected_role_definitions.py # Business rule documentation
```

### Manual Verification Commands
```bash
# Test comprehensive monthly results
python backend/tests/v2/test_comprehensive_monthly_results.py

# Test role-specific KPI calculation
python backend/tests/v2/test_role_specific_kpis.py

# Test monthly KPI breakdown
python backend/tests/v2/test_monthly_kpis.py
```

## Integration Points

### API Integration
The V2 engine integrates with the existing FastAPI system through:

```python
@router.post("/v2/run")
async def run_simulation_v2(scenario: ScenarioRequest):
    """Run V2 simulation with enhanced KPI calculation"""
    engine = SimulationEngineV2Factory.create_engine()
    results = engine.run_scenario(scenario)
    return results
```

### Frontend Integration
V2 results maintain compatibility with existing frontend components while providing enhanced data:

```typescript
// Enhanced monthly results structure
interface MonthlyResultsV2 {
    events: PersonEvent[];
    kpis: {
        // Existing KPIs (backward compatible)
        total_headcount: number;
        total_recruitment: number;
        // ... other existing metrics
        
        // NEW: Role-specific data
        role_specific_workforce: Record<string, RoleWorkforceKPIs>;
        role_specific_financial: Record<string, RoleFinancialKPIs>;
        
        // NEW: Enhanced financial metrics
        net_sales: number;
        utilization_rate: number;
        ebitda: number;
    };
    workforce_snapshot: WorkforceSnapshot;
}
```

## Implementation Status

### ✅ Completed Components
- **Core V2 Engine**: Time-first processing with monthly loops
- **WorkforceManagerV2**: Individual event tracking with CAT matrix integration
- **BusinessPlanProcessorV2**: Monthly target processing with scenario levers
- **Person/Event System**: Comprehensive audit trail and state tracking
- **CAT Matrix System**: Level-specific progression with tenure-based probabilities
- **KPI Calculator**: 39+ monthly metrics with role-specific breakdown
- **Test Suite**: Comprehensive verification with real business plan data

### 🔄 In Progress
- **V2 Architecture Documentation**: This document
- **Business Plan Enhancement**: Adding baseline FTE and utilization fields

### ⏳ Pending
- **Enhanced Business Plan Model**: Implement utilization-based revenue calculation
- **Net Sales Calculator**: Use actual consultant hours and billable rates
- **Business Plan Loader**: Sync with population snapshots for baseline FTE
- **Monthly P&L Generator**: Full financial statement generation
- **V2 Conversion Utilities**: Convert existing scenarios to V2 format

## Future Roadmap

### Phase 1: Enhanced Financial Modeling (Current)
- Implement utilization-based net sales calculation
- Add detailed cost breakdown to business plans
- Create monthly P&L statement generation

### Phase 2: Advanced Analytics
- Predictive modeling for workforce planning
- Sensitivity analysis for scenario parameters
- Advanced visualization of role-specific trends

### Phase 3: Real-time Integration
- Live data feeds from HR systems
- Real-time KPI dashboards
- Automated alerting for workforce metrics

## Conclusion

The SimpleSim V2 Engine represents a significant advancement in workforce simulation capabilities, providing:

- **Individual-level tracking** with comprehensive event audit trails
- **Role-specific business rules** that accurately model different workforce functions
- **Enhanced KPI calculation** with 39+ monthly metrics and role-specific breakdown
- **Deterministic simulation** with time-first processing for consistent results
- **Scalable architecture** that supports complex multi-office scenarios

The V2 engine maintains backward compatibility while providing the foundation for advanced workforce analytics and strategic planning capabilities.