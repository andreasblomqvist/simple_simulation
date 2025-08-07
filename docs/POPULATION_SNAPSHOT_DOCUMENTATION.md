# SimpleSim Population Snapshot System Documentation

## Overview & Architecture

### What are Population Snapshots?

Population snapshots are point-in-time captures of office workforce data that serve as baselines for scenario planning and historical analysis in SimpleSim. They provide a complete picture of workforce composition including headcount, FTE (Full-Time Equivalent) distribution across roles and levels, and associated metadata.

**Key Benefits:**
- **Historical Analysis**: Track workforce changes over time
- **Scenario Planning**: Use snapshots as baselines for simulations
- **Comparison & Benchmarking**: Compare different time periods or office states
- **Data Governance**: Create approved baselines for official planning
- **Audit Trail**: Maintain comprehensive history of workforce decisions

### System Architecture

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Frontend (React)  │    │  Backend (FastAPI)   │    │  Database (Postgres)│
│                     │    │                      │    │                     │
│ ┌─────────────────┐ │    │ ┌──────────────────┐ │    │ ┌─────────────────┐ │
│ │SnapshotManager  │◄┼────┼►│  Snapshot API    │◄┼────┼►│ Snapshot Tables │ │
│ │SnapshotSelector │ │    │ │  Endpoints       │ │    │ │ & Views         │ │
│ │CreateModal      │ │    │ └──────────────────┘ │    │ └─────────────────┘ │
│ │SnapshotComparison│ │    │                     │    │                     │
│ └─────────────────┘ │    │ ┌──────────────────┐ │    │ ┌─────────────────┐ │
│                     │    │ │ Snapshot Service │ │    │ │ Audit & Triggers│ │
│ ┌─────────────────┐ │    │ │ Business Logic   │ │    │ │                 │ │
│ │ Zustand Store   │ │    │ └──────────────────┘ │    │ └─────────────────┘ │
│ │ State Mgmt      │ │    │                     │    │                     │
│ └─────────────────┘ │    │ ┌──────────────────┐ │    │                     │
└─────────────────────┘    │ │ Repository Layer │ │    │                     │
                           │ │ Data Access      │ │    │                     │
                           │ └──────────────────┘ │    │                     │
                           └──────────────────────┘    └─────────────────────┘
```

### Data Flow

1. **Snapshot Creation**: Current office workforce → Snapshot creation → Database storage
2. **Retrieval**: Frontend requests → API layer → Service layer → Repository → Database
3. **Comparison**: Multiple snapshots → Comparison engine → Calculated deltas → Frontend display
4. **Integration**: Snapshots used in scenarios/business plans → Audit logging → Usage tracking

### Integration Points

- **Office Management**: Creates snapshots from current workforce data
- **Scenario Planning**: Uses snapshots as baseline inputs for simulations
- **Business Planning**: References snapshots in planning workflows
- **Reporting**: Historical trend analysis and workforce analytics

## Database Schema

### Core Tables

#### `population_snapshots`
Primary snapshot metadata and summary information.

```sql
CREATE TABLE population_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    office_id UUID NOT NULL REFERENCES offices(id) ON DELETE CASCADE,
    snapshot_date VARCHAR(6) NOT NULL, -- YYYYMM format
    snapshot_name VARCHAR(200) NOT NULL,
    description TEXT,
    total_fte INTEGER NOT NULL CHECK (total_fte >= 0),
    is_default BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT FALSE,
    source VARCHAR(50) NOT NULL CHECK (source IN ('manual', 'simulation', 'import', 'business_plan', 'current')),
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100) NOT NULL,
    last_used_at TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    UNIQUE(office_id, snapshot_name)
);
```

#### `snapshot_workforce`
Detailed workforce composition data.

```sql
CREATE TABLE snapshot_workforce (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_id UUID NOT NULL REFERENCES population_snapshots(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    level VARCHAR(20), -- NULL for flat roles like Operations
    fte INTEGER NOT NULL CHECK (fte >= 0),
    UNIQUE(snapshot_id, role, level)
);
```

#### `snapshot_tags`
Flexible tagging system for categorization and filtering.

```sql
CREATE TABLE snapshot_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_id UUID NOT NULL REFERENCES population_snapshots(id) ON DELETE CASCADE,
    tag VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(snapshot_id, tag)
);
```

#### `snapshot_comparisons`
Stored comparison results between snapshots.

```sql
CREATE TABLE snapshot_comparisons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_1_id UUID NOT NULL REFERENCES population_snapshots(id) ON DELETE CASCADE,
    snapshot_2_id UUID NOT NULL REFERENCES population_snapshots(id) ON DELETE CASCADE,
    comparison_date TIMESTAMP DEFAULT NOW(),
    compared_by VARCHAR(100),
    delta_data JSONB NOT NULL,
    insights TEXT,
    CHECK (snapshot_1_id != snapshot_2_id)
);
```

#### `snapshot_audit_log`
Complete audit trail of snapshot usage and modifications.

```sql
CREATE TABLE snapshot_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_id UUID NOT NULL REFERENCES population_snapshots(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL CHECK (action IN (
        'created', 'modified', 'approved', 'set_default',
        'used_in_scenario', 'used_in_plan', 'used_in_simulation'
    )),
    entity_type VARCHAR(50), -- 'scenario', 'business_plan', 'simulation'
    entity_id UUID,
    user_id VARCHAR(100),
    timestamp TIMESTAMP DEFAULT NOW(),
    details JSONB DEFAULT '{}'
);
```

### Performance Indexes

```sql
-- Core query optimization
CREATE INDEX idx_snapshots_office_date ON population_snapshots(office_id, snapshot_date DESC);
CREATE INDEX idx_snapshots_office_default ON population_snapshots(office_id, is_default) WHERE is_default = TRUE;
CREATE INDEX idx_snapshots_approved ON population_snapshots(office_id, is_approved) WHERE is_approved = TRUE;

