# V2 Engine: Integrated Monthly KPI Architecture

## Current Architecture vs Proposed Enhancement

### Current V2 Engine Flow
```python
for year, month in scenario.time_range.get_month_list():
    # 1. Process month: recruitment + churn + progression  
    month_events = _process_office_month(office_state, year, month, ...)
    
    # 2. Collect basic office metrics
    office_metrics = _collect_office_metrics(office_state, year, month)
    
    # 3. Store monthly results (events only)
    monthly_results[month_key] = MonthlyResults(
        year=year,
        month=month, 
        office_results={office_id: office_metrics},
        events=month_events
    )

# 4. Calculate KPIs at END (entire period)
if kpi_calculator:
    kpi_data = kpi_calculator.calculate_all_kpis(results, business_model)
    results.kpi_data = kpi_data  # Single period KPIs
```

### Proposed Integrated Architecture
```python  
for year, month in scenario.time_range.get_month_list():
    # 1. Process month: recruitment + churn + progression
    month_events = _process_office_month(office_state, year, month, ...)
    
    # 2. Calculate monthly KPIs (NEW - within month loop!)
    monthly_kpis = _calculate_monthly_kpis(
        office_state, month_events, business_plan_targets, previous_workforce
    )
    
    # 3. Store enhanced monthly results (events + KPIs together)
    monthly_results[month_key] = EnhancedMonthlyResults(
        year=year,
        month=month,
        events=month_events,
        office_metrics=office_metrics,
        kpis=monthly_kpis,  # NEW - KPIs stored per month
        business_plan_targets=targets
    )
```

## Enhanced Monthly Results Structure

### Data Structure
```python
enhanced_monthly_results = {
    '2024-06': {
        'year': 2024,
        'month': 6,
        'events': [PersonEvent, PersonEvent, ...],  # Individual events
        'office_metrics': {
            'total_workforce': 54,
            'workforce_by_role': {'Consultant': 32, 'Sales': 16, ...}
        },
        'kpis': {
            'workforce': {      # 13 workforce KPIs
                'starting_headcount': 50,
                'ending_headcount': 54,
                'headcount_change': +4,
                'headcount_change_pct': +8.0,
                'total_hires': 7,
                'total_churns': 3,
                'total_promotions': 0,
                'net_recruitment': 4,
                'hire_rate_pct': 13.0,
                'churn_rate_pct': 6.0,
                'promotion_rate_pct': 0.0,
                'workforce_by_role': {...},
                'workforce_by_level': {...}
            },
            'financial': {      # 7 financial KPIs  
                'revenue': 519107,
                'operating_costs': 433182,
                'gross_profit': 85925,
                'profit_margin_pct': 16.6,
                'revenue_per_fte': 9613,
                'cost_per_fte': 8022,
                'salary_budget': 300000
            },
            'activity': {       # 4 activity KPIs
                'total_events': 10,
                'events_per_person': 0.19,
                'event_types': {'hired': 7, 'churned': 3},
                'activity_rate_pct': 18.5
            }
        },
        'business_plan_targets': {
            'recruitment_targets': {...},
            'churn_targets': {...},
            'revenue_target': 519107,
            'operating_costs': 433182
        }
    },
    '2024-07': { ... },  # Same structure for each month
    # ...
}
```

## Implementation Changes Needed

### 1. Enhance MonthlyResults Class
```python
@dataclass
class EnhancedMonthlyResults:
    """Enhanced monthly results with integrated KPIs"""
    year: int
    month: int
    events: List[PersonEvent]
    office_metrics: Dict[str, Any]
    kpis: Dict[str, Dict[str, Any]]  # NEW - monthly KPIs
    business_plan_targets: Dict[str, Any]  # NEW - context
```

