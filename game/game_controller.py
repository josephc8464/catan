from game.player import Player
from game.board_presets.default.default_board import DefaultBoard
from game.turn_manager import TurnManager
from game.board_presets.default.board_context import BoardContext
from game.messages import GameMsg
import random
import logging


class GameController:
    """
    Orchestrates all game actions and enforces Catan rule logic.
    Acts as the single authority between the board state, players, and turn flow.
    """

    def __init__(self, board: DefaultBoard, players: list[Player], turn_manager: TurnManager, board_context: BoardContext):
        self.board = board
        self.players = players
        self.turn_manager = turn_manager
        self.board_context = board_context

    # =========================================================================
    # --- HELPERS ---
    # =========================================================================

    def _is_turn(self, player: Player) -> bool:
        """Returns True if it is the specified player's turn, logs and returns False otherwise."""
        if not self.turn_manager.is_current_player(player):
            logging.info(GameMsg.err_not_turn(player.name))
            return False
        return True

    def _has_rolled(self, player: Player) -> bool:
        """Returns True if the current player has rolled"""
        if not self.turn_manager.dice_rolled:
            logging.info(GameMsg.err_dice_not_rolled(player.name))
            return False
        return True
    
    def _get_player_by_color(self, color: str) -> Player | None:
        """Returns the player object matching a given color string, or None."""
        return next((p for p in self.players if p.color == color), None)

    # =========================================================================
    # --- SETUP PHASE ---
    # =========================================================================

    def place_initial_settlement(self, player: Player, vertex: int) -> bool:
        """
        Places a free settlement during the setup phase.
        Enforces the distance rule but skips resource cost checks.
        Does NOT grant starting resources — use place_initial_settlement_r2
        for the second placement round.
        """
        structure = 'settlement'

        if not self._is_turn(player):
            return False

        if self.board.get_structure(vertex) != (None, None):
            logging.info(GameMsg.err_vertex_occupied(player.name, structure, vertex))
            return False

        if self.board.has_structure_neighbor(vertex):
            logging.info(GameMsg.err_distance_rule(vertex))
            return False

        self.board.add_structure(vertex, player.color, structure)
        player.structures.append((vertex, structure))

        logging.info(GameMsg.success_build_structure(player.name, structure, vertex))
        return True

    def place_initial_settlement_r2(self, player: Player, vertex: int) -> bool:
        """
        Places a free settlement during the SECOND setup round.
        Identical to round 1 placement, but additionally grants the player
        one resource card from each adjacent producing tile, per Catan rules.
        """
        if not self.place_initial_settlement(player, vertex):
            return False

        # Grant one resource per adjacent producing tile
        for tile_id, verts in self.board.tile_vertices.items():
            if vertex in verts:
                tile = self.board.tiles.get(tile_id)
                if tile and tile.resource in self.board_context.RESOURCES:
                    if self.board.bank_has_resource(tile.resource, 1):
                        player.add_resource(tile.resource, 1)
                        self.board.remove_bank_resource(tile.resource, 1)
                        logging.info(GameMsg.info_setup_resource_grant(
                            player.name, tile.resource, tile_id
                        ))

        return True

    def place_initial_road(self, player: Player, vertex1: int, vertex2: int) -> bool:
        """
        Places a free road during the setup phase.
        Road must connect directly to the player's most recently placed settlement.
        """
        if not self._is_turn(player):
            return False

        if not player.structures:
            logging.error(GameMsg.err_initial_road_no_settlement(player.name))
            return False

        last_settlement_vertex = player.structures[-1][0]

        if last_settlement_vertex not in (vertex1, vertex2):
            logging.info(GameMsg.err_road_connection(player.name, vertex1, vertex2))
            return False

        if self.board.get_road_color(vertex1, vertex2) is not None:
            logging.info(GameMsg.err_edge_occupied(vertex1, vertex2))
            return False

        self.board.add_road(vertex1, vertex2, player.color)
        player.roads.append((vertex1, vertex2))

        logging.info(GameMsg.success_build_road(player.name, vertex1, vertex2))
        return True

    # =========================================================================
    # --- DICE PHASE ---
    # =========================================================================

    def roll_dice(self, player: Player) -> tuple[int, int]:
        """
        Rolls two six-sided dice and triggers resource distribution.
        Returns (0, 0) if it is not the player's turn or dice were already rolled.
        """
        if not self._is_turn(player):
            return (0, 0)

        if self.turn_manager.dice_rolled:
            return (0, 0)

        first_roll = random.randint(1, 6)
        second_roll = random.randint(1, 6)
        result = first_roll + second_roll

        self._distribute_resources(result)
        self.turn_manager.set_dice_rolled()

        return (first_roll, second_roll)

    def _distribute_resources(self, roll: int) -> bool:
        """
        Distributes resources to all players based on the dice roll and current board state.
        Returns False on a roll of 7 (robber activation), True otherwise.
        Per Catan rules, if the bank cannot cover the total demand for a resource,
        NO player receives that resource for this roll.
        """
        if roll == 7:
            logging.info(GameMsg.info_rolled_seven(roll))
            return False

        hexes = [
            tile for tile in self.board.tiles.values()
            if tile.number == roll and tile.resource in self.board_context.RESOURCES
        ]

        # Tally what each player should collect, and the total per resource
        total: dict[str, int] = dict.fromkeys(self.board_context.RESOURCES, 0)
        player_collects: dict[str, dict[str, int]] = {}

        for tile in hexes:
            verts = self.board.tile_vertices[tile.tile_id]
            for vertex in verts:
                level, owner = self.board.get_structure(vertex)
                if level is not None and owner is not None:
                    player_collects.setdefault(owner, dict.fromkeys(self.board_context.RESOURCES, 0))
                    amount = self.board_context.STRUCTURE_RESOURCES.get(level, 0)
                    player_collects[owner][tile.resource] += amount
                    total[tile.resource] += amount

        # Distribute only if bank can cover the full demand for each resource
        for resource, demand in total.items():
            if demand == 0:
                continue

            if not self.board.bank_has_resource(resource, demand):
                logging.info(GameMsg.err_bank_not_enough(resource))
                # Per official rules: nobody gets this resource this round
                continue

            for player in self.players:
                if player.color in player_collects:
                    collect = player_collects[player.color][resource]
                    if collect > 0:
                        player.add_resource(resource, collect)
                        self.board.remove_bank_resource(resource, collect)

        return True

    # =========================================================================
    # --- ROBBER & STEALING ---
    # =========================================================================

    def move_robber(self, tile_id: int) -> bool:
        """
        Moves the robber to a new tile.
        Fails if the robber is already on the target tile.
        """
        if tile_id == self.board.robber_placement:
            logging.info(GameMsg.err_robber_same_tile())
            return False

        self.board.robber_placement = tile_id
        logging.info(GameMsg.info_robber_moved(tile_id))
        return True

    def steal(self, selection: int, robber: Player, victim: Player) -> bool:
        """
        Steals one resource card from the victim and gives it to the robber.
        The stolen card is chosen by index into a shuffled resource list,
        falling back to random.choice if selection is out of bounds.
        Returns False if the victim has no resources, or if robber == victim.
        """
        # FIX: Prevent stealing from yourself
        if robber == victim:
            logging.info(GameMsg.err_steal_self(robber.name))
            return False

        resource_list = [
            resource
            for resource, amount in victim.resources.items()
            for _ in range(amount)
        ]

        if not resource_list:
            logging.info(GameMsg.err_no_resources_to_steal(victim.name))
            return False

        random.shuffle(resource_list)

        stolen = (
            resource_list[selection]
            if selection <= len(resource_list) - 1
            else random.choice(resource_list)
        )

        logging.info(GameMsg.info_stole_resource_from(robber.name, stolen, victim.name))
        robber.add_resource(stolen, 1)
        victim.remove_resource(stolen, 1)
        return True

    # =========================================================================
    # --- TRADE PHASE ---
    # =========================================================================

    def trade_bank(self, player: Player, resource_in: str, resource_out: str) -> bool:
        """
        Executes a standard 4:1 trade with the bank.
        Validates turn, affordability, bank stock, and that the resources differ.
        """
        if not self._is_turn(player):
            return False

        # FIX: Prevent trading a resource for itself
        if resource_in == resource_out:
            logging.info(GameMsg.err_trade_same_resource(resource_in))
            return False

        bank_ratio = self.board_context.get_bank_ratio()
        if bank_ratio is None:
            logging.warning(GameMsg.err_not_in_board_context('bank ratio', 'BANK_RATIO'))
            return False

        ratio_in, ratio_out = bank_ratio
        cost = {resource_in: ratio_in}

        if not self.board_context.is_valid_resource_cost(cost):
            logging.warning(GameMsg.err_not_valid_cost(cost))
            return False

        if not player.can_afford(cost):
            logging.info(GameMsg.info_trade_cant_afford(player.name))
            return False

        if not self.board.bank_has_resource(resource_out, ratio_out):
            logging.info(GameMsg.err_bank_empty(resource_out))
            return False

        player.remove_resource(resource_in, ratio_in)
        player.add_resource(resource_out, ratio_out)
        self.board.remove_bank_resource(resource_out, ratio_out)
        self.board.add_bank_resource(resource_in, ratio_in)

        logging.info(GameMsg.info_trade_success(player.name, 'bank'))
        return True

    def trade_port(self, player: Player, vertices: tuple[int, int],
                   resource_in: str, resource_out: str) -> bool:
        """
        Executes a trade at a maritime port (3:1 generic or 2:1 specific).
        Player must own a settlement or city on one of the port's two vertices.
        """
        if not self._is_turn(player):
            return False

        port_resource = self.board.get_port(vertices)
        if port_resource is None:
            logging.warning(GameMsg.err_no_port(vertices))
            return False
        
        _, v1_owner = self.board.get_structure(vertices[0])
        _, v2_owner = self.board.get_structure(vertices[1])

        if v1_owner != player.color and v2_owner != player.color:
            logging.info(GameMsg.err_no_building_on_port(player.name))
            return False

        ratio = self.board_context.get_port_ratio(port_resource)
        if ratio == (0, 0):
            logging.warning(GameMsg.err_not_in_board_context(port_resource, 'PORT_RATIO'))
            return False

        ratio_in, ratio_out = ratio
        cost = {resource_in: ratio_in}

        if not player.can_afford(cost):
            logging.info(GameMsg.info_trade_cant_afford(player.name))
            return False

        if not self.board.bank_has_resource(resource_out, ratio_out):
            logging.info(GameMsg.err_bank_empty(resource_out))
            return False

        player.add_resource(resource_out, ratio_out)
        player.remove_resource(resource_in, ratio_in)
        self.board.remove_bank_resource(resource_out, ratio_out)
        self.board.add_bank_resource(resource_in, ratio_in)

        logging.info(GameMsg.info_trade_success(player.name, f'Port ({port_resource})'))
        return True

    def trade_player(self, player1: Player, player2: Player,
                     res_req1: dict, res_req2: dict) -> bool:
        """
        Executes a domestic trade between two players.
        Only player1 (the initiator) must be the active player.
        player1 offers res_req1 and receives res_req2 in return.
        """
        # FIX: Only the current player (initiator) needs to be active
        if not self._is_turn(player1):
            return False

        if not self.board_context.is_valid_resource_cost(res_req1):
            logging.error(GameMsg.err_not_valid_cost(res_req1))
            return False

        if not self.board_context.is_valid_resource_cost(res_req2):
            logging.error(GameMsg.err_not_valid_cost(res_req2))
            return False

        if not player1.can_afford(res_req1):
            logging.info(GameMsg.info_trade_cant_afford(player1.name))
            return False

        if not player2.can_afford(res_req2):
            logging.info(GameMsg.info_trade_cant_afford(player2.name))
            return False

        player1.add_resources(res_req2)
        player2.add_resources(res_req1)
        player1.remove_resources(res_req1)
        player2.remove_resources(res_req2)

        logging.info(GameMsg.info_trade_success(player1.name, player2.name))
        return True

    # =========================================================================
    # --- ACTION PHASE ---
    # =========================================================================

    def buy_dev_card(self, player: Player) -> bool:
        """
        Purchases the top development card from the deck.
        Validates turn, affordability, and deck availability before mutating state.
        """
        dev_card = 'dev_card'
        cost = self.board_context.get_cost(dev_card)

        if not self._is_turn(player):
            return False

        if not cost:
            logging.error(GameMsg.err_not_in_board_context(dev_card, 'BUILDING_COSTS'))
            return False

        if not player.can_afford(cost):
            logging.info(GameMsg.err_cant_afford(player.name, 'development card'))
            return False

        card = self.board.get_top_dev_card()
        if card is None:
            logging.info(GameMsg.err_dev_card_pile_empty())
            return False

        player.remove_resources(cost)
        player.add_dev_card(card)

        logging.info(GameMsg.success_buy_dev_card(player.name))
        return True

    def build_road(self, vertex1: int, vertex2: int, player: Player, free: bool = False) -> bool:
        """
        Builds a road on the edge between two vertices.
        Validates edge existence, occupancy, network connectivity, and piece count.
        Pass free=True to skip resource cost (e.g. Road Building card).
        """
        road = 'road'
        cost = self.board_context.get_cost(road)

        if not self._is_turn(player):
            return False

        if not self._has_rolled(player) and not free:
            return False
        
        if not cost:
            logging.error(GameMsg.err_not_in_board_context(road, 'BUILDING_COSTS'))
            return False

        if not free and not player.can_afford(cost):
            logging.info(GameMsg.err_cant_afford(player.name, road))
            return False

        if not self.board.has_edge(vertex1, vertex2):
            logging.warning(GameMsg.err_edge_not_exist(vertex1, vertex2))
            return False

        if self.board.get_road_color(vertex1, vertex2) is not None:
            logging.info(GameMsg.err_edge_occupied(vertex1, vertex2))
            return False

        if not self.board.has_connected_neighbor(player.color, vertex1, vertex2):
            logging.info(GameMsg.err_road_connection(player.name, vertex1, vertex2))
            return False

        if not player.has_available_pieces(road):
            logging.info(GameMsg.err_max_pieces(player.name, road))
            return False

        self.board.add_road(vertex1, vertex2, player.color)
        player.add_road(vertex1, vertex2)

        if not free:
            player.remove_resources(cost)

        logging.info(GameMsg.success_build_road(player.name, vertex1, vertex2))
        return True

    def upgrade_structure(self, vertex: int, player: Player) -> bool:
        """
        Upgrades the structure at a vertex to the next tier (e.g., settlement -> city).
        Validates ownership, upgrade availability, affordability, and piece count.
        Returns the old settlement piece to the player's available supply.
        """
        current_type, current_color = self.board.get_structure(vertex)

        if not self._is_turn(player):
            return False

        if current_type is None:
            logging.info(GameMsg.err_no_structure(vertex))
            return False

        if current_color != player.color:
            logging.info(GameMsg.err_vertex_occupied(player.name, current_type, vertex))
            return False

        next_type = self.board_context.get_next_upgrade(current_type)
        if next_type is None:
            logging.info(GameMsg.err_fully_upgraded(current_type, vertex))
            return False

        cost = self.board_context.get_cost(next_type)
        if not cost:
            logging.error(GameMsg.err_not_in_board_context(next_type, 'BUILDING_COSTS'))
            return False

        if not player.can_afford(cost):
            logging.info(GameMsg.err_cant_afford(player.name, next_type))
            return False

        if not player.has_available_pieces(next_type):
            logging.info(GameMsg.err_max_pieces(player.name, next_type))
            return False

        # FIX: Remove old structure from player list, add upgraded one
        # This also returns the settlement piece to the player's supply
        player.remove_structure(vertex)
        player.remove_resources(cost)
        self.board.add_structure(vertex, player.color, next_type)
        player.add_structure(vertex, next_type)

        logging.info(GameMsg.success_build_structure(player.name, next_type, vertex))
        return True

    def place_structure(self, vertex: int, player: Player, init_setup: bool = False) -> bool:
        """
        Places a new base-tier structure (settlement) on an empty vertex.
        During normal play, requires road connectivity and resource payment.
        During init_setup, skips both the road check and the resource cost.
        """
        current_type, _ = self.board.get_structure(vertex)
        starting_building = self.board_context.STRUCTURE_TYPES[0]
        cost = self.board_context.get_cost(starting_building)

        if not self._is_turn(player):
            return False

        if not starting_building:
            logging.error(GameMsg.err_not_in_board_context(starting_building, 'STRUCTURE_TYPES'))
            return False

        if not cost:
            logging.error(GameMsg.err_not_in_board_context(starting_building, 'BUILDING_COSTS'))
            return False

        if not init_setup and not player.can_afford(cost):
            logging.info(GameMsg.err_cant_afford(player.name, starting_building))
            return False

        if current_type is not None:
            logging.info(GameMsg.err_vertex_occupied(player.name, starting_building, vertex))
            return False

        if self.board.has_structure_neighbor(vertex):
            logging.info(GameMsg.err_distance_rule(vertex))
            return False

        if not init_setup and not self.board.has_road_neighbor(player.color, vertex):
            logging.info(GameMsg.err_structure_connection(player.name, vertex))
            return False

        if not player.has_available_pieces(starting_building):
            logging.info(GameMsg.err_max_pieces(player.name, starting_building))
            return False

        self.board.add_structure(vertex, player.color, starting_building)
        player.add_structure(vertex, starting_building)

        if not init_setup:
            player.remove_resources(cost)

        logging.info(GameMsg.success_build_structure(player.name, starting_building, vertex))
        return True

    # =========================================================================
    # --- ANY PHASE ---
    # =========================================================================

    def play_knight(self, player: Player, tile_id: int,
                    victim: Player, selection: int) -> bool:
        """
        Plays a Knight development card.
        Moves the robber to a new tile and steals one resource from the victim.
        Knight may be played before or after rolling — no dice_rolled check applied.
        All preconditions are validated before any state mutation occurs.
        """
        dev_card = 'knight'

        if not self._is_turn(player):
            return False

        if self.turn_manager.played_dev_card:
            logging.info(GameMsg.err_dev_card_already_played(player.name))
            return False

        if not player.has_dev_card(dev_card):
            logging.info(GameMsg.err_no_dev_card(player.name, dev_card))
            return False

        if tile_id == self.board.robber_placement:
            logging.info(GameMsg.err_robber_same_tile())
            return False

        if player == victim:
            logging.info(GameMsg.err_steal_self(player.name))
            return False

        victim_resources = [r for r, a in victim.resources.items() if a > 0]
        if not victim_resources:
            logging.info(GameMsg.err_no_resources_to_steal(victim.name))
            return False

        # All checks passed — safe to mutate
        self.move_robber(tile_id)
        self.steal(selection, player, victim)
        player.remove_dev_card(dev_card)
        self.turn_manager.set_played_dev_card()

        logging.info(GameMsg.success_dev_card(player.name, dev_card))
        return True

    def play_monopoly(self, player: Player, resource: str) -> bool:
        """
        Plays a Monopoly development card.
        Steals all cards of the chosen resource from every other player.
        Must be played after rolling the dice.
        """
        dev_card = 'monopoly'

        if not self._is_turn(player):
            return False

        if self.turn_manager.played_dev_card:
            logging.info(GameMsg.err_dev_card_already_played(player.name))
            return False

        # FIX: Enforce dice-first rule for non-knight dev cards
        if not self.turn_manager.dice_rolled:
            logging.info(GameMsg.err_dice_not_rolled(player.name))
            return False

        if not player.has_dev_card(dev_card):
            logging.info(GameMsg.err_no_dev_card(player.name, dev_card))
            return False

        if resource not in self.board_context.RESOURCES:
            logging.warning(GameMsg.err_not_in_board_context(resource, 'RESOURCES'))
            return False

        for victim in self.players:
            if victim == player:
                continue
            amount = victim.resources.get(resource, 0)
            if amount > 0:
                logging.info(GameMsg.info_stole_resource_from(player.name, resource, victim.name))
                player.add_resource(resource, amount)
                victim.remove_resource(resource, amount)

        player.remove_dev_card(dev_card)
        self.turn_manager.set_played_dev_card()
        logging.info(GameMsg.success_dev_card(player.name, dev_card))
        return True

    def play_year_of_plenty(self, player: Player, resource1: str, resource2: str) -> bool:
        """
        Plays a Year of Plenty development card.
        Grants the player any two resources directly from the bank.
        Must be played after rolling the dice.
        """
        dev_card = 'year_of_plenty'

        if not self._is_turn(player):
            return False

        if self.turn_manager.played_dev_card:
            logging.info(GameMsg.err_dev_card_already_played(player.name))
            return False

        # FIX: Enforce dice-first rule for non-knight dev cards
        if not self.turn_manager.dice_rolled:
            logging.info(GameMsg.err_dice_not_rolled(player.name))
            return False

        if not player.has_dev_card(dev_card):
            logging.info(GameMsg.err_no_dev_card(player.name, dev_card))
            return False

        if not self.board_context.is_valid_resource(resource1):
            logging.warning(GameMsg.err_not_in_board_context(resource1, 'RESOURCES'))
            return False

        if not self.board_context.is_valid_resource(resource2):
            logging.warning(GameMsg.err_not_in_board_context(resource2, 'RESOURCES'))
            return False

        # Check bank stock, handling the case where both resources are the same
        if resource1 == resource2:
            if not self.board.bank_has_resource(resource1, 2):
                logging.info(GameMsg.err_bank_empty(resource1))
                return False
        else:
            if not self.board.bank_has_resource(resource1, 1):
                logging.info(GameMsg.err_bank_empty(resource1))
                return False
            if not self.board.bank_has_resource(resource2, 1):
                logging.info(GameMsg.err_bank_empty(resource2))
                return False

        # FIX: Give to player first so bank debit is never orphaned
        player.add_resource(resource1, 1)
        player.add_resource(resource2, 1)
        self.board.remove_bank_resource(resource1, 1)
        self.board.remove_bank_resource(resource2, 1)

        player.remove_dev_card(dev_card)
        self.turn_manager.set_played_dev_card()
        logging.info(GameMsg.success_dev_card(player.name, dev_card))
        return True

    def play_road_building(self, player: Player,
                           v1: int, v2: int, v3: int, v4: int) -> bool:
        """
        Plays a Road Building development card, placing two free roads atomically.
        If the second road fails, the first is rolled back entirely.
        Must be played after rolling the dice.
        Requires room for at least 2 roads in the player's supply.
        """
        dev_card = 'road_building'

        if not self._is_turn(player):
            return False

        if self.turn_manager.played_dev_card:
            logging.info(GameMsg.err_dev_card_already_played(player.name))
            return False

        if not self.turn_manager.dice_rolled:
            logging.info(GameMsg.err_dice_not_rolled(player.name))
            return False

        if not player.has_dev_card(dev_card):
            logging.warning(GameMsg.err_no_dev_card(player.name, dev_card))
            return False

        roads_remaining = self.board_context.get_max_pieces('road') - player.count_roads()
        if roads_remaining < 2:
            logging.info(GameMsg.err_max_pieces(player.name, 'road'))
            return False

        if not self.build_road(v1, v2, player, free=True):
            logging.info(GameMsg.err_road_building_failed(v1, v2))
            return False

        if not self.build_road(v3, v4, player, free=True):
            logging.info(GameMsg.err_road_building_failed(v3, v4))
            # FIX: Rollback first road using the dedicated clear method
            self.board.graph.clear_edge_color(v1, v2)
            player.roads.remove((v1, v2))
            return False

        player.remove_dev_card(dev_card)
        self.turn_manager.set_played_dev_card()
        logging.info(GameMsg.success_dev_card(player.name, dev_card))
        return True

    # =========================================================================
    # --- VICTORY ---
    # =========================================================================

    def check_victory(self, player: Player) -> bool:
        """
        Calculates a player's total VP including board awards (Longest Road, Largest Army).
        Returns True if the player meets or exceeds the winning threshold.
        """
        total = player.local_vp()

        for award_name, point_value in self.board_context.AWARDS.items():
            award_owner = getattr(self.board, award_name, None)
            if award_owner == player.color:
                total += point_value
                logging.info(GameMsg.info_award_vp(player.name, award_name, point_value))

        logging.info(GameMsg.info_total_vp(player.name, total))
        return total >= self.board_context.WINNING_VP_THRESHOLD

    # =========================================================================
    # --- TURN MANAGEMENT ---
    # =========================================================================

    def end_turn(self) -> None:
        """
        Ends the current player's turn.
        Triggers dev card cooldown processing before advancing to the next player.
        """
        # FIX: Trigger cooldown processing so newly bought cards become active next turn
        current_player = self.turn_manager.get_current_player()
        current_player.update_dev_cards()
        self.turn_manager.next_turn()