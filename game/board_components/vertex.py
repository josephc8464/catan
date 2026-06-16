class Vertex():
    def __init__(self, id):
        self.node_id = id
        self.tilesAdj = []
        self.owner = None
        self.structure = "None" #can be "None", "Road", "Settlement", "City", leaves room for expansions