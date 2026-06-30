class ColorUtility:    
    def get_color(self, color):
        match color:
            case "red":
                return (255, 0, 0)
            case "blue":
                return (0, 0, 255)
            case "green":
                return (0, 165, 0)
            case "purple":
                return (255, 0, 255)