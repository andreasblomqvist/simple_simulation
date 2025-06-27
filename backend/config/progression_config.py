PROGRESSION_CONFIG = {
    'A': {
        'progression_months': [1, 4, 7, 10],
        'start_tenure': 0,
        'time_of_level': 6,
        'next_level': 'AC',
        'journey': 'J-1',
    },
    'AC': {
        'progression_months': [1, 4, 7, 10],
        'start_tenure': 6,
        'time_of_level': 9,
        'next_level': 'C',
        'journey': 'J-1',
    },
    'C': {
        'progression_months': [1, 7],
        'start_tenure': 15,
        'time_of_level': 18,
        'next_level': 'SrC',
        'journey': 'J-1',
    },
    'SrC': {
        'progression_months': [1, 7],
        'start_tenure': 33,
        'time_of_level': 18,
        'next_level': 'AM',
        'journey': 'J-2',
    },
    'AM': {
        'progression_months': [1, 7],
        'start_tenure': 51,
        'time_of_level': 48,
        'next_level': 'M',
        'journey': 'J-2',
    },
    'M': {
        'progression_months': [1],
        'start_tenure': 99,
        'time_of_level': 48,
        'next_level': 'SrM',
        'journey': 'J-3',
    },
    'SrM': {
        'progression_months': [1],
        'start_tenure': 147,
        'time_of_level': 120,
        'next_level': 'Pi',
        'journey': 'J-3',
    },
    'Pi': {
        'progression_months': [1],
        'start_tenure': 267,
        'time_of_level': 12,
        'next_level': 'Pi',
        'journey': 'J-3',
    },
    'P': {
        'progression_months': [1],
        'start_tenure': 279,
        'time_of_level': 1000,
        'next_level': 'P',
        'journey': 'J-3',
    },
    'X': {
        'progression_months': [1],
        'start_tenure': 1279,
        'time_of_level': 1000,
        'next_level': 'X',
        'journey': 'J-3',
    },
    'OPE': {
        'progression_months': [13],
        'start_tenure': 1279,
        'time_of_level': 1000,
        'next_level': 'OPE',
        'journey': None,
    }
}

# CAT progression curves (probabilities for each level and CAT stage)
CAT_CURVES = {
    'A':   {'CAT0': 0.0, 'CAT6': 0.919, 'CAT12': 0.85, 'CAT18': 0.0, 'CAT24': 0.0, 'CAT30': 0.0},
    'AC':  {'CAT0': 0.0, 'CAT6': 0.054, 'CAT12': 0.759, 'CAT18': 0.400, 'CAT24': 0.0, 'CAT30': 0.0},
    'C':   {'CAT0': 0.0, 'CAT6': 0.050, 'CAT12': 0.442, 'CAT18': 0.597, 'CAT24': 0.278, 'CAT30': 0.643, 'CAT36': 0.200, 'CAT42': 0.0},
    'SrC': {'CAT0': 0.0, 'CAT6': 0.206, 'CAT12': 0.438, 'CAT18': 0.317, 'CAT24': 0.211, 'CAT30': 0.206, 'CAT36': 0.167, 'CAT42': 0.0, 'CAT48': 0.0, 'CAT54': 0.0, 'CAT60': 0.0},
    'AM':  {'CAT0': 0.0, 'CAT6': 0.0, 'CAT12': 0.0, 'CAT18': 0.189, 'CAT24': 0.197, 'CAT30': 0.234, 'CAT36': 0.048, 'CAT42': 0.0, 'CAT48': 0.0, 'CAT54': 0.0, 'CAT60': 0.0},
    'M':   {'CAT0': 0.0, 'CAT6': 0.00, 'CAT12': 0.01, 'CAT18': 0.02, 'CAT24': 0.03, 'CAT30': 0.04, 'CAT36': 0.05, 'CAT42': 0.06, 'CAT48': 0.07, 'CAT54': 0.08, 'CAT60': 0.10},
    'SrM': {'CAT0': 0.0, 'CAT6': 0.00, 'CAT12': 0.005, 'CAT18': 0.01, 'CAT24': 0.015, 'CAT30': 0.02, 'CAT36': 0.025, 'CAT42': 0.03, 'CAT48': 0.04, 'CAT54': 0.05, 'CAT60': 0.06},
    'Pi':  {'CAT0': 0.0},
    'P':   {'CAT0': 0.0},
    'X':   {'CAT0': 0.0},
    'OPE': {'CAT0': 0.0},
} 