-- Workforce data access
CREATE INDEX idx_snapshot_workforce_snapshot ON snapshot_workforce(snapshot_id);
CREATE INDEX idx_snapshot_workforce_role ON snapshot_workforce(role, level);

-- Tagging and search
CREATE INDEX idx_snapshot_tags_snapshot ON snapshot_tags(snapshot_id);
CREATE INDEX idx_snapshot_tags_tag ON snapshot_tags(tag);

-- Audit and tracking
CREATE INDEX idx_audit_snapshot ON snapshot_audit_log(snapshot_id, timestamp DESC);
CREATE INDEX idx_audit_action ON snapshot_audit_log(action, timestamp DESC);
```

### Database Triggers

#### Single Default Enforcement
```sql
CREATE OR REPLACE FUNCTION ensure_single_default_snapshot()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_default = TRUE THEN
        UPDATE population_snapshots 
        SET is_default = FALSE 
        WHERE office_id = NEW.office_id 
        AND id != NEW.id 
        AND is_default = TRUE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

#### Usage Logging
Automatically logs snapshot usage when `last_used_at` is updated.

### Views and Helper Functions

#### `v_snapshot_summary`
Comprehensive snapshot overview with aggregated metadata.

```sql
CREATE OR REPLACE VIEW v_snapshot_summary AS
SELECT 
    ps.id, ps.office_id, o.name as office_name,
    ps.snapshot_date, ps.snapshot_name, ps.description,
    ps.total_fte, ps.is_default, ps.is_approved, ps.source,
    ps.created_at, ps.created_by, ps.last_used_at,
    array_agg(DISTINCT st.tag) FILTER (WHERE st.tag IS NOT NULL) as tags,
    COUNT(DISTINCT sw.id) as workforce_entries
FROM population_snapshots ps
JOIN offices o ON ps.office_id = o.id
LEFT JOIN snapshot_tags st ON ps.id = st.snapshot_id
LEFT JOIN snapshot_workforce sw ON ps.id = sw.snapshot_id
GROUP BY ps.id, o.id, o.name;
```

### Migration Strategy

Snapshots integrate with existing schema through:
- Foreign key to `offices` table
- Optional foreign keys from `scenarios` and `office_business_plans`
- Non-breaking additions to existing workflows

## Backend API Reference

### Authentication & Permissions

All endpoints require valid user context. No role-based restrictions currently implemented.

### Base URL
`/api/snapshots`

### Endpoints

#### Create Snapshot from Current Office Data
```http
POST /snapshots/
Content-Type: application/json

{
  "office_id": "uuid",
  "snapshot_name": "string",
  "description": "string?",
  "tags": ["string"]?,
  "is_default": boolean?,
  "created_by": "string"
}
```

**Response**: `SnapshotResponse`

#### Create Snapshot from Simulation Results
```http
POST /snapshots/from-simulation
Content-Type: application/json

{
  "office_name": "string",
  "simulation_results": object,
  "snapshot_date": "YYYYMM",
  "snapshot_name": "string",
  "description": "string?",
  "tags": ["string"]?,
  "created_by": "string"
}
```

#### Create Snapshot from Business Plan
```http
POST /snapshots/from-business-plan
Content-Type: application/json

{
  "office_id": "uuid",
  "business_plan_data": object,
  "snapshot_name": "string",
  "snapshot_date": "YYYYMM",
  "description": "string?",
  "tags": ["string"]?,
  "created_by": "string"
}
```

#### Get Snapshot by ID
```http
GET /snapshots/{snapshot_id}
```

**Response**: `SnapshotResponse`

#### Search Snapshots
```http
GET /snapshots/
?office_id=uuid
&tags=tag1,tag2
&source=manual|simulation|import|business_plan|current
&date_from=YYYYMM
&date_to=YYYYMM
&search_term=string
&approved_only=boolean
&page=integer
&limit=integer
```

**Response**: `SnapshotListResponse`

#### Get Office Snapshots
```http
GET /snapshots/office/{office_id}
?approved_only=boolean
&limit=integer
&offset=integer
```

**Response**: `List[SnapshotResponse]`

#### Get Default Snapshot
```http
GET /snapshots/office/{office_id}/default
```

**Response**: `SnapshotResponse?`

#### Update Snapshot
```http
PUT /snapshots/{snapshot_id}
Content-Type: application/json

{
  "snapshot_name": "string?",
  "description": "string?",
  "is_approved": boolean?,
  "updated_by": "string?"
}
```

#### Set Default Snapshot
```http
POST /snapshots/{snapshot_id}/set-default
?user_id=string
```

#### Approve Snapshot
```http
POST /snapshots/{snapshot_id}/approve
?user_id=string
```

