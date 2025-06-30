"""
Event logging system for tracking all workforce events per person.

This module provides comprehensive logging of all events that happen to individuals
in the simulation: promotions, recruitment, churn, etc.
"""

import csv
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class EventType(Enum):
    """Types of events that can occur to a person"""
    RECRUITMENT = "recruitment"
    PROMOTION = "promotion"
    CHURN = "churn"
    GRADUATION = "graduation"

@dataclass
class PersonEvent:
    """Represents a single event that happened to a person"""
    event_id: str
    person_id: str
    event_type: EventType
    date: str  # YYYY-MM format
    total_tenure_months: int
    time_on_level_months: int
    level: str
    role: str
    office: str
    from_level: Optional[str] = None  # For promotions
    to_level: Optional[str] = None    # For promotions
    cat_category: Optional[str] = None  # For promotions
    progression_probability: Optional[float] = None  # For promotions
    churn_rate: Optional[float] = None  # For churn
    recruitment_rate: Optional[float] = None  # For recruitment

class EventLogger:
    """
    Comprehensive event logging system for tracking all workforce events.
    
    Logs all events (promotions, recruitment, churn) with detailed information
    about each person including their tenure, level, role, office, and event-specific details.
    """
    
    def __init__(self, run_id: str, output_dir: str = "logs"):
        self.run_id = run_id
        self.output_dir = output_dir
        self.events: List[PersonEvent] = []
        self.event_counter = 0
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Create the main events log file
        self.events_file = os.path.join(output_dir, f"person_events_{run_id}.csv")
        self._initialize_events_file()
    
    def _initialize_events_file(self):
        """Initialize the CSV file with headers"""
        headers = [
            'event_id', 'person_id', 'event_type', 'date', 'total_tenure_months',
            'time_on_level_months', 'level', 'role', 'office', 'from_level',
            'to_level', 'cat_category', 'progression_probability', 'churn_rate',
            'recruitment_rate'
        ]
        
        with open(self.events_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
    
    def _get_next_event_id(self) -> str:
        """Generate unique event ID"""
        self.event_counter += 1
        return f"{self.run_id}_{self.event_counter:06d}"
    
    def log_recruitment(self, person, current_date: str, role: str, office: str, 
                       recruitment_rate: float = None):
        """Log a recruitment event"""
        event = PersonEvent(
            event_id=self._get_next_event_id(),
            person_id=person.id,
            event_type=EventType.RECRUITMENT,
            date=current_date,
            total_tenure_months=person.get_career_tenure_months(current_date),
            time_on_level_months=person.get_level_tenure_months(current_date),
            level=person.current_level,
            role=role,
            office=office,
            recruitment_rate=recruitment_rate
        )
        self.events.append(event)
        self._write_event_to_csv(event)
    
    def log_promotion(self, person, current_date: str, from_level: str, to_level: str,
                     role: str, office: str, cat_category: str = None, 
                     progression_probability: float = None):
        """Log a promotion event"""
        event = PersonEvent(
            event_id=self._get_next_event_id(),
            person_id=person.id,
            event_type=EventType.PROMOTION,
            date=current_date,
            total_tenure_months=person.get_career_tenure_months(current_date),
            time_on_level_months=person.get_level_tenure_months(current_date),
            level=from_level,  # The level they're being promoted from
            role=role,
            office=office,
            from_level=from_level,
            to_level=to_level,
            cat_category=cat_category,
            progression_probability=progression_probability
        )
        self.events.append(event)
        self._write_event_to_csv(event)
    
    def log_churn(self, person, current_date: str, role: str, office: str, 
                  churn_rate: float = None):
        """Log a churn event"""
        event = PersonEvent(
            event_id=self._get_next_event_id(),
            person_id=person.id,
            event_type=EventType.CHURN,
            date=current_date,
            total_tenure_months=person.get_career_tenure_months(current_date),
            time_on_level_months=person.get_level_tenure_months(current_date),
            level=person.current_level,
            role=role,
            office=office,
            churn_rate=churn_rate
        )
        self.events.append(event)
        self._write_event_to_csv(event)
    
    def log_graduation(self, person, current_date: str, role: str, office: str, 
                      from_level: str):
        """Log a graduation event (when someone graduates from top level)"""
        event = PersonEvent(
            event_id=self._get_next_event_id(),
            person_id=person.id,
            event_type=EventType.CHURN,  # Use CHURN type but with special handling
            date=current_date,
            total_tenure_months=person.get_career_tenure_months(current_date),
            time_on_level_months=person.get_level_tenure_months(current_date),
            level=from_level,
            role=role,
            office=office,
            churn_rate=None,  # Graduation, not churn
            from_level=from_level,
            to_level="GRADUATED"  # Mark as graduated
        )
        self.events.append(event)
        self._write_event_to_csv(event)
    
    def _write_event_to_csv(self, event: PersonEvent):
        """Write a single event to the CSV file"""
        row = [
            event.event_id,
            event.person_id,
            event.event_type.value,
            event.date,
            event.total_tenure_months,
            event.time_on_level_months,
            event.level,
            event.role,
            event.office,
            event.from_level or '',
            event.to_level or '',
            event.cat_category or '',
            event.progression_probability or '',
            event.churn_rate or '',
            event.recruitment_rate or ''
        ]
        
        with open(self.events_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)
    
    def get_events_summary(self) -> Dict:
        """Get a summary of all events"""
        summary = {
            'total_events': len(self.events),
            'events_by_type': {},
            'events_by_office': {},
            'events_by_role': {},
            'events_by_level': {},
            'events_by_month': {}
        }
        
        for event in self.events:
            # Count by event type
            event_type = event.event_type.value
            summary['events_by_type'][event_type] = summary['events_by_type'].get(event_type, 0) + 1
            
            # Count by office
            summary['events_by_office'][event.office] = summary['events_by_office'].get(event.office, 0) + 1
            
            # Count by role
            summary['events_by_role'][event.role] = summary['events_by_role'].get(event.role, 0) + 1
            
            # Count by level
            summary['events_by_level'][event.level] = summary['events_by_level'].get(event.level, 0) + 1
            
            # Count by month
            summary['events_by_month'][event.date] = summary['events_by_month'].get(event.date, 0) + 1
        
        return summary
    
    def export_events_summary(self, filename: str = None):
        """Export events summary to a separate file"""
        if filename is None:
            filename = os.path.join(self.output_dir, f"events_summary_{self.run_id}.csv")
        
        summary = self.get_events_summary()
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Summary Type', 'Category', 'Count'])
            
            # Events by type
            for event_type, count in summary['events_by_type'].items():
                writer.writerow(['Event Type', event_type, count])
            
            # Events by office
            for office, count in summary['events_by_office'].items():
                writer.writerow(['Office', office, count])
            
            # Events by role
            for role, count in summary['events_by_role'].items():
                writer.writerow(['Role', role, count])
            
            # Events by level
            for level, count in summary['events_by_level'].items():
                writer.writerow(['Level', level, count])
            
            # Events by month
            for month, count in summary['events_by_month'].items():
                writer.writerow(['Month', month, count])
        
        return filename
    
    def get_person_history(self, person_id: str) -> List[PersonEvent]:
        """Get all events for a specific person"""
        return [event for event in self.events if event.person_id == person_id]
    
    def get_events_by_date_range(self, start_date: str, end_date: str) -> List[PersonEvent]:
        """Get all events within a date range"""
        return [event for event in self.events if start_date <= event.date <= end_date]
    
    def get_events_by_type(self, event_type: EventType) -> List[PersonEvent]:
        """Get all events of a specific type"""
        return [event for event in self.events if event.event_type == event_type]
    
    def get_all_events(self):
        """Return all logged events as a list of dicts."""
        result = []
        for event in getattr(self, 'events', []):
            if hasattr(event, 'to_dict'):
                result.append(event.to_dict())
            elif hasattr(event, '__dict__'):
                result.append(event.__dict__)
            else:
                result.append(event)
        return result 