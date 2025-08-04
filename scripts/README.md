# Business Plan Data Population Scripts

This directory contains scripts to populate the business planning system with realistic test data.

## 📁 Files Overview

### Core Scripts
- **`populate_business_plan.py`** - Populates business plan data via API (requires running backend)
- **`generate_test_business_plan_data.py`** - Generates JSON test data files (offline)
- **`setup_business_plan_data.sh`** - Master script to run both operations easily
- **`demo_business_plan.js`** - JavaScript demo for working with the test data

### Generated Data
- **`test_data/`** - Directory containing generated JSON test files
  - `business_plan_test_data.json` - Complete dataset for all offices
  - `business_plan_stockholm-office.json` - Stockholm office data
  - `business_plan_gothenburg-office.json` - Gothenburg office data  
  - `business_plan_malmo-office.json` - Malmö office data

## 🚀 Quick Start

### Option 1: Use the Master Script (Recommended)
```bash
# Generate test data AND populate via API
./setup_business_plan_data.sh

# Only generate JSON files
./setup_business_plan_data.sh generate

# Only populate via API (requires backend running)
./setup_business_plan_data.sh populate
```

### Option 2: Run Scripts Individually

#### Generate Test Data Files
```bash
python3 generate_test_business_plan_data.py
```

#### Populate via API
```bash
# Start backend first
cd ../backend
uvicorn main:app --reload

# Then populate
python3 populate_business_plan.py
```

## 📊 Test Data Structure

### Offices
- **Stockholm** - Mature Office (679 FTE)
- **Gothenburg** - Established Office (234 FTE)  
- **Malmö** - Emerging Office (87 FTE)

### Roles and Levels
- **Consultant** (A, AC, C, SrC, AM, M, SrM, PiP) - Has price/UTR
- **Sales** (A, AC, C, SrC, AM, M, SrM, PiP) - No price/UTR
- **Recruitment** (A, AC, C, SrC, AM, M, SrM, PiP) - No price/UTR
- **Operations** (General) - Flat role, no price/UTR

### Data Points per Entry
- **recruitment** - Monthly recruitment rate
- **churn** - Monthly churn rate  
- **salary** - Monthly salary cost
- **price** - Hourly price (billable roles only)
- **utr** - Utilization rate (billable roles only)

### Realistic Variations
- **Journey-based**: Different multipliers for Emerging/Established/Mature offices
- **Level-based**: Higher values for senior levels
- **Seasonal**: Higher activity in Q1 and Q3
- **Role-specific**: Different base rates for each role type

## 🎯 Usage Examples

### Frontend Integration
```typescript
// Load test data in React component
const [businessPlan, setBusinessPlan] = useState(null);

useEffect(() => {
  // Load from API or test file
  fetch('/api/business-plans?office_id=stockholm-office&year=2025')
    .then(res => res.json())
    .then(data => setBusinessPlan(data));
}, []);

// Use with ExpandablePlanningGrid
<ExpandablePlanningGrid 
  office={office}
  year={2025}
  onYearChange={setYear}
/>
```

### Browser Console Demo
```javascript
// Load demo functions
// Then run:
window.businessPlanDemo.run()
```

## 📈 Data Statistics

- **3 offices** with different journey stages
- **12 months** of data for 2025
- **4 roles** with 25 total role-level combinations
- **36 monthly plans** total (12 months × 3 offices)
- **900 total entries** across all plans

## 🔧 Customization

### Modify Base Values
Edit values in `generate_test_business_plan_data.py`:

```python
# Level-based data
LEVEL_DATA = {
    "A": {"salary_base": 42000, "price_base": 95, "recruitment": 0.08},
    # ... modify as needed
}

# Journey multipliers  
JOURNEY_MULTIPLIERS = {
    "Emerging Office": {"recruitment": 1.5, "salary": 0.9},
    # ... modify as needed
}
```

### Add More Offices
Add to the `OFFICES` list:

```python
OFFICES = [
    # ... existing offices
    {
        "id": "new-office",
        "name": "New Office", 
        "journey": "Emerging Office",
        "total_fte": 50
    }
]
```

## 🧪 Testing

### Verify Generated Data
```bash
# Check file structure
ls -la test_data/

# Validate JSON format
python3 -m json.tool test_data/business_plan_test_data.json > /dev/null && echo "Valid JSON"

# Count entries
cat test_data/business_plan_test_data.json | jq '.business_plans | length'
```

### Test API Population
```bash
# Check if backend is running
curl http://localhost:8000/docs

# Test business plan endpoint
curl http://localhost:8000/business-plans
```

## 🚨 Troubleshooting

### Backend Not Starting
- Check Python virtual environment is activated
- Install dependencies: `pip install -r requirements.txt`
- Check port 8000 is available

### API Population Fails
- Verify backend is running: `curl http://localhost:8000/docs`
- Check database connectivity
- Review API endpoint URLs in populate script

### Missing Test Data
- Run generation script: `python3 generate_test_business_plan_data.py`
- Check permissions on `test_data/` directory
- Verify Python path includes script directory

## 📚 Next Steps

1. **Start the frontend**: `cd frontend && npm run dev`
2. **Navigate to Business Planning** section in the app
3. **Select an office** to see populated data
4. **Test the expandable grid** interface
5. **Modify values** to test the editing functionality

## 🤝 Contributing

To add new test scenarios or modify existing data:

1. Update the generation scripts with new patterns
2. Re-run the generation: `./setup_business_plan_data.sh generate`
3. Test with the frontend interface
4. Document any new data structures or patterns