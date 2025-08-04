# Office Business Plans & Scenario System Integration

## Overview

Design how office-specific business plans integrate with the existing scenario system, enabling them to function as baseline input for both individual office simulations and aggregated multi-office scenarios.

## Current Scenario System Structure

### Existing Baseline Input Format
```typescript
interface BaselineInput {
  global: {
    recruitment: {
      Consultant: {
        levels: {
          [level: string]: {
            recruitment: { values: { [monthKey: string]: number } }
            churn: { values: { [monthKey: string]: number } }
          }
        }
      }
    },
    churn: {
      Consultant: {
        levels: {
          [level: string]: {
            recruitment: { values: { [monthKey: string]: number } }
            churn: { values: { [monthKey: string]: number } }
          }
        }
      }
    }
  },
  offices?: {
    [officeName: string]: {
      // Office-specific baseline data
    }
  }
}
```

## Integration Architecture

### 1. Office Business Plan as Baseline Source

#### Business Plan to Baseline Transformation
```typescript
interface OfficeBusinessPlanTransformer {
  // Transform single office business plan to baseline format
  transformToBaseline(
    businessPlan: MonthlyBusinessPlan,
    officeId: string
  ): BaselineInput;
  
  // Aggregate multiple office business plans
  aggregateOfficesBaseline(
    businessPlans: Map<string, MonthlyBusinessPlan>
  ): BaselineInput;
  
  // Merge office plans with global baseline
  mergeWithGlobalBaseline(
    officeBaselines: BaselineInput,
    globalBaseline: BaselineInput
  ): BaselineInput;
}
```

### 2. Enhanced Scenario Structure

#### Extended Scenario Model
```typescript
interface EnhancedScenario {
  // Existing fields
  name: string;
  description: string;
  time_range: TimeRange;
  levers: Levers;
  
  // Enhanced baseline input
  baseline_input: EnhancedBaselineInput;
  
  // New office configuration
  office_scope: OfficeScope;
  business_plan_source: BusinessPlanSource;
}

interface EnhancedBaselineInput {
  // Existing global baseline
  global?: GlobalBaseline;
  
  // Office-specific baselines (from business plans)
  offices?: {
    [officeName: string]: OfficeBaseline;
  };
  
  // Source information
  source: 'global' | 'office_plans' | 'mixed';
  generated_from?: {
    business_plan_ids: string[];
    aggregation_method: 'sum' | 'proportional' | 'custom';
    timestamp: Date;
  };
}

interface OfficeScope {
  mode: 'all' | 'selected' | 'journey_based' | 'single';
  offices?: string[];
  journeys?: ('emerging' | 'established' | 'mature')[];
  single_office?: string;
}

interface BusinessPlanSource {
  type: 'business_plans' | 'global_baseline' | 'mixed';
  use_business_plans: boolean;
  fallback_to_global: boolean;
  override_with_levers: boolean;
}
```

### 3. Transformation Logic

#### Single Office to Baseline
```typescript
function transformOfficeBusinessPlanToBaseline(
  businessPlan: MonthlyBusinessPlan,
  officeId: string
): BaselineInput {
  const baseline: BaselineInput = {
    offices: {
      [officeId]: {
        recruitment: { Consultant: { levels: {} } },
        churn: { Consultant: { levels: {} } }
      }
    }
  };
  
  // Transform each role and level
  Object.entries(businessPlan.months).forEach(([month, monthData]) => {
    Object.entries(monthData).forEach(([role, roleData]) => {
      Object.entries(roleData).forEach(([level, levelData]) => {
        const monthKey = `${businessPlan.year}${month.padStart(2, '0')}`;
        
        // Initialize level if not exists
        if (!baseline.offices[officeId].recruitment[role].levels[level]) {
          baseline.offices[officeId].recruitment[role].levels[level] = {
            recruitment: { values: {} },
            churn: { values: {} }
          };
        }
        
        // Set recruitment and churn values
        baseline.offices[officeId].recruitment[role].levels[level].recruitment.values[monthKey] = levelData.recruitment;
        baseline.offices[officeId].recruitment[role].levels[level].churn.values[monthKey] = levelData.churn;
        
        // Handle other parameters (price, UTR, salary) in economic parameters
        // These go to office-specific configuration, not baseline input
      });
    });
  });
  
  return baseline;
}
```

