from dataclasses import dataclass, field
from typing import ClassVar
from .board_presets.default.board_context import BoardContext


@dataclass
class Player:
    """
    Represents a Catan player. Manages their resource inventory,
    placed structures, roads, development cards, and score calculation.
    Acts as a pure data model — no game rule enforcement lives here.
    """
    name: str
    color: str
    resources: dict[str, int]

    structures: list[tuple[int, str]] = field(default_factory=list)  # (vertex, structure_type)
    roads: list[tuple[int, int]] = field(default_factory=list)      
    bought_dev_cards: list[str] = field(default_factory=list)
    active_dev_cards: list[str] = field(default_factory=list)
    used_cards: list[str] = field(default_factory=list)

    board_context: ClassVar[BoardContext] = BoardContext()

    # =========================================================================
    # --- RESOURCE MANAGEMENT ---
    # =========================================================================

    def can_afford(self, cost: dict[str, int]) -> bool:
        """Returns True if the player has at least the specified amount of each resource."""
        if not self.board_context.is_valid_resource_cost(cost):
            return False
        return all(self.resources.get(res, 0) >= amt for res, amt in cost.items())

    def add_resource(self, resource: str, amount: int) -> bool:
        """Adds a single valid resource to the player's inventory. Returns False on invalid input."""
        if not self.board_context.is_valid_resource(resource):
            return False
        self.resources[resource] = self.resources.get(resource, 0) + amount
        return True

    def add_resources(self, resources: dict[str, int]) -> bool:
        """
        Adds multiple resources at once.
        Validates the full cost map before applying any changes (all-or-nothing).
        """
        if not self.board_context.is_valid_resource_cost(resources):
            return False
        for res, amt in resources.items():
            self.resources[res] = self.resources.get(res, 0) + amt
        return True

    def remove_resource(self, resource: str, amount: int) -> bool:
        """Deducts a single resource. Returns False if invalid or insufficient funds."""
        if not self.board_context.is_valid_resource(resource):
            return False
        if self.resources.get(resource, 0) < amount:
            return False
        self.resources[resource] -= amount
        return True

    def remove_resources(self, resources: dict[str, int]) -> bool:
        """
        Deducts multiple resources at once.
        Fails entirely if the player cannot afford the total cost (all-or-nothing).
        """
        if not self.board_context.is_valid_resource_cost(resources) or not self.can_afford(resources):
            return False
        for res, amt in resources.items():
            self.resources[res] -= amt
        return True

    # =========================================================================
    # --- DEVELOPMENT CARDS ---
    # =========================================================================

    def has_dev_card(self, card: str) -> bool:
        """Returns True if the player holds the specified card in their ACTIVE hand."""
        if not self.board_context.is_valid_dev_card(card):
            return False
        return card in self.active_dev_cards

    def update_dev_cards(self) -> bool:
        """
        Moves all newly bought cards into the active hand.
        Called at the end of each turn to enforce the one-turn play cooldown.
        """
        self.active_dev_cards.extend(self.bought_dev_cards)
        self.bought_dev_cards.clear()
        return True

    def add_dev_card(self, card: str) -> bool:
        """
        Adds a development card to the appropriate hand.
        Cards with a cooldown go to bought_dev_cards (playable next turn).
        Cards without a cooldown (e.g., victory_point) go directly to active_dev_cards.
        """
        if not self.board_context.is_valid_dev_card(card):
            return False
        if self.board_context.has_cooldown(card):
            self.bought_dev_cards.append(card)
        else:
            self.active_dev_cards.append(card)
        return True

    def remove_dev_card(self, card: str) -> bool:
        """Moves a development card from the active hand to the used pile."""
        if not self.board_context.is_valid_dev_card(card) or not self.has_dev_card(card):
            return False
        self.active_dev_cards.remove(card)
        self.used_cards.append(card)
        return True

    def count_used(self, card: str) -> int:
        """Returns how many times the player has played a specific card type. Returns -1 if invalid."""
        if not self.board_context.is_valid_dev_card(card):
            return -1
        return self.used_cards.count(card)

    # =========================================================================
    # --- STRUCTURES & SCORING ---
    # =========================================================================

    def add_structure(self, vertex: int, structure_type: str) -> bool:
        """Appends a structure to the player's structure list. Returns False if type is invalid."""
        if not self.board_context.is_valid_structure(structure_type):
            return False
        self.structures.append((vertex, structure_type))
        return True

    def remove_structure(self, vertex: int) -> bool:
        """
        Removes the structure at the specified vertex from the player's list.
        Used when upgrading (settlement -> city) to return the piece to supply.
        Returns False if no structure is found at the vertex.
        """
        for pair in self.structures:
            if pair[0] == vertex:
                self.structures.remove(pair)
                return True
        return False

    def count_structure(self, structure_type: str) -> int:
        """Returns the number of a specific structure type the player has placed. Returns -1 if invalid."""
        if not self.board_context.is_valid_structure(structure_type):
            return -1
        return sum(1 for _, s_type in self.structures if s_type == structure_type)

    def add_road(self, v1: int, v2: int) -> bool:
        """Appends a road to the player's road list."""
        self.roads.append((v1, v2))
        return True
    
    def remove_road(self, v1: int, v2: int) -> bool:
        """
        Removes a road at the specified edge (v1, v2) from the player's list.
        Returns False if no road is found for that edge.
        """
        if (v1, v2) in self.roads:
            self.roads.remove((v1, v2))
            return True
        elif (v2, v1) in self.roads:
            self.roads.remove((v2, v1))
            return True
            
        return False
    
    def count_roads(self) -> int:
        """Returns the number of roads the player has placed on the board."""
        return len(self.roads)

    def local_vp(self) -> int:
        """
        Calculates the player's locally visible Victory Points.
        Includes VP from placed structures and from victory point dev cards.
        Does NOT include board awards (Longest Road, Largest Army) — see check_victory().
        """
        struct_vp = sum(self.board_context.get_structure_vp(s[1]) for s in self.structures)
        card_vp = sum(self.board_context.get_card_vp(c) for c in self.active_dev_cards)
        return struct_vp + card_vp

    def has_available_pieces(self, buildable: str) -> bool:
        """
        Returns True if the player has not yet reached the maximum allowed
        pieces for the given buildable type.
        Handles roads separately since they are stored in self.roads, not self.structures.
        Raises ValueError on state corruption (placed count exceeds max).
        """
        # FIX: Roads are tracked in self.roads, not self.structures
        if buildable == 'road':
            count = self.count_roads()
        else:
            count = self.count_structure(buildable)
            if count == -1:
                return False  # Invalid buildable type

        limit = self.board_context.get_max_pieces(buildable)
        if limit == 0:
            return False

        if count > limit:
            raise ValueError(
                f"STATE CORRUPTION: {self.color} has {count} {buildable}s, max is {limit}!"
            )

        return count < limit