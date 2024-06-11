import os
import pygame

from vue.Scene import Scene
from vue.Button import Button
from vue.Select import Select

class SavesScene(Scene):
    """
    Cette classe représente la scène de sauvegarde du jeu.

    Attributs:
    ----------
    parent_render : function
        La fonction de rendu de la scène parente.
    opacity : pygame.Surface
        La surface de l'opacité de la scene.
    scale : float
        L'échelle de la scène (float entre 0 et 1 pour l'agrandissement de la scene à l'ouverture).
    save_name : str
        Le nom de la sauvegarde.
    save_menu : Select
        Le menu de sélection de sauvegarde.
    apply_button : Button
        Le bouton pour appliquer la sauvegarde.
    cancel_button : Button
        Le bouton pour annuler la sélection.
    """

    __slots__ = ["parent_render", "opacity", "scale", "save_name", "save_menu", "apply_button", "cancel_button"]

    def __init__(self, core, parent_render):
        # Initialisation de la scène
        super().__init__(core)
        self.parent_render = parent_render
        self.opacity = pygame.Surface(
            (self.screen.get_width(), self.screen.get_height())
        )
        self.opacity.set_alpha(160)
        self.scale = 0.0

        # Initialisation des attributs
        self.save_name = None

        # Chargement des noms des sauvegardes
        saves_directory = "saves"
        saves = [""]
        if os.path.exists(saves_directory):
            for name in os.listdir(saves_directory):
                if os.path.isdir(os.path.join(saves_directory, name)):
                    saves.append(name)

        # Initialisation du menu de selection de sauvegarde
        self.save_menu = None
        if len(saves) > 0:
            self.save_menu = Select(
                20,
                200,
                300,
                50,
                saves,
                self.save_name,
            )

        # Initialisation des boutons
        button_width = self.screen.get_width() * 0.156
        button_height = self.screen.get_height() * 0.062
        font_size = int(self.screen.get_height() * 0.065)

        self.apply_button = Button(
            "Ok",
            self.screen.get_width() * 3 / 4 - button_width / 2,
            self.screen.get_height() * 0.9,
            button_width,
            button_height,
            (0, 255, 0),
            "assets/font/Space-Laser-BF65f80ab15c082.otf",
            font_size,
        )
        self.cancel_button = Button(
            "Retour",
            self.screen.get_width() / 4 - button_width / 2,
            self.screen.get_height() * 0.9,
            button_width,
            button_height,
            (255, 0, 0),
            "assets/font/Space-Laser-BF65f80ab15c082.otf",
            font_size,
        )

    def handle_events(self, event: pygame.event.Event):
        """
        Gère les événements de la scène.

        Paramètres:
        -----------
        event : pygame.event.Event
            L'événement à gérer.
        """
        if self.apply_button.is_clicked(event):
            # On applique la sauvegarde
            self.core.save_name = self.save_name
            pygame.event.post(pygame.event.Event(self.event, {"scene": "title"}))
            self.running = False
        elif self.cancel_button.is_clicked(event):
            # On retourne à la scène précédente
            pygame.event.post(pygame.event.Event(self.event, {"scene": "title"}))
            self.running = False
        elif event.type == pygame.MOUSEMOTION:
            # Si la souris survole un bouton, on change sa couleur
            for button in [self.apply_button, self.cancel_button]:
                if button.is_hovered(event):
                    self.change_button_color(button, True)
                else:
                    self.change_button_color(button, False)
        if self.save_menu is not None:
            # Gestion des événements du menu de sauvegarde
            self.save_menu.handle_event(event)
        if event.type == pygame.QUIT:
            # Si l'événement est de type QUIT, on quitte le jeu
            pygame.event.post(pygame.event.Event(self.event, {"scene": "quit"}))

    def update(self):
        """
        Met à jour la scène.
        """
        if self.scale < 0.99:
            self.scale += 0.05

        save_name = self.save_menu.get_value()
        if save_name != "":
            self.core.save_name = save_name

    def render(self):
        """
        Affiche la scène.
        """
        self.parent_render()

        self.screen.blit(self.opacity, (0, 0))

        # Affichage du menu de selection de sauvegarde
        if self.save_menu is not None:
            self.save_menu.render(self.screen)

        # Affichage des boutons
        self.apply_button.render(self.screen)
        self.cancel_button.render(self.screen)

        scaled_screen = pygame.transform.scale(
            self.screen,
            (
                int(self.screen.get_width() * self.scale),
                int(self.screen.get_height() * self.scale),
            ),
        )

        self.parent_render()
        self.screen.blit(
            scaled_screen,
            (
                (self.screen.get_width() - scaled_screen.get_width()) // 2,
                (self.screen.get_height() - scaled_screen.get_height()) // 2,
            ),
        )

    @staticmethod
    def change_button_color(button, hovered):
        """
        Change la couleur du bouton en fonction de si la souris le survole ou non.

        Paramètres:
        -----------
        button : Button
            Le bouton à modifier.
        hovered : bool
            Si la souris survole le bouton ou non.
        """
        if hovered:
            if button.text == "Ok":
                button.color = (0, 255, 0)
            else:
                button.color = (255, 0, 0)
        else:
            if button.text == "Ok":
                button.color = (0, 200, 0)
            else:
                button.color = (200, 0, 0)