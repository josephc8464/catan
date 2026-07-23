from dataclasses import dataclass, field
from typing import ClassVar
from .board_presets.default.board_context import BoardContext

@dataclass
class Player:
    """
    Represents a player in the game, managing their inventory, structures, and score.
    Acts as a data model that encapsulates its internal state.
    """
    name: str
    color: str
    resources: dict[str, int]
    
    structures: list[tuple[int, str]] = field(default_factory=list) #(vertex, structure_type)
    roads: list[tuple[int, int]] = field(default_factory=list)
    dev_cards: list[str] = field(default_factory=list)
    used_cards: list[str] = field(default_factory=list)

    board_context: ClassVar[BoardContext] = BoardContext()

    # =========================================================================
    # --- RESOURCE MANAGEMENT ---
    # =========================================================================

    def can_afford(self, cost: dict[str, int]) -> bool:
        """Evaluates if the player has the resources to meet a specified cost map."""
        if not self.board_context.is_valid_resource_cost(cost):
            return False
        return all(self.resources.get(res, 0) >= amt for res, amt in cost.items())
    
    def add_resource(self, resource: str, amount: int) -> bool:
        """Safely adds a single valid resource to the player's inventory."""
        if not self.board_context.is_valid_resource(resource):
            return False
        self.resources[resource] = self.resources.get(resource, 0) + amount
        return True
    
    def add_resources(self, resources: dict[str, int]) -> bool:
        """Safely adds multiple resources. Follows an all-or-nothing rule."""
        if not self.board_context.is_valid_resource_cost(resources):
            return False
        for res, amt in resources.items():
            self.resources[res] = self.resources.get(res, 0) + amt
        return True
    
    def remove_resource(self, resource: str, amount: int) -> bool:
        """Deducts a single valid resource from the player's inventory."""
        if not self.board_context.is_valid_resource(resource):
            return False
        if self.resources.get(resource, 0) < amount:
            return False
        self.resources[resource] -= amount
        return True
        
    def remove_resources(self, resources: dict[str, int]) -> bool:
        """Deducts multiple resources. Fails entirely if the player cannot afford the total cost."""
        if not self.board_context.is_valid_resource_cost(resources) or not self.can_afford(resources):
            return False
        for res, amt in resources.items():
            self.resources[res] -= amt
        return True

    # =========================================================================
    # --- DEVELOPMENT CARDS ---
    # =========================================================================

    def has_dev_card(self, card: str) -> bool:
        """Checks if the player currently holds a specific, valid development card."""
        if not self.board_context.is_valid_dev_card(card):
            return False
        return card in self.dev_cards

    def add_dev_card(self, card: str) -> bool:
        """Moves a development card into the player's active hand."""
        if not self.board_context.is_valid_dev_card(card):
            return False
        self.dev_cards.append(card)
        return True
     
    def remove_dev_card(self, card: str) -> bool:
        """Moves a development card from the active hand to the used pile."""
        if not self.board_context.is_valid_dev_card(card) or not self.has_dev_card(card):
            return False
        self.dev_cards.remove(card)
        self.used_cards.append(card)
        return True

    def count_used(self, card: str) -> int:
        """Returns the total number of times the player has played a specific card type."""
        if not self.board_context.is_valid_dev_card(card):
            return -1
        return self.used_cards.count(card)

    # =========================================================================
    # --- STRUCTURES & SCORING ---
    # =========================================================================
    def add_structure(self, vertex: int, structure_type: str) -> bool:
        """Add a structure into the player list"""
        if not self.board_context.is_valid_structure(structure_type):
            return False
        
        self.structures.append((vertex, structure_type))
        return True
    
    def remove_structure(self, vertex: int) -> bool:
        """Removes a structure at the specified vertex from the player's list."""
        for pair in self.structures:
            if pair[0] == vertex:
                self.structures.remove(pair)
                return True
                
        return False

    def count_structure(self, structure_type: str) -> int:
        """Returns the current number of a specific structure type placed on the board."""
        if not self.board_context.is_valid_structure(structure_type):
            return -1 
        return sum(1 for _, s_type in self.structures if s_type == structure_type)
    
    def count_roads(self) -> int:
        """Returns the current number of roads placed on the board."""
        return len(self.roads)
    
    def local_vp(self) -> int:
        """Calculates and returns the player's visible, structural, and card-based Victory Points."""
        struct_vp = sum(self.board_context.get_structure_vp(s[1]) for s in self.structures)
        card_vp = sum(self.board_context.get_card_vp(c) for c in self.dev_cards)
        return struct_vp + card_vp
    
    def has_available_pieces(self, buildable: str) -> bool:
        """Calculates and returns whether a player has reach the maximum amount of pieces of a buildable."""
        sum_builds = self.count_structure(buildable)
        limit = self.board_context.get_max_pieces(buildable)
        
        if limit is 0:
            return False
        
        if sum_builds > limit:
            raise ValueError(f"STATE CORRUPTION: {self.color} has {sum_builds} {buildable}s, max is {limit}!")
        
        return sum_builds < limit