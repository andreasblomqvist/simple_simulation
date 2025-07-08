# Current SimpleSim System Architecture

## Executive Summary

SimpleSim is a workforce simulation and business planning platform that models organizational growth, financial performance, and strategic scenarios across multiple offices. The system simulates monthly workforce dynamics including recruitment, churn, progression, and financial metrics over multi-year periods.

## System Overview

### Core Purpose
- **Workforce Simulation**: Model headcount changes, recruitment, churn, and career progression
- **Financial Modeling**: Calculate revenue, costs, EBITDA, and other financial KPIs
- **Scenario Planning**: Compare different strategic scenarios and their outcomes
- **Multi-Office Management**: Handle data for 12 offices across Europe and North America

### Key Capabilities
- Monthly simulation over 1-5 year periods
- Role-based workforce modeling (Consultant, Sales, Recruitment, Operations)
- Level-based progression (A, AC, C, SrC, AM, M, SrM, PiP)
- Financial calculations with currency conversion
- Excel import/export functionality
- Scenario comparison and analysis

## Architecture Overview

### Technology Stack
- **Backend**: Python 3.x with FastAPI
- **Frontend**: React with TypeScript
- **Data Storage**: JSON files for configuration, in-memory for simulation
- **Excel Integration**: pandas/openpyxl for import/export
- **API**: RESTful endpoints with JSON responses

### System Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Data Layer    │
│   (React/TS)    │◄──►│   (FastAPI)     │◄──►│   (JSON Files)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Simulation      │
                       │ Engine          │
                       └─────────────────┘
```

## Backend Architecture

### 1. API Layer (`backend/routers/`)

#### Health Endpoints (`health.py`)
- `GET /health` - System health check
- `GET /health/detailed` - Detailed system status

#### Office Management (`offices.py`)
- `GET /offices/config` - Get all office configurations
- `POST /offices/config/update` - Update office configuration
- `POST /offices/config/import` - Import Excel configuration
- `POST /offices/config/export` - Export to Excel format

#### Simulation (`simulation.py`)
- `POST /simulation/run` - Run simulation with parameters
- `POST /simulation/config/validation` - Validate configuration
- `POST /simulation/export/excel` - Export results to Excel

### 2. Service Layer (`backend/src/services/`)

#### Configuration Service (`config_service.py`)
```python
class ConfigService:
    """Manages office configuration data"""
    
    def get_config() -> Dict[str, Any]
    def import_from_excel(df: pd.DataFrame) -> int
    def update_config(updates: Dict[str, Any]) -> bool
```

**Responsibilities**:
- Load/save configuration from JSON files
- Import configuration from Excel files
- Validate configuration data
- Calculate office totals and journey classifications

#### Simulation Engine (`simulation_engine.py`)
```python
class SimulationEngine:
    """Core simulation logic"""
    
    def run_simulation(
        start_year: int,
        start_month: int,
        end_year: int,
        end_month: int,
        lever_plan: Dict[str, Any],
        economic_params: EconomicParameters
    ) -> Dict[str, Any]
```

**Responsibilities**:
- Execute monthly simulation steps
- Handle recruitment, churn, and progression
- Calculate financial metrics
- Generate detailed movement logs

#### KPI Service (`kpi.py`)
```python
class KPIService:
    """Calculate financial and operational KPIs"""
    
    def calculate_all_kpis(
        results: Dict[str, Any],
        simulation_duration_months: int,
        unplanned_absence: float,
        other_expense: float
    ) -> AllKPIs
```

**Responsibilities**:
- Calculate financial metrics (Revenue, EBITDA, Margin)
- Calculate growth metrics (Headcount growth, Revenue growth)
- Calculate journey-based metrics
- Provide baseline comparisons

#### Excel Export Service (`excel_export_service.py`)
```python
class ExcelExportService:
    """Export simulation results to Excel"""
    
    def export_simulation_results(
        simulation_results: Dict[str, Any],
        kpis: Dict[str, Any],
        output_path: str
    ) -> None
```

**Responsibilities**:
- Generate multi-sheet Excel exports
- Create summary, financial, and detailed sheets
- Format data for business users
- Handle missing data gracefully

### 3. Data Models (`backend/src/services/simulation/models.py`)

#### Core Data Structures
```python
@dataclass
class RoleData:
    """Flat role data (Operations)"""
    recruitment_1: float = 0.0  # Monthly recruitment rates
    churn_1: float = 0.0        # Monthly churn rates
    price_1: float = 0.0        # Monthly prices
    salary_1: float = 0.0       # Monthly salaries
    utr_1: float = 1.0          # Monthly utilization rates
    # ... months 2-12

@dataclass
class LevelData:
    """Level-specific data (Consultant, Sales, Recruitment)"""
    recruitment_1: float = 0.0
    churn_1: float = 0.0
    price_1: float = 0.0
    salary_1: float = 0.0
    utr_1: float = 1.0
    progression_1: float = 0.0  # Monthly progression rates
    # ... months 2-12

