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
    },
    
    # Original currency values before conversion (for reference)
    'original_eur_base_prices': {
        'A': 106.09, 'AC': 127.31, 'C': 159.13, 'SrC': 190.96,
        'AM': 233.40, 'M': 297.05, 'SrM': 371.31, 'PiP': 477.41
    },
    'original_eur_base_salaries': {
        'A': 53.05, 'AC': 63.65, 'C': 79.57, 'SrC': 95.48,
        'AM': 116.70, 'M': 148.53, 'SrM': 185.66, 'PiP': 238.70
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

# Base pricing per level - actual pricing data from avg_prices.xlsx
# All prices converted to SEK using current exchange rates
# Base pricing per level - actual pricing data from avg_prices.xlsx
# All prices converted to SEK using current exchange rates
BASE_PRICING = {
    'Amsterdam': {  # AMS - EUR -> SEK
        'A': round(105.00 * EUR_TO_SEK, 2),     # 1,151.17 SEK
        'AC': round(101.68 * EUR_TO_SEK, 2),    # 1,114.77 SEK
        'C': round(118.21 * EUR_TO_SEK, 2),     # 1,295.89 SEK
        'SrC': round(113.35 * EUR_TO_SEK, 2),   # 1,242.60 SEK
        'AM': round(120.79 * EUR_TO_SEK, 2),    # 1,324.18 SEK
        'M': round(137.50 * EUR_TO_SEK, 2),     # 1,507.48 SEK
        'SrM': round(135.00 * EUR_TO_SEK, 2),   # 1,479.73 SEK
        'PiP': round(179.94 * EUR_TO_SEK, 2)    # 1,973.00 SEK (using HAM PI value)
    },
    'Berlin': {  # BER - EUR -> SEK
        'A': round(127.06 * EUR_TO_SEK, 2),     # 1,393.05 SEK
        'AC': round(127.08 * EUR_TO_SEK, 2),    # 1,393.27 SEK
        'C': round(135.87 * EUR_TO_SEK, 2),     # 1,489.66 SEK
        'SrC': round(143.10 * EUR_TO_SEK, 2),   # 1,568.95 SEK
        'AM': round(157.16 * EUR_TO_SEK, 2),    # 1,723.18 SEK
        'M': round(149.28 * EUR_TO_SEK, 2),     # 1,636.78 SEK
        'SrM': round(147.06 * EUR_TO_SEK, 2),   # 1,612.44 SEK
        'PiP': round(225.00 * EUR_TO_SEK, 2)    # 2,466.79 SEK
    },
    'Cologne': {  # COL - EUR -> SEK
        'A': round(122.28 * EUR_TO_SEK, 2),     # 1,340.63 SEK
        'AC': round(131.25 * EUR_TO_SEK, 2),    # 1,438.96 SEK
        'C': round(131.71 * EUR_TO_SEK, 2),     # 1,444.00 SEK
        'SrC': round(142.56 * EUR_TO_SEK, 2),   # 1,563.03 SEK
        'AM': round(160.80 * EUR_TO_SEK, 2),    # 1,763.11 SEK
        'M': round(171.06 * EUR_TO_SEK, 2),     # 1,875.63 SEK
        'SrM': round(171.06 * EUR_TO_SEK, 2),   # 1,875.63 SEK (using M value)
        'PiP': round(179.94 * EUR_TO_SEK, 2)    # 1,973.00 SEK (using HAM PI value)
    },
    'Copenhagen': {  # CPH - DKK -> SEK
        'A': round(918.95 * 1.4697, 2),        # 1,350.56 SEK
        'AC': round(983.03 * 1.4697, 2),       # 1,444.73 SEK
        'C': round(993.65 * 1.4697, 2),        # 1,460.34 SEK
        'SrC': round(1117.08 * 1.4697, 2),     # 1,641.85 SEK
        'AM': round(1163.72 * 1.4697, 2),      # 1,710.39 SEK
        'M': round(1205.31 * 1.4697, 2),       # 1,771.50 SEK
        'SrM': round(1461.51 * 1.4697, 2),     # 2,148.18 SEK
        'PiP': round(1400.00 * 1.4697, 2)      # 2,057.58 SEK
    },
    'Frankfurt': {  # FRA - EUR -> SEK
        'A': round(122.50 * EUR_TO_SEK, 2),     # 1,343.04 SEK
        'AC': round(142.59 * EUR_TO_SEK, 2),    # 1,563.37 SEK
        'C': round(137.41 * EUR_TO_SEK, 2),     # 1,506.56 SEK
        'SrC': round(139.63 * EUR_TO_SEK, 2),   # 1,530.90 SEK
        'AM': round(157.34 * EUR_TO_SEK, 2),    # 1,725.16 SEK
        'M': round(166.47 * EUR_TO_SEK, 2),     # 1,825.25 SEK
        'SrM': round(166.47 * EUR_TO_SEK, 2),   # 1,825.25 SEK (using M value)
        'PiP': round(179.94 * EUR_TO_SEK, 2)    # 1,973.00 SEK (using HAM PI value)
    },
    'Hamburg': {  # HAM - EUR -> SEK
        'A': round(119.30 * EUR_TO_SEK, 2),     # 1,307.95 SEK
        'AC': round(118.59 * EUR_TO_SEK, 2),    # 1,300.17 SEK
        'C': round(127.93 * EUR_TO_SEK, 2),     # 1,402.58 SEK
        'SrC': round(134.17 * EUR_TO_SEK, 2),   # 1,471.00 SEK
        'AM': round(145.00 * EUR_TO_SEK, 2),    # 1,589.71 SEK
        'M': round(164.87 * EUR_TO_SEK, 2),     # 1,807.71 SEK
        'SrM': round(167.15 * EUR_TO_SEK, 2),   # 1,832.72 SEK
        'PiP': round(179.94 * EUR_TO_SEK, 2)    # 1,973.00 SEK
    },
    'Helsinki': {  # HEL - EUR -> SEK
        'A': round(108.30 * EUR_TO_SEK, 2),     # 1,187.49 SEK
        'AC': round(111.37 * EUR_TO_SEK, 2),    # 1,221.15 SEK
        'C': round(115.35 * EUR_TO_SEK, 2),     # 1,264.79 SEK
        'SrC': round(118.11 * EUR_TO_SEK, 2),   # 1,295.05 SEK
        'AM': round(123.14 * EUR_TO_SEK, 2),    # 1,350.20 SEK
        'M': round(126.67 * EUR_TO_SEK, 2),     # 1,388.90 SEK
        'SrM': round(145.00 * EUR_TO_SEK, 2),   # 1,589.71 SEK
        'PiP': round(179.94 * EUR_TO_SEK, 2)    # 1,973.00 SEK (using HAM PI value)
    },
    'Munich': {  # MUN - EUR -> SEK
        'A': round(116.99 * EUR_TO_SEK, 2),     # 1,282.63 SEK
        'AC': round(117.18 * EUR_TO_SEK, 2),    # 1,284.71 SEK
        'C': round(122.42 * EUR_TO_SEK, 2),     # 1,342.16 SEK
        'SrC': round(129.50 * EUR_TO_SEK, 2),   # 1,419.73 SEK
        'AM': round(139.18 * EUR_TO_SEK, 2),    # 1,525.84 SEK
        'M': round(152.56 * EUR_TO_SEK, 2),     # 1,672.65 SEK
        'SrM': round(178.09 * EUR_TO_SEK, 2),   # 1,952.72 SEK
        'PiP': round(162.42 * EUR_TO_SEK, 2)    # 1,780.18 SEK (using actual PI value)
    },
    'Oslo': {  # OSL - NOK -> SEK
        'A': round(1177.33 * 0.9580, 2),       # 1,128.09 SEK
        'AC': round(1236.10 * 0.9580, 2),      # 1,184.18 SEK
        'C': round(1263.27 * 0.9580, 2),       # 1,210.25 SEK
        'SrC': round(1350.30 * 0.9580, 2),     # 1,293.79 SEK
        'AM': round(1416.98 * 0.9580, 2),      # 1,357.47 SEK
        'M': round(1472.50 * 0.9580, 2),       # 1,410.68 SEK
        'SrM': round(1683.47 * 0.9580, 2),     # 1,612.76 SEK
        'PiP': round(179.94 * EUR_TO_SEK, 2)   # 1,973.00 SEK (using HAM PI value)
    },
    'Stockholm': {  # STO - SEK (already in SEK)
        'A': 1106.61,
        'AC': 1114.57,
        'C': 1153.80,
        'SrC': 1185.03,
        'AM': 1247.87,
        'M': 1377.61,
        'SrM': 1461.70,
        'PiP': 2000.00  # Updated to correct rate
    },
    'Toronto': {  # TOR - CAD -> SEK (limited levels available)
        'A': round(210.00 * 6.9887, 2),        # 1,467.63 SEK (using SrC value)
        'AC': round(210.00 * 6.9887, 2),       # 1,467.63 SEK (using SrC value)
        'C': round(210.00 * 6.9887, 2),        # 1,467.63 SEK (using SrC value)
        'SrC': round(210.00 * 6.9887, 2),      # 1,467.63 SEK
        'AM': round(210.00 * 6.9887, 2),       # 1,467.63 SEK
        'M': round(210.00 * 6.9887, 2),        # 1,467.63 SEK (using AM value)
        'SrM': round(250.00 * 6.9887, 2),      # 1,747.18 SEK
        'PiP': round(205.99 * 6.9887, 2)       # 1,439.63 SEK (using MUN P value converted)
    },
    'Zurich': {  # ZUR - CHF -> SEK
        'A': round(134.60 * 11.7156, 2),       # 1,577.72 SEK
        'AC': round(111.89 * 11.7156, 2),      # 1,311.25 SEK
        'C': round(162.57 * 11.7156, 2),       # 1,904.95 SEK
        'SrC': round(172.10 * 11.7156, 2),     # 2,016.65 SEK
        'AM': round(183.55 * 11.7156, 2),      # 2,150.89 SEK
        'M': round(184.46 * 11.7156, 2),       # 2,161.55 SEK
        'SrM': round(205.49 * 11.7156, 2),     # 2,407.89 SEK
        'PiP': round(179.94 * EUR_TO_SEK, 2)   # 1,973.00 SEK (using HAM PI value)
    }
}

# Base salary per level - actual salary data from salary ladders (converted to SEK)
BASE_SALARIES = {
    'Stockholm': {  # TSEK/month (already in SEK, multiply by 1000)
        'A': 42000, 'AC': 44000, 'C': 48000, 'SrC': 53000,
        'AM': 58000, 'M': 70000, 'SrM': 84000, 'PiP': 90000
    },
    'Munich': {  # EUR/year -> SEK/month (divide by 12, then convert)
        'A': round((63000 / 12) * EUR_TO_SEK, 2),     # 57,583 SEK/month
        'AC': round((63000 / 12) * EUR_TO_SEK, 2),    # 57,583 SEK/month  
        'C': round((65424 / 12) * EUR_TO_SEK, 2),     # 59,833 SEK/month
        'SrC': round((74544 / 12) * EUR_TO_SEK, 2),   # 68,167 SEK/month
        'AM': round((85656 / 12) * EUR_TO_SEK, 2),    # 78,333 SEK/month
        'M': round((99600 / 12) * EUR_TO_SEK, 2),     # 91,083 SEK/month
        'SrM': round((120780 / 12) * EUR_TO_SEK, 2),  # 110,500 SEK/month
        'PiP': round((148800 / 12) * EUR_TO_SEK, 2)   # 136,083 SEK/month
    },
    'Hamburg': {  # EUR/year -> SEK/month
        'A': round((63000 / 12) * EUR_TO_SEK, 2),     # Same as Munich base
        'AC': round((63000 / 12) * EUR_TO_SEK, 2),    
        'C': round((65424 / 12) * EUR_TO_SEK, 2),     
        'SrC': round((74544 / 12) * EUR_TO_SEK, 2),   
        'AM': round((85656 / 12) * EUR_TO_SEK, 2),    
        'M': round((99600 / 12) * EUR_TO_SEK, 2),     
        'SrM': round((120780 / 12) * EUR_TO_SEK, 2),  
        'PiP': round((148800 / 12) * EUR_TO_SEK, 2)   
    },
    'Helsinki': {  # EUR/month -> SEK/month
        'A': round(4500 * EUR_TO_SEK, 2),     # 49,336 SEK/month
        'AC': round(4500 * EUR_TO_SEK, 2),    # 49,336 SEK/month
        'C': round(4800 * EUR_TO_SEK, 2),     # 52,625 SEK/month
        'SrC': round(5300 * EUR_TO_SEK, 2),   # 58,107 SEK/month
        'AM': round(5900 * EUR_TO_SEK, 2),    # 64,685 SEK/month
        'M': round(6800 * EUR_TO_SEK, 2),     # 74,552 SEK/month
        'SrM': round(8200 * EUR_TO_SEK, 2),   # 89,901 SEK/month
        'PiP': round(8832 * EUR_TO_SEK, 2)    # 96,833 SEK/month
    },
    'Oslo': {  # NOK/year -> SEK/month (divide by 12, then convert)
        'A': round((640000 / 12) * 0.9580, 2),    # 51,093 SEK/month
        'AC': round((670000 / 12) * 0.9580, 2),   # 53,483 SEK/month
        'C': round((750000 / 12) * 0.9580, 2),    # 59,875 SEK/month
        'SrC': round((800000 / 12) * 0.9580, 2),  # 63,867 SEK/month
        'AM': round((860000 / 12) * 0.9580, 2),   # 68,660 SEK/month
        'M': round((920000 / 12) * 0.9580, 2),    # 73,453 SEK/month
        'SrM': round((1050000 / 12) * 0.9580, 2), # 83,825 SEK/month
        'PiP': round((1240000 / 12) * 0.9580, 2)  # 98,987 SEK/month
    },
    'Berlin': {  # EUR/year -> SEK/month (same as Munich/Hamburg)
        'A': round((63000 / 12) * EUR_TO_SEK, 2),     
        'AC': round((63000 / 12) * EUR_TO_SEK, 2),    
        'C': round((65424 / 12) * EUR_TO_SEK, 2),     
        'SrC': round((74544 / 12) * EUR_TO_SEK, 2),   
        'AM': round((85656 / 12) * EUR_TO_SEK, 2),    
        'M': round((99600 / 12) * EUR_TO_SEK, 2),     
        'SrM': round((120780 / 12) * EUR_TO_SEK, 2),  
        'PiP': round((148800 / 12) * EUR_TO_SEK, 2)   
    },
    'Copenhagen': {  # TDKK/month -> SEK/month
        'A': round(44 * 1000 * 1.4697, 2),      # 64,667 SEK/month
        'AC': round(44.5 * 1000 * 1.4697, 2),   # 65,402 SEK/month
        'C': round(47.5 * 1000 * 1.4697, 2),    # 69,811 SEK/month
        'SrC': round(52 * 1000 * 1.4697, 2),    # 76,424 SEK/month
        'AM': round(57.25 * 1000 * 1.4697, 2),  # 84,140 SEK/month
        'M': round(67.5 * 1000 * 1.4697, 2),    # 99,205 SEK/month
        'SrM': round(73.5 * 1000 * 1.4697, 2),  # 108,023 SEK/month
        'PiP': round(86 * 1000 * 1.4697, 2)     # 126,394 SEK/month
    },
    'Zurich': {  # CHF/year -> SEK/month (divide by 12, then convert)
        'A': round((102000 / 12) * 11.7156, 2),    # 99,583 SEK/month
        'AC': round((107400 / 12) * 11.7156, 2),   # 104,889 SEK/month
        'C': round((112800 / 12) * 11.7156, 2),    # 110,196 SEK/month
        'SrC': round((126000 / 12) * 11.7156, 2),  # 123,114 SEK/month
        'AM': round((145800 / 12) * 11.7156, 2),   # 142,439 SEK/month
        'M': round((159000 / 12) * 11.7156, 2),    # 155,331 SEK/month
        'SrM': round((170000 / 12) * 11.7156, 2),  # 166,087 SEK/month
        'PiP': round((212400 / 12) * 11.7156, 2)   # 207,527 SEK/month
    },
    'Frankfurt': {  # EUR/year -> SEK/month (same as Munich/Hamburg/Berlin)
        'A': round((63000 / 12) * EUR_TO_SEK, 2),     
        'AC': round((63000 / 12) * EUR_TO_SEK, 2),    
        'C': round((65424 / 12) * EUR_TO_SEK, 2),     
        'SrC': round((74544 / 12) * EUR_TO_SEK, 2),   
        'AM': round((85656 / 12) * EUR_TO_SEK, 2),    
        'M': round((99600 / 12) * EUR_TO_SEK, 2),     
        'SrM': round((120780 / 12) * EUR_TO_SEK, 2),  
        'PiP': round((148800 / 12) * EUR_TO_SEK, 2)   
    },
    'Amsterdam': {  # EUR/month -> SEK/month
        'A': round(4000 * EUR_TO_SEK, 2),     # 43,854 SEK/month
        'AC': round(4200 * EUR_TO_SEK, 2),    # 46,047 SEK/month
        'C': round(4400 * EUR_TO_SEK, 2),     # 48,239 SEK/month
        'SrC': round(5050 * EUR_TO_SEK, 2),   # 55,366 SEK/month
        'AM': round(5740 * EUR_TO_SEK, 2),    # 62,930 SEK/month
        'M': round(6720 * EUR_TO_SEK, 2),     # 73,675 SEK/month
        'SrM': round(8385 * EUR_TO_SEK, 2),   # 91,930 SEK/month
        'PiP': round(12945 * EUR_TO_SEK, 2)   # 141,925 SEK/month
    },
    'Toronto': {  # Estimated based on market rates, CAD -> SEK
        'A': round(5000 * 6.9887, 2),      # 34,944 SEK/month
        'AC': round(5500 * 6.9887, 2),     # 38,438 SEK/month
        'C': round(6000 * 6.9887, 2),      # 41,932 SEK/month
        'SrC': round(7000 * 6.9887, 2),    # 48,921 SEK/month
        'AM': round(8000 * 6.9887, 2),     # 55,910 SEK/month
        'M': round(9500 * 6.9887, 2),      # 66,393 SEK/month
        'SrM': round(11000 * 6.9887, 2),   # 76,876 SEK/month
        'PiP': round(14000 * 6.9887, 2)    # 97,842 SEK/month
    }
}

# Current headcount distribution based on headcount.xlsx (Q1 2025 data)
OFFICE_HEADCOUNT = {
    'Stockholm': 821,
    'Munich': 410,
    'Hamburg': 165,
    'Helsinki': 130,
    'Oslo': 123,
    'Berlin': 109,
    'Copenhagen': 94,
    'Zurich': 43,
    'Frankfurt': 27,
    'Amsterdam': 23,
    'Cologne': 22,
    'Toronto': 5
}

# Role distribution percentages (based on actual data from headcount.xlsx)
ROLE_DISTRIBUTION = {
    'Consultant': 0.809,  # 1596/1972 = 80.9%
    'Operations': 0.061,  # 120/1972 = 6.1%
    'Recruitment': 0.047,  # 93/1972 = 4.7%
    'Sales': 0.083        # 163/1972 = 8.3%
}

# Level distribution within consultant role (estimated from data)
CONSULTANT_LEVEL_DISTRIBUTION = {
    'A': 0.15,      # Analyst
    'AC': 0.18,     # Associate Consultant
    'C': 0.22,      # Consultant
    'SrC': 0.20,    # Senior Consultant
    'AM': 0.15,     # Associate Manager
    'M': 0.07,      # Manager
    'SrM': 0.025,   # Senior Manager
    'PiP': 0.005    # Partner
}

# Actual level distributions by office (based on real headcount data from Q1 2025)
ACTUAL_OFFICE_LEVEL_DATA = {
    'Stockholm': {
        'Consultant': {
            'A': 69, 'AC': 54, 'C': 123, 'SrC': 162, 'AM': 178, 'M': 47, 'SrM': 32, 'PiP': 14
        },
        'Sales': {
            'A': 6, 'AC': 8, 'C': 4, 'SrC': 4, 'AM': 10, 'M': 6, 'SrM': 3, 'PiP': 8
        },
        'Recruitment': {
            'A': 4, 'AC': 3, 'C': 5, 'SrC': 3, 'AM': 4, 'M': 2, 'SrM': 4, 'PiP': 1
        },
        'Operations': 67  # 57 + 10 (ALT category moved to Operations)
    },
    'Munich': {
        'Consultant': {
            'A': 18, 'AC': 32, 'C': 61, 'SrC': 89, 'AM': 89, 'M': 30, 'SrM': 6, 'PiP': 7
        },
        'Sales': {
            'AC': 2, 'C': 2, 'SrC': 6, 'AM': 4, 'M': 5, 'SrM': 2, 'PiP': 4
        },
        'Recruitment': {
            'A': 2, 'AC': 2, 'C': 2, 'SrC': 1, 'AM': 5, 'M': 3, 'SrM': 2, 'PiP': 1
        },
        'Operations': 35
    },
    'Hamburg': {
        'Consultant': {
            'A': 9, 'AC': 27, 'C': 29, 'SrC': 27, 'AM': 26, 'M': 8, 'SrM': 2, 'PiP': 1
        },
        'Sales': {
            'A': 2, 'AC': 1, 'C': 5, 'SrC': 2, 'AM': 3, 'M': 2, 'SrM': 1, 'PiP': 2
        },
        'Recruitment': {
            'AC': 4, 'C': 2, 'SrC': 1, 'AM': 3
        },
        'Operations': 8
    },
    'Helsinki': {
        'Consultant': {
            'A': 16, 'AC': 16, 'C': 17, 'SrC': 24, 'AM': 20, 'M': 11, 'SrM': 1
        },
        'Sales': {
            'A': 2, 'AC': 5, 'C': 1, 'SrC': 1, 'M': 2, 'PiP': 1
        },
        'Recruitment': {
            'AM': 3, 'C': 3, 'M': 1, 'SrM': 1
        },
        'Operations': 5
    },
    'Oslo': {
        'Consultant': {
            'A': 5, 'AC': 11, 'C': 23, 'SrC': 20, 'AM': 21, 'M': 10, 'SrM': 5, 'PiP': 1
        },
        'Sales': {
            'AC': 3, 'C': 4, 'SrC': 2, 'AM': 2, 'M': 2
        },
        'Recruitment': {
            'AM': 1, 'C': 4, 'M': 1, 'SrC': 2
        },
        'Operations': 6
    },
    'Berlin': {
        'Consultant': {
            'A': 4, 'AC': 17, 'C': 20, 'SrC': 24, 'AM': 15, 'M': 5
        },
        'Sales': {
            'AC': 2, 'C': 3, 'SrC': 3, 'AM': 2, 'M': 3, 'SrM': 1
        },
        'Recruitment': {
            'AM': 2, 'C': 3, 'SrC': 1
        },
        'Operations': 4
    },
    'Copenhagen': {
        'Consultant': {
            'A': 7, 'AC': 15, 'C': 22, 'SrC': 12, 'AM': 11, 'M': 4, 'SrM': 2, 'PiP': 1
        },
        'Sales': {
            'AC': 2, 'C': 1, 'SrC': 2, 'AM': 2, 'M': 1, 'SrM': 1, 'PiP': 1
        },
        'Recruitment': {
            'AC': 1, 'C': 1, 'SrC': 3, 'M': 1
        },
        'Operations': 4
    },
    'Zurich': {
        'Consultant': {
            'A': 4, 'AC': 3, 'C': 4, 'SrC': 9, 'AM': 8, 'M': 6
        },
        'Sales': {
            'AC': 2, 'C': 2, 'AM': 1, 'M': 1
        },
        'Recruitment': {
            'A': 1, 'AC': 1
        },
        'Operations': 1
    },
    'Frankfurt': {
        'Consultant': {
            'A': 1, 'AC': 5, 'C': 4, 'SrC': 3, 'AM': 4, 'M': 1, 'SrM': 1
        },
        'Sales': {
            'A': 2, 'AC': 2, 'SrC': 1
        },
        'Recruitment': {
            'A': 1, 'C': 1, 'SrC': 1
        },
        'Operations': 0  # No operations in Frankfurt
    },
    'Amsterdam': {
        'Consultant': {
            'A': 2, 'AC': 5, 'C': 2, 'SrC': 2, 'AM': 1, 'SrM': 2
        },
        'Sales': {
            'A': 2, 'AC': 1, 'C': 1, 'AM': 1, 'PiP': 1
        },
        'Recruitment': {
            'A': 1, 'AC': 1, 'SrC': 1
        },
        'Operations': 0  # No operations in Amsterdam
    },
    'Cologne': {
        'Consultant': {
            'A': 4, 'AC': 3, 'C': 3, 'SrC': 2, 'AM': 1, 'M': 3
        },
        'Sales': {
            'AC': 2, 'C': 2
        },
        'Recruitment': {
            'C': 1, 'M': 1
        },
        'Operations': 0  # No operations in Cologne
    },
    'Toronto': {
        'Consultant': {
            'A': 1, 'AC': 1, 'C': 1, 'SrC': 1, 'AM': 1, 'M': 0, 'SrM': 0, 'PiP': 0
        },
        'Sales': {
            'A': 0, 'AC': 0, 'C': 0, 'SrC': 0, 'AM': 0, 'M': 0, 'SrM': 0, 'PiP': 0
        },
        'Recruitment': {
            'A': 0, 'AC': 0, 'C': 0, 'SrC': 0, 'AM': 0, 'M': 0, 'SrM': 0, 'PiP': 0
        },
        'Operations': 0
    }
}

# Default rates for simulation (based on actual historical data 2020-2025)
DEFAULT_RATES = {
    'recruitment': {
        'Consultant': {
            'A': 0.040,      # 4.0% monthly - Sustainable growth rate (48% annually)
            'AC': 0.025,     # 2.5% monthly - Balanced growth rate (30% annually)
            'C': 0.020,      # 2.0% monthly - Positive growth rate (24% annually)
            'SrC': 0.018,    # 1.8% monthly - Above churn rate (21.6% annually)
            'AM': 0.015,     # 1.5% monthly - Match churn to maintain headcount (18% annually)
            'M': 0.010,      # 1.0% monthly - Slight growth above churn (12% annually)
            'SrM': 0.010,    # 1.0% monthly - Slight growth above churn (12% annually)
            'PiP': 0.008     # 0.8% monthly - Slight growth above churn (9.6% annually)
        },
        'Sales': {
            'A': 0.025,      # 2.5% monthly - Positive growth rate (30% annually)
            'AC': 0.022,     # 2.2% monthly - Above churn rate (26.4% annually)
            'C': 0.022,      # 2.2% monthly - Above churn rate (26.4% annually)
            'SrC': 0.022,    # 2.2% monthly - Above churn rate (26.4% annually)
            'AM': 0.020,     # 2.0% monthly - Above churn rate (24% annually)
            'M': 0.020,      # 2.0% monthly - Above churn rate (24% annually)
            'SrM': 0.018,    # 1.8% monthly - Slight growth above churn (21.6% annually)
            'PiP': 0.018     # 1.8% monthly - Slight growth above churn (21.6% annually)
        },
        'Recruitment': {
            'A': 0.020,      # 2.0% monthly - Positive growth rate (24% annually)
            'AC': 0.018,     # 1.8% monthly - Balanced growth rate (21.6% annually)
            'C': 0.018,      # 1.8% monthly - Above churn rate (21.6% annually)
            'SrC': 0.016,    # 1.6% monthly - Above churn rate (19.2% annually)
            'AM': 0.016,     # 1.6% monthly - Above churn rate (19.2% annually)
            'M': 0.016,      # 1.6% monthly - Above churn rate (19.2% annually)
            'SrM': 0.016,    # 1.6% monthly - Above churn rate (19.2% annually)
            'PiP': 0.016     # 1.6% monthly - Above churn rate (19.2% annually)
        },
        'Operations': 0.021  # 2.1% monthly - Historical rate (25.2% annually)
    },
    'churn': {
        'Consultant': {
            'A': 0.0128,     # 1.28% monthly - Historical rate (14.3% annually)
            'AC': 0.0153,    # 1.53% monthly - Historical rate (16.9% annually)
            'C': 0.0173,     # 1.73% monthly - Historical rate (18.9% annually)
            'SrC': 0.0173,   # 1.73% monthly - Use C rate for SrC
            'AM': 0.0127,    # 1.27% monthly - Historical rate (14.2% annually)
            'M': 0.0071,     # 0.71% monthly - Historical rate (8.2% annually)
            'SrM': 0.0071,   # 0.71% monthly - Use M rate for SrM
            'PiP': 0.0071    # 0.71% monthly - Use M rate for PiP
        },
        'Sales': {
            'A': 0.0175,     # 1.75% monthly - Historical SRC rate (19.1% annually)
            'AC': 0.0175,    # 1.75% monthly - Use SRC rate
            'C': 0.0175,     # 1.75% monthly - Use SRC rate
            'SrC': 0.0175,   # 1.75% monthly - Historical SRC rate
            'AM': 0.0175,    # 1.75% monthly - Use SRC rate
            'M': 0.0175,     # 1.75% monthly - Use SRC rate
            'SrM': 0.0175,   # 1.75% monthly - Use SRC rate
            'PiP': 0.0175    # 1.75% monthly - Use SRC rate
        },
        'Recruitment': {
            'A': 0.0150,     # 1.50% monthly - Estimated rate
            'AC': 0.0150,    # 1.50% monthly - Estimated rate
            'C': 0.0150,     # 1.50% monthly - Estimated rate
            'SrC': 0.0150,   # 1.50% monthly - Estimated rate
            'AM': 0.0150,    # 1.50% monthly - Estimated rate
            'M': 0.0150,     # 1.50% monthly - Estimated rate
            'SrM': 0.0150,   # 1.50% monthly - Estimated rate
            'PiP': 0.0150    # 1.50% monthly - Estimated rate
        },
        'Operations': 0.0149  # 1.49% monthly - Historical OPE rate (16.5% annually)
    },
    'progression': {
        'evaluation_months': [5, 11],  # May and November
        'A_AM_rate': 0.15,            # 15% for A-AM levels in evaluation months
        'M_plus_rate': 0.05,          # 5% for M+ levels in November only
        'non_evaluation_rate': 0.0    # 0% in non-evaluation months
    },
    'utr': 0.85,            # 85% utilization rate
    'unplanned_absence': 0.05,  # 5% unplanned absence
    'working_hours': 1800,      # Annual working hours
    'other_expense': 10000      # Other expenses per office
}

# Journey classifications
JOURNEY_CLASSIFICATION = {
    'Journey 1': ['A', 'AC'],           # Junior levels
    'Journey 2': ['C', 'SrC'],         # Mid levels
    'Journey 3': ['AM', 'M'],          # Senior levels
    'Journey 4': ['SrM', 'PiP']        # Principal levels
}

def get_monthly_pricing(base_price, monthly_increase=0.0025):
    """Generate monthly pricing with gradual increase throughout the year"""
    return {
        f'price_{i}': base_price * (1 + monthly_increase * (i-1)) 
        for i in range(1, 13)
    }

def get_monthly_salaries(base_salary, monthly_increase=0.0025):
    """Generate monthly salaries with gradual increase throughout the year"""
    return {
        f'salary_{i}': base_salary * (1 + monthly_increase * (i-1)) 
        for i in range(1, 13)
    }

def get_monthly_rates(role_name='Consultant', level_name='A'):
    """Generate monthly rates with progression timing for specific role/level"""
    rates = {}
    for i in range(1, 13):
        # Get recruitment rate based on role and level
        if role_name in DEFAULT_RATES['recruitment'] and isinstance(DEFAULT_RATES['recruitment'][role_name], dict):
            rates[f'recruitment_{i}'] = DEFAULT_RATES['recruitment'][role_name].get(level_name, 0.01)
        elif role_name in DEFAULT_RATES['recruitment']:
            rates[f'recruitment_{i}'] = DEFAULT_RATES['recruitment'][role_name]
        else:
            rates[f'recruitment_{i}'] = 0.01  # Default fallback
            
        # Get churn rate based on role and level
        if role_name in DEFAULT_RATES['churn'] and isinstance(DEFAULT_RATES['churn'][role_name], dict):
            rates[f'churn_{i}'] = DEFAULT_RATES['churn'][role_name].get(level_name, 0.014)
        elif role_name in DEFAULT_RATES['churn']:
            rates[f'churn_{i}'] = DEFAULT_RATES['churn'][role_name]
        else:
            rates[f'churn_{i}'] = 0.014  # Default fallback
            
        rates[f'utr_{i}'] = DEFAULT_RATES['utr']
        
        # Progression rates based on evaluation timing and level
        if i in DEFAULT_RATES['progression']['evaluation_months']:
            if level_name in ['M', 'SrM', 'PiP']:
                # M+ levels only progress in November
                if i == 11:
                    rates[f'progression_{i}'] = DEFAULT_RATES['progression']['M_plus_rate']
                else:
                    rates[f'progression_{i}'] = DEFAULT_RATES['progression']['non_evaluation_rate']
            else:
                # A-AM levels progress in May and November
                rates[f'progression_{i}'] = DEFAULT_RATES['progression']['A_AM_rate']
        else:
            # Other months
            rates[f'progression_{i}'] = DEFAULT_RATES['progression']['non_evaluation_rate']
    
    return rates

def get_office_fte_distribution(total_fte):
    """Calculate FTE distribution for an office"""
    consultant_fte = int(total_fte * ROLE_DISTRIBUTION['Consultant'])
    sales_fte = int(total_fte * ROLE_DISTRIBUTION['Sales'])
    recruitment_fte = int(total_fte * ROLE_DISTRIBUTION['Recruitment'])
    operations_fte = total_fte - consultant_fte - sales_fte - recruitment_fte
    
    return {
        'Consultant': consultant_fte,
        'Sales': sales_fte,
        'Recruitment': recruitment_fte,
        'Operations': operations_fte
    }

def get_consultant_level_distribution(consultant_fte):
    """Distribute consultant FTE across levels"""
    distribution = {}
    remaining_fte = consultant_fte
    
    for level, percentage in CONSULTANT_LEVEL_DISTRIBUTION.items():
        if level == 'PiP':  # Last level gets remaining
            distribution[level] = remaining_fte
        else:
            level_fte = int(consultant_fte * percentage)
            distribution[level] = level_fte
            remaining_fte -= level_fte
    
    return distribution

def generate_default_config():
    """Generate complete default configuration for all offices using real headcount data"""
    config_data = []
    
    for office_name in OFFICE_HEADCOUNT.keys():
        # Get actual office data
        office_data = ACTUAL_OFFICE_LEVEL_DATA.get(office_name, {})
        
        # Get pricing and salary base values
        office_pricing = BASE_PRICING.get(office_name, BASE_PRICING['Stockholm'])
        office_salaries = BASE_SALARIES.get(office_name, BASE_SALARIES['Stockholm'])
        
        # Add roles with levels (Consultant, Sales, Recruitment)
        for role_name in ['Consultant', 'Sales', 'Recruitment']:
            role_levels = office_data.get(role_name, {})
            
            for level, fte in role_levels.items():
                if fte > 0:  # Only add levels with actual FTE
                    base_price = office_pricing.get(level, office_pricing.get('A', 1000))  # Default fallback
                    base_salary = office_salaries.get(level, office_salaries.get('A', 40000))  # Default fallback
                    
                    # Get monthly rates specific to this role and level
                    monthly_rates = get_monthly_rates(role_name, level)
                
                    row = {
                        'Office': office_name,
                        'Role': role_name,
                        'Level': level,
                        'FTE': fte,
                        **get_monthly_pricing(base_price),
                        **get_monthly_salaries(base_salary),
                        **monthly_rates
                    }
                
                # Adjust progression rates for M+ levels (only November)
                if level in ['M', 'SrM', 'PiP']:
                    for i in range(1, 13):
                        if i == 11:  # November only for senior levels
                            row[f'progression_{i}'] = DEFAULT_RATES['progression']['M_plus_rate']
                        else:
                            row[f'progression_{i}'] = DEFAULT_RATES['progression']['non_evaluation_rate']
                
                config_data.append(row)
        
        # Add Operations (flat role)
        operations_fte = office_data.get('Operations', 0)
        if operations_fte > 0:
            # Get monthly rates for Operations
            operations_rates = get_monthly_rates('Operations', 'Operations')
            
            row = {
                'Office': office_name,
                'Role': 'Operations',
                'Level': None,
                'FTE': operations_fte,
                **get_monthly_pricing(80.0),  # Lower pricing for operations
                **get_monthly_salaries(40.0),  # Lower salary for operations
                **operations_rates
            }
            
            # Operations has no progression
            for i in range(1, 13):
                row[f'progression_{i}'] = 0.0
            
            config_data.append(row)
    
    return config_data

if __name__ == "__main__":
    # Generate and display sample configuration
    config = generate_default_config()
    print(f"Generated {len(config)} configuration rows")
    print(f"Offices: {len(OFFICE_HEADCOUNT)}")
    print(f"Total FTE: {sum(OFFICE_HEADCOUNT.values())}") 