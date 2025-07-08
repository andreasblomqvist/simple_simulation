# Data Handling and Configuration Solution

## Executive Summary

The current SimpleSim system suffers from critical data handling and configuration issues that have been major pain points:

1. **Hardcoded Values**: Extensive hardcoded data in Python files
2. **Data Conversion Issues**: Complex currency and unit conversions
3. **Data Mapping Problems**: Inconsistent field naming and structure mapping
4. **Dict vs Objects Confusion**: Mixed data structures causing type errors
5. **Excel Import/Export Complexity**: Fragile data transformation pipelines

This document outlines a comprehensive solution for the new business planning platform.

## Current Problems Analysis

### 1. Hardcoded Configuration Values

**Problem**: Massive hardcoded data in `default_config.py`:
- 20,000+ lines of hardcoded pricing, salary, and headcount data
- Currency conversion rates embedded in code
- Office mappings and level distributions hardcoded
- No way to update without code changes

**Impact**:
- Cannot run simulations with desired numbers
- Requires developer intervention for data updates
- No audit trail for configuration changes
- Difficult to maintain multiple scenarios

### 2. Data Conversion and Mapping Issues

**Problem**: Complex data transformation between formats:
- Excel ↔ JSON ↔ Python objects ↔ API responses
- Inconsistent field naming (`fte` vs `total`, `price_1` vs `Price_1`)
- Currency conversion scattered across codebase
- Type conversion errors (strings to floats, NaN handling)

**Impact**:
- Data corruption during import/export
- Simulation results based on wrong data
- Debugging nightmares with data flow
- User confusion about what data is being used

### 3. Dict vs Objects Confusion

**Problem**: Mixed data structures throughout the system:
- Some services use dataclasses, others use dictionaries
- Inconsistent serialization/deserialization
- Type hints not enforced
- Runtime errors from structure mismatches

**Impact**:
- Type errors during simulation execution
- Inconsistent API responses
- Difficult to maintain and extend
- Poor developer experience

### 4. Excel Import/Export Complexity

**Problem**: Fragile data transformation pipeline:
- Complex field mapping between Excel and internal format
- No validation of imported data
- Silent failures during import
- Inconsistent export formats

**Impact**:
- Users cannot reliably import their data
- Export files don't match import expectations
- Data loss during round-trip operations
- Poor user experience

## Solution Architecture

### 1. Unified Data Model

#### Core Data Structures

```python
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from decimal import Decimal
from enum import Enum

@dataclass
class Currency:
    code: str  # SEK, EUR, USD, etc.
    name: str
    symbol: str
    exchange_rate_to_sek: Decimal

@dataclass
class Level:
    name: str  # A, AC, C, SrC, AM, M, SrM, PiP
    display_name: str
    sort_order: int
    roles: List[str]  # Which roles can have this level

@dataclass
class Role:
    name: str  # Consultant, Sales, Recruitment, Operations
    display_name: str
    has_levels: bool  # True for Consultant/Sales/Recruitment, False for Operations
    levels: List[str]  # Which levels this role supports

@dataclass
class Office:
    code: str  # STO, MUN, AMS, etc.
    name: str  # Stockholm, Munich, Amsterdam
    currency: Currency
    timezone: str
    region: str

@dataclass
class BaselineValue:
    """Represents a single baseline value for a specific field"""
    office_code: str
    role_name: str
    level_name: Optional[str]  # None for flat roles like Operations
    field_name: str  # fte, price, salary, utr, etc.
    month: int  # 1-12
    value: Decimal
    currency: Currency
    last_updated: datetime
    updated_by: str

@dataclass
class ScenarioAdjustment:
    """Represents a scenario adjustment (multiplier/lever)"""
    scenario_id: str
    office_code: str
    role_name: str
    level_name: Optional[str]
    field_name: str
    month: int  # 1-12
    multiplier: Decimal  # 1.0 = no change, 1.1 = 10% increase
    description: str
    created_by: str
    created_at: datetime
```

#### Configuration Schema

```python
@dataclass
class SystemConfiguration:
    """Complete system configuration"""
    version: str
    currencies: Dict[str, Currency]
    levels: Dict[str, Level]
    roles: Dict[str, Role]
    offices: Dict[str, Office]
    baseline_values: List[BaselineValue]
    metadata: Dict[str, Any]

@dataclass
class BusinessPlan:
    """A complete business plan for an office"""
    id: str
    office_code: str
    name: str
    description: str
    baseline_values: List[BaselineValue]
    scenario_adjustments: List[ScenarioAdjustment]
    created_by: str
    created_at: datetime
    status: str  # draft, submitted, approved, rejected
    approved_by: Optional[str]
    approved_at: Optional[datetime]
```

