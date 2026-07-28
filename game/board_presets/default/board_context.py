class BoardContext:
    """
    Immutable configuration constants for the standard Catan board.
    Single source of truth for all game rules, costs, limits,
    and valid identifiers.
    __slots__ prevents accidental attribute addition at runtime.
    """

    __slots__ = ()

    RESOURCES: frozenset[str] = frozenset({'wood', 'brick', 'sheep', 'wheat', 'ore'})

    DEVELOPMENT_CARDS: dict[str, int] = {
        'knight':         0,
        'victory_point':  1,
        'road_building':  0,
        'year_of_plenty': 0,
        'monopoly':       0,
    }

    DEVELOPMENT_CARDS_PLAY_COOLDOWN: dict[str, bool] = {
        'knight':         True,
        'victory_point':  False,
        'road_building':  True,
        'year_of_plenty': True,
        'monopoly':       True,
    }

    BUILDING_COSTS: dict[str, dict[str, int]] = {
        'settlement': {'wood': 1, 'brick': 1, 'sheep': 1, 'wheat': 1},
        'city':       {'wheat': 2, 'ore': 3},
        'road':       {'wood': 1, 'brick': 1},
        'dev_card':   {'sheep': 1, 'wheat': 1, 'ore': 1},
    }

    STRUCTURE_TYPES: tuple[str, ...] = ('settlement', 'city')

    STRUCTURE_RESOURCES: dict[str, int] = {
        'settlement': 1,
        'city':       2,
    }

    STRUCTURE_VP: dict[str, int] = {
        'settlement': 1,
        'city':       2,
    }

    WINNING_VP_THRESHOLD: int = 10

    AWARDS: dict[str, int] = {
        'longest_road': 2,
        'largest_army': 2,
    }

    BANK_RATIO: tuple[int, int] = (4, 1)

    PORT_RATIO: dict[str, tuple[int, int]] = {
        'any':   (3, 1),
        'sheep': (2, 1),
        'wood':  (2, 1),
        'wheat': (2, 1),
        'ore':   (2, 1),
        'brick': (2, 1),
    }

    MAX_PIECES: dict[str, int] = {
        'settlement': 5,
        'city':       4,
        'road':       15,
    }

    # =========================================================================

    # --- VALIDATORS ---

    # =========================================================================

    def validate_resource(self, resource: str) -> None:
        """Raises ValueError if the resource is not a recognised Catan resource."""
        if resource not in self.RESOURCES:
            raise ValueError(f"Unknown resource: '{resource}'")

    def validate_resource_cost(self, resource_cost: dict[str, int]) -> None:
        """
        Raises ValueError if any key is not a valid resource
        or any amount is negative.
        """
        for res, amount in resource_cost.items():
            self.validate_resource(res)
            if amount < 0:
                raise ValueError(
                    f"Resource amount for '{res}' cannot be negative, got {amount}."
                )

    def validate_dev_card(self, card_name: str) -> None:
        """Raises ValueError if the card name is not in the development card registry."""
        if card_name not in self.DEVELOPMENT_CARDS:
            raise ValueError(f"Unknown development card: '{card_name}'")

    def validate_buildable(self, item_name: str) -> None:
        """Raises ValueError if the item has no entry in BUILDING_COSTS."""
        if item_name not in self.BUILDING_COSTS:
            raise ValueError(f"Unknown buildable: '{item_name}'")

    def validate_structure(self, structure_name: str) -> None:
        """Raises ValueError if the name is not a recognised placeable structure."""
        if structure_name not in self.STRUCTURE_TYPES:
            raise ValueError(f"Unknown structure type: '{structure_name}'")

    def validate_port(self, port: str) -> None:
        """Raises ValueError if the port is not a recognized port."""
        if port not in self.PORT_RATIO:
            raise ValueError(f"Unknown port type: '{port}'")

    def validate_award(self, award_name: str) -> None:
        """Raises ValueError if the award name is not in the awards registry."""
        if award_name not in self.AWARDS:
            raise ValueError(f"Unknown award: '{award_name}'")

    # =========================================================================

    # --- QUERIES ---

    # =========================================================================

    def has_cooldown(self, card: str) -> bool:
        """
        Returns True if the card must wait one turn before it can be played.
        Raises KeyError if the card is not registered — call validate_dev_card first.
        """
        self.validate_dev_card(card)
        return self.DEVELOPMENT_CARDS_PLAY_COOLDOWN[card]

    def get_next_upgrade(self, current_building: str) -> str | None:
        """
        Returns the next structure tier above current_building, or None if fully upgraded.
        Rasies ValueError if structure is invalid
        """
        self.validate_structure(current_building)
        idx = self.STRUCTURE_TYPES.index(current_building)
        return None if idx == len(self.STRUCTURE_TYPES) - 1 else self.STRUCTURE_TYPES[idx + 1]

    # =========================================================================

    # --- SAFE GETTERS ---

    # =========================================================================

    def get_cost(self, item_name: str) -> dict[str, int]:
        """Returns the cost dict for the item. Raises ValueError if item is invalid."""
        self.validate_buildable(item_name)
        return self.BUILDING_COSTS[item_name]

    def get_max_pieces(self, piece_name: str) -> int:
        """Returns the piece limit. Raises ValueError if piece is invalid."""
        self.validate_buildable(piece_name)
        return self.MAX_PIECES[piece_name]

    def get_structure_vp(self, structure_name: str) -> int:
        """Returns the VP value of the structure. Raises ValueError if structure is invalid."""
        self.validate_structure(structure_name)
        return self.STRUCTURE_VP[structure_name]

    def get_card_vp(self, card: str) -> int:
        """Returns the VP value of the dev card. Raises ValueError if card is invalid."""
        self.validate_dev_card(card)
        return self.DEVELOPMENT_CARDS[card]

    def get_resource_yield(self, structure_name: str) -> int:
        """Returns resource yield. Raises ValueError if structure is invalid."""
        self.validate_structure(structure_name)
        return self.STRUCTURE_RESOURCES[structure_name]

    def get_port_ratio(self, port: str) -> tuple[int, int]:
        """Returns the trade ratio for the port. Raises ValueError if port is invalid."""
        self.validate_port(port)
        return self.PORT_RATIO[port]