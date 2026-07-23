class GameMsg:
    """Centralized catalog for all UI-facing player messages.
    
    Provides formatted strings for game events, placement checks, 
    and validation errors to ensure consistent logging and rendering across the UI.
    """

    # =========================================================================
    # --- VALIDATION & ECONOMY ERRORS ---
    # =========================================================================

    @staticmethod
    def err_not_turn(player_name: str) -> str:
        return f"It is not {player_name}'s turn."

    @staticmethod
    def err_cant_afford(player_name: str, item: str) -> str:
        return f"{player_name} cannot afford {item}."

    @staticmethod
    def err_max_pieces(player_name: str, item: str) -> str:
        return f"{player_name} has already placed the maximum allowed number of '{item}'."

    @staticmethod
    def err_no_dev_card(player_name: str, card: str) -> str:
        return f"{player_name} does not have a '{card}' development card in hand."

    @staticmethod
    def err_bank_empty(resource: str) -> str:
        return f"The bank has no remaining '{resource}'."

    @staticmethod
    def err_bank_not_enough(resource: str) -> str:
        return f"The bank does not have enough '{resource}' to fulfill this request."

    @staticmethod
    def err_dev_card_pile_empty() -> str:
        return f"There are no more development cards available in the deck."

    @staticmethod
    def err_not_in_board_context(item: str, attribute: str) -> str:
        return f"'{item}' is not defined in the board context ({attribute})."

    @staticmethod
    def err_not_valid_cost(cost) -> str:
        return f"Unknown or invalid cost identifier: '{cost}'."

    # =========================================================================
    # --- PLACEMENT & MAP GEOMETRY ERRORS ---
    # =========================================================================

    @staticmethod
    def err_vertex_occupied(player_name: str, buildable: str, vertex: int) -> str:
        return f"{player_name} cannot place '{buildable}': Vertex {vertex} is already occupied."

    @staticmethod
    def err_edge_occupied(v1: int, v2: int) -> str:
        return f"Edge ({v1}, {v2}) is already occupied by a road."

    @staticmethod
    def err_edge_not_exist(v1: int, v2: int) -> str:
        return f"No valid edge exists between vertex {v1} and vertex {v2}."

    @staticmethod
    def err_no_structure(vertex: int) -> str:
        return f"There is no structure present at vertex {vertex}."

    @staticmethod
    def err_fully_upgraded(building_type: str, vertex: int) -> str:
        return f"Cannot upgrade: Structure at vertex {vertex} is already a fully upgraded '{building_type}'."

    @staticmethod
    def err_distance_rule(vertex: int) -> str:
        return f"Building at vertex {vertex} violates the distance rule."

    @staticmethod
    def err_road_connection(player_name: str, v1: int, v2: int) -> str:
        return f"{player_name} must connect their road to an owned settlement, city, or road near edge ({v1}, {v2})."

    @staticmethod
    def err_structure_connection(player_name: str, vertex: int) -> str:
        return f"{player_name} must connect their structure to an owned road touching vertex {vertex}."

    @staticmethod
    def err_initial_road_no_settlement(player_name: str) -> str:
        return f"{player_name} must build a road touching their newly placed setup settlement."

    @staticmethod
    def err_road_building_failed(v1: int, v2: int) -> str:
        return f"Road Building card action failed: Invalid placement between vertex {v1} and vertex {v2}."

    # =========================================================================
    # --- ROBBER & STEALING ---
    # =========================================================================

    @staticmethod
    def err_robber_same_tile() -> str:
        return f"The robber must be moved to a different tile."

    @staticmethod
    def err_no_resources_to_steal(victim_name: str) -> str:
        return f"{victim_name} has no resources to steal."

    @staticmethod
    def info_robber_moved(tile_id: int) -> str:
        return f"The robber was moved to tile {tile_id}."

    @staticmethod
    def info_stole_resource_from(robber_name: str, resource: str, victim_name: str) -> str:
        return f"{robber_name} stole 1 '{resource}' from {victim_name}."

    # =========================================================================
    # --- PORTS & TRADES ---
    # =========================================================================

    @staticmethod
    def err_no_port(vertices: tuple[int, int]) -> str:
        return f"No port exists across vertices {vertices}."

    @staticmethod
    def err_no_building_on_port(player_name: str) -> str:
        return f"{player_name} does not own a settlement or city at this port."

    @staticmethod
    def info_trade_cant_afford(player_name: str) -> str:
        return f"Trade failed: {player_name} cannot afford the requested offer."

    @staticmethod
    def info_trade_success(p1_name: str, p2_name: str) -> str:
        return f"Trade between {p1_name} and {p2_name} completed successfully."

    # =========================================================================
    # --- SUCCESS & GAMEPLAY INFO ---
    # =========================================================================

    @staticmethod
    def info_rolled_seven(roll: int) -> str:
        return f"A {roll} was rolled! The robber is activated and players with over 7 cards must discard."

    @staticmethod
    def info_award_vp(player_name: str, award_name: str, point_value: int) -> str:
        return f"{player_name} was awarded {award_name} (+{point_value} Victory Point{'s' if point_value > 1 else ''})."

    @staticmethod
    def info_total_vp(player_name: str, total: int) -> str:
        return f"{player_name} now has a total of {total} Victory Point{'s' if total != 1 else ''}."

    @staticmethod
    def success_build_structure(player_name: str, building: str, vertex: int) -> str:
        return f"{player_name} built a {building} at vertex {vertex}."

    @staticmethod
    def success_build_road(player_name: str, v1: int, v2: int) -> str:
        return f"{player_name} built a road between vertex {v1} and vertex {v2}."

    @staticmethod
    def success_buy_dev_card(player_name: str) -> str:
        return f"{player_name} bought a development card."

    @staticmethod
    def success_dev_card(player_name: str, dev_card: str) -> str:
        return f"{player_name} played a '{dev_card}' development card."