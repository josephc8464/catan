class GameMsg:
    """
    Centralized catalog for all game-facing log messages.
    Provides consistently formatted strings for events, placement validation,
    trade outcomes, and error conditions across the entire engine.
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
        return f"{player_name} has placed the maximum allowed '{item}' pieces."

    @staticmethod
    def err_no_dev_card(player_name: str, card: str) -> str:
        return f"{player_name} does not have a '{card}' card in their active hand."

    @staticmethod
    def err_bank_empty(resource: str) -> str:
        return f"The bank has no remaining '{resource}'."

    @staticmethod
    def err_bank_not_enough(resource: str) -> str:
        return f"Bank cannot cover all '{resource}' demand — no one receives it this round."

    @staticmethod
    def err_dev_card_pile_empty() -> str:
        return "There are no more development cards in the deck."

    @staticmethod
    def err_dev_card_already_played(player_name: str) -> str:
        return f"{player_name} has already played a development card this turn."

    @staticmethod
    def err_dice_not_rolled(player_name: str) -> str:
        return f"{player_name} must roll the dice before performing the attempted action."

    @staticmethod
    def err_not_in_board_context(item: str, attribute: str) -> str:
        return f"'{item}' is not defined in board context ({attribute})."

    @staticmethod
    def err_not_valid_cost(cost) -> str:
        return f"Invalid or unknown cost: '{cost}'."

    @staticmethod
    def err_trade_same_resource(resource: str) -> str:
        return f"Cannot trade '{resource}' for itself."

    # =========================================================================
    # --- PLACEMENT & MAP GEOMETRY ERRORS ---
    # =========================================================================

    @staticmethod
    def err_vertex_occupied(player_name: str, buildable: str, vertex: int) -> str:
        return f"{player_name} cannot place '{buildable}': vertex {vertex} is already occupied."

    @staticmethod
    def err_edge_occupied(v1: int, v2: int) -> str:
        return f"Edge ({v1}, {v2}) is already occupied."

    @staticmethod
    def err_edge_not_exist(v1: int, v2: int) -> str:
        return f"No valid edge exists between vertex {v1} and vertex {v2}."

    @staticmethod
    def err_no_structure(vertex: int) -> str:
        return f"No structure exists at vertex {vertex}."

    @staticmethod
    def err_fully_upgraded(building_type: str, vertex: int) -> str:
        return f"Vertex {vertex} already holds a fully upgraded '{building_type}'."

    @staticmethod
    def err_distance_rule(vertex: int) -> str:
        return f"Placement at vertex {vertex} violates the distance rule."

    @staticmethod
    def err_road_connection(player_name: str, v1: int, v2: int) -> str:
        return f"{player_name} must connect their road to an owned structure or road near ({v1}, {v2})."

    @staticmethod
    def err_structure_connection(player_name: str, vertex: int) -> str:
        return f"{player_name} must connect their settlement to an owned road at vertex {vertex}."

    @staticmethod
    def err_initial_road_no_settlement(player_name: str) -> str:
        return f"{player_name} has no settlement to connect a setup road to."

    @staticmethod
    def err_road_building_failed(v1: int, v2: int) -> str:
        return f"Road Building failed: invalid placement at edge ({v1}, {v2})."

    # =========================================================================
    # --- ROBBER & STEALING ---
    # =========================================================================

    @staticmethod
    def err_robber_same_tile() -> str:
        return "The robber must be moved to a different tile."

    @staticmethod
    def err_no_resources_to_steal(victim_name: str) -> str:
        return f"{victim_name} has no resources to steal."

    @staticmethod
    def err_steal_self(player_name: str) -> str:
        return f"{player_name} cannot steal from themselves."

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
        return f"No port exists at vertices {vertices}."

    @staticmethod
    def err_no_building_on_port(player_name: str) -> str:
        return f"{player_name} does not own a building at this port."

    @staticmethod
    def info_trade_cant_afford(player_name: str) -> str:
        return f"Trade failed: {player_name} cannot afford their offer."

    @staticmethod
    def info_trade_success(p1_name: str, p2_name: str) -> str:
        return f"Trade between {p1_name} and {p2_name} completed."

    # =========================================================================
    # --- SUCCESS & GAMEPLAY INFO ---
    # =========================================================================

    @staticmethod
    def info_rolled_seven(roll: int) -> str:
        return f"Rolled {roll} — robber activates. Players over 7 cards must discard."

    @staticmethod
    def info_award_vp(player_name: str, award_name: str, point_value: int) -> str:
        pts = f"+{point_value} VP"
        return f"{player_name} holds {award_name} ({pts})."

    @staticmethod
    def info_total_vp(player_name: str, total: int) -> str:
        suffix = 'Victory Point' if total == 1 else 'Victory Points'
        return f"{player_name} has {total} {suffix}."

    @staticmethod
    def info_setup_resource_grant(player_name: str, resource: str, tile_id: int) -> str:
        return f"{player_name} received 1 '{resource}' from tile {tile_id} (setup round 2)."

    @staticmethod
    def success_build_structure(player_name: str, building: str, vertex: int) -> str:
        return f"{player_name} built a {building} at vertex {vertex}."

    @staticmethod
    def success_build_road(player_name: str, v1: int, v2: int) -> str:
        return f"{player_name} built a road on edge ({v1}, {v2})."

    @staticmethod
    def success_buy_dev_card(player_name: str) -> str:
        return f"{player_name} purchased a development card."

    @staticmethod
    def success_dev_card(player_name: str, dev_card: str) -> str:
        return f"{player_name} played '{dev_card}'."