### 2. Data Validation and Transformation

#### Validation Rules

```python
from pydantic import BaseModel, validator, Field
from typing import Dict, List, Optional

class BaselineValueValidator(BaseModel):
    office_code: str = Field(..., regex=r'^[A-Z]{3}$')
    role_name: str = Field(..., regex=r'^(Consultant|Sales|Recruitment|Operations)$')
    level_name: Optional[str] = Field(None, regex=r'^(A|AC|C|SrC|AM|M|SrM|PiP)$')
    field_name: str = Field(..., regex=r'^(fte|price|salary|utr|recruitment|churn|progression)$')
    month: int = Field(..., ge=1, le=12)
    value: Decimal = Field(..., ge=0)
    currency_code: str = Field(..., regex=r'^[A-Z]{3}$')

    @validator('level_name')
    def validate_level_for_role(cls, v, values):
        role_name = values.get('role_name')
        if role_name == 'Operations' and v is not None:
            raise ValueError('Operations role cannot have levels')
        if role_name != 'Operations' and v is None:
            raise ValueError('Non-Operations roles must have a level')
        return v

    @validator('value')
    def validate_value_ranges(cls, v, values):
        field_name = values.get('field_name')
        if field_name == 'fte' and v > 1000:
            raise ValueError('FTE value too high')
        if field_name == 'utr' and (v < 0 or v > 1):
            raise ValueError('UTR must be between 0 and 1')
        return v
```

#### Data Transformation Service

```python
class DataTransformationService:
    """Handles all data transformations between formats"""
    
    def __init__(self, config: SystemConfiguration):
        self.config = config
    
    def excel_to_baseline_values(self, df: pd.DataFrame) -> List[BaselineValue]:
        """Convert Excel DataFrame to baseline values"""
        baseline_values = []
        
        for _, row in df.iterrows():
            try:
                # Validate and transform each row
                office_code = self._normalize_office_code(row['Office'])
                role_name = self._normalize_role_name(row['Role'])
                level_name = self._normalize_level_name(row['Level'])
                
                # Process each field
                for month in range(1, 13):
                    for field in ['fte', 'price', 'salary', 'utr', 'recruitment', 'churn']:
                        excel_col = f'{field.capitalize()}_{month}'
                        if excel_col in row and pd.notna(row[excel_col]):
                            value = self._convert_to_decimal(row[excel_col])
                            currency = self.config.offices[office_code].currency
                            
                            baseline_value = BaselineValue(
                                office_code=office_code,
                                role_name=role_name,
                                level_name=level_name,
                                field_name=field,
                                month=month,
                                value=value,
                                currency=currency,
                                last_updated=datetime.now(),
                                updated_by='excel_import'
                            )
                            baseline_values.append(baseline_value)
                            
            except Exception as e:
                raise ValueError(f"Error processing row {_}: {e}")
        
        return baseline_values
    
    def baseline_values_to_excel(self, baseline_values: List[BaselineValue]) -> pd.DataFrame:
        """Convert baseline values to Excel DataFrame"""
        # Group by office, role, level
        grouped_data = {}
        
        for value in baseline_values:
            key = (value.office_code, value.role_name, value.level_name)
            if key not in grouped_data:
                grouped_data[key] = {}
            
            field_key = f"{value.field_name}_{value.month}"
            grouped_data[key][field_key] = value.value
        
        # Convert to DataFrame
        rows = []
        for (office_code, role_name, level_name), fields in grouped_data.items():
            row = {
                'Office': office_code,
                'Role': role_name,
                'Level': level_name or 'N/A'
            }
            row.update(fields)
            rows.append(row)
        
        return pd.DataFrame(rows)
    
    def _normalize_office_code(self, office: str) -> str:
        """Normalize office name to code"""
        office_mapping = {
            'Stockholm': 'STO',
            'Munich': 'MUN',
            'Amsterdam': 'AMS',
            # ... etc
        }
        return office_mapping.get(office, office.upper())
    
    def _convert_to_decimal(self, value: Any) -> Decimal:
        """Safely convert any value to Decimal"""
        if pd.isna(value):
            return Decimal('0')
        if isinstance(value, str):
            # Handle comma-separated numbers
            value = value.replace(',', '.')
        return Decimal(str(value))
```

