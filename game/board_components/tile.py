class Tile():
    def __init__(self, resource, number, id):
        self.resource = resource
        self.number = number

        #identifier for the tile, used for graph construction
        self.tile_id = id           
    
