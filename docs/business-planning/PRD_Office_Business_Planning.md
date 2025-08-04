# PRD: Office-Specific Business Planning & Configuration System

## Executive Summary

Design and implement a comprehensive office-specific configuration and business planning system that allows users to create detailed monthly business plans for each office, configure office-specific parameters, and run simulations at both individual office and aggregated levels.

## Problem Statement

Currently, the simulation system uses global baseline values with proportional distribution, leading to:
- Inaccurate office-specific modeling
- Inability to create realistic office business plans
- Limited control over office-specific parameters
- No support for office journey-based management

## Solution Overview

Create a dedicated office management system with:
- Individual office configuration pages
- Monthly business planning tables
- Office journey-based navigation
- Individual and aggregated simulation capabilities
- CAT progression configuration per office

## Product Requirements

### Core Features

#### 1. Office Management Dashboard
- **Navigation**: Sidebar grouped by office journey (Emerging, Established, Mature)
- **Office List**: All offices with quick status indicators
- **Journey Grouping**: Visual separation of offices by maturity level

#### 2. Office Configuration Page
Each office has a dedicated page with multiple sections:

##### 2.1 Office Information
- Office name and journey status
- Total FTE capacity
- Regional/timezone settings
- Office-specific economic parameters

##### 2.2 Initial Population Configuration
- **Workforce Table**: FTE per level and role at start date
- **All Levels**: A, AC, C, SrC, AM, M, SrM, PiP
- **All Roles**: Consultant, Sales, Operations
- **Editable Fields**: Current FTE count per level/role
- **Validation**: Total FTE consistency checks

##### 2.3 Monthly Business Plan Table
Interactive table with 12 months × all levels/roles:

**Editable Fields per Cell**:
- Recruitment (absolute numbers)
- Churn (absolute numbers)  
- Price (hourly rate)
- UTR (utilization rate 0-1)
- Salary (monthly)

**Table Structure**:
```
| Level/Role | Jan | Feb | Mar | ... | Dec |
|------------|-----|-----|-----|-----|-----|
| Consultant-A | [5 fields] | [5 fields] | ... |
| Consultant-AC | [5 fields] | [5 fields] | ... |
| Sales-A | [5 fields] | [5 fields] | ... |
```

##### 2.4 CAT Progression Configuration
- **Progression Rules**: Monthly progression rates per level
- **Custom Curves**: Office-specific progression curves
- **Timeline**: Progression schedule and milestones

#### 3. Simulation Capabilities
- **Individual Office**: Run simulation for single office
- **Aggregated**: Run simulation across selected offices
- **Comparison**: Compare office performance
- **What-if Analysis**: Test different business plan scenarios

#### 4. Business Plan Templates
- **Journey Templates**: Pre-configured plans by office journey
- **Copy Plans**: Duplicate plans between offices
- **Plan Validation**: Consistency and feasibility checks

## Technical Architecture

### Backend Design

#### 3.1 Data Models

```typescript
// Office Configuration
interface OfficeConfig {
  id: string;
  name: string;
  journey: 'emerging' | 'established' | 'mature';
  timezone: string;
  economicParameters: {
    costOfLiving: number;
    marketMultiplier: number;
    taxRate: number;
  };
  initialPopulation: WorkforceDistribution;
  businessPlan: MonthlyBusinessPlan;
  catProgression: ProgressionConfig;
  createdAt: Date;
  updatedAt: Date;
}

// Workforce Distribution
interface WorkforceDistribution {
  startDate: Date;
  distribution: {
    [role: string]: {
      [level: string]: {
        fte: number;
        notes?: string;
      }
    }
  }
}

// Monthly Business Plan
interface MonthlyBusinessPlan {
  year: number;
  months: {
    [month: string]: {
      [role: string]: {
        [level: string]: {
          recruitment: number;
          churn: number;
          price: number;
          utr: number;
          salary: number;
        }
      }
    }
  }
}

// CAT Progression Config
interface ProgressionConfig {
  curves: {
    [level: string]: {
      monthlyRate: number;
      curve: 'linear' | 'exponential' | 'custom';
      customPoints?: Array<{month: number, rate: number}>;
    }
  };
  milestones: Array<{
    month: number;
    description: string;
    impact: string;
  }>;
}
```