@dataclass
class Office:
    """Complete office configuration"""
    name: str
    total_fte: float
    journey: str
    roles: Dict[str, Union[RoleData, Dict[str, LevelData]]]
```

### 4. Configuration Management

#### Default Configuration (`backend/config/default_config.py`)
- **20,000+ lines** of hardcoded data
- Office mappings and currency conversions
- Base pricing and salary data
- Level distributions and recruitment rates

#### Office Configuration (`backend/config/office_configuration.json`)
- Current office configurations
- Monthly data for all roles and levels
- FTE counts and financial parameters

## Frontend Architecture

### 1. Application Structure (`frontend/src/`)

#### Pages (`pages/`)
- **Configuration.tsx** - Office configuration management
- **Simulation.tsx** - Simulation setup and execution
- **Results.tsx** - Simulation results visualization
- **Scenarios.tsx** - Scenario management and comparison

#### Components (`components/`)
- **ConfigurationMatrix.tsx** - Office configuration editing
- **SimulationControls.tsx** - Simulation parameter controls
- **ResultsCharts.tsx** - Results visualization
- **ExcelImportExport.tsx** - File upload/download

#### Services (`services/`)
- **api.ts** - API client functions
- **types.ts** - TypeScript type definitions

### 2. Key Frontend Features

#### Configuration Management
- **Office Selection**: Dropdown to select specific office
- **Role/Level Editing**: Inline editing of FTE, pricing, salaries
- **Excel Import/Export**: File upload and download
- **Global Configuration**: Apply changes across multiple offices

#### Simulation Interface
- **Parameter Setup**: Time range, economic parameters
- **Lever Configuration**: Adjust recruitment, churn, pricing
- **Execution**: Run simulation with progress indication
- **Results Display**: Charts and tables of simulation outcomes

#### Results Visualization
- **Financial Metrics**: Revenue, EBITDA, margins
- **Growth Metrics**: Headcount and revenue growth
- **Journey Analysis**: Office maturity progression
- **Comparison Tools**: Baseline vs simulation comparison

## Data Flow

### 1. Configuration Data Flow
```
Excel File → ConfigService.import_from_excel() → JSON Storage
     ↓
Frontend API Call → ConfigService.get_config() → React State
     ↓
User Edits → ConfigService.update_config() → JSON Storage
```

### 2. Simulation Data Flow
```
Configuration → SimulationEngine.run_simulation() → Results
     ↓
Results → KPIService.calculate_all_kpis() → Enhanced Results
     ↓
Enhanced Results → ExcelExportService → Excel File
```

### 3. API Data Flow
```
Frontend Request → FastAPI Router → Service Layer → Data Layer
     ↓
