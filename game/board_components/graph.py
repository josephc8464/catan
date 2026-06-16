class Graph():

    def __init__(self, size):
        self.adj_list = {i: [] for i in range(size)}
        self.edge_color = {} #blue, red, orange, white

    def add_edge(self, u, v):
        if v not in self.adj_list[u] and u not in self.adj_list[v]:
            self.adj_list[u].append(v)
            self.adj_list[v].append(u)
            self.edge_color[(u, v)] = None
            self.edge_color[(v, u)] = None
    
    def remove_edge(self, u, v):
        if v in self.adj_list[u] and u in self.adj_list[v]:
            self.adj_list[u].remove(v)
            self.adj_list[v].remove(u)
            del self.edge_color[(u, v)]
            del self.edge_color[(v, u)]
    
    def get_neighbors(self, node):
        return self.adj_list[node]
    
    def set_edge_color(self, u, v, color):
        if (u, v) in self.edge_color and self.edge_color[(u, v)] is None:
            self.edge_color[(u, v)] = color
            self.edge_color[(v, u)] = color

    def get_edge_color(self, u, v):
        return self.edge_color.get((u, v))