#### Delete Snapshot
```http
DELETE /snapshots/{snapshot_id}
```

#### Update Workforce Data
```http
PUT /snapshots/{snapshot_id}/workforce
Content-Type: application/json

{
  "workforce_data": object
}
```

#### Update Tags
```http
PUT /snapshots/{snapshot_id}/tags
Content-Type: application/json

{
  "tags": ["string"]
}
```

#### Compare Snapshots
```http
POST /snapshots/{snapshot_1_id}/compare/{snapshot_2_id}
?user_id=string
```

**Response**: `ComparisonResponse`

#### Get Audit Log
```http
GET /snapshots/{snapshot_id}/audit-log
?limit=integer
```

**Response**: `List[AuditLogEntry]`

#### Record Usage in Scenario
```http
POST /snapshots/{snapshot_id}/use-in-scenario/{scenario_id}
?user_id=string
```

#### Record Usage in Business Plan
```http
POST /snapshots/{snapshot_id}/use-in-business-plan/{business_plan_id}
?user_id=string
```

### Response Models

#### SnapshotResponse
```typescript
{
  id: string;
  office_id: string;
  office_name?: string;
  snapshot_date: string;
  snapshot_name: string;
  description?: string;
  total_fte: number;
  is_default: boolean;
  is_approved: boolean;
  source: string;
  created_at: string;
  created_by: string;
  last_used_at?: string;
  tags: string[];
  workforce_data: object;
  metadata: object;
}
```

#### ComparisonResponse
```typescript
{
  snapshot_1: SnapshotResponse;
  snapshot_2: SnapshotResponse;
  total_fte_delta: number;
  workforce_changes: object;
  insights: string[];
}
```

### Error Codes

- `400` - Bad Request (validation errors)
- `404` - Snapshot/Office not found
- `409` - Conflict (duplicate names, constraint violations)
- `500` - Internal server error

## Frontend Component Guide

### Component Hierarchy

```
SnapshotManager (Main Interface)
├── SnapshotSelector (Dropdown Selection)
├── CreateSnapshotModal (Creation Form)
├── SnapshotComparison (Side-by-side Analysis)
├── SnapshotWorkforceTable (Data Display)
└── DataTableMinimal (List Display)
```

### Core Components

#### SnapshotManager
**Purpose**: Complete snapshot management interface with filtering, sorting, and actions.

**Key Features**:
- List view with search and tag filtering
- Sortable columns (name, date, FTE, created_at)
- Bulk operations and comparison mode
- Create, edit, delete, export functionality
- Real-time updates with Zustand store

**Usage**:
```tsx
<SnapshotManager
  officeId={office.id}
  onSnapshotCreated={(snapshot) => console.log('Created:', snapshot)}
  onSnapshotDeleted={(id) => console.log('Deleted:', id)}
/>
```

#### SnapshotSelector
**Purpose**: Dropdown component for selecting between current data and historical snapshots.

**Key Features**:
- Shows "Current Workforce" option
- Lists available snapshots with metadata
- Auto-refresh and loading states
- Selected snapshot details display

**Usage**:
```tsx
<SnapshotSelector
  officeId={office.id}
  selectedSnapshot={selectedSnapshot}
  onSnapshotSelect={setSelectedSnapshot}
  showCurrentOption={true}
/>
```

#### CreateSnapshotModal
**Purpose**: Modal form for creating new population snapshots.

**Key Features**:
- Form validation and error handling
- Tag management with autocomplete
- Preview of current workforce data
- Success/error feedback

**Usage**:
```tsx
<CreateSnapshotModal
  isOpen={showModal}
  onClose={() => setShowModal(false)}
  onSnapshotCreated={handleSnapshotCreated}
  officeId={office.id}
/>
```

#### SnapshotComparison
**Purpose**: Side-by-side comparison of two snapshots with change analysis.

**Key Features**:
- Baseline vs comparison layout
- Change indicators (additions, reductions, modifications)
- Summary metrics and detailed workforce table
- Export comparison results

**Usage**:
```tsx
<SnapshotComparison
  baseline={baselineSnapshot}
  comparison={comparisonSnapshot}
  onClose={() => setViewMode('list')}
/>
```

#### SnapshotWorkforceTable
**Purpose**: Tabular display of snapshot workforce data with role/level breakdown.

**Key Features**:
- Role and level hierarchy display
- Optional salary information
- Summary totals and percentages
- Responsive design with mobile optimization

**Usage**:
```tsx
<SnapshotWorkforceTable
  workforce={snapshot.workforce}
  showSalary={true}
  showNotes={false}
/>
```

### State Management Patterns

#### Zustand Store Architecture
```typescript
interface SnapshotStore {
  // State
  snapshots: Record<string, PopulationSnapshot[]>; // By office ID
  loading: boolean;
  error: string | null;
  
  // Actions
  loadSnapshotsByOffice: (officeId: string) => Promise<void>;
  createSnapshot: (request: CreateSnapshotRequest) => Promise<PopulationSnapshot>;
  deleteSnapshot: (snapshotId: string) => Promise<void>;
  compareSnapshots: (baseline: PopulationSnapshot, comparison: PopulationSnapshot) => Promise<ComparisonResult>;
  
  // Selectors
  getOfficeSnapshots: (officeId: string) => PopulationSnapshot[];
  getSnapshotById: (snapshotId: string) => PopulationSnapshot | undefined;
}
```

