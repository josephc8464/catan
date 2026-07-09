from .board_presets.default.board_context import BoardContext

class Player():
    def __init__(self, name, color, resources) -> None:
        self.name = name
        self.color = color
        self.resources = resources
        self.buildings = []             #(vertex_id, building_type)
        self.roads = []                 #(u, v) Edge
        self.development_cards = []     #String

        self.board_context = BoardContext()

    def return_total_vp(self) -> int:
        total_vp = 0
        
        for building in self.buildings:
            total_vp += self.board_context.BUILDING_VP[building[1]]
        
        for card in self.development_cards:
            total_vp += self.board_context.DEVELOPMENT_CARDS[card]
        
        return total_vp
    
    def can_afford(self, cost) -> bool:
        for resource, amount in cost.items():
            if self.resources.get(resource, 0) < amount:
                return False
        return True
    
    def add_resource(self, resource, amount) -> bool:
        if resource in self.resources:
            self.resources[resource] += amount
            return True
        else:
            print(f"Resource {resource} does not exist.")
        return False
    
    def remove_resource(self, resource, amount) -> bool:
        if resource in self.resources:
            if self.resources[resource] >= amount:
                self.resources[resource] -= amount
                return True
            else:
                print(f"Not enough {resource} to remove.")
        else:
            print(f"Resource {resource} does not exist.")
        return False
    