#### Multi-Office Aggregation
```typescript
function aggregateOfficeBusinessPlans(
  businessPlans: Map<string, MonthlyBusinessPlan>,
  aggregationMethod: 'sum' | 'proportional' | 'custom'
): BaselineInput {
  switch (aggregationMethod) {
    case 'sum':
      return sumOfficeBaselines(businessPlans);
    case 'proportional':
      return proportionalAggregation(businessPlans);
    case 'custom':
      return customAggregation(businessPlans);
  }
}

function sumOfficeBaselines(
  businessPlans: Map<string, MonthlyBusinessPlan>
): BaselineInput {
  const aggregated: BaselineInput = {
    global: {
      recruitment: { Consultant: { levels: {} } },
      churn: { Consultant: { levels: {} } }
    },
    source: 'office_plans',
    generated_from: {
      business_plan_ids: Array.from(businessPlans.keys()),
      aggregation_method: 'sum',
      timestamp: new Date()
    }
  };
  
  // Sum all office values by level and month
  businessPlans.forEach((businessPlan, officeId) => {
    Object.entries(businessPlan.months).forEach(([month, monthData]) => {
      Object.entries(monthData).forEach(([role, roleData]) => {
        Object.entries(roleData).forEach(([level, levelData]) => {
          const monthKey = `${businessPlan.year}${month.padStart(2, '0')}`;
          
          // Initialize if not exists
          if (!aggregated.global.recruitment[role].levels[level]) {
            aggregated.global.recruitment[role].levels[level] = {
              recruitment: { values: {} },
              churn: { values: {} }
            };
          }
          
          // Sum values
          const currentRec = aggregated.global.recruitment[role].levels[level].recruitment.values[monthKey] || 0;
          const currentChurn = aggregated.global.recruitment[role].levels[level].churn.values[monthKey] || 0;
          
          aggregated.global.recruitment[role].levels[level].recruitment.values[monthKey] = currentRec + levelData.recruitment;
          aggregated.global.recruitment[role].levels[level].churn.values[monthKey] = currentChurn + levelData.churn;
        });
      });
    });
  });
  
  return aggregated;
}
```

## Scenario Builder Integration

### 1. Enhanced Scenario Creation UI

#### Scenario Builder Flow
```
1. Scenario Basic Info
   ├─ Name, Description, Time Range
   └─ Simulation Type Selection
   
2. Baseline Input Source Selection
   ├─ Global Baseline (existing)
   ├─ Office Business Plans
   └─ Mixed (office plans + global fallback)
   
3. Office Scope Configuration
   ├─ Single Office
   ├─ Selected Offices
   ├─ Journey-Based Selection
   └─ All Offices
   
4. Business Plan Integration
   ├─ Select Business Plans
   ├─ Aggregation Method
   └─ Preview Generated Baseline
   
5. Lever Configuration
   ├─ Apply to All
   ├─ Office-Specific Levers
   └─ Override Business Plans
```

#### Business Plan Source Selection Component
```typescript
interface BusinessPlanSourceSelectorProps {
  onSourceChange: (source: BusinessPlanSource) => void;
  availableBusinessPlans: OfficeBusinessPlan[];
}

const BusinessPlanSourceSelector: React.FC<BusinessPlanSourceSelectorProps> = ({
  onSourceChange, availableBusinessPlans
}) => {
  return (
    <div className="baseline-source-selector">
      <h3>Baseline Input Source</h3>
      
      <RadioGroup>
        <RadioOption value="global_baseline">
          <span>Global Baseline Values</span>
          <small>Use traditional global distribution approach</small>
        </RadioOption>
        
        <RadioOption value="business_plans">
          <span>Office Business Plans</span>
          <small>Use detailed monthly business plans from offices</small>
        </RadioOption>
        
        <RadioOption value="mixed">
          <span>Mixed Approach</span>
          <small>Business plans where available, global baseline as fallback</small>
        </RadioOption>
      </RadioGroup>
      
      {/* Office selection when business_plans or mixed is selected */}
      <OfficeBusinessPlanSelector 
        businessPlans={availableBusinessPlans}
        onSelectionChange={handleBusinessPlanSelection}
      />
    </div>
  );
};
```

### 2. Office Business Plan Selector

#### Multi-Office Selection Interface
```typescript
interface OfficeBusinessPlanSelectorProps {
  businessPlans: OfficeBusinessPlan[];
  onSelectionChange: (selected: string[]) => void;
  selectionMode: 'single' | 'multiple' | 'journey_based';
}

const OfficeBusinessPlanSelector: React.FC<OfficeBusinessPlanSelectorProps> = ({
  businessPlans, onSelectionChange, selectionMode
}) => {
  const businessPlansByJourney = groupBy(businessPlans, 'journey');
  
  return (
    <div className="business-plan-selector">
      <div className="selection-mode">
        <TabGroup>
          <Tab>Single Office</Tab>
          <Tab>Multiple Offices</Tab>
          <Tab>By Journey</Tab>
          <Tab>All Offices</Tab>
        </TabGroup>
      </div>
      
      {selectionMode === 'journey_based' ? (
        <JourneyBasedSelector 
          businessPlans={businessPlansByJourney}
          onJourneyToggle={handleJourneyToggle}
        />
      ) : (
        <IndividualOfficeSelector
          businessPlans={businessPlans}
          onOfficeToggle={handleOfficeToggle}
          multiSelect={selectionMode === 'multiple'}
        />
      )}
      
      <AggregationMethodSelector 
        onMethodChange={handleAggregationMethod}
      />
    </div>
  );
};
```

