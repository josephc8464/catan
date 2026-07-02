import pygame 

class ColorUtility:    
    def get_color(self, color) -> pygame.Color:
        match color:
            case "red":
                return pygame.Color(255, 0, 0)
            case "blue":
                return pygame.Color(0, 0, 255)
            case "green":
                return pygame.Color(0, 165, 0)
            case "purple":
                return pygame.Color(255, 0, 255)
        
        return pygame.Color(255, 255, 255)  # Default to white if color not recognized