# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SimpleSim is a workforce simulation platform for modeling organizational growth, workforce planning, and scenario analysis. It consists of a React frontend and FastAPI backend with a deterministic simulation engine.

## Development Commands

### Backend (Python/FastAPI)
```bash
# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Unix/macOS
.venv\Scripts\activate     # Windows

# Install dependencies
cd backend
pip install -r requirements.txt

# Start development server (from project root)
uvicorn backend.main:app --reload
# Backend runs at http://localhost:8000
```

### Frontend (React/TypeScript)
```bash
cd frontend

# Install dependencies
npm install

# Development
npm run dev          # Start dev server at http://localhost:3000
npm run build        # Production build
npm run preview      # Preview production build

# Testing
npm run test         # Unit tests with Vitest
npm run test:ui      # Vitest UI
npm run test:e2e     # Playwright E2E tests
npm run test:e2e:ui  # Playwright UI mode
```

### Testing Backend
```bash
# From project root
python3 -m pytest backend/tests/unit/
python3 -m pytest backend/tests/unit/test_engine_basic.py  # Specific test
```

### Server Management
```bash
# Always use this script to start/restart servers
./scripts/restart-servers.sh
```

**IMPORTANT**: Always use `./scripts/restart-servers.sh` when starting or restarting development servers. This script handles both frontend and backend startup in the correct order and configuration.

## Architecture Overview

### High-Level Structure
```
Frontend (React) → Backend API (FastAPI) → Simulation Engine → Data Storage (JSON)
```

### Key Components

**Frontend (`frontend/src/`)**:
- Modern React 18 with TypeScript
- Two routing systems: `AppRoutes.tsx` (current) and `EnhancedRoutes.tsx` (enhanced)
- Layout: `AppLayoutV2.tsx` (modern) with sidebar navigation, breadcrumbs, search, user menu
- UI: shadcn/ui components with Tailwind CSS and dark mode support
- State: React Context and Zustand for state management

**Backend (`backend/`)**:
- FastAPI with automatic OpenAPI documentation
- Routers in `/routers/` for API endpoints
- Business logic in `/src/services/`
- Configuration loaded from `backend/config/office_configuration.json`

**Simulation Engine (`backend/src/services/simulation_engine.py`)**:
- Deterministic monthly simulations
- Processes recruitment, churn, and progression
- Handles complex data structures (leveled vs flat roles)

### Data Flow Architecture

**Scenario Execution**:
1. User creates scenario in React UI (name, time range, office scope, levers)
2. Frontend sends scenario payload to `/scenarios/run` endpoint
3. Backend transforms UI payload to simulation engine format
4. Engine executes monthly simulation with business logic
5. Results returned in structured format: `year → office → role → level/month`

**Data Structures**:
- **Leveled roles** (e.g., Consultant): `roles['Consultant']['A'][month_index]`
- **Flat roles** (e.g., Operations): `roles['Operations'][month_index]`
- Always check `isinstance(role_data, dict)` vs `isinstance(role_data, list)`

## Key Files and Patterns

### Frontend Navigation
- **Current**: `src/main.tsx` uses `AppLayoutV2` + `EnhancedRoutes`
- **Legacy**: `AppRoutes.tsx` with different layout system
- Navigation items defined in `AppLayoutV2.tsx` with icons and paths

### Backend API Patterns
- Routers in `/routers/` use dependency injection pattern
- Configuration service (`config_service.py`) handles office data
- Scenario service layer translates between UI and engine formats
- All business logic stays in simulation engine (never duplicate calculations)

### Type Safety
- Frontend: TypeScript with strict mode, types in `/src/types/`
- Backend: Pydantic models for API validation
- Key types: `unified-data-structures.ts`, `office.ts`, `simulation.ts`

## Data Structure Requirements

⚠️ **CRITICAL: Always check these files when making data structure changes:**
- `backend/src/services/unified_data_models.py` - Pydantic models for validation
- `frontend/src/types/unified-data-structures.ts` - TypeScript type definitions

### Baseline Input Structure
The `baseline_input` must follow this exact structure from `unified_data_models.py`:

```python
BaselineInput {
  global_data: Dict[str, Dict[str, RoleData]]  # alias for "global"
}

RoleData {
  levels: Dict[str, LevelData]  # For leveled roles (Consultant)
  # OR
  recruitment: MonthlyValues    # For flat roles (Operations)
  churn: MonthlyValues
}

LevelData {
  recruitment: MonthlyValues
  churn: MonthlyValues
}

MonthlyValues {
  values: Dict[str, float]  # Keys: "YYYYMM" format
}
```

