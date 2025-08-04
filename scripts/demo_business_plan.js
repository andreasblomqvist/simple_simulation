/**
 * Business Plan Demo Script
 * 
 * This script demonstrates how to work with the generated business plan test data
 * Can be run in browser console or used as reference for frontend integration
 */

// Load test data (this would typically come from API)
async function loadTestData() {
    try {
        const response = await fetch('./test_data/business_plan_test_data.json');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Failed to load test data:', error);
        return null;
    }
}

// Demo function to show business plan data structure
function demonstrateBusinessPlanData() {
    console.log('🚀 Business Plan Demo');
    console.log('==================');
    
    // Sample business plan entry structure
    const sampleEntry = {
        "role": "Consultant",
        "level": "A",
        "recruitment": 0.096,
        "churn": 0.036,
        "salary": 37800,
        "price": 90,
        "utr": 0.75
    };
    
    console.log('📋 Sample Business Plan Entry:', sampleEntry);
    
    // Show how entries are organized by office and month
    const sampleMonthlyPlan = {
        "id": "stockholm-office-2025-01",
        "office_id": "stockholm-office",
        "year": 2025,
        "month": 1,
        "entries": [sampleEntry] // Array of entries for all roles/levels
    };
    
    console.log('📅 Sample Monthly Plan Structure:', sampleMonthlyPlan);
    
    // Show available roles and levels
    const roles = {
        "Consultant": ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"], // Has price/UTR
        "Sales": ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"],      // No price/UTR
        "Recruitment": ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"], // No price/UTR
        "Operations": ["General"]                                        // Flat role, no price/UTR
    };
    
    console.log('👥 Available Roles and Levels:', roles);
    
    // Show office types
    const offices = [
        { "name": "Stockholm", "journey": "Mature Office", "total_fte": 679 },
        { "name": "Gothenburg", "journey": "Established Office", "total_fte": 234 },
        { "name": "Malmö", "journey": "Emerging Office", "total_fte": 87 }
    ];
    
    console.log('🏢 Test Offices:', offices);
}

// Function to calculate totals from business plan data
function calculateBusinessPlanTotals(monthlyPlan) {
    const totals = {
        recruitment: 0,
        churn: 0,
        salary_cost: 0,
        revenue_potential: 0,
        net_growth: 0
    };
    
    monthlyPlan.entries.forEach(entry => {
        totals.recruitment += entry.recruitment;
        totals.churn += entry.churn;
        totals.salary_cost += entry.salary;
        
        // Revenue calculation for billable roles
        if (entry.price > 0 && entry.utr > 0) {
            // Assuming 166.4 working hours per month
            const monthly_revenue = entry.price * entry.utr * 166.4;
            totals.revenue_potential += monthly_revenue;
        }
    });
    
    totals.net_growth = totals.recruitment - totals.churn;
    
    return totals;
}

// Function to generate summary statistics
function generateBusinessPlanSummary(businessPlans) {
    const summary = {
        total_plans: businessPlans.length,
        offices: new Set(),
        months: new Set(),
        years: new Set(),
        total_entries: 0,
        roles: new Set(),
        levels: new Set()
    };
    
    businessPlans.forEach(plan => {
        summary.offices.add(plan.office_id);
        summary.months.add(plan.month);
        summary.years.add(plan.year);
        summary.total_entries += plan.entries.length;
        
        plan.entries.forEach(entry => {
            summary.roles.add(entry.role);
            summary.levels.add(entry.level);
        });
    });
    
    return {
        ...summary,
        offices: Array.from(summary.offices),
        months: Array.from(summary.months).sort((a, b) => a - b),
        years: Array.from(summary.years).sort((a, b) => a - b),
        roles: Array.from(summary.roles),
        levels: Array.from(summary.levels)
    };
}

// Main demo function
async function runBusinessPlanDemo() {
    console.clear();
    console.log('🎯 Business Plan Test Data Demo');
    console.log('===============================\n');
    
    // Show data structure
    demonstrateBusinessPlanData();
    
    console.log('\n📊 Calculation Examples:');
    console.log('========================');
    
    // Example calculations
    const examplePlan = {
        entries: [
            { role: "Consultant", level: "A", recruitment: 0.08, churn: 0.03, salary: 42000, price: 95, utr: 0.75 },
            { role: "Sales", level: "AC", recruitment: 0.06, churn: 0.025, salary: 48000, price: 0, utr: 0 },
            { role: "Operations", level: "General", recruitment: 0.02, churn: 0.02, salary: 50000, price: 0, utr: 0 }
        ]
    };
    
    const totals = calculateBusinessPlanTotals(examplePlan);
    console.log('💰 Example Calculations:', totals);
    
    console.log('\n🚀 Usage Instructions:');
    console.log('======================');
    console.log('1. Load test data from ./test_data/ directory');
    console.log('2. Use business_plan_test_data.json for complete dataset');
    console.log('3. Use individual office files for specific office data');
    console.log('4. Integrate with ExpandablePlanningGrid component');
    console.log('5. Use businessPlanStore for state management');
    
    console.log('\n📁 Available Test Files:');
    console.log('========================');
    console.log('• business_plan_test_data.json - Complete dataset');
    console.log('• business_plan_stockholm-office.json - Stockholm data');
    console.log('• business_plan_gothenburg-office.json - Gothenburg data');
    console.log('• business_plan_malmo-office.json - Malmö data');
}

// Export functions for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        loadTestData,
        demonstrateBusinessPlanData,
        calculateBusinessPlanTotals,
        generateBusinessPlanSummary,
        runBusinessPlanDemo
    };
}

// Auto-run demo if in browser
if (typeof window !== 'undefined') {
    // Add to window for easy access in console
    window.businessPlanDemo = {
        loadTestData,
        demonstrateBusinessPlanData,
        calculateBusinessPlanTotals,
        generateBusinessPlanSummary,
        run: runBusinessPlanDemo
    };
    
    console.log('💡 Business Plan Demo loaded! Run window.businessPlanDemo.run() to start');
}