#### 3.2 API Endpoints

```typescript
// Office Management
GET    /api/offices                          // List all offices
GET    /api/offices/{id}                     // Get office details
POST   /api/offices                          // Create new office
PUT    /api/offices/{id}                     // Update office
DELETE /api/offices/{id}                     // Delete office

// Business Plans
GET    /api/offices/{id}/business-plan       // Get business plan
PUT    /api/offices/{id}/business-plan       // Update business plan
POST   /api/offices/{id}/business-plan/copy  // Copy from template
POST   /api/offices/{id}/business-plan/validate // Validate plan

// Initial Population
GET    /api/offices/{id}/population          // Get workforce distribution
PUT    /api/offices/{id}/population          // Update workforce

// CAT Progression
GET    /api/offices/{id}/progression         // Get progression config
PUT    /api/offices/{id}/progression         // Update progression

// Simulation
POST   /api/simulation/office/{id}           // Run single office simulation
POST   /api/simulation/aggregated            // Run multi-office simulation
GET    /api/simulation/results/{id}          // Get simulation results

// Templates
GET    /api/templates/business-plans         // List plan templates
GET    /api/templates/business-plans/{journey} // Get templates by journey
```

#### 3.3 Database Schema

```sql
-- Offices table
CREATE TABLE offices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL UNIQUE,
  journey office_journey_enum NOT NULL,
  timezone VARCHAR(50) DEFAULT 'UTC',
  economic_parameters JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Office workforce distributions
CREATE TABLE office_workforce (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  office_id UUID REFERENCES offices(id) ON DELETE CASCADE,
  start_date DATE NOT NULL,
  role VARCHAR(50) NOT NULL,
  level VARCHAR(10) NOT NULL,
  fte INTEGER NOT NULL DEFAULT 0,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(office_id, start_date, role, level)
);

-- Office business plans
CREATE TABLE office_business_plans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  office_id UUID REFERENCES offices(id) ON DELETE CASCADE,
  year INTEGER NOT NULL,
  month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
  role VARCHAR(50) NOT NULL,
  level VARCHAR(10) NOT NULL,
  recruitment INTEGER DEFAULT 0,
  churn INTEGER DEFAULT 0,
  price DECIMAL(10,2),
  utr DECIMAL(3,2) CHECK (utr BETWEEN 0 AND 1),
  salary DECIMAL(10,2),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(office_id, year, month, role, level)
);

-- CAT progression configurations
CREATE TABLE office_progressions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  office_id UUID REFERENCES offices(id) ON DELETE CASCADE,
  level VARCHAR(10) NOT NULL,
  monthly_rate DECIMAL(5,4),
  curve_type progression_curve_enum DEFAULT 'linear',
  custom_points JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(office_id, level)
);
```

### Frontend Design

#### 4.1 Component Architecture

```typescript
// Main Office Management Components
<OfficeManagement>
  <OfficeSidebar>
    <JourneyGroup journey="emerging">
      <OfficeNavItem />
    </JourneyGroup>
  </OfficeSidebar>
  
  <OfficeContent>
    <OfficeConfigPage>
      <OfficeInfoSection />
      <InitialPopulationTable />
      <BusinessPlanTable />
      <CATProgressionConfig />
      <SimulationControls />
    </OfficeConfigPage>
  </OfficeContent>
</OfficeManagement>

// Business Plan Table Component
<BusinessPlanTable>
  <TableHeader months={12} />
  <TableBody>
    {roles.map(role => 
      levels.map(level => 
        <BusinessPlanRow 
          role={role} 
          level={level}
          months={months}
          onCellChange={handleCellChange}
        />
      )
    )}
  </TableBody>
</BusinessPlanTable>

// Editable Cell Component
<EditableCell 
  fields={['recruitment', 'churn', 'price', 'utr', 'salary']}
  values={cellValues}
  validation={cellValidation}
  onChange={onFieldChange}
/>
```