### UI Implementation
- `BaselineInputGrid.tsx` generates this structure in `getCurrentData()`
- Both `global_data.recruitment` and `global_data.churn` contain the same role data
- Each role contains both recruitment and churn values at the level

## Testing Strategy

### Frontend Testing
- Unit tests with Vitest and Testing Library
- E2E tests with Playwright covering critical user flows
- Test files co-located with components or in `/src/tests/`

#### UI Feature Verification Testing
**MANDATORY: Run comprehensive UI tests after building features to verify functionality**

```bash
# Always test UI features after implementation
./scripts/restart-servers.sh  # Start both servers first

# Primary comprehensive test - covers full simulation workflow
npx playwright test e2e/final-simulation-test.spec.ts --headed --project=chromium

# Bug fix verification - tests specific issues and regressions
npx playwright test e2e/verify-bug-fixes.spec.ts --headed --project=chromium

# Basic functionality test - quick verification of core features  
npx playwright test e2e/simple-simulation-test.spec.ts --headed --project=chromium

# Run all E2E tests
npm run test:e2e

# Run with UI mode for debugging
npm run test:e2e:ui
```

**Comprehensive E2E Test Suite** (`frontend/e2e/`):
- `final-simulation-test.spec.ts` - Complete simulation workflow testing
- `verify-bug-fixes.spec.ts` - Focused bug fix validation and regression testing
- `simple-simulation-test.spec.ts` - Basic functionality verification
- `debug-scenarios-ui.spec.ts` - UI debugging and troubleshooting utilities
- `simulation-workflow.spec.ts` - Advanced workflow and data validation
- `test-helpers.ts` - Reusable test utilities and helper functions
- `TEST_SUITE_README.md` - Complete testing documentation and guidelines

**What the tests verify**:
1. **Navigation and page loading** - All major pages accessible
2. **Scenario creation workflow** - Form submission and validation
3. **Simulation execution** - Run scenarios and generate results
4. **Results display accuracy** - Workforce KPIs show non-zero values
5. **Year switching functionality** - Multi-year data navigation works
6. **Chart and visualization rendering** - All charts display correctly
7. **UI responsiveness** - Components respond to user interactions
8. **Error handling** - Graceful failure and recovery mechanisms

**When to run UI tests**:
- ✅ After implementing new features
- ✅ After fixing bugs (especially data display issues)
- ✅ Before deploying to production
- ✅ After significant UI/UX changes
- ✅ When adding new simulation capabilities
- ✅ After modifying service layer business logic

#### JavaScript Error Detection Testing
**CRITICAL: Always check for console errors before considering features complete**

```bash
# 1. MANDATORY: Test basic frontend loading first
./scripts/restart-servers.sh
# Open http://localhost:3000 in browser
# Check browser console (F12 -> Console) for ANY errors

# 2. Navigate through ALL major pages and check console:
# - Dashboard: /
# - Scenarios: /scenarios  
# - Business Planning: /business-planning
# - Offices: /offices
# - Settings: /settings

# 3. Test simulation workflow completely:
# - Create scenario
# - Run simulation  
# - View results
# - Switch between years
# - Check console after EACH step

# 4. If ANY JavaScript errors appear:
# - Fix immediately before proceeding
# - Re-test the complete workflow
# - Verify console is clean across all pages
```

**Common JavaScript Error Patterns to Watch For**:
- ❌ `TypeError: undefined is not an object` - Usually missing imports or incorrect static method calls
- ❌ `ReferenceError: Cannot access uninitialized variable` - Variable hoisting or scope issues
- ❌ `TypeError: Cannot read property X of undefined` - Missing null checks or data validation
- ❌ `TypeError: X is not a function` - Incorrect function references or missing methods
- ❌ Component rendering errors - Usually data structure mismatches

**Error Detection Best Practices**:
1. **Always check browser console first** - Before running any automated tests
2. **Test real user workflows** - Navigate through UI manually to trigger all code paths
3. **Check console after every major action** - Create scenario, run simulation, view results
4. **Verify service layer methods** - Ensure static methods use correct `ClassName.method()` syntax
5. **Test with real data** - JavaScript errors often only appear with actual simulation results

### Backend Testing
- Unit tests with pytest in `backend/tests/unit/`
- Focus on simulation engine accuracy and API contract validation
- Test both individual components and full integration flows

## Configuration and Data

### Office Configuration
- Stored in `backend/config/office_configuration.json`
- Loaded at startup via config service
- Contains baseline FTE, salaries, economic parameters per office
- Modified through Settings UI with CAT matrix and progression curves

