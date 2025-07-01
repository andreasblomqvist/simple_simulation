#!/usr/bin/env python3
"""
Comprehensive Simulation Results Verification Script

This script analyzes simulation results to verify:
- Growth patterns and rates
- Recruitment and churn consistency
- Progression logic and rates
- Financial calculations (EBITDA, margins, etc.)
- Data consistency across time periods
- Reasonableness of outcomes given parameters

Usage:
    python scripts/analysis/verify_simulation_results.py [simulation_results_file.json]
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.kpi import EconomicParameters
from backend.src.services.config_service import config_service


class SimulationVerifier:
    """Comprehensive verification of simulation results"""
    
    def __init__(self, results_file: Optional[str] = None):
        self.results_file = results_file
        self.results = None
        self.verification_results = {
            'passed': [],
            'warnings': [],
            'errors': [],
            'summary': {}
        }
        
    def load_results(self, results_file: Optional[str] = None) -> bool:
        """Load simulation results from file or run new simulation"""
        if results_file:
            self.results_file = results_file
            
        if self.results_file and os.path.exists(self.results_file):
            print(f"📁 Loading results from: {self.results_file}")
            try:
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    self.results = json.load(f)
                return True
            except Exception as e:
                print(f"❌ Failed to load results: {e}")
                return False
        else:
            print("🔄 Running new simulation for verification...")
            return self._run_simulation()
    
    def _run_simulation(self) -> bool:
        """Run a test simulation to get results for verification"""
        try:
            engine = SimulationEngine()
            
            # Run a 3-year simulation with typical parameters
            results = engine.run_simulation(
                start_year=2025,
                start_month=1,
                end_year=2027,
                end_month=12,
                price_increase=0.05,  # 5% annual price increase
                salary_increase=0.03   # 3% annual salary increase
            )
            
            self.results = results
            print("✅ Simulation completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Simulation failed: {e}")
            return False
    
    def verify_all(self) -> Dict[str, Any]:
        """Run all verification checks"""
        print("\n🔍 Starting comprehensive simulation verification...")
        print("=" * 80)
        
        if not self.results:
            self.verification_results['errors'].append("No simulation results available")
            return self.verification_results
        
        # Run all verification checks
        self._verify_data_structure()
        self._verify_growth_patterns()
        self._verify_recruitment_churn_consistency()
        self._verify_progression_logic()
        self._verify_financial_calculations()
        self._verify_event_logging()
        self._verify_kpi_consistency()
        self._verify_reasonableness()
        
        # Generate summary
        self._generate_summary()
        
        return self.verification_results
    
    def _verify_data_structure(self):
        """Verify the basic structure of simulation results"""
        print("\n📋 Verifying data structure...")
        
        # Check if this is comprehensive JSON export format or standard simulation results
        is_comprehensive_format = 'metadata' in self.results and 'time_series_data' in self.results
        
        if is_comprehensive_format:
            # Comprehensive JSON export format
            required_sections = [
                'metadata', 'simulation_period', 'configuration',
                'time_series_data', 'summary_metrics', 'event_data',
                'kpi_data', 'office_analysis', 'level_analysis'
            ]
            
            for section in required_sections:
                if section in self.results:
                    self.verification_results['passed'].append(f"✅ {section} section present")
                else:
                    self.verification_results['errors'].append(f"❌ Missing {section} section")
            
            # Check time series data structure
            if 'time_series_data' in self.results:
                yearly_data = self.results['time_series_data'].get('yearly_data', {})
                if yearly_data:
                    years = list(yearly_data.keys())
                    if len(years) >= 2:
                        self.verification_results['passed'].append(f"✅ Time series covers {len(years)} years: {min(years)}-{max(years)}")
                    else:
                        self.verification_results['warnings'].append(f"⚠️ Limited time series: only {len(years)} year(s)")
        else:
            # Standard simulation results format
            required_sections = [
                'years', 'simulation_period', 'configuration', 'monthly_office_metrics'
            ]
            
            for section in required_sections:
                if section in self.results:
                    self.verification_results['passed'].append(f"✅ {section} section present")
                else:
                    self.verification_results['warnings'].append(f"⚠️ Missing {section} section (standard format)")
            
            # Check years data structure
            if 'years' in self.results:
                years_data = self.results['years']
                if years_data:
                    years = list(years_data.keys())
                    if len(years) >= 2:
                        self.verification_results['passed'].append(f"✅ Years data covers {len(years)} years: {min(years)}-{max(years)}")
                    else:
                        self.verification_results['warnings'].append(f"⚠️ Limited years data: only {len(years)} year(s)")
            
            # Check monthly office metrics
            if 'monthly_office_metrics' in self.results:
                monthly_data = self.results['monthly_office_metrics']
                if monthly_data:
                    self.verification_results['passed'].append("✅ Monthly office metrics present")
                else:
                    self.verification_results['warnings'].append("⚠️ Monthly office metrics empty")
    
    def _verify_growth_patterns(self):
        """Verify growth patterns are logical and consistent"""
        print("\n📈 Verifying growth patterns...")
        
        # Check if this is comprehensive format or standard format
        if 'summary_metrics' in self.results:
            # Comprehensive format
            growth_summary = self.results['summary_metrics'].get('headcount_summary', {})
            
            # Check basic growth metrics
            initial_fte = growth_summary.get('initial_fte', 0)
            final_fte = growth_summary.get('final_fte', 0)
            total_growth = growth_summary.get('total_growth', 0)
            growth_percentage = growth_summary.get('growth_percentage', 0)
            
            # Verify growth calculations
            calculated_growth = final_fte - initial_fte
            if abs(calculated_growth - total_growth) < 1:  # Allow for rounding
                self.verification_results['passed'].append("✅ Growth calculation correct")
            else:
                self.verification_results['errors'].append(f"❌ Growth calculation error: expected {calculated_growth}, got {total_growth}")
            
            # Check growth percentage
            if initial_fte > 0:
                calculated_percentage = (total_growth / initial_fte) * 100
                if abs(calculated_percentage - growth_percentage) < 0.1:  # Allow for rounding
                    self.verification_results['passed'].append("✅ Growth percentage calculation correct")
                else:
                    self.verification_results['errors'].append(f"❌ Growth percentage error: expected {calculated_percentage:.1f}%, got {growth_percentage:.1f}%")
            
            # Check growth reasonableness
            if total_growth < 0:
                self.verification_results['warnings'].append(f"⚠️ Negative growth detected: {total_growth} FTE")
            elif growth_percentage > 100:
                self.verification_results['warnings'].append(f"⚠️ Very high growth: {growth_percentage:.1f}%")
            elif growth_percentage > 50:
                self.verification_results['warnings'].append(f"⚠️ High growth: {growth_percentage:.1f}%")
            else:
                self.verification_results['passed'].append(f"✅ Reasonable growth: {growth_percentage:.1f}%")
        
        elif 'years' in self.results:
            # Standard format - calculate growth from years data
            years_data = self.results['years']
            if years_data:
                years = sorted(years_data.keys())
                if len(years) >= 2:
                    first_year = years[0]
                    last_year = years[-1]
                    
                    first_year_fte = years_data[first_year].get('total_fte', 0)
                    last_year_fte = years_data[last_year].get('total_fte', 0)
                    
                    total_growth = last_year_fte - first_year_fte
                    growth_percentage = (total_growth / first_year_fte * 100) if first_year_fte > 0 else 0
                    
                    self.verification_results['passed'].append(f"✅ Growth calculated: {first_year_fte} → {last_year_fte} (+{total_growth})")
                    
                    # Check growth reasonableness
                    if total_growth < 0:
                        self.verification_results['warnings'].append(f"⚠️ Negative growth detected: {total_growth} FTE")
                    elif growth_percentage > 100:
                        self.verification_results['warnings'].append(f"⚠️ Very high growth: {growth_percentage:.1f}%")
                    elif growth_percentage > 50:
                        self.verification_results['warnings'].append(f"⚠️ High growth: {growth_percentage:.1f}%")
                    else:
                        self.verification_results['passed'].append(f"✅ Reasonable growth: {growth_percentage:.1f}%")
    
    def _verify_recruitment_churn_consistency(self):
        """Verify recruitment and churn rates are consistent"""
        print("\n🔄 Verifying recruitment and churn consistency...")
        
        # Check if event data is available
        event_data = None
        if 'event_data' in self.results:
            event_data = self.results['event_data']
        elif 'event_logger' in self.results:
            # Standard format - event logger is available
            event_logger = self.results['event_logger']
            if event_logger and hasattr(event_logger, 'get_events_summary'):
                try:
                    events_summary = event_logger.get_events_summary()
                    event_data = {
                        'available': True,
                        'events_summary': events_summary
                    }
                except:
                    event_data = {'available': False}
            else:
                event_data = {'available': False}
        
        if not event_data or not event_data.get('available', False):
            self.verification_results['warnings'].append("⚠️ Event data not available for recruitment/churn verification")
            return
        
        events_summary = event_data.get('events_summary', {})
        events_by_type = events_summary.get('events_by_type', {})
        
        total_recruitment = events_by_type.get('recruitment', 0)
        total_churn = events_by_type.get('churn', 0)
        total_graduation = events_by_type.get('graduation', 0)
        
        # Check if recruitment exceeds churn (expected for growth)
        net_recruitment = total_recruitment - total_churn - total_graduation
        
        if net_recruitment > 0:
            self.verification_results['passed'].append(f"✅ Net positive recruitment: +{net_recruitment}")
        elif net_recruitment == 0:
            self.verification_results['passed'].append("✅ Balanced recruitment and churn")
        else:
            self.verification_results['warnings'].append(f"⚠️ Net negative recruitment: {net_recruitment}")
        
        # Check recruitment/churn ratio
        if total_churn > 0:
            recruitment_churn_ratio = total_recruitment / total_churn
            if recruitment_churn_ratio > 1.5:
                self.verification_results['passed'].append(f"✅ Healthy recruitment/churn ratio: {recruitment_churn_ratio:.2f}")
            elif recruitment_churn_ratio > 1.0:
                self.verification_results['passed'].append(f"✅ Balanced recruitment/churn ratio: {recruitment_churn_ratio:.2f}")
            else:
                self.verification_results['warnings'].append(f"⚠️ Low recruitment/churn ratio: {recruitment_churn_ratio:.2f}")
    
    def _verify_progression_logic(self):
        """Verify progression logic and rates"""
        print("\n📊 Verifying progression logic...")
        
        # Check if event data is available
        event_data = None
        if 'event_data' in self.results:
            event_data = self.results['event_data']
        elif 'event_logger' in self.results:
            # Standard format - event logger is available
            event_logger = self.results['event_logger']
            if event_logger and hasattr(event_logger, 'get_events_summary'):
                try:
                    events_summary = event_logger.get_events_summary()
                    event_data = {
                        'available': True,
                        'events_summary': events_summary
                    }
                except:
                    event_data = {'available': False}
            else:
                event_data = {'available': False}
        
        if not event_data or not event_data.get('available', False):
            self.verification_results['warnings'].append("⚠️ Event data not available for progression verification")
            return
        
        events_summary = event_data.get('events_summary', {})
        events_by_type = events_summary.get('events_by_type', {})
        
        total_promotions = events_by_type.get('promotion', 0)
        total_recruitment = events_by_type.get('recruitment', 0)
        
        # Check promotion rate relative to recruitment
        if total_recruitment > 0:
            promotion_rate = total_promotions / total_recruitment
            if 0.1 <= promotion_rate <= 0.5:  # 10-50% promotion rate is reasonable
                self.verification_results['passed'].append(f"✅ Reasonable promotion rate: {promotion_rate:.1%}")
            elif promotion_rate > 0.5:
                self.verification_results['warnings'].append(f"⚠️ High promotion rate: {promotion_rate:.1%}")
            else:
                self.verification_results['warnings'].append(f"⚠️ Low promotion rate: {promotion_rate:.1%}")
        
        # Check progression by level (if available)
        if 'level_analysis' in self.results:
            level_analysis = self.results['level_analysis']
            level_movement = level_analysis.get('level_movement', {})
            
            for level_name, movement_data in level_movement.items():
                progressed_in = movement_data.get('total_progressed_in', 0)
                progressed_out = movement_data.get('total_progressed_out', 0)
                
                if progressed_in > 0 or progressed_out > 0:
                    self.verification_results['passed'].append(f"✅ Level {level_name}: {progressed_in} in, {progressed_out} out")
    
    def _verify_financial_calculations(self):
        """Verify financial calculations (EBITDA, margins, etc.)"""
        print("\n💰 Verifying financial calculations...")
        
        # Check if KPI data is available
        kpi_data = None
        if 'kpi_data' in self.results:
            kpi_data = self.results['kpi_data']
        elif 'years' in self.results:
            # Standard format - check if KPI data is in years
            years_data = self.results['years']
            if years_data:
                # Look for KPI data in the first year
                first_year = min(years_data.keys())
                year_data = years_data[first_year]
                if 'kpis' in year_data:
                    kpi_data = {'yearly_kpis': years_data}
        
        if not kpi_data:
            self.verification_results['warnings'].append("⚠️ KPI data not available for financial verification")
            return
        
        yearly_kpis = kpi_data.get('yearly_kpis', {})
        
        for year, year_kpis in yearly_kpis.items():
            # Handle both comprehensive and standard formats
            if isinstance(year_kpis, dict) and 'kpis' in year_kpis:
                financial_metrics = year_kpis['kpis'].get('financial', {})
            else:
                financial_metrics = year_kpis.get('financial_metrics', {})
            
            # Check EBITDA calculation
            net_sales = financial_metrics.get('net_sales', 0)
            ebitda = financial_metrics.get('ebitda', 0)
            margin = financial_metrics.get('margin', 0)
            
            if net_sales > 0:
                # Verify margin calculation
                calculated_margin = (ebitda / net_sales) * 100
                if abs(calculated_margin - margin) < 0.1:  # Allow for rounding
                    self.verification_results['passed'].append(f"✅ {year} EBITDA margin calculation correct: {margin:.1f}%")
                else:
                    self.verification_results['errors'].append(f"❌ {year} EBITDA margin error: expected {calculated_margin:.1f}%, got {margin:.1f}%")
                
                # Check margin reasonableness
                if 10 <= margin <= 30:
                    self.verification_results['passed'].append(f"✅ {year} Reasonable EBITDA margin: {margin:.1f}%")
                elif margin < 0:
                    self.verification_results['warnings'].append(f"⚠️ {year} Negative EBITDA margin: {margin:.1f}%")
                elif margin > 50:
                    self.verification_results['warnings'].append(f"⚠️ {year} Very high EBITDA margin: {margin:.1f}%")
                
                # Check EBITDA vs net sales relationship
                if ebitda > net_sales:
                    self.verification_results['errors'].append(f"❌ {year} EBITDA cannot exceed net sales")
    
    def _verify_event_logging(self):
        """Verify event logging completeness and consistency"""
        print("\n📝 Verifying event logging...")
        
        # Check if event data is available
        event_data = None
        if 'event_data' in self.results:
            event_data = self.results['event_data']
        elif 'event_logger' in self.results:
            # Standard format - event logger is available
            event_logger = self.results['event_logger']
            if event_logger:
                try:
                    total_events = len(event_logger.get_all_events()) if hasattr(event_logger, 'get_all_events') else 0
                    events_summary = event_logger.get_events_summary() if hasattr(event_logger, 'get_events_summary') else {}
                    events_file = getattr(event_logger, 'events_file', None)
                    run_id = getattr(event_logger, 'run_id', None)
                    
                    event_data = {
                        'available': True,
                        'total_events': total_events,
                        'events_summary': events_summary,
                        'events_file': events_file,
                        'run_id': run_id
                    }
                except:
                    event_data = {'available': False}
            else:
                event_data = {'available': False}
        
        if not event_data or not event_data.get('available', False):
            self.verification_results['warnings'].append("⚠️ Event logging not available")
            return
        
        total_events = event_data.get('total_events', 0)
        events_summary = event_data.get('events_summary', {})
        events_by_type = events_summary.get('events_by_type', {})
        
        # Check if events were logged
        if total_events > 0:
            self.verification_results['passed'].append(f"✅ {total_events} events logged")
            
            # Check event type distribution
            event_types = list(events_by_type.keys())
            if len(event_types) >= 3:  # Should have recruitment, promotion, churn
                self.verification_results['passed'].append(f"✅ Event types logged: {', '.join(event_types)}")
            else:
                self.verification_results['warnings'].append(f"⚠️ Limited event types: {', '.join(event_types)}")
        else:
            self.verification_results['warnings'].append("⚠️ No events logged")
        
        # Check event file reference
        events_file = event_data.get('events_file')
        if events_file:
            if os.path.exists(events_file):
                self.verification_results['passed'].append(f"✅ Event file exists: {events_file}")
            else:
                self.verification_results['warnings'].append(f"⚠️ Event file not found: {events_file}")
    
    def _verify_kpi_consistency(self):
        """Verify KPI consistency across different data sources"""
        print("\n🎯 Verifying KPI consistency...")
        
        # Check if this is comprehensive format or standard format
        if 'summary_metrics' in self.results:
            # Comprehensive format
            summary_fte = self.results.get('summary_metrics', {}).get('headcount_summary', {}).get('final_fte', 0)
            
            if 'time_series_data' in self.results:
                yearly_data = self.results['time_series_data'].get('yearly_data', {})
                if yearly_data:
                    last_year = max(yearly_data.keys())
                    time_series_fte = yearly_data[last_year].get('total_fte', 0)
                    
                    if abs(summary_fte - time_series_fte) < 1:  # Allow for rounding
                        self.verification_results['passed'].append("✅ FTE consistency between summary and time series")
                    else:
                        self.verification_results['errors'].append(f"❌ FTE inconsistency: summary={summary_fte}, time_series={time_series_fte}")
            
            # Check office-level consistency
            if 'office_analysis' in self.results:
                office_analysis = self.results['office_analysis']
                office_performance = office_analysis.get('office_performance', {})
                
                total_office_fte = 0
                for office_name, performance in office_performance.items():
                    if performance:
                        last_year = max(performance.keys())
                        office_fte = performance[last_year].get('total_fte', 0)
                        total_office_fte += office_fte
                
                if abs(total_office_fte - summary_fte) < 1:  # Allow for rounding
                    self.verification_results['passed'].append("✅ Office-level FTE aggregation correct")
                else:
                    self.verification_results['errors'].append(f"❌ Office FTE aggregation error: sum={total_office_fte}, total={summary_fte}")
        
        elif 'years' in self.results:
            # Standard format
            years_data = self.results['years']
            if years_data:
                years = sorted(years_data.keys())
                if len(years) >= 2:
                    first_year = years[0]
                    last_year = years[-1]
                    
                    first_year_fte = years_data[first_year].get('total_fte', 0)
                    last_year_fte = years_data[last_year].get('total_fte', 0)
                    
                    # Check if FTE values are reasonable
                    if first_year_fte > 0 and last_year_fte > 0:
                        self.verification_results['passed'].append(f"✅ FTE consistency: {first_year_fte} → {last_year_fte}")
                    else:
                        self.verification_results['warnings'].append("⚠️ Zero or negative FTE values detected")
    
    def _verify_reasonableness(self):
        """Verify overall reasonableness of results"""
        print("\n🧠 Verifying overall reasonableness...")
        
        # Check for extreme values
        if 'summary_metrics' in self.results:
            growth_summary = self.results['summary_metrics'].get('headcount_summary', {})
            growth_percentage = growth_summary.get('growth_percentage', 0)
            
            if growth_percentage > 200:
                self.verification_results['warnings'].append(f"⚠️ Extremely high growth: {growth_percentage:.1f}%")
            elif growth_percentage < -50:
                self.verification_results['warnings'].append(f"⚠️ Extremely high decline: {growth_percentage:.1f}%")
        
        elif 'years' in self.results:
            # Standard format - calculate growth from years data
            years_data = self.results['years']
            if years_data:
                years = sorted(years_data.keys())
                if len(years) >= 2:
                    first_year = years[0]
                    last_year = years[-1]
                    
                    first_year_fte = years_data[first_year].get('total_fte', 0)
                    last_year_fte = years_data[last_year].get('total_fte', 0)
                    
                    if first_year_fte > 0:
                        growth_percentage = ((last_year_fte - first_year_fte) / first_year_fte) * 100
                        
                        if growth_percentage > 200:
                            self.verification_results['warnings'].append(f"⚠️ Extremely high growth: {growth_percentage:.1f}%")
                        elif growth_percentage < -50:
                            self.verification_results['warnings'].append(f"⚠️ Extremely high decline: {growth_percentage:.1f}%")
        
        # Check financial reasonableness
        if 'kpi_data' in self.results:
            yearly_kpis = self.results['kpi_data'].get('yearly_kpis', {})
            for year, year_kpis in yearly_kpis.items():
                financial_metrics = year_kpis.get('financial_metrics', {})
                margin = financial_metrics.get('margin', 0)
                
                if margin > 100:
                    self.verification_results['errors'].append(f"❌ {year} Impossible margin: {margin:.1f}%")
                elif margin < -100:
                    self.verification_results['warnings'].append(f"⚠️ {year} Very negative margin: {margin:.1f}%")
        
        # Check for data completeness
        if 'time_series_data' in self.results:
            yearly_data = self.results['time_series_data'].get('yearly_data', {})
            if len(yearly_data) == 0:
                self.verification_results['errors'].append("❌ No yearly data available")
            elif len(yearly_data) < 2:
                self.verification_results['warnings'].append(f"⚠️ Limited time series: {len(yearly_data)} year(s)")
        
        elif 'years' in self.results:
            years_data = self.results['years']
            if len(years_data) == 0:
                self.verification_results['errors'].append("❌ No years data available")
            elif len(years_data) < 2:
                self.verification_results['warnings'].append(f"⚠️ Limited years data: {len(years_data)} year(s)")
            else:
                self.verification_results['passed'].append(f"✅ Years data complete: {len(years_data)} years")
    
    def _generate_summary(self):
        """Generate verification summary"""
        print("\n📊 Generating verification summary...")
        
        total_checks = (
            len(self.verification_results['passed']) +
            len(self.verification_results['warnings']) +
            len(self.verification_results['errors'])
        )
        
        self.verification_results['summary'] = {
            'total_checks': total_checks,
            'passed': len(self.verification_results['passed']),
            'warnings': len(self.verification_results['warnings']),
            'errors': len(self.verification_results['errors']),
            'success_rate': (len(self.verification_results['passed']) / total_checks * 100) if total_checks > 0 else 0,
            'verification_timestamp': datetime.now().isoformat()
        }
    
    def print_results(self):
        """Print verification results in a readable format"""
        print("\n" + "=" * 80)
        print("🔍 SIMULATION VERIFICATION RESULTS")
        print("=" * 80)
        
        # Print summary
        summary = self.verification_results['summary']
        print(f"\n📊 SUMMARY:")
        print(f"   Total checks: {summary['total_checks']}")
        print(f"   ✅ Passed: {summary['passed']}")
        print(f"   ⚠️  Warnings: {summary['warnings']}")
        print(f"   ❌ Errors: {summary['errors']}")
        print(f"   Success rate: {summary['success_rate']:.1f}%")
        
        # Print passed checks
        if self.verification_results['passed']:
            print(f"\n✅ PASSED CHECKS ({len(self.verification_results['passed'])}):")
            for check in self.verification_results['passed']:
                print(f"   {check}")
        
        # Print warnings
        if self.verification_results['warnings']:
            print(f"\n⚠️  WARNINGS ({len(self.verification_results['warnings'])}):")
            for warning in self.verification_results['warnings']:
                print(f"   {warning}")
        
        # Print errors
        if self.verification_results['errors']:
            print(f"\n❌ ERRORS ({len(self.verification_results['errors'])}):")
            for error in self.verification_results['errors']:
                print(f"   {error}")
        
        # Final verdict
        print(f"\n🎯 VERDICT:")
        if summary['errors'] == 0 and summary['warnings'] == 0:
            print("   🟢 EXCELLENT - All checks passed!")
        elif summary['errors'] == 0:
            print("   🟡 GOOD - All critical checks passed, some warnings")
        else:
            print("   🔴 ISSUES FOUND - Critical errors detected")
        
        print("=" * 80)
    
    def save_results(self, output_file: str = None):
        """Save verification results to file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"verification_results_{timestamp}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.verification_results, f, indent=2, default=str)
            print(f"💾 Verification results saved to: {output_file}")
        except Exception as e:
            print(f"❌ Failed to save results: {e}")


def main():
    """Main function to run verification"""
    # Parse command line arguments
    results_file = None
    if len(sys.argv) > 1:
        results_file = sys.argv[1]
    
    # Create verifier and run checks
    verifier = SimulationVerifier(results_file)
    
    if verifier.load_results():
        results = verifier.verify_all()
        verifier.print_results()
        verifier.save_results()
        
        # Exit with appropriate code
        if results['summary']['errors'] > 0:
            sys.exit(1)  # Exit with error code if critical issues found
        else:
            sys.exit(0)  # Exit successfully
    else:
        print("❌ Failed to load or run simulation")
        sys.exit(1)


if __name__ == "__main__":
    main() 