#### 4.2 State Management

```typescript
// Office Store (Zustand)
interface OfficeStore {
  // State
  offices: Office[];
  currentOffice: Office | null;
  businessPlan: MonthlyBusinessPlan | null;
  
  // Actions
  loadOffices: () => Promise<void>;
  selectOffice: (id: string) => Promise<void>;
  updateBusinessPlan: (plan: MonthlyBusinessPlan) => Promise<void>;
  runSimulation: (officeIds: string[]) => Promise<SimulationResult>;
  
  // Computed
  officesByJourney: () => Record<string, Office[]>;
  currentPlanValidation: () => ValidationResult;
}

// Business Plan Store
interface BusinessPlanStore {
  plan: MonthlyBusinessPlan;
  editingCell: CellAddress | null;
  validationErrors: ValidationError[];
  
  updateCell: (address: CellAddress, field: string, value: any) => void;
  validatePlan: () => ValidationResult;
  copyFromTemplate: (template: BusinessPlanTemplate) => void;
}
```

#### 4.3 UI Components

##### OfficeSidebar Component
```tsx
interface OfficeSidebarProps {
  offices: Office[];
  currentOfficeId?: string;
  onOfficeSelect: (id: string) => void;
}

const OfficeSidebar: React.FC<OfficeSidebarProps> = ({
  offices, currentOfficeId, onOfficeSelect 
}) => {
  const officesByJourney = groupBy(offices, 'journey');
  
  return (
    <div className="office-sidebar">
      {Object.entries(officesByJourney).map(([journey, offices]) => (
        <JourneyGroup 
          key={journey}
          journey={journey}
          offices={offices}
          currentOfficeId={currentOfficeId}
          onOfficeSelect={onOfficeSelect}
        />
      ))}
    </div>
  );
};
```

##### BusinessPlanTable Component
```tsx
interface BusinessPlanTableProps {
  plan: MonthlyBusinessPlan;
  onCellChange: (address: CellAddress, field: string, value: any) => void;
  validation: ValidationResult;
}

const BusinessPlanTable: React.FC<BusinessPlanTableProps> = ({
  plan, onCellChange, validation
}) => {
  const roles = ['Consultant', 'Sales', 'Operations'];
  const levels = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'];
  const months = Array.from({length: 12}, (_, i) => i + 1);
  
  return (
    <div className="business-plan-table">
      <table>
        <thead>
          <tr>
            <th>Role/Level</th>
            {months.map(month => (
              <th key={month}>
                {new Date(2024, month - 1).toLocaleString('default', {month: 'short'})}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {roles.map(role => 
            levels.map(level => (
              <BusinessPlanRow
                key={`${role}-${level}`}
                role={role}
                level={level}
                months={months}
                plan={plan}
                onCellChange={onCellChange}
                validation={validation}
              />
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};
```

##### EditableCell Component
```tsx
interface EditableCellProps {
  address: CellAddress;
  field: 'recruitment' | 'churn' | 'price' | 'utr' | 'salary';
  value: number;
  validation: FieldValidation;
  onChange: (address: CellAddress, field: string, value: number) => void;
}

const EditableCell: React.FC<EditableCellProps> = ({
  address, field, value, validation, onChange
}) => {
  const [editing, setEditing] = useState(false);
  const [tempValue, setTempValue] = useState(value);
  
  const handleSubmit = () => {
    if (validation.isValid(tempValue)) {
      onChange(address, field, tempValue);
      setEditing(false);
    }
  };
  
  return (
    <div className={`editable-cell ${validation.hasError ? 'error' : ''}`}>
      {editing ? (
        <input
          type="number"
          value={tempValue}
          onChange={(e) => setTempValue(Number(e.target.value))}
          onBlur={handleSubmit}
          onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
          autoFocus
        />
      ) : (
        <span onClick={() => setEditing(true)}>
          {formatValue(value, field)}
        </span>
      )}
    </div>
  );
};
```