### Scenario Storage
- Definitions: `backend/data/scenarios/definitions/`
- Results: `backend/data/scenarios/results/`
- JSON format with unique IDs

## UI Guidelines

### Component Structure
- V2 components in `components/v2/` for enhanced features
- UI primitives in `components/ui/` (shadcn/ui based)
- Page components in `pages/` with V2 variants (e.g., `ScenariosV2.tsx`)

### Layout System
- Single layout in `AppLayoutV2.tsx` prevents header duplication
- Breadcrumbs auto-generated from routes
- Dark/light theme with system preference detection
- Mobile-responsive sidebar navigation

### Styling
- Tailwind CSS with custom design tokens
- CSS custom properties for theming
- Consistent spacing and typography scales

## Common Development Pitfalls

### Backend
- Always run backend from project root, not from `/backend/`
- Simulation engine expects specific data structure (see `SIMULATION_DATA_STRUCTURES.md`)
- Never recalculate business metrics outside the simulation engine
- Check virtual environment activation if import errors occur

### Frontend
- Avoid double layouts (use either AppLayout or AppLayoutV2, not both)
- Check component imports - V2 components may have different APIs
- Use proper TypeScript types from `/src/types/`
- Test routing changes in both desktop and mobile views

### Data Handling
- Leveled vs flat role distinction is critical for data processing
- Always validate data structures before iteration
- Month indices are 0-based (0=January, 11=December)
- FTE values are absolute numbers, not percentages

### Workforce KPI Requirements
⚠️ **CRITICAL: Scenarios with null baseline data will show 0 workforce KPIs**

**Common Issue**: Workforce KPIs (Total Recruitment, Total Churn, Net Recruitment) showing 0 values

**Root Cause**: Scenarios with `null` baseline recruitment and churn data in the baseline_input structure

**Examples**:
- ❌ **Problematic baseline data**: `{"Consultant": {"levels": null, "recruitment": null, "churn": null}}`
- ✅ **Valid baseline data**: `{"Consultant": {"levels": {"A": {"recruitment": {"values": {"202501": 5.0}}, "churn": {"values": {"202501": 2.0}}}}}}`

**Solution**: Ensure scenarios include proper baseline input data with non-null recruitment and churn values for all role levels

**UI Feedback**: The frontend now displays a warning when zero metrics are detected, indicating insufficient baseline data

## Performance Considerations

- Frontend: Vite for fast development, code splitting for production
- Backend: FastAPI with async support where beneficial
- Simulation: Deterministic engine optimized for monthly calculations
- Large datasets: Consider pagination and virtualization in UI components

## Security Notes

- CORS configured for development (all origins allowed)
- No authentication currently implemented
- Configuration files should not contain sensitive data
- API endpoints validate input data with Pydantic models

## Design System Guidelines

⚠️ **MANDATORY: All UI/UX work must follow the SimpleSim Design System located in `frontend/src/design/`**

### Core Design Principles
- **Eliminate UI Bloat**: Single navigation system, unified components, no duplicate headers
- **Task-Oriented Architecture**: Organize by user goals (Plan Growth → See Results → Manage Settings)
- **Progressive Disclosure**: Simple → Intermediate → Advanced complexity layers
- **Desktop-First**: Optimized for 1024px+ desktop interfaces (no mobile responsive needed)
- **Consistency**: Single source of truth for all UI patterns and components

### Design System Files (ALWAYS CONSULT BEFORE UI CHANGES)
```
frontend/src/design/
├── ui-design-system.md           # Core principles, layout architecture
├── design-tokens.md              # Colors, typography, spacing, shadows  
├── component-api-specifications.md # Component APIs and TypeScript interfaces
├── information-architecture.md    # User mental models, content strategy
├── interaction-patterns.md        # Micro-interactions, hover states, behaviors
├── layout-composition-patterns.md # Desktop layouts, component composition
├── accessibility-guidelines.md    # WCAG 2.1 compliance, assistive technology
└── implementation-plan.md         # 12-week phased rollout strategy
```

### Mandatory UI Implementation Rules
1. **Navigation**: Use single top navigation + context bar (NO sidebar, tabs, breadcrumbs)
2. **Components**: Use design system components only (NO custom button/table/modal variations)
3. **Layout**: Use standardized page templates (Dashboard, List, Detail, Form layouts)
4. **Spacing**: Use design tokens for all spacing (NO arbitrary margins/padding)
5. **Colors**: Use design token colors only (NO custom color values)
6. **Typography**: Use design system typography scale (NO custom font sizes)
7. **Actions**: Context-aware actions in action bar (NO scattered buttons throughout UI)

