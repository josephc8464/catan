from game.player import Player
from game.board_presets.default.default_board import DefaultBoard
from game.turn_manager import TurnManager
from game.board_presets.default.board_context import BoardContext
from game.messages import GameMsg
import random
import logging

class GameController:
    def __init__(self, board: DefaultBoard, players: list[Player], turn_manager: TurnManager):
        self.board = board
        self.players = players
        self.turn_manager = turn_manager
        self.current_player_index = 0
        self.board_context = BoardContext()

    # --- HELPERS ---        
    def _is_turn(self, player) -> bool:
        """Helper to verify if it is the specified player's turn."""
        if not self.turn_manager.is_current_player(player):
            logging.info(GameMsg.err_not_turn(player.name))
            return False
        
        return True

    # --- SETUP PHASE ---
    def place_initial_settlement(self, player: Player, vertex: int) -> bool:
        """
        Places a free settlement during the setup phase.
        Obeys the distance rule but ignores resource costs.
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

    def place_initial_road(self, player: Player, vertex1: int, vertex2: int) -> bool:
        """
        Places a free road during the setup phase.
        Must connect directly to the player's most recently placed settlement.
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

    # --- ANY PHASE ---
    def play_knight(self, player: Player, tile_id: int, victim: Player, selection: int) -> bool:
        """Plays a Knight development card, moving the robber and stealing a resource."""
        dev_card = 'knight'

        if not self._is_turn(player):
            return False
        
        if not player.has_dev_card(dev_card):
            logging.info(GameMsg.err_no_dev_card(player.name, dev_card))
            return False

        if not self.move_robber(tile_id):
            return False
        
        if not self.steal(selection, player, victim):
            return False

        player.remove_dev_card(dev_card)
        logging.info(GameMsg.success_dev_card(player.name, dev_card))
        return True

        
    def play_monopoly(self, player: Player, resource: str) -> bool:
        """Plays a Monopoly card, stealing all of a specified resource from all other players."""
        dev_card = 'monopoly'

        if not self._is_turn(player):
            return False

        if not player.has_dev_card(dev_card):
            logging.info(GameMsg.err_no_dev_card(player.name, dev_card))
            return False
        
        if resource not in self.board_context.RESOURCES:
            logging.warning(GameMsg.err_not_in_board_context(resource, 'RESOURCES'))
            return False
        
        for victim in self.players:
            if victim != player:
                amount = victim.resources.get(resource, 0)
                if amount > 0:
                    logging.info(GameMsg.info_stole_resource_from(player.name, victim.name, resource))
                    player.add_resource(resource, amount)
                    victim.remove_resource(resource, amount)
            
        player.remove_dev_card(dev_card)
        logging.info(GameMsg.success_dev_card(player.name, dev_card))

        return True
    
    def play_year_of_plenty(self, player: Player, resource1: str, resource2: str) -> bool:
        """Plays a Year of Plenty card, granting the player any two resources from the bank."""
        dev_card = 'year_of_plenty'

        if not self._is_turn(player):
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
        
        # Verify the bank has enough, accounting for duplicates
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

        self.board.remove_bank_resource(resource1, 1)
        self.board.remove_bank_resource(resource2, 1)

        player.add_resource(resource1, 1)
        player.add_resource(resource2, 1)

        player.remove_dev_card(dev_card)

        logging.info(GameMsg.success_dev_card(player.name, dev_card))
        return True

    def play_road_building(self, player: Player, v1: int, v2: int, v3: int, v4: int) -> bool:
        """Plays a Road Building card, placing two free roads as an atomic transaction."""
        dev_card = 'road_building'

        if not self._is_turn(player):
            return False
        
        if not player.has_dev_card('road_building'):
            logging.warning(GameMsg.err_no_dev_card(player.name, dev_card))
            return False
            
        if player.count_roads() >= self.board_context.get_max_pieces('road') - 1:
            logging.info(GameMsg.err_max_pieces(player.name, 'road'))
            return False

        if not self.build_road(v1, v2, player, free=True):
            logging.info(GameMsg.err_road_building_failed(v1, v2))
            return False

        if not self.build_road(v3, v4, player, free=True):
            logging.info(GameMsg.err_road_building_failed(v3, v4))
            
            # Rollback first road
            self.board.graph.set_edge_color(v1, v2, None)
            player.roads.remove((v1, v2)) 
            return False

        player.remove_dev_card(dev_card)
        logging.info(GameMsg.success_dev_card(player.name, dev_card))

        return True

    def check_victory(self, player: Player) -> bool:
        """Calculates a player's total VP (including board awards) to check for a win condition."""
        total = player.local_vp()

        for award_name, point_value in self.board_context.AWARDS.items():
            award_owner = getattr(self.board, award_name)

            if award_owner == player.color:
                total += point_value
                logging.info(GameMsg.info_award_vp(player.name, award_name, point_value))
        
        logging.info(GameMsg.info_total_vp(player.name, total))

        return total >= self.board_context.WINNING_VP_THRESHOLD

    # --- DICE PHASE ---
    def _distribute_resources(self, roll: int) -> bool:
        """Distributes resources to players based on the dice roll and board state."""
        if roll == 7:
            logging.info(GameMsg.info_rolled_seven(roll))
            return False

        hexes = [tile for tile in self.board.tiles.values() if tile.number == roll]
        total = dict.fromkeys(self.board_context.RESOURCES, 0)
        player_collects: dict[str, dict[str, int]] = {}

        for tile in hexes:
            verts = self.board.tile_vertices[tile.tile_id]

            for vertex in verts:
                level, owner = self.board.get_structure(vertex)

                if level is not None and owner is not None:
                    player_collects.setdefault(owner, dict.fromkeys(self.board_context.RESOURCES, 0))
                    
                    amount_produced = self.board_context.STRUCTURE_RESOURCES[level]
                    player_collects[owner][tile.resource] += amount_produced
                    total[tile.resource] += amount_produced
        
        for resource, amount in total.items():
            if amount == 0:
                continue

            if not self.board.bank_has_resource(resource, amount):
                logging.info(GameMsg.err_bank_not_enough(resource))
            else:
                for player in self.players:
                    if player.color in player_collects:
                        collect = player_collects[player.color][resource]
                        if collect > 0:
                            player.add_resource(resource, collect)
                            self.board.remove_bank_resource(resource, collect)

        return True
    
    def roll_dice(self, player: Player) -> tuple[int, int]:
        """Rolls two dice and triggers resource distribution."""
        if not self._is_turn(player):
            return (0,0)
        if self.turn_manager.dice_rolled:
            return (0,0)
        
        first_roll = random.randint(1,6)
        second_roll = random.randint(1,6)

        result = first_roll + second_roll

        self._distribute_resources(result)

        return (first_roll, second_roll)
    
    def steal(self, selection: int, robber: Player, victim: Player) -> bool:
        """Steals a random resource card from the victim and gives it to the robber."""
        has_resources = False
        resource_list = []

        for resource, amount in victim.resources.items():
            if amount > 0:
                has_resources = True
                resource_list += [resource] * amount
        
        if not has_resources:
            logging.info(GameMsg.err_no_resources_to_steal(victim.name))
            return False
        
        random.shuffle(resource_list)

        if selection > len(resource_list) - 1:
            resource = random.choice(resource_list)
        else:
            resource = resource_list[selection]
        
        logging.info(GameMsg.info_stole_resource_from(robber.name, resource, victim.name))

        robber.add_resource(resource, 1)
        victim.remove_resource(resource, 1)

        return True
        
    def move_robber(self, tile_id: int) -> bool:
        """Moves the robber to a new tile on the board."""
        if tile_id == self.board.robber_placement:
            logging.info(GameMsg.err_robber_same_tile())
            return False
        
        self.board.robber_placement = tile_id

        logging.info(GameMsg.info_robber_moved(tile_id))
        
        return True

    # --- TRADE PHASE ---
    def trade_bank(self, player: Player, resource_in: str, resource_out: str) -> bool:
        """Executes a standard 4:1 trade with the bank."""
        if not self._is_turn(player):
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

    def trade_port(self, player: Player, vertices: tuple[int, int], resource_in: str, resource_out: str) -> bool:
        """Executes a trade using a maritime port (3:1 generic or 2:1 specific)."""
        port_resource = self.board.get_port(vertices)

        if not self._is_turn(player):
            return False
        
        if port_resource is None:
            logging.warning(GameMsg.err_no_port(vertices))
            return False
        
        _, vertex1_owner = self.board.get_structure(vertices[0])
        _, vertex2_owner = self.board.get_structure(vertices[1])

        if vertex1_owner != player.color and vertex2_owner != player.color:
            logging.info(GameMsg.err_no_building_on_port(player.name))
            return False
        
        ratio = self.board_context.get_port_ratio(port_resource)
        ratio_in, ratio_out = ratio

        if ratio == (0,0):
            logging.warning(GameMsg.err_not_in_board_context(port_resource, 'PORT_RATIO'))
            return False
        
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
        
        logging.info(GameMsg.info_trade_success(player.name, f'Port {port_resource}'))
        return True
    
    def trade_player(self, player1: Player, player2: Player, res_req1: dict, res_req2: dict) -> bool: 
        """Executes a domestic trade between two players."""
        if not self._is_turn(player1) and not self._is_turn(player2):
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
    
    # --- BUILD PHASE ---
        
    def buy_dev_card(self, player: Player) -> bool:
        """Purchases a development card for the player."""
        dev_card = 'dev_card'
        cost = self.board_context.get_cost(dev_card)
        
        if not self._is_turn(player):
            return False
                        
        if cost is None:
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
        """Builds a road on an edge between two vertices."""
        road = 'road'
        current_road_color = self.board.get_road_color(vertex1, vertex2)
        cost = self.board_context.get_cost(road)

        if not self._is_turn(player): 
            return False

        if cost is None:
            logging.error(GameMsg.err_not_in_board_context(road, 'BUILDING_COSTS'))
            return False
        
        if not free and not player.can_afford(cost):
            logging.info(GameMsg.err_cant_afford(player.name, road))
            return False
        
        if not self.board.has_edge(vertex1, vertex2):
            logging.warning(GameMsg.err_edge_not_exist(vertex1, vertex2))
            return False

        if current_road_color is not None:
            logging.info(GameMsg.err_edge_occupied(vertex1, vertex2))
            return False

        if not self.board.has_connected_neighbor(player.color, vertex1, vertex2):
            logging.info(GameMsg.err_road_connection(player.name, vertex1, vertex2))
            return False
        
        if not player.has_available_pieces(road):
            logging.info(GameMsg.err_max_pieces(player.name, road))
            return False
        
        self.board.add_road(vertex1, vertex2, player.color)

        if not free:
            player.remove_resources(cost)
        
        logging.info(GameMsg.success_build_road(player.name, vertex1, vertex2))
        return True

    def upgrade_structure(self, vertex: int, player: Player) -> bool:
        """Upgrades an existing structure on a vertex to the next tier (e.g., settlement to city)."""
        building_at_vertex, building_color = self.board.get_structure(vertex)

        if not self._is_turn(player):
            return False
        
        if building_at_vertex is None:
            logging.info(GameMsg.err_no_structure(vertex))
            return False
        
        next_building_type = self.board_context.get_next_upgrade(building_at_vertex)
        
        if next_building_type is None:
            logging.info(GameMsg.err_fully_upgraded(building_at_vertex, vertex))
            return False
        
        cost = self.board_context.get_cost(next_building_type)

        if cost is None:
            logging.error(GameMsg.err_not_in_board_context(next_building_type, 'BUILDING_COSTS'))
            return False

        if not player.can_afford(cost):
            logging.info(GameMsg.err_cant_afford(player.name, next_building_type))
            return False
        
        if building_color != player.color:
            logging.info(GameMsg.err_vertex_occupied(player.name, next_building_type, vertex))
            return False

        if not player.has_available_pieces(next_building_type):
            logging.info(GameMsg.err_max_pieces(player.name, next_building_type))
            return False
        
        player.remove_resources(cost)
        self.board.add_structure(vertex, player.color, next_building_type)
        logging.info(GameMsg.success_build_structure(player.name, next_building_type, vertex))

        return True

    def place_structure(self, vertex: int, player: Player, init_setup: bool = False) -> bool:
        """Builds a starting tier structure (e.g., settlement) on an empty vertex."""
        building_at_vertex, building_color = self.board.get_structure(vertex)
        starting_building = self.board_context.STRUCTURE_TYPES[0]
        
        cost = self.board_context.get_cost(starting_building)
        
        if not self._is_turn(player):
            return False
        
        if starting_building is None:
            logging.error(GameMsg.err_not_in_board_context(starting_building, 'STRUCTURE_TYPES'))
            return False
        
        if cost is None:
            logging.error(GameMsg.err_not_in_board_context(cost, 'BUILDING_COSTS'))
            return False
        
        if not init_setup and not player.can_afford(cost):
            logging.info(GameMsg.err_cant_afford(player.name, starting_building))
            return False

        if building_at_vertex is not None:
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