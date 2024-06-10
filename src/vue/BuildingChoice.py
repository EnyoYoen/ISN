import pygame

from vue.Button import Button

from model.Geometry import Point, Rectangle
from model.Structures import BuildingType
from model.Ressource import RessourceType

class BuildingChoice:
    __slots__ = ["buttons", "player", "screen", "screen_size", "ressource_rect_size", "width", "margin", "padding", "building_size", "internal_origin", "rect", "building_costs", "font", "ressource_icons", "building_icons", "building_rendered_names", "background"]

    def __init__(self, player, screen, screen_size, ressource_rect_size, ressource_icons, scale_factor):
        building_names =  {
            BuildingType.FARM: "Ferme", 
            BuildingType.PANTRY: "Garde-Manger",
            BuildingType.MINER_CAMP: "Camp de Mineurs",
            BuildingType.LUMBER_CAMP: "Camp de bucherons",
            BuildingType.HUNTER_CAMP: "Camp de chasseurs",
            BuildingType.SOLDIER_CAMP: "Camp de soldats",
        }
        self.building_costs = {
            BuildingType.FARM: {RessourceType.WOOD: 50},
            BuildingType.PANTRY: {RessourceType.WOOD: 75, RessourceType.STONE: 25},
            BuildingType.MINER_CAMP: {RessourceType.WOOD: 75, RessourceType.STONE: 25, RessourceType.IRON: 25},
            BuildingType.LUMBER_CAMP: {RessourceType.WOOD: 100, RessourceType.STONE: 25},
            BuildingType.HUNTER_CAMP: {RessourceType.WOOD: 50, RessourceType.STONE: 25, RessourceType.FOOD: 25},
            BuildingType.SOLDIER_CAMP: {RessourceType.WOOD: 50, RessourceType.STONE: 25, RessourceType.IRON: 50},
        }
        
        self.font = pygame.font.Font("assets/font/Junter.otf", 12)

        self.building_icons = {}
        self.building_rendered_names = {}
        for type, name in building_names.items():
            self.building_icons[type] = pygame.transform.scale(pygame.image.load(f"assets/icons/{type.name.lower()}.png").convert_alpha(), (50, 50))
            self.building_rendered_names[type] = self.font.render(name, True, (255, 255, 255))
            
        self.ressource_icons = {}
        for ressource_type, ressource_icon in ressource_icons.items():
            self.ressource_icons[ressource_type] = pygame.transform.scale(ressource_icon, (30, 30))

        self.buttons = {}
        self.player = player
        self.screen = screen
        self.screen_size = screen_size
        self.ressource_rect_size = ressource_rect_size
        self.width = ressource_rect_size.x
        self.margin = 5
        self.padding = 3
        self.building_size = 115 * scale_factor
        self.internal_origin = Point(34, 44) * scale_factor
        self.rect = Rectangle(0, 0, self.width, self.screen_size.y - self.ressource_rect_size.y - 20)
        self.ressource_icons = ressource_icons
        self.background = pygame.transform.scale(pygame.image.load("assets/Textures/UI/building_ui.png").convert_alpha(), (self.rect.x2, self.rect.y2))

        self.create_buttons()

    def create_buttons(self):
        i = 0
        for building_type in self.building_costs.keys():
            button = Button("", self.margin + i % 2 * (self.building_size + self.margin * 2) + self.internal_origin.x, self.margin + (self.building_size + self.margin * 2) * (i // 2) + self.internal_origin.y, self.building_size, self.building_size, (175, 175, 175), None, 0)
            button.color = (74, 88, 128)
            self.buttons[building_type] = button
            i += 1

    def display_building(self, building_type, position):
        self.buttons[building_type].render(self.screen)

        name = self.building_rendered_names[building_type]
        self.screen.blit(name, (position.x + max(self.building_size - name.get_width(), 0) // 2, position.y + self.padding))
        self.screen.blit(self.building_icons[building_type], (position.x + (self.building_size - 50) // 2, position.y + 20))
        
        i = 0
        for ressource_type, ressource_number in self.building_costs[building_type].items():
            ressource_quantity = self.font.render(str(ressource_number), True, (255, 255, 255) if self.player.get_ressource(ressource_type) >= ressource_number else (255, 50, 50))
            self.screen.blit(ressource_quantity, (position.x + i * 48 + self.padding, position.y + 87))
            self.screen.blit(self.ressource_icons[ressource_type], (position.x + i * 48 + self.padding + 15, position.y + 75))
            i += 1

    def render(self):
        self.screen.blit(self.background, (self.rect.x1, self.rect.y1))
        i = 0
        for building_type in self.building_costs.keys():
            self.display_building(building_type, Point(self.margin + i % 2 * (self.building_size + self.margin * 2), self.margin + (self.building_size + self.margin * 2 - 1) * (i // 2)) + self.internal_origin) 
            i += 1

    def event_stream(self, event):
        result = None
        for building_type, button in self.buttons.items():
            clicked = button.is_clicked(event)
            if clicked:
                enough_ressources = True
                for ressource_type, ressource_number in self.building_costs[building_type].items():
                    if self.player.get_ressource(ressource_type) < ressource_number:
                        enough_ressources = False
                if enough_ressources:
                    result = building_type
                
                button.color = (110, 126, 180)
            if button.is_hovered(event):
                button.color = (92, 104, 155)
            elif not clicked:
                button.color = (74, 88, 128)
        return result