#### Optimistic Updates
Store updates UI immediately while syncing with backend:
```typescript
const createSnapshot = async (request: CreateSnapshotRequest) => {
  // Optimistically add to UI
  const tempSnapshot = generateTempSnapshot(request);
  addSnapshotToStore(tempSnapshot);
  
  try {
    // Sync with backend
    const savedSnapshot = await snapshotApi.create(request);
    replaceSnapshotInStore(tempSnapshot.id, savedSnapshot);
    return savedSnapshot;
  } catch (error) {
    // Rollback on error
    removeSnapshotFromStore(tempSnapshot.id);
    throw error;
  }
};
```

### UI/UX Workflows

#### Snapshot Creation Workflow
1. **Trigger**: User clicks "Create Snapshot" button
2. **Modal**: CreateSnapshotModal opens with form
3. **Preview**: Shows current workforce data to be captured
4. **Validation**: Form validates name uniqueness and required fields
5. **Creation**: API call creates snapshot from current office data
6. **Feedback**: Success message and list refresh

#### Comparison Workflow
1. **Selection**: User selects "Add to Comparison" for first snapshot
2. **Indicator**: Visual indicator shows snapshot in comparison mode
3. **Second Selection**: User selects second snapshot for comparison
4. **Analysis**: Comparison view opens with side-by-side display
5. **Navigation**: Can return to list or start new comparison

#### Integration with Office Management
```tsx
// Office view integration
const OfficeWorkforceTab = ({ office }) => {
  const [selectedSnapshot, setSelectedSnapshot] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  
  const workforceData = selectedSnapshot 
    ? selectedSnapshot.workforce 
    : getCurrentOfficeWorkforce(office.id);
  
  return (
    <div>
      <div className="flex justify-between items-center">
        <SnapshotSelector
          officeId={office.id}
          selectedSnapshot={selectedSnapshot}
          onSnapshotSelect={setSelectedSnapshot}
        />
        <Button onClick={() => setShowCreateModal(true)}>
          Save Current as Snapshot
        </Button>
      </div>
      
      <WorkforceTable workforce={workforceData} />
      
      <CreateSnapshotModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        officeId={office.id}
      />
    </div>
  );
};
```

## Development Guide

### Setup and Installation

#### Prerequisites
- Node.js 18+ and npm
- Python 3.9+ and pip
- PostgreSQL 14+
- Git

#### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Unix/macOS
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set up database (ensure PostgreSQL is running)
# Create database: createdb simplesim_dev

# Run migrations
python -c "from src.database.connection import ensure_database_setup; ensure_database_setup()"

# Start development server
uvicorn main:app --reload --port 8000
```

#### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### Environment Variables
Create `.env` files:

**Backend (.env)**:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/simplesim_dev
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Frontend (.env.local)**:
```bash
VITE_API_BASE_URL=http://localhost:8000
```

### Running Migrations

#### Create New Migration
```bash
# Backend directory
cd backend/migrations

# Create SQL files
touch 003_new_feature.sql
touch 003_rollback_new_feature.sql
```

#### Migration Structure
```sql
-- 003_new_feature.sql
-- Migration: Description of changes
-- Version: 003

-- Add your changes here
ALTER TABLE population_snapshots ADD COLUMN new_field VARCHAR(50);

-- Create index if needed
CREATE INDEX idx_new_field ON population_snapshots(new_field);
```

```sql
-- 003_rollback_new_feature.sql
-- Rollback for migration 003

DROP INDEX IF EXISTS idx_new_field;
ALTER TABLE population_snapshots DROP COLUMN IF EXISTS new_field;
```

#### Apply Migration
```bash
# From project root
python -c "
from backend.src.database.connection import get_connection
from backend.src.database.migrations import apply_migration
apply_migration('003_new_feature.sql')
"
```

### Testing Strategy

#### Backend Testing
```bash
# Unit tests
pytest backend/tests/unit/ -v

# Integration tests
pytest backend/tests/integration/ -v

# Specific test module
pytest backend/tests/unit/test_snapshot_service.py -v

# Database tests
pytest backend/tests/database/ -v
```

#### Frontend Testing
```bash
# Unit and component tests
npm test

# E2E tests (requires servers running)
npm run test:e2e

# Specific test file
npm test -- --testPathPattern=snapshot

# Watch mode
npm test -- --watch
```

#### Test Database Setup
Create separate test database:
```bash
createdb simplesim_test

# Set test environment
export DATABASE_URL=postgresql://user:password@localhost:5432/simplesim_test
export NODE_ENV=test
```

### Common Development Tasks

#### Add New Snapshot Source Type
1. **Update Enum** in `backend/src/database/models.py`:
```python
class SnapshotSource(str, Enum):
    MANUAL = "manual"
    SIMULATION = "simulation"
    IMPORT = "import"
    BUSINESS_PLAN = "business_plan"
    CURRENT = "current"
    NEW_SOURCE = "new_source"  # Add new source
```

2. **Update Database Constraint**:
```sql
ALTER TABLE population_snapshots 
DROP CONSTRAINT population_snapshots_source_check;

