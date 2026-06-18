class player():
    def __init__(self, name, color) -> None:
        self.name = name
        self.color = None
        self.vp = 0
        self.resources = {
            'wood': 0,
            'brick': 0,
            'sheep': 0,
            'wheat': 0,
            'ore': 0
        }
        self.settlements = []           #Vertex Ids
        self.cities = []                #Vertex Ids
        self.roads = []                 #(u, v) Edge
        self.development_cards = []     #String
    
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
    