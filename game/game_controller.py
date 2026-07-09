from game import player
from board_presets import board
from game.turn_manager import TurnManager
from game.board_presets.default.board_context import BoardContext

class GameController:
    def __init__(self, board, players, turn_manager: TurnManager):
        self.board = board
        self.players = players
        self.turn_manager = turn_manager
        self.current_player_index = 0
        self.board_context = BoardContext()

    def _deduct_cost(self, player, cost):
        for resource, amount in cost.items():
            player.remove_resource(resource, amount)
        
    def _is_player_turn(self, player) -> bool:
        if self.turn_manager.is_current_player(player) == False:
            print(f"It's not {player.name}'s turn.")
            return False
        
        return True
    
    def _player_can_afford(self, player, cost) -> bool:
        if player.can_afford(cost):
            return True
        
        return False
    
    def build_road(self, vertex1, vertex2, player) -> bool:
        player_color = player.color
        current_road_color = self.board.get_road_color(vertex1, vertex2)
        cost = self.board_context.BUILDING_COSTS['road']

        if not self.board.graph.has_edge(vertex1, vertex2):
            print(f"Edge between {vertex1} and {vertex2} does not exist")
            return False
        
        if not self._is_player_turn(player):
            return False
        
        if not self._player_can_afford(player, cost):
            print(f"{player.name} cannot afford to build a road")
            return False

        if current_road_color is not None:
            print(f"Road already exists at edge ({vertex1}, {vertex2})")
            return False

        if not self.board.has_color_neighbor(self, player_color, vertex1, vertex2):
            print(f"Road does not have existing connection at either {vertex1} or {vertex2}, for {player.color}")

        self.board.graph.add_edge(vertex1, vertex2, player_color)
        self._deduct_cost(player, cost)
        print(f"{player_color} built a road between {vertex1} and {vertex2}.")
        return True
        
    def build_building(self, vertex_id, player, building_type) -> bool:
        building_at_vertex, building_color = self.board.buildings[vertex_id]
        player_color = player.color
        cost = self.board_context.BUILDING_COSTS[building_type]

        if not self._is_player_turn(player):
            return False
        
        if not self._player_can_afford(player, cost):
            print(f"{player.name} cannot afford to build a {building_type}")
            return False

        #Check if building already constructed at vertex
        if building_at_vertex != None and building_color != player_color:
            print(f"Building already at {vertex_id}, {building_color} does not match {player_color}")
            return False
        elif building_at_vertex != None:
            for i, building in enumerate(self.board_context.BUILDING_TYPES):

                #Building level exists at vertex (and player owns it)
                if building == building_at_vertex:

                    #Progression in building upgrade incorrect
                    if self.board_context.BUILDING_TYPES[i-1] != building_type:
                        print(f"Incorrect progression, cannot build {building_type} on top of {building_at_vertex}.")
                        return False
                    
                    #Progression satisfied
                    else:
                        player.buildings.remove((vertex_id, building_at_vertex))
                        self.board.add_building(vertex_id, player_color, building_type)
                        player.buildings.append((vertex_id, building_type))
                        return True
        
        #Check if there are buildings directly next to wanted placement
        for vertex in self.board.graph.adj_list[vertex_id]:
            if self.board.buildings[vertex] != (None, None):
                print(f"Building cannot be built directly next to building at {vertex}")
                return False
        
        #Build the settlement
        self.board.add_building(vertex_id, player_color, building_type)
        player.buildings.append((vertex_id, building_type))
        
        self._deduct_cost(player, cost)
        
        print(f"{player_color} built a {building_type} at vertex {vertex_id}.")
        return True
    
    
    