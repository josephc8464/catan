from dataclasses import dataclass
from typing import ClassVar


@dataclass
class Tile:
    """
    Represents a single hex tile on the Catan board.
    Holds the resource type, dice number, and unique tile ID
    used for graph construction and robber placement tracking.
    """
    tile_id: int
    resource: str
    number: int | None  # None for the desert tile

    DESERT_RESOURCE: ClassVar[str] = 'desert'

    @property
    def is_desert(self) -> bool:
        """Returns True if this tile is the desert (no resource production)."""
        return self.resource == self.DESERT_RESOURCE

    @property
    def is_productive(self) -> bool:
        """Returns True if this tile can produce resources on a dice roll."""
        return not self.is_desert and self.number is not None

    def produces_on_roll(self, roll: int) -> bool:
        """Returns True if this tile activates on the given dice roll value."""
        return self.is_productive and self.number == roll

    def __str__(self) -> str:
        if self.is_desert:
            return f"Tile {self.tile_id}: Desert"
        return f"Tile {self.tile_id}: {self.resource} ({self.number})"