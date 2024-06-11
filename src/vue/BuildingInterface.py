import pygame

from vue.Button import Button

from model.Geometry import Point, Rectangle
from model.Human import HumanType
from model.Structures import Technologies

class BuildingInterface:
    """
    La classe BuildingInterface représente l'interface utilisateur pour les boutons (améliorations, unités) d'un bâtiments.

    Attributs:
    ----------
    font : pygame.font.Font
        La police de caractères pour afficher les informations des boutons.
    buttons : dict
        Les boutons chargé pour un bâtiment.
    buttons_infos : dict
        Les informations des boutons {Point(ligne, column) : (couts, type de l'icone, callback à l'appui du bouton)}.
    player : Player
        Le joueur qui intéragit avec l'interface.
    screen : pygame.Surface
        La surface de la fenêtre du jeu.
    screen_size : Point
        La taille de la fenêtre du jeu.
    ressource_rect_size : Point
        La taille de la zone de l'interface des ressources.
    margin : int
        La marge entre les boutons.
    padding : int
        La marge interne des boutons.
    cell_size : Point
        La taille d'une cellule de l'interface.
    internal_origin : Point
        L'origine interne de l'interface (pour afficher dans le carré de la texture).
    rect : Rectangle
        Le rectangle de l'interface.
    ressource_icons : dict
        Les icônes des ressources.
    technology_icons : dict
        Les icônes des technologies.
    human_icon : dict
        Les icônes des unités.
    background : pygame.Surface
        L'image de fond de l'interface.
    """
    __slots__ = ["font", "buttons", "buttons_infos", "player", "screen", "screen_size", "ressource_rect_size", "margin", "padding", "cell_size", "internal_origin", "rect", "ressource_icons", "technology_icons", "human_icon", "background"]

    def __init__(self, player, screen, screen_size, ressource_rect_size, ressource_icons, scale_factor):
        # Chargement de la police de caractères
        self.font = pygame.font.Font("assets/font/Junter.otf", 12)

        # Initialisation des attributs
        self.buttons_infos = {}
        self.buttons = {}
        self.player = player
        self.screen = screen
        self.screen_size = screen_size
        self.ressource_rect_size = ressource_rect_size
        self.margin = 5
        self.padding = 3
        self.cell_size = Point(140, 70)
        self.internal_origin = Point(140 * scale_factor + ressource_rect_size.x, self.screen_size.y - self.ressource_rect_size.y + 50 * scale_factor)
        self.rect = Rectangle(ressource_rect_size.x + 100 * scale_factor, self.screen_size.y - self.ressource_rect_size.y, ressource_rect_size.x + 600 * scale_factor, self.screen_size.y)

        # Chargement des icônes
        self.ressource_icons = {}
        for ressource_type, ressource_icon in ressource_icons.items():
            self.ressource_icons[ressource_type] = pygame.transform.scale(ressource_icon, (30, 30))
        self.technology_icons = {}
        for technology in Technologies:
            self.technology_icons[technology] = pygame.transform.scale(pygame.image.load(f"assets/icons/{technology.name.lower()}.png").convert_alpha(), (30, 30))
        self.human_icon = {}
        for human_type in HumanType:
            self.human_icon[human_type] = pygame.transform.scale(pygame.image.load(f"assets/icons/{human_type.name.lower()}.png").convert_alpha(), (30, 30))

        # Chargement de l'image de fond
        self.background = pygame.transform.scale(pygame.image.load("assets/Textures/UI/building.png").convert_alpha(), (self.rect.x2 - self.rect.x1, self.rect.y2 - self.rect.y1))

    def create_buttons(self, buttons_info):
        """
        Crée les boutons de l'interface.

        Paramètres:
        -----------
        buttons_info : dict
            Les informations des boutons {Point(ligne, column) : (couts, type de l'icone, callback à l'appui du bouton)}.
        """
        self.buttons.clear()
        self.buttons_infos = buttons_info
        for cell_pos in buttons_info.keys():
            button = Button("", self.internal_origin.x + cell_pos.y * (self.cell_size.x + self.margin), self.internal_origin.y + cell_pos.x * (self.cell_size.y + self.margin), self.cell_size.x, self.cell_size.y, (74, 88, 128), "assets/font/Junter.otf", 15)
            self.buttons[cell_pos] = button

    def render(self):
        """
        Affiche l'interface.
        """
        # Affichage de l'image de fond
        self.screen.blit(self.background, (self.rect.x1, self.rect.y1))

        # Affichage des boutons
        for pos, button in self.buttons.items():
            position = Point(self.internal_origin.x + pos.y * (self.cell_size.x + self.margin), self.internal_origin.y + pos.x * (self.cell_size.y + self.margin))
            button.render(self.screen)

            # Affichage des icônes
            costs, icon, _ = self.buttons_infos[pos]
            if icon is not None:
                image = None
                if icon in Technologies:
                    image = self.technology_icons[icon]
                else:
                    image = self.human_icon[icon]
                self.screen.blit(image, (position.x + (self.cell_size.x - 30) // 2, position.y + 4))

            # Affichage des coûts
            i = 0
            for ressource_type, ressource_number in costs.items():
                ressource_quantity = self.font.render(str(ressource_number), True, (255, 255, 255) if self.player.get_ressource(ressource_type) >= ressource_number else (255, 50, 50))
                self.screen.blit(ressource_quantity, (position.x + i * 48 + self.padding, position.y + 42))
                self.screen.blit(self.ressource_icons[ressource_type], (position.x + i * 48 + self.padding + 15, position.y + 35))
                i += 1

    def event_stream(self, event):
        """
        Gère les événements de l'interface (donnés par GameVue).

        Paramètres:
        -----------
        event : pygame.event.Event
            L'événement à traiter.
        """
        result = False
        # Vérification des boutons
        for pos, button in self.buttons.items():
            clicked = button.is_clicked(event)
            if clicked:
                # Vérification des ressources si le bouton est cliqué
                enough_ressources = True
                for ressource_type, ressource_number in self.buttons_infos[pos][0].items():
                    if self.player.get_ressource(ressource_type) < ressource_number:
                        enough_ressources = False
                if enough_ressources:
                    self.buttons_infos[pos][2]()
                    result = True
                button.color = (110, 126, 180)
            if button.is_hovered(event):
                button.color = (92, 104, 155)
            elif not clicked:
                button.color = (74, 88, 128)
        return result