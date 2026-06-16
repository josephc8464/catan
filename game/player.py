class player():
    def __init__(self, name) -> None:
        self.name = name
        self.vp = 0
        self.resources = {
            'wood': 0,
            'brick': 0,
            'sheep': 0,
            'wheat': 0,
            'ore': 0
        }
        self.settlements = []
        self.cities = []
        self.roads = []
        self.development_cards = []
    
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
    