Data Layer → Service Layer → FastAPI Router → JSON Response
```

## Data Models and Relationships

### 1. Office Structure
```
Office
├── name: string
├── total_fte: number
├── journey: string (New/Emerging/Established/Mature)
└── roles: {
    Consultant: {
        A: LevelData,
        AC: LevelData,
        C: LevelData,
        ...
    },
    Sales: {
        A: LevelData,
        AC: LevelData,
        ...
    },
    Recruitment: {
        A: LevelData,
        ...
    },
    Operations: RoleData
}
```

### 2. Level Data Structure
```
LevelData
├── recruitment_1-12: number (monthly rates)
├── churn_1-12: number (monthly rates)
├── price_1-12: number (monthly prices)
├── salary_1-12: number (monthly salaries)
├── utr_1-12: number (utilization rates)
└── progression_1-12: number (progression rates)
```

### 3. Simulation Results Structure
```
SimulationResults
├── years: {
    "2025": {
        offices: {
            "Stockholm": {
                total_fte: number,
                roles: {...},
                financial: {...}
            }
        }
    }
}
├── logs: [...],
└── kpis: {...}
```

## Key Features and Functionality

### 1. Workforce Simulation
- **Monthly Processing**: Simulate workforce changes month by month
- **Recruitment**: Add new employees based on rates
- **Churn**: Remove employees based on rates
- **Progression**: Move employees between levels
- **Financial Impact**: Calculate revenue and costs

### 2. Financial Modeling
- **Revenue Calculation**: FTE × Price × UTR × Hours
- **Cost Calculation**: FTE × Salary + Benefits + Overhead
- **EBITDA**: Revenue - Costs
- **Margin Analysis**: EBITDA as percentage of revenue

### 3. Scenario Planning
- **Baseline Scenario**: Current state simulation
- **Adjustment Scenarios**: Modified parameters
- **Comparison Tools**: Side-by-side scenario analysis
- **Export Capabilities**: Excel reports for stakeholders

### 4. Multi-Office Support
- **12 Offices**: Stockholm, Munich, Hamburg, Helsinki, Oslo, Berlin, Copenhagen, Zurich, Frankfurt, Amsterdam, Cologne, Toronto
- **Currency Conversion**: All calculations in SEK
- **Office-Specific Data**: Different pricing, salaries, rates per office

## Configuration Management

### 1. Excel Import/Export
- **Import Format**: Office, Role, Level, FTE, Price_1-12, Salary_1-12, etc.
- **Export Format**: Same structure as import
- **Validation**: Basic data type and range validation
- **Error Handling**: Partial imports with error reporting

### 2. Configuration Storage
- **Primary Storage**: JSON files in `backend/config/`
- **Backup Files**: `.backup` versions for rollback
- **In-Memory Cache**: Fast access during simulation
- **Persistence**: Automatic saving on changes

### 3. Data Validation
- **Type Checking**: Ensure numeric values
- **Range Validation**: UTR between 0-1, positive FTE
- **Consistency Checks**: Role/level combinations
- **Currency Handling**: Automatic SEK conversion

## Performance Characteristics

### 1. Simulation Performance
- **Speed**: ~1-2 seconds for 5-year simulation
- **Memory Usage**: ~100-200MB for large simulations
- **Scalability**: Linear with simulation duration
- **Concurrency**: Single-threaded simulation engine

### 2. Data Access Performance
- **Configuration Loading**: ~100ms for full config
- **API Response Time**: ~50-200ms typical
- **Excel Export**: ~2-5 seconds for large datasets
- **Memory Footprint**: ~50MB for typical usage

### 3. Frontend Performance
- **Initial Load**: ~2-3 seconds
- **Configuration Updates**: Real-time
- **Chart Rendering**: ~100-500ms
- **Excel Operations**: ~1-3 seconds

## Current Limitations and Issues

### 1. Data Management Issues
- **Hardcoded Values**: 20,000+ lines in Python files
- **Data Conversion**: Complex Excel ↔ JSON transformations
- **Field Mapping**: Inconsistent naming conventions
- **Type Safety**: Mixed dict/object structures

### 2. User Experience Issues
- **Complex Configuration**: Difficult to understand data structure
- **Error Handling**: Limited feedback on import errors
- **Validation**: Basic validation with unclear error messages
- **Workflow**: No guided setup process

### 3. Technical Debt
- **Code Duplication**: Similar logic across services
- **Error Handling**: Inconsistent error management
- **Testing**: Limited test coverage
- **Documentation**: Minimal inline documentation

## Integration Points

### 1. External Systems
- **Excel Files**: Primary data import/export format
- **File System**: JSON configuration storage
- **Web Browser**: Frontend interface

### 2. APIs and Endpoints
- **REST API**: All backend functionality exposed
- **File Upload**: Excel import endpoints
- **File Download**: Excel export endpoints
- **Health Checks**: System monitoring endpoints

### 3. Data Formats
- **JSON**: Internal data representation
- **Excel**: User-facing data format
- **CSV**: Alternative export format
- **TypeScript**: Frontend type definitions

## Security and Access Control

### 1. Current State
- **No Authentication**: Open access to all functionality
- **No Authorization**: No role-based access control
- **No Data Isolation**: All users see all data
- **No Audit Trail**: No tracking of changes

### 2. Data Protection
- **Input Validation**: Basic validation on API inputs
- **Error Handling**: Limited exposure of internal errors
- **File Upload**: Basic file type validation
- **No Encryption**: Data stored in plain text

## Monitoring and Observability

### 1. Logging
- **Console Logging**: Basic print statements
- **Error Logging**: Exception handling with logging
- **Performance Logging**: Basic timing information
- **No Structured Logging**: Limited log analysis capability

### 2. Health Monitoring
- **Health Endpoints**: Basic system status
- **No Metrics**: No performance metrics collection
- **No Alerts**: No automated alerting
- **No Dashboards**: No operational dashboards

## Deployment and Infrastructure

### 1. Current Deployment
- **Local Development**: Python virtual environment
- **No Containerization**: Direct Python execution
- **No Orchestration**: Manual process management
- **No CI/CD**: Manual deployment process

### 2. Configuration Management
- **Environment Variables**: Limited use
- **Configuration Files**: JSON and Python files
- **No Secrets Management**: Hardcoded sensitive data
- **No Environment Separation**: Single configuration

## Future Architecture Considerations

### 1. Scalability Needs
- **Multi-User Support**: Current single-user design
- **Data Volume**: Growing configuration complexity
- **Performance**: Larger simulation requirements
- **Integration**: External system connections

### 2. Maintainability Improvements
- **Code Organization**: Better service separation
- **Testing**: Comprehensive test coverage
- **Documentation**: Improved code documentation
- **Error Handling**: Consistent error management

### 3. User Experience Enhancements
- **Workflow Optimization**: Streamlined user processes
- **Data Validation**: Better error messages and guidance
- **Visualization**: Enhanced charts and reports
- **Accessibility**: Improved usability features

This architecture document provides a comprehensive overview of the current SimpleSim system, highlighting both its capabilities and areas for improvement in the new business planning platform. 