### 3. Baseline Preview Component

#### Generated Baseline Visualization
```typescript
interface BaselinePreviewProps {
  generatedBaseline: BaselineInput;
  sourceBusinessPlans: OfficeBusinessPlan[];
  aggregationMethod: 'sum' | 'proportional' | 'custom';
}

const BaselinePreview: React.FC<BaselinePreviewProps> = ({
  generatedBaseline, sourceBusinessPlans, aggregationMethod
}) => {
  return (
    <div className="baseline-preview">
      <h4>Generated Baseline Preview</h4>
      
      <div className="preview-summary">
        <div className="summary-card">
          <span>Source Business Plans</span>
          <strong>{sourceBusinessPlans.length} offices</strong>
        </div>
        
        <div className="summary-card">
          <span>Aggregation Method</span>
          <strong>{aggregationMethod}</strong>
        </div>
        
        <div className="summary-card">
          <span>Total Monthly Values</span>
          <BaselineValuesSummary baseline={generatedBaseline} />
        </div>
      </div>
      
      <div className="detailed-preview">
        <BaselineValuesTable 
          baseline={generatedBaseline}
          showByMonth={true}
          showByLevel={true}
        />
      </div>
    </div>
  );
};
```

## API Integration

### 1. Enhanced Scenario APIs

#### New Endpoints
```typescript
// Generate baseline from business plans
POST /api/scenarios/baseline/from-business-plans
{
  business_plan_ids: string[];
  aggregation_method: 'sum' | 'proportional' | 'custom';
  time_range: TimeRange;
}
→ Returns: BaselineInput

// Preview business plan aggregation
POST /api/scenarios/baseline/preview
{
  business_plan_ids: string[];
  aggregation_method: 'sum' | 'proportional' | 'custom';
}
→ Returns: BaselinePreview

// Create scenario from business plans
POST /api/scenarios/from-business-plans
{
  name: string;
  description: string;
  business_plan_ids: string[];
  office_scope: OfficeScope;
  aggregation_method: string;
  levers: Levers;
  time_range: TimeRange;
}
→ Returns: ScenarioCreateResponse

// Get available business plans for scenario
GET /api/scenarios/available-business-plans
→ Returns: OfficeBusinessPlan[]
```

### 2. Business Plan to Scenario Service

#### Service Implementation
```typescript
class BusinessPlanScenarioService {
  
  async generateBaselineFromBusinessPlans(
    businessPlanIds: string[],
    aggregationMethod: 'sum' | 'proportional' | 'custom',
    timeRange: TimeRange
  ): Promise<BaselineInput> {
    // Load business plans
    const businessPlans = await this.loadBusinessPlans(businessPlanIds);
    
    // Transform to baseline format
    const baseline = this.aggregateBusinessPlansToBaseline(
      businessPlans, 
      aggregationMethod
    );
    
    // Apply time range filtering
    return this.filterBaselineByTimeRange(baseline, timeRange);
  }
  
  async createScenarioFromBusinessPlans(
    request: CreateScenarioFromBusinessPlansRequest
  ): Promise<Scenario> {
    // Generate baseline from business plans
    const baseline = await this.generateBaselineFromBusinessPlans(
      request.business_plan_ids,
      request.aggregation_method,
      request.time_range
    );
    
    // Create scenario with generated baseline
    const scenario: Scenario = {
      name: request.name,
      description: request.description,
      time_range: request.time_range,
      office_scope: request.office_scope.offices || [],
      baseline_input: baseline,
      levers: request.levers,
      business_plan_source: {
        type: 'business_plans',
        use_business_plans: true,
        fallback_to_global: false,
        override_with_levers: true
      },
      // Additional metadata
      created_from_business_plans: {
        business_plan_ids: request.business_plan_ids,
        aggregation_method: request.aggregation_method,
        created_at: new Date()
      }
    };
    
    return this.scenarioService.createScenario(scenario);
  }
  
  private aggregateBusinessPlansToBaseline(
    businessPlans: Map<string, MonthlyBusinessPlan>,
    method: 'sum' | 'proportional' | 'custom'
  ): BaselineInput {
    switch (method) {
      case 'sum':
        return this.sumAggregation(businessPlans);
      case 'proportional':
        return this.proportionalAggregation(businessPlans);
      case 'custom':
        return this.customAggregation(businessPlans);
    }
  }
}
```

## Scenario Execution Flow

### 1. Office-Based Scenario Execution