ALTER TABLE population_snapshots 
ADD CONSTRAINT population_snapshots_source_check 
CHECK (source IN ('manual', 'simulation', 'import', 'business_plan', 'current', 'new_source'));
```

3. **Update Frontend Types** in `frontend/src/types/snapshots.ts`:
```typescript
export type SnapshotSource = 
  | 'manual' 
  | 'simulation' 
  | 'import' 
  | 'business_plan' 
  | 'current'
  | 'new_source';
```

4. **Add Service Method**:
```python
async def create_snapshot_from_new_source(
    self,
    office_id: UUID,
    source_data: Dict[str, Any],
    snapshot_name: str,
    created_by: str
) -> PopulationSnapshot:
    # Implementation
    pass
```

5. **Add API Endpoint**:
```python
@router.post("/from-new-source", response_model=SnapshotResponse)
async def create_snapshot_from_new_source(
    request: CreateFromNewSourceRequest,
    service: SnapshotService = Depends(get_snapshot_service_dep)
):
    # Implementation
    pass
```

#### Add Custom Validation Rule
1. **Create Validation Function**:
```python
def validate_minimum_workforce(snapshot: PopulationSnapshot) -> List[str]:
    """Ensure minimum workforce requirements are met."""
    errors = []
    if snapshot.metadata.total_fte < 5:
        errors.append("Office must have minimum 5 FTE")
    return errors
```

2. **Register in Service**:
```python
class SnapshotService:
    def __init__(self):
        self.validation_rules = [
            validate_minimum_workforce,
            validate_role_distribution,
            # Add custom validation
        ]
```

#### Extend Comparison Analysis
1. **Add Comparison Metric**:
```python
def calculate_role_diversity_change(
    baseline: PopulationSnapshot, 
    comparison: PopulationSnapshot
) -> Dict[str, Any]:
    """Calculate change in role diversity."""
    baseline_roles = len(baseline.get_roles())
    comparison_roles = len(comparison.get_roles())
    
    return {
        "diversity_change": comparison_roles - baseline_roles,
        "diversity_percentage": (comparison_roles / baseline_roles - 1) * 100 if baseline_roles > 0 else 0
    }
```

2. **Update Comparison Service**:
```python
async def compare_snapshots(self, snapshot_1_id: UUID, snapshot_2_id: UUID) -> ComparisonResult:
    # Existing comparison logic
    
    # Add custom analysis
    diversity_change = calculate_role_diversity_change(snapshot_1, snapshot_2)
    comparison_result.insights.append(f"Role diversity changed by {diversity_change['diversity_percentage']:.1f}%")
    
    return comparison_result
```

### Development Best Practices

#### Code Style
- **Backend**: Follow PEP 8, use `black` formatter
- **Frontend**: Follow TypeScript strict mode, use `prettier`
- **Database**: Use snake_case for tables/columns, PascalCase for types

#### Error Handling
```python
# Backend service layer
try:
    snapshot = await self.repository.create(snapshot_data)
    return snapshot
except IntegrityError as e:
    if "unique constraint" in str(e).lower():
        raise ValueError(f"Snapshot with name '{snapshot_data.name}' already exists")
    raise ServiceError("Failed to create snapshot") from e
except Exception as e:
    logger.error(f"Unexpected error creating snapshot: {e}")
    raise ServiceError("Internal error") from e
```

```typescript
// Frontend error handling
const handleCreateSnapshot = async (data: CreateSnapshotRequest) => {
  try {
    setLoading(true);
    const snapshot = await snapshotApi.create(data);
    addSnapshot(snapshot);
    showSuccessMessage('Snapshot created successfully');
  } catch (error) {
    if (error.status === 400) {
      showValidationError(error.detail);
    } else {
      showErrorMessage('Failed to create snapshot');
    }
    console.error('Snapshot creation failed:', error);
  } finally {
    setLoading(false);
  }
};
```

#### Performance Optimization
```python
# Batch operations
async def load_snapshots_with_workforce(office_id: UUID) -> List[PopulationSnapshot]:
    # Single query with joins instead of N+1
    query = """
        SELECT s.*, w.role, w.level, w.fte, t.tags
        FROM population_snapshots s
        LEFT JOIN snapshot_workforce w ON s.id = w.snapshot_id
        LEFT JOIN (
            SELECT snapshot_id, array_agg(tag) as tags
            FROM snapshot_tags
            GROUP BY snapshot_id
        ) t ON s.id = t.snapshot_id
        WHERE s.office_id = $1
    """
    # Process results...
```

#### Security Considerations
```python
# Input validation
@validator('snapshot_name')
def validate_snapshot_name(cls, v):
    if not v or not v.strip():
        raise ValueError('Snapshot name is required')
    if len(v) > 200:
        raise ValueError('Snapshot name too long')
    if any(char in v for char in ['<', '>', '"', "'"]):
        raise ValueError('Invalid characters in snapshot name')
    return v.strip()

# Authorization checks
def check_office_access(user: User, office_id: UUID) -> bool:
    """Verify user has access to office data."""
    # Implementation depends on auth system
    pass
