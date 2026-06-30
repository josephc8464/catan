class PositionUtility:
   
    def __init__(self):
            
        self._PORT_OFFSETS = {
            "topLeft":      [-1.0, -0.5],
            "topRight":     [ 1.0, -0.5],
            "topCenter":    [ 0.0, -1.0],
            "bottomLeft":   [-1.0,  0.5],
            "bottomRight":  [ 1.0,  0.5],
            "bottomCenter": [ 0.0,  1.0],
        }

        self._ROAD_OFFSETS = {
            "topLeft":      [0.0,   0.125, 60],
            "topRight":     [1.0,   0.125, -60],
            "topCenter":    [0.425, 0.05,  0],
            "bottomLeft":   [0.0,   0.625, -60],
            "bottomRight":  [1.0,   0.625, 60],
            "bottomCenter": [0.425, 1.05,  0],
        }

        self._BUILDING_OFFSETS = {
            0: [0.1,  -0.05],  # TopLeft
            1: [0.9,  -0.05],  # TopRight
            2: [-0.1,  0.45],  # Left
            3: [1.1,   0.45],  # Right
            4: [0.1,   0.95],  # BottomLeft
            5: [0.9,   0.95],  # BottomRight
        }

    def _determine_vertex_index(self, tile_vertices, target_vertex) -> int:
        try:
            return tile_vertices.index(target_vertex)
        except ValueError:
            return -1
    
    def determine_orientation(self, tile_vertices, vertex1, vertex2) -> str:
        index1 = self._determine_vertex_index(tile_vertices, vertex1)
        index2 = self._determine_vertex_index(tile_vertices, vertex2)

        if index1 < 2:
            if index2 - index1 == 1: return "topCenter"
            if index2 == 2:          return "topLeft"
            return "topRight"
        if index1 < 4:
            return "bottomLeft" if index1 == 2 else "bottomRight"
        return "bottomCenter"
        
    def get_port_offset(self, orientation) -> list[float]:
        return self._PORT_OFFSETS.get(orientation, [0.0, 0.0])
    
    def get_road_offset(self, orientation) -> list[float]:
        return self._ROAD_OFFSETS.get(orientation, [0.0, 0.0, 0.0])
    
    def get_building_offset(self, tile_vertices, vertex) -> list[float]:
        index = self._determine_vertex_index(tile_vertices, vertex)
        return self._BUILDING_OFFSETS.get(index, [0.0, 0.0])