#### Execution Pipeline
```
1. Scenario Loaded
   ├─ Check baseline_input.source
   └─ Determine execution path
   
2. Business Plan Resolution
   ├─ Load referenced business plans
   ├─ Transform to baseline format
   └─ Apply time range filtering
   
3. Office Configuration Assembly
   ├─ Merge business plan baseline
   ├─ Apply economic parameters
   └─ Include initial population data
   
4. Simulation Engine Execution
   ├─ Use office-specific absolute values
   ├─ Skip proportional distribution
   └─ Apply levers if configured
   
5. Results Aggregation
   ├─ Individual office results
   ├─ Aggregated global results
   └─ Comparison metrics
```

### 2. Mixed Baseline Handling

#### Fallback Logic
```typescript
class MixedBaselineResolver {
  
  async resolveBaseline(
    scenario: EnhancedScenario
  ): Promise<ResolvedBaselineInput> {
    const resolved: ResolvedBaselineInput = {
      offices: {},
      global: {},
      resolution_log: []
    };
    
    // For each office in scope
    for (const officeId of scenario.office_scope.offices) {
      
      // Try to use business plan first
      const businessPlan = await this.getBusinessPlanForOffice(officeId);
      
      if (businessPlan && scenario.business_plan_source.use_business_plans) {
        // Use business plan baseline
        resolved.offices[officeId] = this.transformBusinessPlanToBaseline(businessPlan);
        resolved.resolution_log.push({
          office: officeId,
          source: 'business_plan',
          business_plan_id: businessPlan.id
        });
        
      } else if (scenario.business_plan_source.fallback_to_global) {
        // Fallback to global baseline with proportional distribution
        resolved.offices[officeId] = this.distributeGlobalToOffice(
          scenario.baseline_input.global,
          officeId
        );
        resolved.resolution_log.push({
          office: officeId,
          source: 'global_fallback',
          reason: businessPlan ? 'business_plan_disabled' : 'no_business_plan'
        });
        
      } else {
        // No baseline available
        resolved.resolution_log.push({
          office: officeId,
          source: 'none',
          warning: 'No baseline input available for office'
        });
      }
    }
    
    return resolved;
  }
}
```

## UI Integration Points

### 1. Scenario Editor Enhancements

#### Business Plan Integration Tab
```
Scenario Editor
├─ Basic Information
├─ Time Range
├─ Baseline Input Source ← NEW
│  ├─ Global Baseline
│  ├─ Office Business Plans
│  └─ Mixed Approach
├─ Office Scope ← ENHANCED
│  ├─ Single Office
│  ├─ Selected Offices
│  ├─ Journey-Based
│  └─ All Offices
├─ Business Plan Selection ← NEW
│  ├─ Available Plans List
│  ├─ Aggregation Method
│  └─ Preview Generated Baseline
├─ Levers Configuration
└─ Review & Create
```

### 2. Scenario List Enhancements

#### Source Indicators
```typescript
const ScenarioListItem: React.FC<{scenario: EnhancedScenario}> = ({scenario}) => {
  const getSourceBadge = () => {
    switch (scenario.baseline_input.source) {
      case 'office_plans':
        return <Badge color="blue">Office Plans</Badge>;
      case 'global':
        return <Badge color="gray">Global Baseline</Badge>;
      case 'mixed':
        return <Badge color="purple">Mixed</Badge>;
    }
  };
  
  return (
    <div className="scenario-item">
      <div className="scenario-header">
        <h3>{scenario.name}</h3>
        {getSourceBadge()}
      </div>
      
      <div className="scenario-details">
        <span>Offices: {scenario.office_scope.offices?.length || 'All'}</span>
        {scenario.created_from_business_plans && (
          <span>From {scenario.created_from_business_plans.business_plan_ids.length} business plans</span>
        )}
      </div>
    </div>
  );
};
```

## Benefits of Integration

### 1. For Users
- **Seamless Workflow**: Create business plans → Generate scenarios → Run simulations
- **Accurate Modeling**: No more proportional distribution errors
- **Flexible Aggregation**: Compare individual offices or aggregate results
- **Mixed Approaches**: Use business plans where available, fallback to global

### 2. For System
- **Backward Compatibility**: Existing global baseline scenarios continue to work
- **Data Consistency**: Business plans become the single source of truth
- **Scalability**: Easy to add new offices and business plans
- **Auditability**: Clear lineage from business plans to simulation results

## Migration Strategy

### 1. Phase 1: Infrastructure
- Extend scenario model to support business plan sources
- Create transformation services
- Build API endpoints

### 2. Phase 2: UI Integration
- Add business plan source selection to scenario builder
- Create preview and validation components
- Update scenario list to show source types

### 3. Phase 3: Advanced Features
- Mixed baseline resolution
- Custom aggregation methods
- Business plan versioning and comparison

This integration design ensures that office business plans seamlessly work with the existing scenario system while providing the flexibility to use them at individual office or aggregated levels, solving the current distribution accuracy issues.