```

## User Guide

### Getting Started with Snapshots

Population snapshots capture your office workforce at specific points in time, creating historical baselines for analysis and planning.

#### When to Create Snapshots

**Regular Snapshots** (Monthly/Quarterly):
- End-of-month workforce capture for historical tracking
- Quarterly planning baseline preparation
- Pre-budget planning data capture

**Event-Driven Snapshots**:
- Before major reorganizations
- After significant hiring campaigns
- When launching new service lines
- During market expansion

**Planning Snapshots**:
- Start of annual planning cycle
- Before scenario modeling sessions
- Creating "what-if" baselines

### Creating Your First Snapshot

#### Step 1: Navigate to Office Management
1. Go to **Offices** in the main navigation
2. Select your office from the list
3. Click on the **Workforce** tab

#### Step 2: Review Current Workforce
1. Verify the current workforce data is accurate
2. Check role and level distributions
3. Confirm FTE totals match expectations

#### Step 3: Create Snapshot
1. Click **"Save Current as Snapshot"**
2. Enter a descriptive name (e.g., "July 2025 Month-End")
3. Add description explaining the context
4. Add relevant tags (e.g., "monthly", "planning", "pre-expansion")
5. Click **"Create Snapshot"**

### Using Snapshots in Analysis

#### Switching Between Current and Historical Data
1. In any workforce view, use the **Snapshot Selector** dropdown
2. Choose "Current Workforce" for live data
3. Select any historical snapshot for point-in-time data
4. Data tables update automatically

#### Comparing Snapshots
1. Go to **Snapshots** management page
2. Click the comparison icon for your first snapshot
3. Select a second snapshot to compare
4. Review the comparison analysis:
   - **Summary metrics**: Total FTE changes, role additions/removals
   - **Detailed changes**: Role-by-role workforce deltas
   - **Insights**: Automatically generated observations

#### Example Comparison Workflow
**Scenario**: Comparing Q1 and Q2 workforce data

1. Create "Q1 2025 Baseline" snapshot (March 31)
2. Create "Q2 2025 End" snapshot (June 30)
3. Compare snapshots:
   - **Total Growth**: +15 FTE (+12.5%)
   - **New Roles**: Data Analyst added
   - **Changes**: Consultant A: +3, Consultant C: +2, Operations: +1
   - **Insights**: Strong consultant growth, new analytics capability

### Snapshot Management

#### Organizing Snapshots

**Naming Conventions**:
- **Time-based**: "2025-07 Month End", "Q2 2025 Planning"
- **Event-based**: "Pre-Merger Baseline", "Post-Reorganization"
- **Purpose-based**: "Annual Planning Start", "Budget Baseline"

**Tag Strategy**:
- **Frequency**: `monthly`, `quarterly`, `annual`
- **Purpose**: `planning`, `analysis`, `milestone`
- **Events**: `merger`, `expansion`, `reorganization`
- **Status**: `draft`, `approved`, `archived`

#### Snapshot Lifecycle

1. **Creation**: Capture workforce data with context
2. **Review**: Validate data accuracy and completeness
3. **Approval**: Mark as approved for official planning
4. **Usage**: Reference in scenarios and business plans
5. **Archival**: Retain for historical analysis

#### Setting Default Snapshots
1. Navigate to snapshot management
2. Find your preferred baseline snapshot
3. Click **Actions > Set as Default**
4. This snapshot becomes the default for new scenarios

### Best Practices

#### Creating Meaningful Snapshots
- **Consistent timing**: Create monthly snapshots on the same day
- **Clear context**: Always add descriptions explaining the snapshot purpose
- **Relevant tags**: Use consistent tagging for easy filtering
- **Data quality**: Verify workforce data before capturing

#### Comparison Analysis
- **Meaningful periods**: Compare snapshots with sufficient time gaps
- **Context awareness**: Consider external factors affecting changes
- **Multiple perspectives**: Look at both percentage and absolute changes
- **Trend analysis**: Use 3+ snapshots to identify patterns

#### Integration with Planning
- **Baseline selection**: Choose representative snapshots for scenario planning
- **What-if analysis**: Create hypothetical snapshots for planning scenarios
- **Progress tracking**: Compare actual results against planned snapshots
- **Continuous refinement**: Update baselines as business evolves

### Troubleshooting Common Issues

#### Snapshot Creation Fails
**Problem**: Error creating snapshot from current workforce
**Solutions**:
1. Verify workforce data exists for the office
2. Check for duplicate snapshot names
3. Ensure all required fields are completed
4. Refresh office data if outdated

#### Missing Workforce Data
**Problem**: Snapshot shows zero or incomplete workforce
**Solutions**:
1. Verify office has current workforce configuration
2. Check role and level definitions are complete
3. Ensure FTE values are properly set
4. Update office workforce before creating snapshot

#### Comparison Shows No Changes
**Problem**: Snapshot comparison indicates no differences
**Solutions**:
1. Verify comparing different snapshots (not same one twice)
2. Check if snapshots are from different time periods
3. Ensure workforce actually changed between snapshots
4. Consider data granularity (level vs role-only changes)

#### Performance Issues
**Problem**: Slow snapshot loading or creation
**Solutions**:
1. Limit snapshot list display to recent items
2. Use filtering to reduce data load
3. Archive old snapshots if system performance degrades
4. Contact administrator if issues persist

### Advanced Features

#### Bulk Operations
- **Batch creation**: Create multiple snapshots across offices
- **Bulk tagging**: Apply tags to multiple snapshots
- **Archive management**: Bulk archive old snapshots

#### Export and Reporting
- **CSV export**: Download snapshot workforce data
- **Comparison reports**: Export comparison analysis
- **Historical trends**: Generate multi-snapshot trend reports

#### API Integration
Advanced users can integrate with snapshot API for:
- Automated snapshot creation
- Custom analysis workflows  
- External system integration
- Bulk data operations

## Deployment Guide

### Production Configuration

#### Database Setup
```sql
-- Production database creation
CREATE DATABASE simplesim_prod;
CREATE USER simplesim_app WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE simplesim_prod TO simplesim_app;

