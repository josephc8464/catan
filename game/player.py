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
    resources: dict[str, int] = field(default_factory=dict)

    structures: list[tuple[int, str]] = field(default_factory=list)   # (vertex, structure_type)
    roads: set[tuple[int, int]] = field(default_factory=set)          # canonical (min, max) pairs
    bought_dev_cards: list[str] = field(default_factory=list)
    active_dev_cards: list[str] = field(default_factory=list)
    used_cards: list[str] = field(default_factory=list)

    board_context: ClassVar[BoardContext] = BoardContext()

    @classmethod
    def create(cls, name: str, color: str, context: BoardContext) -> "Player":
        """Factory method that constructs a Player with initialized resource counts."""
        initial_resources = {res: 0 for res in context.RESOURCES}
        return cls(name=name, color=color, resources=initial_resources)
    
    # =========================================================================

    # --- HELPERS ---

    # =========================================================================

    @staticmethod
    def _canonical_road(v1: int, v2: int) -> tuple[int, int]:
        """Returns a canonical undirected edge key — mirrors Graph._canonical."""
        return (v1, v2) if v1 < v2 else (v2, v1)

    # =========================================================================

    # --- RESOURCE MANAGEMENT ---

    # =========================================================================

    def can_afford(self, cost: dict[str, int]) -> bool:
        """
        Returns True if the player has at least the specified amount of each resource.
        Raises ValueError if the cost map contains invalid resources or negative amounts.
        """
        self.board_context.validate_resource_cost(cost)
        return all(self.resources.get(res, 0) >= amt for res, amt in cost.items())

    def add_resource(self, resource: str, amount: int) -> None:
        """
        Adds a single resource to the player's inventory.
        Raises ValueError if the resource is not defined in BoardContext.
        """
        self.board_context.validate_resource(resource)
        self.resources[resource] = self.resources.get(resource, 0) + amount

    def add_resources(self, resources: dict[str, int]) -> None:
        """
        Adds multiple resources at once (all-or-nothing).
        Raises ValueError if any resource in the map is invalid.
        Validates the full map before applying any changes.
        """
        self.board_context.validate_resource_cost(resources)
        for res, amt in resources.items():
            self.resources[res] = self.resources.get(res, 0) + amt

    def remove_resource(self, resource: str, amount: int) -> bool:
        """
        Deducts a single resource from inventory.
        Raises ValueError if the resource is not defined in BoardContext.
        Returns False if the player has insufficient funds — valid game state.
        """
        self.board_context.validate_resource(resource)
        if self.resources.get(resource, 0) < amount:
            return False
        self.resources[resource] -= amount
        return True

    def remove_resources(self, resources: dict[str, int]) -> bool:
        """
        Deducts multiple resources at once (all-or-nothing).
        Raises ValueError if any resource in the map is invalid.
        Returns False if the player cannot afford the total cost
        """
        self.board_context.validate_resource_cost(resources)
        if not self.can_afford(resources):
            return False
        for res, amt in resources.items():
            self.resources[res] -= amt
        return True

    # =========================================================================

    # --- DEVELOPMENT CARDS ---

    # =========================================================================

    def has_dev_card(self, card: str) -> bool:
        """
        Returns True if the player holds the specified card in their active hand.
        Raises ValueError if the card is not defined in BoardContext.
        """
        self.board_context.validate_dev_card(card)
        return card in self.active_dev_cards

    def update_dev_cards(self) -> None:
        """
        Moves all newly bought cards into the active hand.
        Called at end of turn to enforce the one-turn play cooldown.
        """
        self.active_dev_cards.extend(self.bought_dev_cards)
        self.bought_dev_cards.clear()

    def add_dev_card(self, card: str) -> None:
        """
        Adds a development card to the appropriate hand.
        Cards with a cooldown go to bought_dev_cards (playable next turn).
        Cards without a cooldown (e.g. victory_point) go directly to active_dev_cards.
        Raises ValueError if the card is not defined in BoardContext.
        """
        self.board_context.validate_dev_card(card)
        target = self.bought_dev_cards if self.board_context.has_cooldown(card) else self.active_dev_cards
        target.append(card)

    def remove_dev_card(self, card: str) -> bool:
        """
        Moves a development card from the active hand to the used pile.
        Raises ValueError if the card is not defined in BoardContext.
        Returns False if the player does not currently hold the card — valid game state.
        """
        self.board_context.validate_dev_card(card)
        if not self.has_dev_card(card):
            return False
        self.active_dev_cards.remove(card)
        self.used_cards.append(card)
        return True

    def count_used(self, card: str) -> int:
        """
        Returns how many times the player has played a specific card type.
        Raises ValueError if the card is not defined in BoardContext.
        """
        self.board_context.validate_dev_card(card)
        return self.used_cards.count(card)

    # =========================================================================

    # --- STRUCTURES & SCORING ---

    # =========================================================================

    def add_structure(self, vertex: int, structure_type: str) -> None:
        """
        Appends a structure to the player's structure list.
        Raises ValueError if the structure type is not defined in BoardContext.
        """
        self.board_context.validate_structure(structure_type)
        self.structures.append((vertex, structure_type))

    def remove_structure(self, vertex: int) -> bool:
        """
        Removes the structure at the specified vertex.
        Used when upgrading (settlement -> city) to return the piece to supply.
        Returns False if no structure is found at the vertex — valid game state.
        """
        for i, (v, _) in enumerate(self.structures):
            if v == vertex:
                del self.structures[i]
                return True
        return False

    def count_structure(self, structure_type: str) -> int:
        """
        Returns the number of a specific structure type placed.
        Raises ValueError if the structure type is not defined in BoardContext.
        """
        self.board_context.validate_structure(structure_type)
        return sum(1 for _, s_type in self.structures if s_type == structure_type)

    def add_road(self, v1: int, v2: int) -> None:
        """Adds a road to the player's road set using a canonical undirected key."""
        self.roads.add(self._canonical_road(v1, v2))

    def remove_road(self, v1: int, v2: int) -> bool:
        """
        Removes a road from the player's road set.
        Returns False if the road does not exist — valid game state.
        """
        key = self._canonical_road(v1, v2)
        if key not in self.roads:
            return False
        self.roads.discard(key)
        return True

    def local_vp(self) -> int:
        """
        Calculates the player's locally visible Victory Points.
        Includes VP from placed structures and from victory point dev cards.
        Does NOT include board awards (Longest Road, Largest Army) — see check_victory().
        """
        struct_vp = sum(self.board_context.get_structure_vp(s_type) for _, s_type in self.structures)
        card_vp = sum(self.board_context.get_card_vp(c) for c in self.active_dev_cards)
        return struct_vp + card_vp

    def has_available_pieces(self, buildable: str) -> bool:
        """
        Returns True if the player has not yet reached the maximum allowed pieces.
        Raises ValueError if the buildable type is not defined in BoardContext.
        Raises ValueError on state corruption (placed count exceeds max).
        """
        self.board_context.validate_buildable(buildable)

        count = len(self.roads) if buildable == 'road' else self.count_structure(buildable)
        limit = self.board_context.get_max_pieces(buildable)

        if limit == 0:
            return False

        if count > limit:
            raise ValueError(
                f"STATE CORRUPTION: {self.color} has {count} {buildable}s, max is {limit}!"
            )

        return count < limit