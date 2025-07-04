"""
Default Configuration for SimpleSim
Based on real data from config/avg_prices.xlsx and config/headcount.xlsx
"""

# Office mapping from abbreviations to full names
OFFICE_MAPPING = {
    'AMS': 'Amsterdam',
    'BER': 'Berlin', 
    'COL': 'Cologne',
    'CPH': 'Copenhagen',
    'FRA': 'Frankfurt',
    'HAM': 'Hamburg',
    'HEL': 'Helsinki',
    'MUN': 'Munich',
    'OSL': 'Oslo',
    'STO': 'Stockholm',
    'TOR': 'Toronto',
    'ZUR': 'Zurich'
}

# Currency Configuration
# All pricing is standardized to SEK (Swedish Krona) as the base currency
# Exchange rates as of June 13, 2025 (ECB reference rates)

CURRENCY_CONFIG = {
    'base_currency': 'SEK',
    'last_updated': '2025-06-13',
    'source': 'European Central Bank (ECB)',
    
    # Office to currency mapping
    'office_currencies': {
        'Stockholm': 'SEK',
        'Munich': 'EUR',
        'Hamburg': 'EUR', 
        'Berlin': 'EUR',
        'Frankfurt': 'EUR',
        'Cologne': 'EUR',
        'Amsterdam': 'EUR',
        'Helsinki': 'EUR',
        'Oslo': 'NOK',
        'Copenhagen': 'DKK',
        'Zurich': 'CHF',
        'Toronto': 'CAD'
    },
    
    # Conversion factors to SEK (1 foreign currency = X SEK)
    'conversion_to_sek': {
        'SEK': 1.0000,      # Base currency
        'EUR': 10.9635,     # 1 EUR = 10.9635 SEK
        'NOK': 0.9580,      # 1 NOK = 0.9580 SEK
        'DKK': 1.4697,      # 1 DKK = 1.4697 SEK
        'CHF': 11.7156,     # 1 CHF = 11.7156 SEK
        'CAD': 6.9887       # 1 CAD = 6.9887 SEK
    }
}

def convert_to_sek(amount, from_currency):
    """Convert amount from given currency to SEK using current rates."""
    if from_currency not in CURRENCY_CONFIG['conversion_to_sek']:
        raise ValueError(f"Currency {from_currency} not supported")
    
    conversion_factor = CURRENCY_CONFIG['conversion_to_sek'][from_currency]
    return amount * conversion_factor

def get_office_currency(office_name):
    """Get the local currency for a given office."""
    return CURRENCY_CONFIG['office_currencies'].get(office_name, 'SEK')

# Updated pricing in SEK (converted from EUR base prices)
EUR_TO_SEK = CURRENCY_CONFIG['conversion_to_sek']['EUR']

# Journey classifications
JOURNEY_CLASSIFICATION = {
    'Journey 1': ['A', 'AC', 'C'],    # A-C
    'Journey 2': ['SrC', 'AM'],       # SrC-AM
    'Journey 3': ['M', 'SrM', 'Pi'],  # M-SrM-Pi
    'Journey 4': ['P']                # P
}

# Consultant level distribution (percentages)
CONSULTANT_LEVEL_DISTRIBUTION = {
    'A': 0.15,      # Analyst
    'AC': 0.18,     # Associate Consultant
    'C': 0.22,      # Consultant
    'SrC': 0.20,    # Senior Consultant
    'AM': 0.15,     # Associate Manager
    'M': 0.07,      # Manager
    'SrM': 0.025,   # Senior Manager
    'Pi': 0.004,    # Principe
    'P': 0.001      # Partner
}

if __name__ == "__main__":
    # Generate and display sample configuration
    config = generate_default_config()
    print(f"Generated {len(config)} configuration rows")
    print(f"Offices: {len(OFFICE_HEADCOUNT)}")
    print(f"Total FTE: {sum(OFFICE_HEADCOUNT.values())}") 