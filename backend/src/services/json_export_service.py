"""
Comprehensive JSON export service for simulation results.

This service aggregates all simulation data into a structured JSON format
without modifying any existing simulation logic.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import asdict, is_dataclass


class JSONExportService:
    """Service for exporting comprehensive simulation results to JSON format."""
    
    def export_simulation_results(
        self,
        simulation_results: Dict[str, Any],
        scenario_metadata: Optional[Dict[str, Any]] = None,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export comprehensive simulation results to JSON format.
        
        Args:
            simulation_results: The results dictionary from SimulationEngine.run_simulation()
            scenario_metadata: Optional metadata about the scenario (name, description, etc.)
            output_path: Optional path to save the JSON file
            
        Returns:
            Comprehensive JSON structure with all simulation data
        """
        
        # Build comprehensive JSON structure
        comprehensive_results = {
            "metadata": self._build_metadata(simulation_results, scenario_metadata),
            "simulation_period": simulation_results.get("simulation_period", {}),
            "configuration": simulation_results.get("configuration", {}),
            "time_series_data": self._build_time_series_data(simulation_results),
            "summary_metrics": self._build_summary_metrics(simulation_results),
            "event_data": self._build_event_data(simulation_results),
            "kpi_data": self._build_kpi_data(simulation_results),
            "office_analysis": self._build_office_analysis(simulation_results),
            "level_analysis": self._build_level_analysis(simulation_results),
            "journey_analysis": self._build_journey_analysis(simulation_results),
            "movement_analysis": self._build_movement_analysis(simulation_results)
        }
        
        # Save to file if path provided
        if output_path:
            self._save_to_file(comprehensive_results, output_path)
        
        return comprehensive_results
    
    def _build_metadata(self, simulation_results: Dict[str, Any], scenario_metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build metadata section"""
        metadata = {
            "export_timestamp": datetime.now().isoformat(),
            "export_version": "1.0",
            "simulation_engine_version": "1.0",
            "data_sources": [
                "simulation_engine_results",
                "event_logger",
                "kpi_service",
                "configuration_service"
            ]
        }
        
        if scenario_metadata:
            metadata.update(scenario_metadata)
        
        return metadata
    
    def _build_time_series_data(self, simulation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build time series data section"""
        years_data = simulation_results.get("years", {})
        time_series = {
            "yearly_data": {},
            "monthly_data": simulation_results.get("monthly_office_metrics", {}),
            "aggregated_metrics": {}
        }
        
        # Process yearly data
        for year, year_data in years_data.items():
            year_summary = {
                "total_fte": year_data.get("total_fte", 0),
                "offices": {},
                "financial_metrics": year_data.get("financial_metrics", {}),
                "growth_metrics": year_data.get("growth_metrics", {}),
                "journey_metrics": year_data.get("journey_metrics", {})
            }
            
            # Process office data for this year
            offices_data = year_data.get("offices", {})
            for office_name, office_data in offices_data.items():
                office_summary = {
                    "total_fte": office_data.get("total_fte", 0),
                    "journey": office_data.get("journey", ""),
                    "levels": self._process_level_data(office_data.get("levels", {}))
                }
                year_summary["offices"][office_name] = office_summary
            
            time_series["yearly_data"][year] = year_summary
        
        return time_series
    
    def _process_level_data(self, levels_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process level data structure"""
        processed_levels = {}
        
        for role_name, role_data in levels_data.items():
            if isinstance(role_data, dict):
                # Role with levels (Consultant, Sales, Recruitment)
                processed_levels[role_name] = {}
                for level_name, level_data in role_data.items():
                    if isinstance(level_data, list) and level_data:
                        # Process monthly array data
                        processed_levels[role_name][level_name] = {
                            "monthly_data": level_data,
                            "summary": self._calculate_level_summary(level_data)
                        }
            elif isinstance(role_data, list) and role_data:
                # Flat role (Operations)
                processed_levels[role_name] = {
                    "monthly_data": role_data,
                    "summary": self._calculate_level_summary(role_data)
                }
        
        return processed_levels
    
    def _calculate_level_summary(self, monthly_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary metrics for a level's monthly data"""
        if not monthly_data:
            return {}
        
        # Get the last month's data for current state
        last_month = monthly_data[-1]
        
        # Calculate averages across all months
        total_fte_avg = sum(month.get('total', 0) for month in monthly_data) / len(monthly_data)
        total_recruited = sum(month.get('recruited', 0) for month in monthly_data)
        total_churned = sum(month.get('churned', 0) for month in monthly_data)
        total_progressed_in = sum(month.get('progressed_in', 0) for month in monthly_data)
        total_progressed_out = sum(month.get('progressed_out', 0) for month in monthly_data)
        
        return {
            "current_fte": last_month.get('total', 0),
            "average_fte": total_fte_avg,
            "total_recruited": total_recruited,
            "total_churned": total_churned,
            "total_progressed_in": total_progressed_in,
            "total_progressed_out": total_progressed_out,
            "net_growth": total_recruited - total_churned + total_progressed_in - total_progressed_out,
            "current_price": last_month.get('price', 0),
            "current_salary": last_month.get('salary', 0),
            "current_utr": last_month.get('utr', 0.85)
        }
    
    def _build_summary_metrics(self, simulation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build summary metrics section"""
        years_data = simulation_results.get("years", {})
        
        if not years_data:
            return {}
        
        # Get first and last year data
        years_list = sorted(years_data.keys())
        first_year = years_list[0] if years_list else None
        last_year = years_list[-1] if years_list else None
        
        if not first_year or not last_year:
            return {}
        
        first_year_data = years_data[first_year]
        last_year_data = years_data[last_year]
        
        initial_fte = first_year_data.get("total_fte", 0)
        final_fte = last_year_data.get("total_fte", 0)
        total_growth = final_fte - initial_fte
        growth_percentage = (total_growth / initial_fte * 100) if initial_fte > 0 else 0
        
        return {
            "simulation_period": {
                "start_year": first_year,
                "end_year": last_year,
                "duration_years": int(last_year) - int(first_year) + 1
            },
            "headcount_summary": {
                "initial_fte": initial_fte,
                "final_fte": final_fte,
                "total_growth": total_growth,
                "growth_percentage": growth_percentage,
                "average_annual_growth": total_growth / (int(last_year) - int(first_year) + 1) if int(last_year) > int(first_year) else 0
            },
            "office_summary": {
                "total_offices": len(first_year_data.get("offices", {})),
                "offices_by_journey": self._count_offices_by_journey(last_year_data.get("offices", {}))
            }
        }
    
    def _count_offices_by_journey(self, offices_data: Dict[str, Any]) -> Dict[str, int]:
        """Count offices by journey type"""
        journey_counts = {}
        for office_data in offices_data.values():
            journey = office_data.get("journey", "Unknown")
            journey_counts[journey] = journey_counts.get(journey, 0) + 1
        return journey_counts
    
    def _build_event_data(self, simulation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build event data section"""
        event_logger = simulation_results.get("event_logger")
        
        if not event_logger:
            return {"available": False, "message": "Event logger not available"}
        
        try:
            # Get event summary if available
            events_summary = getattr(event_logger, 'get_events_summary', lambda: {})()
            
            return {
                "available": True,
                "total_events": len(getattr(event_logger, 'events', [])),
                "events_summary": events_summary,
                "events_file": getattr(event_logger, 'events_file', None),
                "run_id": getattr(event_logger, 'run_id', None)
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "message": "Error accessing event data"
            }
    
    def _build_kpi_data(self, simulation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build KPI data section"""
        years_data = simulation_results.get("years", {})
        
        kpi_data = {
            "yearly_kpis": {},
            "financial_metrics": {},
            "growth_metrics": {},
            "journey_metrics": {}
        }
        
        # Extract KPI data from yearly results
        for year, year_data in years_data.items():
            year_kpis = {
                "financial_metrics": year_data.get("financial_metrics", {}),
                "growth_metrics": year_data.get("growth_metrics", {}),
                "journey_metrics": year_data.get("journey_metrics", {})
            }
            kpi_data["yearly_kpis"][year] = year_kpis
        
        return kpi_data
    
    def _build_office_analysis(self, simulation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build office analysis section"""
        years_data = simulation_results.get("years", {})
        
        office_analysis = {
            "office_performance": {},
            "office_growth": {},
            "office_journey_progression": {}
        }
        
        # Analyze each office across years
        all_offices = set()
        for year_data in years_data.values():
            all_offices.update(year_data.get("offices", {}).keys())
        
        for office_name in all_offices:
            office_performance = {}
            office_growth = {}
            office_journey_progression = {}
            
            for year, year_data in years_data.items():
                office_data = year_data.get("offices", {}).get(office_name, {})
                if office_data:
                    office_performance[year] = {
                        "total_fte": office_data.get("total_fte", 0),
                        "journey": office_data.get("journey", ""),
                        "levels_summary": self._summarize_office_levels(office_data.get("levels", {}))
                    }
            
            office_analysis["office_performance"][office_name] = office_performance
            office_analysis["office_growth"][office_name] = self._calculate_office_growth(office_performance)
            office_analysis["office_journey_progression"][office_name] = self._track_journey_progression(office_performance)
        
        return office_analysis
    
    def _summarize_office_levels(self, levels_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize office levels data"""
        summary = {
            "total_fte": 0,
            "consultant_fte": 0,
            "non_consultant_fte": 0,
            "level_breakdown": {}
        }
        
        for role_name, role_data in levels_data.items():
            if isinstance(role_data, dict):
                # Role with levels
                for level_name, level_data in role_data.items():
                    if isinstance(level_data, dict) and "summary" in level_data:
                        fte = level_data["summary"].get("current_fte", 0)
                        summary["total_fte"] += fte
                        
                        if role_name == "Consultant":
                            summary["consultant_fte"] += fte
                        else:
                            summary["non_consultant_fte"] += fte
                        
                        summary["level_breakdown"][f"{role_name}_{level_name}"] = fte
            elif isinstance(role_data, dict) and "summary" in role_data:
                # Flat role
                fte = role_data["summary"].get("current_fte", 0)
                summary["total_fte"] += fte
                summary["non_consultant_fte"] += fte
                summary["level_breakdown"][role_name] = fte
        
        return summary
    
    def _calculate_office_growth(self, office_performance: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate office growth metrics"""
        years = sorted(office_performance.keys())
        if len(years) < 2:
            return {}
        
        first_year = years[0]
        last_year = years[-1]
        
        initial_fte = office_performance[first_year].get("total_fte", 0)
        final_fte = office_performance[last_year].get("total_fte", 0)
        
        return {
            "initial_fte": initial_fte,
            "final_fte": final_fte,
            "total_growth": final_fte - initial_fte,
            "growth_percentage": ((final_fte - initial_fte) / initial_fte * 100) if initial_fte > 0 else 0,
            "annual_growth_rate": ((final_fte / initial_fte) ** (1 / (int(last_year) - int(first_year))) - 1) * 100 if initial_fte > 0 and int(last_year) > int(first_year) else 0
        }
    
    def _track_journey_progression(self, office_performance: Dict[str, Any]) -> Dict[str, Any]:
        """Track office journey progression over time"""
        journey_history = []
        for year, data in office_performance.items():
            journey_history.append({
                "year": year,
                "journey": data.get("journey", ""),
                "fte": data.get("total_fte", 0)
            })
        
        return {
            "journey_history": journey_history,
            "journey_changes": self._identify_journey_changes(journey_history)
        }
    
    def _identify_journey_changes(self, journey_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify when office journey changed"""
        changes = []
        for i in range(1, len(journey_history)):
            prev = journey_history[i-1]
            curr = journey_history[i]
            
            if prev["journey"] != curr["journey"]:
                changes.append({
                    "year": curr["year"],
                    "from_journey": prev["journey"],
                    "to_journey": curr["journey"],
                    "fte_at_change": curr["fte"]
                })
        
        return changes
    
    def _build_level_analysis(self, simulation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build level analysis section"""
        years_data = simulation_results.get("years", {})
        
        level_analysis = {
            "level_performance": {},
            "level_growth": {},
            "level_movement": {}
        }
        
        # Collect all levels across all offices and years
        all_levels = set()
        for year_data in years_data.values():
            for office_data in year_data.get("offices", {}).values():
                levels_data = office_data.get("levels", {})
                for role_name, role_data in levels_data.items():
                    if isinstance(role_data, dict):
                        all_levels.update(role_data.keys())
                    else:
                        all_levels.add(role_name)
        
        # Analyze each level
        for level_name in all_levels:
            level_performance = {}
            level_movement = {
                "total_recruited": 0,
                "total_churned": 0,
                "total_progressed_in": 0,
                "total_progressed_out": 0
            }
            
            for year, year_data in years_data.items():
                year_level_data = {}
                for office_data in year_data.get("offices", {}).values():
                    levels_data = office_data.get("levels", {})
                    for role_name, role_data in levels_data.items():
                        if isinstance(role_data, dict) and level_name in role_data:
                            level_data = role_data[level_name]
                            if isinstance(level_data, dict) and "summary" in level_data:
                                summary = level_data["summary"]
                                year_level_data[role_name] = summary
                                
                                # Accumulate movement data
                                level_movement["total_recruited"] += summary.get("total_recruited", 0)
                                level_movement["total_churned"] += summary.get("total_churned", 0)
                                level_movement["total_progressed_in"] += summary.get("total_progressed_in", 0)
                                level_movement["total_progressed_out"] += summary.get("total_progressed_out", 0)
                        elif role_name == level_name and isinstance(role_data, dict) and "summary" in role_data:
                            # Flat role
                            summary = role_data["summary"]
                            year_level_data[role_name] = summary
                            
                            # Accumulate movement data
                            level_movement["total_recruited"] += summary.get("total_recruited", 0)
                            level_movement["total_churned"] += summary.get("total_churned", 0)
                            level_movement["total_progressed_in"] += summary.get("total_progressed_in", 0)
                            level_movement["total_progressed_out"] += summary.get("total_progressed_out", 0)
                
                if year_level_data:
                    level_performance[year] = year_level_data
            
            level_analysis["level_performance"][level_name] = level_performance
            level_analysis["level_movement"][level_name] = level_movement
        
        return level_analysis
    
    def _build_journey_analysis(self, simulation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build journey analysis section"""
        years_data = simulation_results.get("years", {})
        
        journey_analysis = {
            "journey_distribution": {},
            "journey_growth": {},
            "journey_transitions": {}
        }
        
        # Analyze journey distribution over time
        for year, year_data in years_data.items():
            journey_distribution = {}
            total_fte = year_data.get("total_fte", 0)
            
            for office_data in year_data.get("offices", {}).values():
                journey = office_data.get("journey", "Unknown")
                fte = office_data.get("total_fte", 0)
                
                if journey not in journey_distribution:
                    journey_distribution[journey] = {"fte": 0, "offices": 0}
                
                journey_distribution[journey]["fte"] += fte
                journey_distribution[journey]["offices"] += 1
            
            # Calculate percentages
            for journey_data in journey_distribution.values():
                journey_data["percentage"] = (journey_data["fte"] / total_fte * 100) if total_fte > 0 else 0
            
            journey_analysis["journey_distribution"][year] = journey_distribution
        
        return journey_analysis
    
    def _build_movement_analysis(self, simulation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build movement analysis section"""
        years_data = simulation_results.get("years", {})
        
        movement_analysis = {
            "system_movement": {},
            "office_movement": {},
            "level_movement": {}
        }
        
        # Aggregate movement data across all levels and offices
        for year, year_data in years_data.items():
            year_movement = {
                "total_recruited": 0,
                "total_churned": 0,
                "total_progressed_in": 0,
                "total_progressed_out": 0,
                "net_growth": 0
            }
            
            for office_data in year_data.get("offices", {}).values():
                levels_data = office_data.get("levels", {})
                for role_name, role_data in levels_data.items():
                    if isinstance(role_data, dict):
                        # Role with levels
                        for level_name, level_data in role_data.items():
                            if isinstance(level_data, dict) and "summary" in level_data:
                                summary = level_data["summary"]
                                year_movement["total_recruited"] += summary.get("total_recruited", 0)
                                year_movement["total_churned"] += summary.get("total_churned", 0)
                                year_movement["total_progressed_in"] += summary.get("total_progressed_in", 0)
                                year_movement["total_progressed_out"] += summary.get("total_progressed_out", 0)
                    elif isinstance(role_data, dict) and "summary" in role_data:
                        # Flat role
                        summary = role_data["summary"]
                        year_movement["total_recruited"] += summary.get("total_recruited", 0)
                        year_movement["total_churned"] += summary.get("total_churned", 0)
                        year_movement["total_progressed_in"] += summary.get("total_progressed_in", 0)
                        year_movement["total_progressed_out"] += summary.get("total_progressed_out", 0)
            
            year_movement["net_growth"] = (
                year_movement["total_recruited"] - 
                year_movement["total_churned"] + 
                year_movement["total_progressed_in"] - 
                year_movement["total_progressed_out"]
            )
            
            movement_analysis["system_movement"][year] = year_movement
        
        return movement_analysis
    
    def _save_to_file(self, data: Dict[str, Any], output_path: str) -> None:
        """Save JSON data to file"""
        dir_name = os.path.dirname(output_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=self._json_serializer)
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for dataclasses and other objects"""
        if is_dataclass(obj):
            return asdict(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable") 