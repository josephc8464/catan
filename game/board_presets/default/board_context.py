class BoardContext:
    
    RESOURCES = ['wood', 'brick', 'sheep', 'wheat', 'ore']
    
    DEVELOPMENT_CARDS = {
        'knight':        0,
        'victory_point': 1,
        'road_building': 0,
        'year_of_plenty':0,
        'monopoly':      0,
    }
    
    BUILDING_COSTS = {
        'settlement': {'wood': 1, 'brick': 1, 'sheep': 1, 'wheat': 1},
        'city':       {'wheat': 2, 'ore': 3},
        'road':       {'wood': 1, 'brick': 1},
        'development':{'sheep': 1, 'wheat': 1, 'ore': 1},
    }
    
    BUILDING_TYPES = [
        'settlement',
        'city'
    ]

    BUILDING_VP = {
        'settlement': 1,
        'city':       2,
    }
    
    MAX_PIECES = {
        'settlement': 5,
        'city':       4,
        'road':       15,
    }