### 3. Configuration Management

#### Configuration Service

```python
class ConfigurationService:
    """Manages all system configuration"""
    
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.config: Optional[SystemConfiguration] = None
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from storage"""
        config_file = os.path.join(self.storage_path, 'system_config.json')
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                data = json.load(f)
                self.config = self._deserialize_config(data)
        else:
            self.config = self._create_default_config()
            self._save_configuration()
    
    def _create_default_config(self) -> SystemConfiguration:
        """Create default system configuration"""
        return SystemConfiguration(
            version="2.0.0",
            currencies={
                'SEK': Currency('SEK', 'Swedish Krona', 'kr', Decimal('1.0')),
                'EUR': Currency('EUR', 'Euro', '€', Decimal('10.9635')),
                'USD': Currency('USD', 'US Dollar', '$', Decimal('8.5')),
            },
            levels={
                'A': Level('A', 'Analyst', 1, ['Consultant', 'Sales', 'Recruitment']),
                'AC': Level('AC', 'Associate Consultant', 2, ['Consultant', 'Sales', 'Recruitment']),
                'C': Level('C', 'Consultant', 3, ['Consultant', 'Sales', 'Recruitment']),
                'SrC': Level('SrC', 'Senior Consultant', 4, ['Consultant', 'Sales', 'Recruitment']),
                'AM': Level('AM', 'Associate Manager', 5, ['Consultant', 'Sales', 'Recruitment']),
                'M': Level('M', 'Manager', 6, ['Consultant', 'Sales', 'Recruitment']),
                'SrM': Level('SrM', 'Senior Manager', 7, ['Consultant', 'Sales', 'Recruitment']),
                'PiP': Level('PiP', 'Partner in Practice', 8, ['Consultant', 'Sales', 'Recruitment']),
            },
            roles={
                'Consultant': Role('Consultant', 'Consultant', True, ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']),
                'Sales': Role('Sales', 'Sales', True, ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']),
                'Recruitment': Role('Recruitment', 'Recruitment', True, ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']),
                'Operations': Role('Operations', 'Operations', False, []),
            },
            offices={
                'STO': Office('STO', 'Stockholm', self.config.currencies['SEK'], 'Europe/Stockholm', 'Nordic'),
                'MUN': Office('MUN', 'Munich', self.config.currencies['EUR'], 'Europe/Berlin', 'DACH'),
                'AMS': Office('AMS', 'Amsterdam', self.config.currencies['EUR'], 'Europe/Amsterdam', 'Benelux'),
            },
            baseline_values=[],
            metadata={}
        )
    
    def import_baseline_from_excel(self, file_path: str, user_id: str) -> ImportResult:
        """Import baseline values from Excel file"""
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Transform to baseline values
            transformer = DataTransformationService(self.config)
            baseline_values = transformer.excel_to_baseline_values(df)
            
            # Validate all values
            validator = BaselineValueValidator()
            for value in baseline_values:
                validator.validate(value)
            
            # Update configuration
            self.config.baseline_values = baseline_values
            
            # Save configuration
            self._save_configuration()
            
            return ImportResult(
                success=True,
                imported_count=len(baseline_values),
                errors=[],
                warnings=[]
            )
            
        except Exception as e:
            return ImportResult(
                success=False,
                imported_count=0,
                errors=[str(e)],
                warnings=[]
            )
    
    def export_baseline_to_excel(self, file_path: str, office_codes: Optional[List[str]] = None):
        """Export baseline values to Excel file"""
        # Filter baseline values by office if specified
        baseline_values = self.config.baseline_values
        if office_codes:
            baseline_values = [v for v in baseline_values if v.office_code in office_codes]
        
        # Transform to Excel format
        transformer = DataTransformationService(self.config)
        df = transformer.baseline_values_to_excel(baseline_values)
        
        # Save to Excel
        df.to_excel(file_path, index=False)
```

### 4. Excel Import/Export System

#### Template Generation

