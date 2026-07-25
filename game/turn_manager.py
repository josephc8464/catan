from dataclasses import dataclass, field
from typing import List, Any


@dataclass
class TurnManager:
    """
    Tracks whose turn it is and manages per-turn state flags.
    Advancing the turn resets all flags for the incoming player.
    """
    players: List[Any]
    current_player_index: int = 0
    dice_rolled: bool = False
    played_dev_card: bool = False

    # =========================================================================
    # --- ACCESSORS ---
    # =========================================================================

    def is_current_player(self, player: Any) -> bool:
        """Returns True if the given player is the currently active player."""
        return self.get_current_player() == player

    def get_current_player(self) -> Any:
        """Returns the currently active player object."""
        return self.players[self.current_player_index]

    # =========================================================================
    # --- MUTATORS ---
    # =========================================================================

    def set_players(self, players: List[Any]) -> None:
        """Replaces the current player list."""
        self.players = players

    def set_current_player_index(self, index: int) -> None:
        """Overrides the current player index. Raises IndexError if out of bounds."""
        if 0 <= index < len(self.players):
            self.current_player_index = index
        else:
            raise IndexError("Player index out of bounds.")

    def set_dice_rolled(self, status: bool = True) -> None:
        """Marks whether the dice have been rolled this turn."""
        self.dice_rolled = status

    def set_played_dev_card(self, status: bool = True) -> None:
        """Marks whether a development card has been played this turn."""
        self.played_dev_card = status

    # =========================================================================
    # --- TURN LOGIC ---
    # =========================================================================

    def next_turn(self) -> None:
        """
        Advances to the next player and resets all per-turn state flags.
        Note: update_dev_cards() on the outgoing player should be called
        by GameController.end_turn() BEFORE this method is invoked.
        """
        self.set_current_player_index((self.current_player_index + 1) % len(self.players))
        self.set_dice_rolled(False)
        self.set_played_dev_card(False)