### Component Usage Requirements
- **Button**: Single Button component with variants (primary|secondary|ghost|destructive)
- **Table**: Single DataTable component for ALL tabular data
- **Form**: Structured Form components with validation patterns
- **Modal**: Single Modal component with compound pattern (Header|Body|Footer)
- **Layout**: Use Container, Stack, Grid components for all layouts
- **Typography**: Use Text component with semantic variants

### Before Any UI Work
1. **Consult design system files** in `frontend/src/design/` directory
2. **Follow component APIs** as specified in component-api-specifications.md
3. **Use design tokens** for colors, spacing, typography
4. **Follow layout patterns** from layout-composition-patterns.md
5. **Implement interactions** per interaction-patterns.md
6. **Ensure accessibility** per accessibility-guidelines.md

### UI Bloat Prevention Checklist
- ❌ NO duplicate navigation systems (sidebar + tabs + breadcrumbs)
- ❌ NO multiple button/table/form implementations  
- ❌ NO duplicate page headers or titles
- ❌ NO scattered action buttons (group in context bar)
- ❌ NO custom spacing/colors outside design tokens
- ❌ NO complex nested layouts (use standard page templates)
- ✅ Single top navigation with context bar
- ✅ Unified component library usage
- ✅ Consistent design token application
- ✅ Task-oriented information architecture
- ✅ Progressive disclosure for complexity

### Implementation Priority
When working on UI features, follow this priority:
1. **Design System Compliance**: Ensure all changes follow design system
2. **Component Reuse**: Use existing design system components
3. **Layout Consistency**: Use standard page layout templates  
4. **User Flow Optimization**: Reduce clicks, simplify workflows
5. **Accessibility**: Ensure WCAG 2.1 AA compliance

**Remember**: The design system eliminates UI bloat while maintaining all powerful functionality. Always consult the design files before making any UI/UX changes.

## Data Architecture & Configuration Management

### Single Source of Truth Pattern
⚠️ **CRITICAL: The system uses `backend/config/office_configuration.json` as the master database**

**Configuration Lifecycle**:
1. **Master File**: `backend/config/office_configuration.json` is the definitive source for all office configurations
2. **Startup Logic**: System checks for existing config file on startup; if empty/missing, requires user upload
3. **Partial Updates**: Excel imports perform partial updates (add/modify offices without removing others)
4. **Baseline Definition**: All KPI calculations use current config state as baseline for comparisons

**Data Flow**: Configuration Service → In-Memory Cache → API Endpoints → Frontend

### Workforce Data Structure Evolution
⚠️ **IMPORTANT: Workforce data has migrated from roles-based to snapshot-based storage**

- **Legacy**: FTE data stored in `roles` objects with individual level breakdowns
- **Current**: FTE data stored in `snapshots` with aggregated totals per office
- **Backend**: Office endpoints now generate mock snapshots from config data
- **Frontend**: Components extract `total_fte` from `office.snapshots[0].total_fte`

### Simulation Engine Architecture
**Processing Order (Monthly)**:
1. **Churn**: Remove people based on monthly churn rates
2. **Progression**: Move people between levels (only in evaluation months: May/November)  
3. **Recruitment**: Add new hires based on recruitment rates with fractional accumulation

**Key Patterns**:
- **Deterministic Results**: Uses fractional accumulation for reproducible outcomes
- **Individual Tracking**: Person-level tracking for detailed analytics
- **Fresh State**: Engine resets before each simulation run

### API Router Architecture
**Multiple Router Systems**:
- **Configuration-based**: `/routers/offices.py` (uses JSON config, `/offices` prefix)
- **Database-based**: `/src/routes/offices.py` (uses database models, `/api/offices` prefix)
- **Route Conflicts**: Ensure specific routes (`/all`, `/health`) are defined before generic `/{office_id}` routes

## Server Management Issues

### Backend Reload Problems
**Common Issue**: FastAPI reload doesn't always pick up changes to router files

**Solutions**:
1. Use `./scripts/restart-servers.sh` for full restart
2. For manual restart: Kill backend process and restart with `uvicorn backend.main:app --reload`
3. Check for cached responses or route conflicts if changes don't appear
4. Verify route registration order in `backend/main.py`

### Port Conflicts
**Default Ports**: Backend (8000), Frontend (3000)
**Alternative Ports**: Use `--port 8001` or `--port 8002` if default ports are occupied