```python
class ExcelTemplateService:
    """Generates Excel templates for data entry"""
    
    def __init__(self, config: SystemConfiguration):
        self.config = config
    
    def generate_baseline_template(self, office_codes: List[str]) -> bytes:
        """Generate Excel template for baseline data entry"""
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Baseline Data"
        
        # Create headers
        headers = ['Office', 'Role', 'Level']
        for month in range(1, 13):
            headers.extend([
                f'FTE_{month}', f'Price_{month}', f'Salary_{month}', 
                f'UTR_{month}', f'Recruitment_{month}', f'Churn_{month}'
            ])
        
        # Write headers
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        
        # Generate data rows
        row = 2
        for office_code in office_codes:
            office = self.config.offices[office_code]
            
            for role_name, role in self.config.roles.items():
                if role.has_levels:
                    # Roles with levels
                    for level_name in role.levels:
                        ws.cell(row=row, column=1, value=office.name)
                        ws.cell(row=row, column=2, value=role.display_name)
                        ws.cell(row=row, column=3, value=level_name)
                        row += 1
                else:
                    # Flat roles (Operations)
                    ws.cell(row=row, column=1, value=office.name)
                    ws.cell(row=row, column=2, value=role.display_name)
                    ws.cell(row=row, column=3, value='N/A')
                    row += 1
        
        # Add validation and formatting
        self._add_data_validation(ws)
        self._add_instructions_sheet(wb)
        
        # Save to bytes
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()
    
    def _add_data_validation(self, ws):
        """Add data validation to worksheet"""
        # Add dropdown for Office column
        office_names = [office.name for office in self.config.offices.values()]
        for row in range(2, ws.max_row + 1):
            cell = ws.cell(row=row, column=1)
            cell.data_validation = DataValidation(
                type="list",
                formula1=f'"{",".join(office_names)}"',
                allow_blank=True
            )
        
        # Add dropdown for Role column
        role_names = [role.display_name for role in self.config.roles.values()]
        for row in range(2, ws.max_row + 1):
            cell = ws.cell(row=row, column=2)
            cell.data_validation = DataValidation(
                type="list",
                formula1=f'"{",".join(role_names)}"',
                allow_blank=True
            )
    
    def _add_instructions_sheet(self, wb):
        """Add instructions sheet to workbook"""
        ws = wb.create_sheet("Instructions")
        
        instructions = [
            ["Baseline Data Entry Instructions"],
            [""],
            ["1. Office: Select the office from the dropdown"],
            ["2. Role: Select the role (Consultant, Sales, Recruitment, Operations)"],
            ["3. Level: For roles with levels, enter the level (A, AC, C, etc.)"],
            ["4. FTE: Full-Time Equivalent headcount"],
            ["5. Price: Hourly rate in local currency"],
            ["6. Salary: Monthly salary in local currency"],
            ["7. UTR: Utilization rate (0.0 to 1.0)"],
            ["8. Recruitment: Monthly recruitment rate (0.0 to 1.0)"],
            ["9. Churn: Monthly churn rate (0.0 to 1.0)"],
            [""],
            ["Notes:"],
            ["- Operations role does not have levels (use N/A)"],
            ["- All rates should be between 0.0 and 1.0"],
            ["- Currency will be automatically converted to SEK for calculations"],
        ]
        
        for row_idx, instruction in enumerate(instructions, 1):
            ws.cell(row=row_idx, column=1, value=instruction[0])
```

#### Import Validation and Error Handling

