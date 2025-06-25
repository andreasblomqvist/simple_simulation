from typing import Dict, List, Any
from backend.src.services.simulation.models import Office, Level, RoleData, Month, Journey, OfficeJourney

class OfficeManager:
    """
    Handles office, role, and level initialization and configuration.
    """
    def __init__(self, config_service):
        self.config_service = config_service
        self.offices: Dict[str, Office] = {}
        self.level_order: List[str] = []

    def initialize_offices_from_config(self):
        config_dict = self.config_service.get_configuration()
        config_data = [office_config for office_config in config_dict.values()]
        self.level_order = self.determine_level_order(config_data)
        self.offices = {}
        for office_config in config_data:
            office = self._create_office_from_config(office_config)
            self.offices[office.name] = office
        return self.offices

    def _create_office_from_config(self, office_config: Dict[str, Any]) -> Office:
        office_name = office_config.get('name', 'Unknown Office')
        total_fte = office_config.get('total_fte', 0)
        office = Office.create_office(office_name, total_fte)
        for role_name, role_data in office_config.get('roles', {}).items():
            if role_name == 'Operations':
                op_fte = role_data.get('fte', 0)
                operations_role = RoleData()
                for i in range(1, 13):
                    salary = role_data.get(f'salary_{i}', role_data.get('salary', 40000.0))
                    price = role_data.get(f'price_{i}', role_data.get('price', 0.0))
                    utr = role_data.get(f'utr_{i}', role_data.get('utr', 0.0))
                    setattr(operations_role, f'salary_{i}', salary)
                    setattr(operations_role, f'price_{i}', price)
                    setattr(operations_role, f'utr_{i}', utr)
                initialization_date_str = "2023-01"
                for _ in range(int(op_fte)):
                    operations_role.add_new_hire(initialization_date_str, "Operations", office_name)
                office.roles['Operations'] = operations_role
            else:
                office.roles[role_name] = {}
                for level_name, level_config in role_data.items():
                    journey_name = self.get_journey_for_level(level_name)
                    level_attributes = {}
                    for key in ['progression', 'recruitment', 'churn', 'price', 'salary', 'utr']:
                        for i in range(1, 13):
                            monthly_key = f'{key}_{i}'
                            if monthly_key in level_config:
                                level_attributes[monthly_key] = level_config[monthly_key]
                            else:
                                default_value = level_config.get(key, 0.0)
                                level_attributes[monthly_key] = default_value
                    level = Level(
                        name=level_name,
                        journey=journey_name,
                        progression_months=[Month(i) for i in range(1, 13)],
                        **level_attributes
                    )
                    level_fte = level_config.get('fte', 0)
                    initialization_date_str = "2023-01"
                    for _ in range(int(level_fte)):
                        level.add_new_hire(initialization_date_str, role_name, office_name)
                    office.roles[role_name][level_name] = level
        return office

    @staticmethod
    def determine_level_order(config_data: List[Dict]) -> List[str]:
        levels = set()
        for office_config in config_data:
            for role_name, role_data in office_config.get('roles', {}).items():
                if role_name != 'Operations':
                    levels.update(role_data.keys())
        standard_order = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']
        sorted_levels = [level for level in standard_order if level in levels]
        return sorted_levels

    @staticmethod
    def get_journey_for_level(level_name: str) -> Journey:
        # Simple journey mapping without default config
        if level_name in ['A', 'AC', 'C']:
            return Journey.JOURNEY_1
        elif level_name in ['SrC', 'AM']:
            return Journey.JOURNEY_2
        elif level_name in ['M', 'SrM']:
            return Journey.JOURNEY_3
        elif level_name == 'PiP':
            return Journey.JOURNEY_4
        else:
            return Journey.JOURNEY_1 