-- Connect to database
\c simplesim_prod

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO simplesim_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO simplesim_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO simplesim_app;
```

#### Environment Variables

**Backend Production (.env)**:
```bash
# Database
DATABASE_URL=postgresql://simplesim_app:secure_password@prod-db-host:5432/simplesim_prod
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Application
APP_ENV=production
LOG_LEVEL=INFO
DEBUG=false

# Security
SECRET_KEY=your-super-secret-production-key
CORS_ORIGINS=https://your-domain.com

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
METRICS_ENABLED=true
```

**Frontend Production (.env.production)**:
```bash
VITE_API_BASE_URL=https://api.your-domain.com
VITE_APP_ENV=production
VITE_SENTRY_DSN=https://your-frontend-sentry-dsn
```

#### Docker Configuration

**Backend Dockerfile** (production optimized):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

**Frontend Dockerfile**:
```dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose (Production)
```yaml
version: '3.8'

services:
  db:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: simplesim_prod
      POSTGRES_USER: simplesim_app
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped

  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      DATABASE_URL: postgresql://simplesim_app:${DB_PASSWORD}@db:5432/simplesim_prod
    depends_on:
      - db
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

volumes:
  postgres_data:
```

### Database Migrations in Production

#### Migration Strategy
1. **Backup database** before migrations
2. **Test migrations** in staging environment
3. **Apply migrations** during maintenance window
4. **Verify data integrity** after migration
5. **Monitor application** post-deployment

#### Backup Script
```bash
#!/bin/bash
# backup-db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="simplesim_backup_${DATE}.sql"

pg_dump -h prod-db-host -U simplesim_app -d simplesim_prod > "/backups/${BACKUP_FILE}"

# Verify backup
if [ $? -eq 0 ]; then
    echo "Backup created successfully: ${BACKUP_FILE}"
    
    # Compress backup
    gzip "/backups/${BACKUP_FILE}"
    
    # Clean old backups (keep 30 days)
    find /backups -name "simplesim_backup_*.sql.gz" -mtime +30 -delete
else
    echo "Backup failed!"
    exit 1
fi
```

#### Migration Application
```bash
#!/bin/bash
# apply-migration.sh

MIGRATION_FILE=$1

if [ -z "$MIGRATION_FILE" ]; then
    echo "Usage: $0 <migration_file>"
    exit 1
fi

echo "Creating database backup..."
./backup-db.sh

echo "Applying migration: $MIGRATION_FILE"
psql -h prod-db-host -U simplesim_app -d simplesim_prod -f "migrations/${MIGRATION_FILE}"

if [ $? -eq 0 ]; then
    echo "Migration applied successfully"
else
    echo "Migration failed! Check logs and consider rollback"
    exit 1
fi
```

### Monitoring and Maintenance

#### Health Checks
```python
# backend/health.py
from fastapi import APIRouter
from sqlalchemy import text
from src.database.connection import get_db

router = APIRouter()

@router.get("/health")
async def health_check():
    """Application health check."""
    try:
        # Database connectivity
        async with get_db() as db:
            await db.execute(text("SELECT 1"))
        
        # Additional checks
        checks = {
            "database": "healthy",
            "snapshots": "healthy",  # Could check snapshot service
            "version": "1.0.0"
        }
        
        return {"status": "healthy", "checks": checks}
    
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 503
```

#### Logging Configuration
```python
# backend/logging_config.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure structured logging for production."""
    
    # JSON formatter
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    # Root logger
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    
    # Application loggers
    logging.getLogger("src.services.snapshot_service").setLevel(logging.INFO)
    logging.getLogger("src.repositories").setLevel(logging.WARNING)
```

#### Metrics Collection
```python
# backend/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
snapshot_operations = Counter(
    'snapshot_operations_total',
    'Total snapshot operations',
    ['operation', 'status']
)

snapshot_creation_time = Histogram(
    'snapshot_creation_duration_seconds',
    'Time spent creating snapshots'
)

active_snapshots = Gauge(
    'active_snapshots_total',
    'Total number of active snapshots'
)

# Usage in service
class SnapshotService:
    async def create_snapshot(self, request):
        start_time = time.time()
        try:
            snapshot = await self._create_snapshot_impl(request)
            snapshot_operations.labels(operation='create', status='success').inc()
            return snapshot
        except Exception as e:
            snapshot_operations.labels(operation='create', status='error').inc()
            raise
        finally:
            snapshot_creation_time.observe(time.time() - start_time)
```