```python
class ExcelImportValidator:
    """Validates Excel imports and provides detailed error reporting"""
    
    def __init__(self, config: SystemConfiguration):
        self.config = config
    
    def validate_excel_file(self, df: pd.DataFrame) -> ValidationResult:
        """Validate Excel file structure and content"""
        errors = []
        warnings = []
        
        # Check required columns
        required_columns = ['Office', 'Role', 'Level']
        for month in range(1, 13):
            required_columns.extend([
                f'FTE_{month}', f'Price_{month}', f'Salary_{month}',
                f'UTR_{month}', f'Recruitment_{month}', f'Churn_{month}'
            ])
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Validate each row
        for row_idx, row in df.iterrows():
            row_errors = self._validate_row(row, row_idx + 2)  # +2 for 1-based indexing and header
            errors.extend(row_errors)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            row_count=len(df)
        )
    
    def _validate_row(self, row: pd.Series, row_num: int) -> List[str]:
        """Validate a single row"""
        errors = []
        
        # Validate Office
        office = row.get('Office')
        if pd.isna(office):
            errors.append(f"Row {row_num}: Office is required")
        elif office not in [o.name for o in self.config.offices.values()]:
            errors.append(f"Row {row_num}: Invalid office '{office}'")
        
        # Validate Role
        role = row.get('Role')
        if pd.isna(role):
            errors.append(f"Row {row_num}: Role is required")
        elif role not in [r.display_name for r in self.config.roles.values()]:
            errors.append(f"Row {row_num}: Invalid role '{role}'")
        
        # Validate Level
        level = row.get('Level')
        role_obj = next((r for r in self.config.roles.values() if r.display_name == role), None)
        if role_obj:
            if role_obj.has_levels:
                if pd.isna(level) or level == 'N/A':
                    errors.append(f"Row {row_num}: Level is required for role '{role}'")
                elif level not in [l.name for l in self.config.levels.values()]:
                    errors.append(f"Row {row_num}: Invalid level '{level}' for role '{role}'")
            else:
                if not pd.isna(level) and level != 'N/A':
                    errors.append(f"Row {row_num}: Role '{role}' does not have levels, use 'N/A'")
        
        # Validate numeric fields
        for month in range(1, 13):
            for field in ['FTE', 'Price', 'Salary', 'UTR', 'Recruitment', 'Churn']:
                col_name = f'{field}_{month}'
                value = row.get(col_name)
                
                if not pd.isna(value):
                    try:
                        num_value = float(value)
                        if field == 'UTR' and (num_value < 0 or num_value > 1):
                            errors.append(f"Row {row_num}: {col_name} must be between 0 and 1")
                        elif field in ['Recruitment', 'Churn'] and (num_value < 0 or num_value > 1):
                            errors.append(f"Row {row_num}: {col_name} must be between 0 and 1")
                        elif field == 'FTE' and num_value < 0:
                            errors.append(f"Row {row_num}: {col_name} must be non-negative")
                    except ValueError:
                        errors.append(f"Row {row_num}: {col_name} must be a number")
        
        return errors
```

### 5. Migration Strategy

#### Phase 1: Data Model Migration

1. **Create new data models** with proper validation
2. **Build configuration service** with JSON storage
3. **Create data transformation service** for Excel ↔ JSON conversion
4. **Add validation and error handling**

#### Phase 2: Backend Migration

1. **Replace hardcoded config** with dynamic configuration service
2. **Update simulation engine** to use new data models
3. **Add configuration API endpoints**
4. **Implement Excel import/export with validation**

#### Phase 3: Frontend Migration

1. **Update frontend** to use new API endpoints
2. **Add Excel template download**
3. **Implement validation feedback**
4. **Add configuration management UI**

#### Phase 4: Data Migration

1. **Export current data** from hardcoded config
2. **Transform to new format** using migration scripts
3. **Validate migrated data**
4. **Deploy new system**

## Implementation Benefits

### 1. Eliminate Hardcoded Values
- **Dynamic Configuration**: All data stored in JSON files
- **User-Editable**: Office owners can update their own data
- **Version Control**: Track configuration changes over time
- **Audit Trail**: Know who changed what and when

### 2. Consistent Data Handling
- **Single Source of Truth**: One data model for entire system
- **Type Safety**: Pydantic validation prevents runtime errors
- **Currency Handling**: Centralized currency conversion
- **Data Integrity**: Validation ensures data quality

### 3. Improved Excel Integration
- **Template Generation**: Pre-filled Excel templates
- **Validation**: Real-time error checking during import
- **Error Reporting**: Clear feedback on import issues
- **Round-trip Safety**: Import → Export → Import works correctly

### 4. Better Developer Experience
- **Clear Data Models**: Well-defined dataclasses
- **Type Hints**: Full type safety throughout
- **Validation**: Catch errors early
- **Documentation**: Self-documenting code

## Success Metrics

1. **Zero Hardcoded Values**: All configuration in external files
2. **100% Data Validation**: No invalid data in system
3. **Seamless Excel Integration**: Import/export works reliably
4. **User Self-Service**: Office owners can manage their own data
5. **Developer Productivity**: Faster feature development

## Next Steps

1. **Create detailed implementation plan** with specific tasks
2. **Build proof of concept** with new data models
3. **Migrate one office** as pilot
4. **Validate approach** with real data
5. **Roll out to all offices**

This solution addresses all the major pain points while providing a solid foundation for the new business planning platform. 