### 2. Add Monthly KPI Calculation Method
```python
def _calculate_monthly_kpis(self, office_state: OfficeState, 
                           month_events: List[PersonEvent],
                           business_targets: MonthlyTargets,
                           previous_workforce_count: int) -> Dict[str, Dict[str, Any]]:
    """Calculate comprehensive KPIs for a single month"""
    
    # Calculate workforce KPIs
    workforce_kpis = self._calculate_monthly_workforce_kpis(
        office_state, month_events, previous_workforce_count
    )
    
    # Calculate financial KPIs  
    financial_kpis = self._calculate_monthly_financial_kpis(
        business_targets, office_state.get_total_workforce()
    )
    
    # Calculate activity KPIs
    activity_kpis = self._calculate_monthly_activity_kpis(
        month_events, office_state.get_total_workforce()
    )
    
    return {
        'workforce': workforce_kpis,
        'financial': financial_kpis, 
        'activity': activity_kpis
    }
```

### 3. Modify Main Simulation Loop
```python
def _execute_time_first_simulation(self, scenario: ScenarioRequest) -> None:
    """Enhanced simulation loop with monthly KPI calculation"""
    
    previous_workforce_counts = {}  # Track workforce between months
    
    for year, month in scenario.time_range.get_month_list():
        month_key = f"{year:04d}-{month:02d}"
        
        monthly_office_results = {}
        monthly_events = []
        
        for office_id, office_state in self.office_states.items():
            # 1. Process month (recruitment + churn + progression)
            office_events = self._process_office_month(
                office_state, year, month, date(year, month, 1), scenario.levers
            )
            monthly_events.extend(office_events)
            
            # 2. Get business plan targets
            business_targets = self.business_processor.get_monthly_targets(
                office_id, year, month
            )
            adjusted_targets = self.business_processor.apply_scenario_levers(
                business_targets, scenario.levers
            )
            
            # 3. Calculate monthly KPIs (NEW!)
            monthly_kpis = self._calculate_monthly_kpis(
                office_state, 
                office_events,
                adjusted_targets,
                previous_workforce_counts.get(office_id, 0)
            )
            
            # 4. Update workforce tracking
            previous_workforce_counts[office_id] = office_state.get_total_workforce()
            
            # 5. Store enhanced results
            office_results = {
                'metrics': self._collect_office_metrics(office_state, year, month),
                'kpis': monthly_kpis,
                'targets': adjusted_targets
            }
            monthly_office_results[office_id] = office_results
        
        # Store enhanced monthly results
        self.monthly_results[month_key] = EnhancedMonthlyResults(
            year=year,
            month=month,
            events=monthly_events,
            office_metrics=monthly_office_results,
            kpis={office_id: results['kpis'] for office_id, results in monthly_office_results.items()},
            business_plan_targets={office_id: results['targets'] for office_id, results in monthly_office_results.items()}
        )
```

## Benefits of Integrated Architecture

### Real-Time Accuracy
- KPIs calculated during simulation execution  
- Workforce state matches KPI calculations exactly
- No post-processing data inconsistencies

### Monthly Granularity  
- 24 KPIs calculated per month
- Month-over-month comparisons accurate
- Trends and patterns visible immediately

### Data Consistency
- Events and KPIs stored together in same monthly result
- Business plan targets linked to actual results
- Individual event tracking preserved

### Performance
- No separate KPI calculation pass required
- Memory efficient - KPIs calculated incrementally
- Real-time monitoring possible

## Test Results Demonstration

### Sample Monthly Output
```
2024-06: 50 -> 54 workforce (+8.0%) | $519K revenue (16.6% margin)
   Events: 10 (7 hired, 3 churned, 0 promoted)
   Rates: 13.0% hire, 6.0% churn, 0.0% promotion  
   Per-FTE: $9,613 revenue, $8,022 costs
   Activity: 0.19 events/person, 18.5% engagement

2024-07: 54 -> 57 workforce (+5.6%) | $587K revenue (27.3% margin)  
   Events: 13 (4 hired, 1 churned, 8 promoted)
   Rates: 7.0% hire, 1.9% churn, 14.8% promotion
   Per-FTE: $10,303 revenue, $7,494 costs
   Activity: 0.23 events/person, 22.8% engagement
```

### Data Volume
- **24 KPIs per month** (13 workforce + 7 financial + 4 activity)  
- **3 months = 72 total KPI data points**
- **Individual event tracking maintained** (30 total events)
- **Business plan integration complete**

This integrated architecture provides comprehensive monthly KPI tracking alongside all simulation events, enabling real-time business intelligence and accurate month-over-month analysis.