#### Database Monitoring
```sql
-- Monitor snapshot table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    pg_total_relation_size(schemaname||'.'||tablename) as bytes
FROM pg_tables 
WHERE tablename LIKE 'snapshot%'
ORDER BY bytes DESC;

-- Monitor snapshot creation rate
SELECT 
    date_trunc('day', created_at) as day,
    count(*) as snapshots_created
FROM population_snapshots 
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY day
ORDER BY day;

-- Check for performance issues
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
WHERE query LIKE '%population_snapshots%'
ORDER BY total_time DESC
LIMIT 10;
```

### Backup and Recovery

#### Automated Backup Schedule
```bash
# /etc/cron.d/simplesim-backup
# Daily backup at 2 AM
0 2 * * * postgres /opt/simplesim/scripts/backup-db.sh

# Weekly full backup on Sunday at 1 AM
0 1 * * 0 postgres /opt/simplesim/scripts/full-backup.sh
```

#### Recovery Procedures

**Point-in-time Recovery**:
```bash
#!/bin/bash
# restore-db.sh

BACKUP_FILE=$1
TARGET_TIME=$2  # Optional: YYYY-MM-DD HH:MM:SS

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file> [target_time]"
    exit 1
fi

echo "Stopping application services..."
docker-compose stop backend frontend

echo "Restoring database from: $BACKUP_FILE"
gunzip -c "$BACKUP_FILE" | psql -h prod-db-host -U simplesim_app -d simplesim_prod

if [ $? -eq 0 ]; then
    echo "Database restored successfully"
    echo "Starting application services..."
    docker-compose start backend frontend
else
    echo "Database restore failed!"
    exit 1
fi
```

#### Disaster Recovery
1. **Data backup**: Automated daily PostgreSQL dumps
2. **Application backup**: Docker images in registry
3. **Configuration backup**: Environment files and configs
4. **Recovery testing**: Monthly restore drills
5. **Documentation**: Detailed runbooks for common scenarios

### Performance Optimization

#### Database Optimization
```sql
-- Vacuum and analyze regularly
VACUUM ANALYZE population_snapshots;
VACUUM ANALYZE snapshot_workforce;

-- Monitor index usage
SELECT 
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE schemaname = 'public' 
AND tablename LIKE 'snapshot%';

-- Optimize common queries
EXPLAIN ANALYZE 
SELECT * FROM v_snapshot_summary 
WHERE office_id = 'some-uuid' 
ORDER BY created_at DESC;
```

#### Application Performance
```python
# Connection pooling
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=3600
)

# Query optimization
async def get_office_snapshots_optimized(office_id: UUID) -> List[PopulationSnapshot]:
    """Optimized snapshot retrieval with single query."""
    query = """
        SELECT 
            s.*,
            json_agg(DISTINCT jsonb_build_object(
                'role', w.role,
                'level', w.level,
                'fte', w.fte
            )) FILTER (WHERE w.id IS NOT NULL) as workforce,
            array_agg(DISTINCT t.tag) FILTER (WHERE t.tag IS NOT NULL) as tags
        FROM population_snapshots s
        LEFT JOIN snapshot_workforce w ON s.id = w.snapshot_id
        LEFT JOIN snapshot_tags t ON s.id = t.snapshot_id
        WHERE s.office_id = $1
        GROUP BY s.id
        ORDER BY s.created_at DESC
    """
    # Execute and process results...
```

#### Caching Strategy
```python
from functools import lru_cache
import redis

redis_client = redis.Redis(host='redis', port=6379, db=0)

@lru_cache(maxsize=128)
async def get_office_snapshots_cached(office_id: str) -> List[PopulationSnapshot]:
    """Cache office snapshots for 5 minutes."""
    cache_key = f"office_snapshots:{office_id}"
    
    # Try cache first
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Fetch from database
    snapshots = await get_office_snapshots(UUID(office_id))
    
    # Cache results
    redis_client.setex(
        cache_key, 
        300,  # 5 minutes
        json.dumps([s.dict() for s in snapshots])
    )
    
    return snapshots
```

### Security Considerations

#### Database Security
```sql
-- Restrict permissions
REVOKE ALL ON population_snapshots FROM public;
GRANT SELECT, INSERT, UPDATE, DELETE ON population_snapshots TO simplesim_app;

-- Enable row-level security if needed
ALTER TABLE population_snapshots ENABLE ROW LEVEL SECURITY;

-- Audit triggers for sensitive operations
CREATE OR REPLACE FUNCTION audit_snapshot_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (
        table_name,
        operation,
        old_values,
        new_values,
        user_name,
        timestamp
    ) VALUES (
        TG_TABLE_NAME,
        TG_OP,
        row_to_json(OLD),
        row_to_json(NEW),
        current_user,
        NOW()
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
```

#### API Security
```python
# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/snapshots/")
@limiter.limit("10/minute")  # Limit snapshot creation
async def create_snapshot(request: CreateSnapshotRequest):
    # Implementation...
    pass

# Input validation
from pydantic import validator

class CreateSnapshotRequest(BaseModel):
    @validator('snapshot_name')
    def validate_name(cls, v):
        # Prevent SQL injection
        if any(char in v for char in [';', '--', '/*', '*/']):
            raise ValueError('Invalid characters in snapshot name')
        return v
```

This comprehensive documentation provides everything needed to understand, develop, deploy, and maintain the SimpleSim population snapshot system. The implementation includes full backend and frontend functionality, database schema, testing suite, and production deployment guidance.