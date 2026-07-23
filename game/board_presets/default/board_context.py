class BoardContext:
    
    RESOURCES = ['wood', 'brick', 'sheep', 'wheat', 'ore']
    
    #Dev Card Name : VP
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
        'dev_card':   {'sheep': 1, 'wheat': 1, 'ore': 1},
    }
    
    WINNING_VP_THRESHOLD = 10

    AWARDS = {
        'longest_road': 2,
        'largest_army': 2,
    }

    #Building types must be placed in order of level
    STRUCTURE_TYPES = [
        'settlement',
        'city'
    ]
    
    #Resource amount a structure type returns when placed on tile
    STRUCTURE_RESOURCES = {
        'settlement': 1,
        'city': 2,
    }

    STRUCTURE_VP = {
        'settlement': 1,
        'city':       2,
    }
    
    BANK_RATIO = (4, 1)

    PORT_RATIO = {
        'any': (3, 1),
        'sheep': (2, 1),
        'wood': (2, 1),
        'wheat': (2, 1),
        'ore': (2, 1),
        'brick': (2, 1),
    }
    #Max amount of allowed buildables per player
    MAX_PIECES = {
        'settlement': 5,
        'city':       4,
        'road':       15,
    }

    # ==========================================
    #                VALIDATORS
    # ==========================================
    def is_valid_resource_cost(self, resource_cost: dict[str, int]) -> bool:
        """
        Validates that a dictionary only contains real resources 
        and that the amounts are positive integers.
        """
        for resource, amount in resource_cost.items():
            if not self.is_valid_resource(resource):
                return False
            if amount < 0:
                return False
        return True

    def is_valid_resource(self, resource: str) -> bool:
        return resource in self.RESOURCES

    def is_valid_dev_card(self, card_name: str) -> bool:
        return card_name in self.DEVELOPMENT_CARDS

    def is_valid_buildable(self, item_name: str) -> bool:
        """Checks if something can be built/bought (includes roads and dev cards)."""
        return item_name in self.BUILDING_COSTS

    def is_valid_structure(self, structure_name: str) -> bool:
        """Checks if a string is strictly a settlement or city."""
        return structure_name in self.STRUCTURE_TYPES
        
    def is_valid_award(self, award_name: str) -> bool:
        return award_name in self.AWARDS

    # ==========================================
    # GETTERS (Safely retrieve data without KeyError crashes)
    # ==========================================

    def get_cost(self, item_name: str) -> dict[str, int]:
        """Returns the dictionary of costs, or an empty dict if invalid."""
        return self.BUILDING_COSTS.get(item_name, {})

    def get_max_pieces(self, piece_name: str) -> int:
        """Returns the max limit, or 0 if the piece doesn't have a limit."""
        return self.MAX_PIECES.get(piece_name, 0)

    def get_structure_vp(self, structure_name: str) -> int:
        """Returns the VP value of a building, or 0 if invalid."""
        return self.STRUCTURE_VP.get(structure_name, 0)

    def get_card_vp(self, card: str) -> int:
        """Returns the VP value of a card, or 0 if invalid."""
        return self.DEVELOPMENT_CARDS.get(card, 0)
    
    def get_resource_yield(self, structure_name: str) -> int:
        """Returns how many resources a building produces (e.g. city = 2), or 0."""
        return self.STRUCTURE_RESOURCES.get(structure_name, 0)
        
    def get_next_upgrade(self, current_building: str) -> str | None:
        """
        Pass 'settlement', returns 'city'. 
        Returns None if already fully upgraded or invalid.
        """
        try:
            current_index = self.STRUCTURE_TYPES.index(current_building)
            if current_index == len(self.STRUCTURE_TYPES) - 1:
                return None
            return self.STRUCTURE_TYPES[current_index + 1]
        except ValueError:
            return None
    
    def get_port_ratio(self, port: str) -> tuple[int, int]:
        """Returns the trade ratio of a port, or (0, 0) if invalid."""
        return self.PORT_RATIO.get(port, (0,0))
    
    def get_bank_ratio(self) -> tuple[int, int]:
        """Returns the trade ratio of the bank."""
        return self.BANK_RATIO