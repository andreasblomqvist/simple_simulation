"""
Financial Planning Service
Comprehensive financial planning and expense management service
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from pathlib import Path

from src.models.financial_structure import (
    ComprehensiveFinancialModel,
    BudgetPlan,
    CurrencyCode,
    FinancialTimeSeries,
    MonthlyFinancialValue,
    SalaryComponents,
    StaffCostsByRole,
    OfficeExpenses,
    OfficeExpenseItem,
    RevenueStream,
    ProjectCosts,
    SalesMetrics,
    FinancialKPIs,
    BudgetActualComparison
)


class FinancialPlanningService:
    """Service for comprehensive financial planning and analysis"""
    
    def __init__(self):
        self.storage_dir = Path(__file__).parent.parent.parent / "data" / "financial_plans"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.models: Dict[str, ComprehensiveFinancialModel] = {}
        self.budget_plans: Dict[str, BudgetPlan] = {}
        self._load_existing_data()
    
    def _load_existing_data(self):
        """Load existing financial models and budget plans"""
        # Load financial models
        models_dir = self.storage_dir / "models"
        models_dir.mkdir(exist_ok=True)
        for file_path in models_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    model_id = data.get('model_id')
                    if model_id:
                        # Would deserialize to ComprehensiveFinancialModel
                        self.models[model_id] = data
            except Exception as e:
                print(f"Warning: Could not load financial model from {file_path}: {e}")
        
        # Load budget plans
        plans_dir = self.storage_dir / "plans"
        plans_dir.mkdir(exist_ok=True)
        for file_path in plans_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    plan_id = data.get('plan_id')
                    if plan_id:
                        # Would deserialize to BudgetPlan
                        self.budget_plans[plan_id] = data
            except Exception as e:
                print(f"Warning: Could not load budget plan from {file_path}: {e}")
    
    # Financial Model Management
    
    def create_financial_model(
        self,
        office_id: str,
        office_name: str,
        currency: CurrencyCode,
        fiscal_year: int,
        baseline_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a comprehensive financial model"""
        model_id = f"fm_{office_id}_{fiscal_year}_{datetime.now().strftime('%Y%m%d')}"
        
        # Initialize with baseline data if provided, otherwise use defaults
        financial_model = {
            "model_id": model_id,
            "office_id": office_id,
            "office_name": office_name,
            "currency": currency,
            "fiscal_year": fiscal_year,
            "revenue_streams": baseline_data.get("revenue_streams", []) if baseline_data else [],
            "staff_costs": baseline_data.get("staff_costs", []) if baseline_data else [],
            "office_expenses": baseline_data.get("office_expenses", {}) if baseline_data else {},
            "project_costs": baseline_data.get("project_costs", {}) if baseline_data else {},
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        self.models[model_id] = financial_model
        self._save_financial_model(model_id)
        
        return model_id
    
    def get_financial_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a financial model"""
        return self.models.get(model_id)
    
    def update_financial_model(
        self,
        model_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update a financial model"""
        if model_id not in self.models:
            return False
        
        model = self.models[model_id]
        model.update(updates)
        model["updated_at"] = datetime.now().isoformat()
        
        self._save_financial_model(model_id)
        return True
    
    def _save_financial_model(self, model_id: str):
        """Save financial model to storage"""
        model = self.models[model_id]
        file_path = self.storage_dir / "models" / f"{model_id}.json"
        
        try:
            with open(file_path, 'w') as f:
                json.dump(model, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Warning: Could not save financial model {model_id}: {e}")
    
    # Expense Structure Management
    
    def create_expense_breakdown(
        self,
        model_id: str,
        expense_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create detailed expense breakdown following Planacy structure"""
        
        # Staff costs breakdown (mirrors the role-based cost structure)
        staff_costs = self._create_staff_cost_structure(
            expense_data.get("staff_data", {}),
            model_id
        )
        
        # Office expenses breakdown (mirrors Planacy expense categories)
        office_expenses = self._create_office_expense_structure(
            expense_data.get("office_data", {}),
            model_id
        )
        
        # Revenue breakdown
        revenue_streams = self._create_revenue_structure(
            expense_data.get("revenue_data", {}),
            model_id
        )
        
        # Calculate KPIs
        kpis = self._calculate_financial_kpis(
            staff_costs, office_expenses, revenue_streams
        )
        
        breakdown = {
            "model_id": model_id,
            "staff_costs": staff_costs,
            "office_expenses": office_expenses,
            "revenue_streams": revenue_streams,
            "kpis": kpis,
            "generated_at": datetime.now().isoformat()
        }
        
        return breakdown
    
    def _create_staff_cost_structure(
        self,
        staff_data: Dict[str, Any],
        model_id: str
    ) -> Dict[str, Any]:
        """Create detailed staff cost structure by role and level"""
        
        roles = ["Consultant", "Operations", "Partner", "Recruitment", "Sales"]
        consultant_levels = ["A", "AC", "C", "SC", "P"]
        
        staff_breakdown = {
            "total_headcount": 0,
            "total_cost": 0,
            "by_role": {},
            "by_component": {
                "base_salary": 0,
                "variable_salary": 0,
                "social_security": 0,
                "pension_contribution": 0,
                "insurance_benefits": 0,
                "bonus_payments": 0,
                "recruitment_costs": 0,
                "training_costs": 0,
                "equipment_costs": 0
            },
            "monthly_breakdown": {}
        }
        
        for role in roles:
            if role == "Consultant":
                # Leveled role structure
                staff_breakdown["by_role"][role] = {}
                for level in consultant_levels:
                    level_data = staff_data.get(f"{role}_{level}", {})
                    level_costs = self._calculate_level_costs(level_data, role, level)
                    staff_breakdown["by_role"][role][level] = level_costs
                    
                    # Aggregate to totals
                    staff_breakdown["total_headcount"] += level_costs.get("headcount", 0)
                    staff_breakdown["total_cost"] += level_costs.get("total_compensation", 0)
            else:
                # Flat role structure
                role_data = staff_data.get(role, {})
                role_costs = self._calculate_role_costs(role_data, role)
                staff_breakdown["by_role"][role] = role_costs
                
                # Aggregate to totals
                staff_breakdown["total_headcount"] += role_costs.get("headcount", 0)
                staff_breakdown["total_cost"] += role_costs.get("total_compensation", 0)
        
        return staff_breakdown
    
    def _calculate_level_costs(
        self,
        level_data: Dict[str, Any],
        role: str,
        level: str
    ) -> Dict[str, Any]:
        """Calculate costs for a specific role level"""
        
        headcount = level_data.get("headcount", 0)
        base_salary = level_data.get("base_salary_monthly", 50000)
        
        # Calculate comprehensive salary components
        components = {
            "base_salary": base_salary * headcount,
            "variable_salary": base_salary * 0.15 * headcount,  # 15% variable
            "social_security": base_salary * 0.31 * headcount,  # 31% employer contribution
            "pension_contribution": base_salary * 0.045 * headcount,  # 4.5% pension
            "insurance_benefits": 2000 * headcount,  # Fixed monthly benefit cost
            "bonus_payments": base_salary * 0.10 * headcount,  # 10% annual bonus (monthly allocation)
            "recruitment_costs": level_data.get("recruitment_budget", 0),
            "training_costs": 1000 * headcount,  # Training budget per person
            "equipment_costs": 800 * headcount  # Equipment amortization per person
        }
        
        total_compensation = sum(components.values())
        
        return {
            "role": role,
            "level": level,
            "headcount": headcount,
            "components": components,
            "total_compensation": total_compensation,
            "cost_per_fte": total_compensation / headcount if headcount > 0 else 0
        }
    
    def _calculate_role_costs(
        self,
        role_data: Dict[str, Any],
        role: str
    ) -> Dict[str, Any]:
        """Calculate costs for a flat role (no levels)"""
        
        headcount = role_data.get("headcount", 0)
        base_salary = role_data.get("base_salary_monthly", 40000)
        
        # Role-specific salary adjustments
        salary_multipliers = {
            "Operations": 0.8,
            "Sales": 1.2,
            "Recruitment": 0.9,
            "Partner": 2.5
        }
        
        adjusted_salary = base_salary * salary_multipliers.get(role, 1.0)
        
        components = {
            "base_salary": adjusted_salary * headcount,
            "variable_salary": adjusted_salary * 0.12 * headcount,
            "social_security": adjusted_salary * 0.31 * headcount,
            "pension_contribution": adjusted_salary * 0.045 * headcount,
            "insurance_benefits": 2000 * headcount,
            "bonus_payments": adjusted_salary * 0.08 * headcount,
            "recruitment_costs": role_data.get("recruitment_budget", 0),
            "training_costs": 800 * headcount,
            "equipment_costs": 600 * headcount
        }
        
        total_compensation = sum(components.values())
        
        return {
            "role": role,
            "headcount": headcount,
            "components": components,
            "total_compensation": total_compensation,
            "cost_per_fte": total_compensation / headcount if headcount > 0 else 0
        }
    
    def _create_office_expense_structure(
        self,
        office_data: Dict[str, Any],
        model_id: str
    ) -> Dict[str, Any]:
        """Create office expense structure mirroring Planacy categories"""
        
        # Base office expenses from Planacy structure
        expense_categories = {
            "facilities": {
                "office_rent": office_data.get("office_rent", 430897),
                "utilities": office_data.get("utilities", 25000),
                "cleaning": office_data.get("cleaning", 8000),
                "security": office_data.get("security", 5000)
            },
            "it_equipment": {
                "software_licenses": office_data.get("software", 21432),
                "hardware_depreciation": office_data.get("hardware_depreciation", 3084),
                "it_support": office_data.get("it_support", 15000)
            },
            "operations": {
                "office_supplies": office_data.get("office_supplies", 2000),
                "communications": office_data.get("communications", 3000),
                "mail_shipping": office_data.get("mail_shipping", 1000)
            },
            "people_culture": {
                "conference_costs": office_data.get("conference_costs", 18900),
                "education_training": office_data.get("education", 355),
                "team_events": office_data.get("team_events", 5000),
                "external_representation": office_data.get("external_representation", 2625)
            },
            "professional_services": {
                "legal_services": office_data.get("legal", 10000),
                "accounting_audit": office_data.get("accounting", 8000),
                "consulting": office_data.get("consulting", 5000)
            },
            "travel_transport": {
                "travel_expenses": office_data.get("travel", 6432),
                "local_transport": office_data.get("local_transport", 2000)
            },
            "other": {
                "insurance": office_data.get("insurance", 5000),
                "bank_charges": office_data.get("bank_charges", 1000),
                "miscellaneous": office_data.get("miscellaneous", 3000)
            }
        }
        
        # Calculate totals
        category_totals = {}
        grand_total = 0
        
        for category, items in expense_categories.items():
            category_total = sum(items.values())
            category_totals[category] = category_total
            grand_total += category_total
        
        return {
            "categories": expense_categories,
            "category_totals": category_totals,
            "grand_total": grand_total,
            "monthly_breakdown": self._generate_monthly_expense_breakdown(expense_categories)
        }
    
    def _create_revenue_structure(
        self,
        revenue_data: Dict[str, Any],
        model_id: str
    ) -> Dict[str, Any]:
        """Create revenue structure"""
        
        revenue_streams = {
            "consulting_services": {
                "amount": revenue_data.get("consulting_revenue", 12000000),
                "client_mix": {
                    "enterprise": 0.6,
                    "mid_market": 0.3,
                    "sme": 0.1
                }
            },
            "product_sales": {
                "amount": revenue_data.get("product_revenue", 2000000),
                "recurring": 0.8
            },
            "training_workshops": {
                "amount": revenue_data.get("training_revenue", 500000),
                "sessions": revenue_data.get("training_sessions", 24)
            }
        }
        
        total_revenue = sum(stream["amount"] for stream in revenue_streams.values())
        
        return {
            "streams": revenue_streams,
            "total_revenue": total_revenue,
            "monthly_revenue": total_revenue / 12
        }
    
    def _calculate_financial_kpis(
        self,
        staff_costs: Dict[str, Any],
        office_expenses: Dict[str, Any],
        revenue_streams: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate financial KPIs matching Planacy structure"""
        
        total_revenue = revenue_streams.get("total_revenue", 0)
        total_staff_costs = staff_costs.get("total_cost", 0) * 12  # Annualize
        total_office_expenses = office_expenses.get("grand_total", 0) * 12  # Annualize
        total_headcount = staff_costs.get("total_headcount", 0)
        
        # Core financial metrics
        total_costs = total_staff_costs + total_office_expenses
        ebitda = total_revenue - total_costs
        ebitda_margin = (ebitda / total_revenue * 100) if total_revenue > 0 else 0
        
        # Efficiency metrics
        revenue_per_fte = total_revenue / total_headcount if total_headcount > 0 else 0
        cost_per_fte = total_costs / total_headcount if total_headcount > 0 else 0
        
        return {
            "revenue_metrics": {
                "total_revenue": total_revenue,
                "monthly_revenue": total_revenue / 12,
                "revenue_per_fte": revenue_per_fte
            },
            "cost_metrics": {
                "total_costs": total_costs,
                "staff_costs": total_staff_costs,
                "office_expenses": total_office_expenses,
                "cost_per_fte": cost_per_fte
            },
            "profitability": {
                "ebitda": ebitda,
                "ebitda_margin": ebitda_margin,
                "gross_margin": 45.0  # Typical consulting margin
            },
            "efficiency": {
                "utilization_rate": 85.0,  # Target utilization
                "billing_rate_realization": 92.0
            }
        }
    
    def _generate_monthly_expense_breakdown(
        self,
        expense_categories: Dict[str, Dict[str, float]]
    ) -> List[Dict[str, Any]]:
        """Generate monthly expense breakdown with seasonality"""
        
        monthly_data = []
        
        # Seasonality factors (some expenses vary by month)
        seasonality = {
            1: 1.1,   # January - higher heating costs
            2: 1.0,   # February
            3: 0.95,  # March
            4: 0.9,   # April
            5: 0.9,   # May
            6: 1.05,  # June - conference season
            7: 0.8,   # July - summer slowdown
            8: 0.8,   # August - summer slowdown
            9: 1.05,  # September - back to work
            10: 1.1,  # October - conference season
            11: 1.0,  # November
            12: 1.15  # December - year-end events
        }
        
        for month in range(1, 13):
            month_key = f"2025{month:02d}"
            factor = seasonality[month]
            
            month_expenses = {}
            month_total = 0
            
            for category, items in expense_categories.items():
                category_month_total = 0
                for item, annual_amount in items.items():
                    monthly_amount = (annual_amount / 12) * factor
                    category_month_total += monthly_amount
                
                month_expenses[category] = category_month_total
                month_total += category_month_total
            
            monthly_data.append({
                "month_key": month_key,
                "month_name": datetime(2025, month, 1).strftime("%B"),
                "expenses": month_expenses,
                "total": month_total,
                "seasonality_factor": factor
            })
        
        return monthly_data
    
    # Budget Planning
    
    def create_budget_plan(
        self,
        office_id: str,
        plan_name: str,
        fiscal_year: int,
        currency: CurrencyCode,
        financial_model_id: str,
        assumptions: Optional[Dict[str, str]] = None
    ) -> str:
        """Create a comprehensive budget plan"""
        
        plan_id = f"bp_{office_id}_{fiscal_year}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        
        budget_plan = {
            "plan_id": plan_id,
            "office_id": office_id,
            "plan_name": plan_name,
            "fiscal_year": fiscal_year,
            "currency": currency,
            "financial_model_id": financial_model_id,
            "assumptions": assumptions or {},
            "variance_tracking": {},
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "created_by": "system"
        }
        
        self.budget_plans[plan_id] = budget_plan
        self._save_budget_plan(plan_id)
        
        return plan_id
    
    def _save_budget_plan(self, plan_id: str):
        """Save budget plan to storage"""
        plan = self.budget_plans[plan_id]
        file_path = self.storage_dir / "plans" / f"{plan_id}.json"
        
        try:
            with open(file_path, 'w') as f:
                json.dump(plan, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Warning: Could not save budget plan {plan_id}: {e}")
    
    # Variance Analysis
    
    def calculate_variance_analysis(
        self,
        plan_id: str,
        actual_data: Dict[str, Any],
        period_start: str,
        period_end: str
    ) -> Dict[str, Any]:
        """Calculate comprehensive variance analysis"""
        
        if plan_id not in self.budget_plans:
            raise ValueError(f"Budget plan {plan_id} not found")
        
        plan = self.budget_plans[plan_id]
        model_id = plan["financial_model_id"]
        
        if model_id not in self.models:
            raise ValueError(f"Financial model {model_id} not found")
        
        model = self.models[model_id]
        
        # Get budget data from model
        budget_breakdown = self.create_expense_breakdown(model_id, model)
        
        # Calculate variances
        variance_analysis = {
            "plan_id": plan_id,
            "period": f"{period_start} to {period_end}",
            "summary": self._calculate_variance_summary(budget_breakdown, actual_data),
            "category_analysis": self._calculate_category_variances(budget_breakdown, actual_data),
            "trend_analysis": self._calculate_trend_analysis(budget_breakdown, actual_data),
            "risk_indicators": self._identify_risk_indicators(budget_breakdown, actual_data)
        }
        
        return variance_analysis
    
    def _calculate_variance_summary(
        self,
        budget_data: Dict[str, Any],
        actual_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate high-level variance summary"""
        
        # Extract totals from budget and actual
        budget_total = (
            budget_data.get("staff_costs", {}).get("total_cost", 0) * 12 +
            budget_data.get("office_expenses", {}).get("grand_total", 0) * 12
        )
        
        actual_total = actual_data.get("total_costs", budget_total * 0.98)  # Assume 2% under budget
        
        variance = actual_total - budget_total
        variance_pct = (variance / budget_total * 100) if budget_total > 0 else 0
        
        return {
            "total_budget": budget_total,
            "total_actual": actual_total,
            "total_variance": variance,
            "variance_percentage": variance_pct,
            "trend": "favorable" if variance < 0 else "unfavorable",
            "categories_analyzed": len(budget_data.get("office_expenses", {}).get("categories", {}))
        }
    
    def _calculate_category_variances(
        self,
        budget_data: Dict[str, Any],
        actual_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate variance by expense category"""
        
        category_variances = {}
        
        # Office expense categories
        budget_categories = budget_data.get("office_expenses", {}).get("category_totals", {})
        actual_categories = actual_data.get("office_expenses", {})
        
        for category, budget_amount in budget_categories.items():
            annual_budget = budget_amount * 12
            actual_amount = actual_categories.get(category, annual_budget * 0.95)  # Default to 5% under
            
            variance = actual_amount - annual_budget
            variance_pct = (variance / annual_budget * 100) if annual_budget > 0 else 0
            
            category_variances[category] = {
                "budget": annual_budget,
                "actual": actual_amount,
                "variance": variance,
                "variance_percentage": variance_pct,
                "trend": "favorable" if variance < 0 else "unfavorable",
                "risk_level": self._assess_risk_level(abs(variance_pct))
            }
        
        return category_variances
    
    def _assess_risk_level(self, variance_percentage: float) -> str:
        """Assess risk level based on variance percentage"""
        if variance_percentage <= 5:
            return "low"
        elif variance_percentage <= 15:
            return "medium"
        else:
            return "high"
    
    def _calculate_trend_analysis(
        self,
        budget_data: Dict[str, Any],
        actual_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Calculate monthly trend analysis"""
        
        # Generate monthly trends (simplified for demo)
        trends = []
        
        for month in range(1, 13):
            month_key = f"2025{month:02d}"
            
            # Simulate some variance patterns
            variance_factor = 1.0 + (month - 6) * 0.01  # Gradual drift over year
            
            trends.append({
                "month_key": month_key,
                "month_name": datetime(2025, month, 1).strftime("%B"),
                "budget_vs_actual_ratio": variance_factor,
                "cumulative_variance": variance_factor - 1.0,
                "trend_direction": "increasing" if variance_factor > 1.0 else "decreasing"
            })
        
        return trends
    
    def _identify_risk_indicators(
        self,
        budget_data: Dict[str, Any],
        actual_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify financial risk indicators"""
        
        risks = []
        
        # Example risk indicators based on variance analysis
        office_expenses = budget_data.get("office_expenses", {}).get("category_totals", {})
        
        # Check for high facility costs
        facilities_budget = office_expenses.get("facilities", 0) * 12
        if facilities_budget > 5000000:  # 5M annual threshold
            risks.append({
                "category": "facilities",
                "risk_level": "medium",
                "description": "High facility costs may impact profitability",
                "recommendation": "Review office space utilization and lease terms",
                "financial_impact": facilities_budget
            })
        
        # Check for IT cost growth
        it_budget = office_expenses.get("it_equipment", 0) * 12
        if it_budget > 500000:  # 500K annual threshold
            risks.append({
                "category": "it_equipment",
                "risk_level": "low",
                "description": "IT costs growing above industry average",
                "recommendation": "Audit software licenses and hardware refresh cycles",
                "financial_impact": it_budget
            })
        
        return risks
    
    # Integration with Simulation Engine
    
    def export_as_simulation_baseline(
        self,
        model_id: str,
        year: int,
        start_month: int = 1,
        end_month: int = 12
    ) -> Dict[str, Any]:
        """Export financial model as simulation baseline format"""
        
        if model_id not in self.models:
            raise ValueError(f"Financial model {model_id} not found")
        
        model = self.models[model_id]
        expense_breakdown = self.create_expense_breakdown(model_id, model)
        
        # Convert to simulation baseline format
        baseline = {
            "global": {
                "recruitment": {},
                "churn": {}
            },
            "metadata": {
                "source": "financial_planning",
                "model_id": model_id,
                "exported_at": datetime.now().isoformat(),
                "period": f"{year}-{start_month:02d} to {year}-{end_month:02d}"
            }
        }
        
        # Extract staff costs and convert to simulation format
        staff_costs = expense_breakdown.get("staff_costs", {})
        
        # Map role structure to simulation format
        for role, role_data in staff_costs.get("by_role", {}).items():
            if isinstance(role_data, dict) and "A" in role_data:
                # Leveled role (Consultant)
                baseline["global"]["recruitment"][role] = {"levels": {}}
                baseline["global"]["churn"][role] = {"levels": {}}
                
                for level, level_data in role_data.items():
                    baseline["global"]["recruitment"][role]["levels"][level] = {
                        "recruitment": self._generate_monthly_values(year, start_month, end_month, 2.0),
                        "churn": self._generate_monthly_values(year, start_month, end_month, 0.5)
                    }
                    baseline["global"]["churn"][role]["levels"][level] = {
                        "recruitment": self._generate_monthly_values(year, start_month, end_month, 2.0),
                        "churn": self._generate_monthly_values(year, start_month, end_month, 0.5)
                    }
            else:
                # Flat role
                baseline["global"]["recruitment"][role] = {
                    "recruitment": self._generate_monthly_values(year, start_month, end_month, 1.0),
                    "churn": self._generate_monthly_values(year, start_month, end_month, 0.3)
                }
                baseline["global"]["churn"][role] = {
                    "recruitment": self._generate_monthly_values(year, start_month, end_month, 1.0),
                    "churn": self._generate_monthly_values(year, start_month, end_month, 0.3)
                }
        
        return baseline
    
    def _generate_monthly_values(
        self,
        year: int,
        start_month: int,
        end_month: int,
        base_rate: float
    ) -> Dict[str, float]:
        """Generate monthly values for simulation baseline"""
        
        values = {}
        
        for month in range(start_month, end_month + 1):
            month_key = f"{year}{month:02d}"
            # Add some seasonality variation
            seasonal_factor = 1.0 + 0.1 * (month - 6) / 6  # Varies ±10% through year
            values[month_key] = base_rate * seasonal_factor
        
        return values


# Global service instance
financial_planning_service = FinancialPlanningService()