## Implementation Plan

### Phase 1: Backend Foundation (2-3 weeks)

#### Week 1: Data Models & Database
- [ ] Create database schema for offices, business plans, workforce
- [ ] Implement Office, BusinessPlan, WorkforceDistribution models
- [ ] Set up migration scripts
- [ ] Create seed data for office journeys

#### Week 2: Core APIs
- [ ] Implement office CRUD endpoints
- [ ] Create business plan management APIs
- [ ] Build workforce distribution endpoints
- [ ] Add validation layer for business plans

#### Week 3: Simulation Integration
- [ ] Modify simulation engine to accept office-specific inputs
- [ ] Create office-specific simulation endpoints
- [ ] Implement aggregated simulation logic
- [ ] Add simulation result comparison APIs

### Phase 2: Frontend Foundation (2-3 weeks)

#### Week 4: Component Architecture
- [ ] Create OfficeManagement layout component
- [ ] Build OfficeSidebar with journey grouping
- [ ] Implement office navigation and routing
- [ ] Set up state management with Zustand

#### Week 5: Business Plan Interface
- [ ] Build BusinessPlanTable component
- [ ] Create EditableCell with validation
- [ ] Implement cell editing interactions
- [ ] Add plan validation and error display

#### Week 6: Office Configuration
- [ ] Create InitialPopulationTable component
- [ ] Build CATProgressionConfig interface
- [ ] Add simulation controls and result display
- [ ] Implement plan templates and copying

### Phase 3: Advanced Features (1-2 weeks)

#### Week 7: Enhanced UX
- [ ] Add bulk editing capabilities
- [ ] Implement plan comparison views
- [ ] Create what-if scenario analysis
- [ ] Add export/import functionality

#### Week 8: Polish & Testing
- [ ] Comprehensive testing suite
- [ ] Performance optimization
- [ ] Documentation and user guides
- [ ] Deployment and monitoring

## Success Metrics

### Functional Requirements
- [ ] Users can create and edit office-specific business plans
- [ ] Monthly values for all parameters are editable per level/role
- [ ] Office navigation works with journey grouping
- [ ] Simulations run correctly for individual and aggregated offices
- [ ] CAT progression is configurable per office

### Technical Requirements
- [ ] API response times < 200ms for office operations
- [ ] Business plan table handles 12 months × 24 level/role combinations
- [ ] Real-time validation with < 100ms feedback
- [ ] Data consistency across office configurations
- [ ] Responsive design works on tablets and desktops

### User Experience
- [ ] Intuitive navigation between offices
- [ ] Efficient bulk editing capabilities
- [ ] Clear validation feedback
- [ ] Fast simulation execution
- [ ] Reliable data persistence

## Risk Mitigation

### Technical Risks
- **Complex Table Performance**: Implement virtualization for large tables
- **Data Consistency**: Use database transactions and validation
- **Simulation Complexity**: Gradual migration from global to office-specific

### UX Risks
- **Overwhelming Interface**: Progressive disclosure and smart defaults
- **Data Entry Fatigue**: Templates, bulk operations, and copy functionality
- **Validation Complexity**: Clear, contextual error messages

## Future Enhancements

- Multi-year business planning
- Advanced analytics and forecasting
- Office performance benchmarking
- Automated plan optimization
- Integration with external business systems
- Mobile application for office managers

---

*This PRD provides the foundation for implementing a comprehensive office-specific business planning system that addresses the current limitations in simulation accuracy and office management capabilities.*