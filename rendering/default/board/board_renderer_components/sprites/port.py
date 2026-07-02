import pygame

class Port(pygame.sprite.Sprite):
    images = {}
    def __init__(self, port_resource, pos, vertices):
        super().__init__()

        if not self.images:
            self.load_images()
        
        self.image = Port.images[port_resource]
        self.rect = self.image.get_rect(topleft=pos)
        self.vertices = vertices

    @staticmethod
    def _get_resource_icon(resource) -> str:
        match resource:
            case 'any':
                return 'graphics/default/resources/any_icon.png'
            case 'wheat':
                return 'graphics/default/resources/wheat_icon.png'
            case 'wood':
                return 'graphics/default/resources/wood_icon.png'
            case 'brick':
                return 'graphics/default/resources/brick_icon.png'
            case 'ore':
                return 'graphics/default/resources/ore_icon.png'
            case 'sheep':
                return 'graphics/default/resources/sheep_icon.png'
        return ''
    
    @staticmethod
    def _conjure_port_image(resource):
        base_image = pygame.image.load('graphics/default/ports/blank_port.png').convert_alpha()
        
        top_layer = pygame.image.load(Port._get_resource_icon(resource)).convert_alpha()
        top_layer = pygame.transform.scale(top_layer, (500, 500))

        combined = base_image.copy()
        combined.blit(top_layer, (200, 85))

        return combined
    
    @classmethod
    def load_images(cls):
        cls.images = {
            'any' : cls._conjure_port_image('any'),
            'wood' : cls._conjure_port_image('wood'),
            'sheep' : cls._conjure_port_image('sheep'),
            'ore' :   cls._conjure_port_image('ore'),
            'wheat' : cls._conjure_port_image('wheat'),
            'brick' : cls._conjure_port_image('brick')
        }