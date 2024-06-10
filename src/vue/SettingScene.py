import pygame

from vue.Button import Button
from vue.Scene import Scene
from vue.Select import Select
from vue.Slider import Slider


class SettingsScene(Scene):
    """
        Represents the settings screen of the game.
        Inherits from the Scene class.

        Attributes:
        ----------
        opacity : pygame.Surface
            A surface that covers the entire screen to create an opacity effect.
        scale : float
            The scale of the screen.
        volume : float
            The current volume of the game.
        resolution : tuple
            The current resolution of the game.
        volume_slider : Slider
            A slider to adjust the volume.
        resolution_menu : Select
            A menu to select the resolution.
        apply_button : Button
            A button to apply the settings.
        cancel_button : Button
            A button to cancel the settings.
        parent_render : callable
            A function to render the parent scene.

        Methods:
        -------
        __init__(core, parent_render):
            Initializes the SettingsScene instance with the core game engine and a function to render the parent scene.
        handle_events(event):
            Handles events specific to the settings screen.
        update():
            Updates the settings screen.
        render():
            Renders the settings screen.
        change_button_color(button, hovered):
            Changes the color of the button when hovered.
    """

    __slots__ = [
        "opacity",
        "scale",
        "volume",
        "resolution",
        "volume_slider",
        "resolution_menu",
        "apply_button",
        "cancel_button",
        "parent_render",
    ]

    def __init__(self, core, parent_render: callable) -> None:
        """
            Initializes the SettingsScene instance with the core game engine and a function to render the parent scene.

            Parameters:
            ----------
            core : any
                The core game engine.
            parent_render : callable
                A function to render the parent scene.
        """
        super().__init__(core)
        self.parent_render = parent_render
        self.opacity = pygame.Surface(
            (self.screen.get_width(), self.screen.get_height())
        )
        self.opacity.set_alpha(160)
        self.scale = 0.0

        self.volume = pygame.mixer.music.get_volume()
        self.resolution = (self.screen.get_width(), self.screen.get_height())

        self.volume_slider = Slider(20, 100, 200, 20, 0.0, 1.0, self.volume)
        self.resolution_menu = Select(
            20,
            200,
            200,
            50,
            [(800, 600), (1024, 768), (1920, 1080), (2560, 1440), (3840, 2160)],
            self.resolution,
        )

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

    def handle_events(self, event: pygame.event.Event) -> None:
        """
            Handles events specific to the settings screen.

            This method checks if the apply button is clicked. If it is, it applies the settings by updating the volume and resolution parameters
            based on the current values of the volume and resolution attributes of the SettingsScene instance.

            Args:
                event (pygame.event.Event): The event to handle.
        """
        if self.apply_button.is_clicked(event):
            # Apply the settings
            self.parameter["volume"] = self.volume
            self.parameter["width"] = self.resolution[0]
            self.parameter["height"] = self.resolution[1]

            self.core.update_parameter(self.parameter)

            pygame.event.post(pygame.event.Event(self.event, {"scene": "title"}))
            self.running = False
        elif self.cancel_button.is_clicked(event):
            # Cancel the settings
            pygame.event.post(pygame.event.Event(self.event, {"scene": "title"}))
            self.running = False
        elif event.type == pygame.MOUSEMOTION:
            for button in [self.apply_button, self.cancel_button]:
                if button.is_hovered(event):
                    self.change_button_color(button, True)
                else:
                    self.change_button_color(button, False)
        self.volume_slider.handle_event(event)
        self.resolution_menu.handle_event(event)
        if event.type == pygame.QUIT:
            pygame.event.post(pygame.event.Event(self.event, {"scene": "quit"}))

    def update(self) -> None:
        """
            Updates the settings screen.
            This method updates the volume based on the volume slider's value and sets the game's music volume accordingly.
            It also updates the resolution based on the resolution menu's value.
            If the scale is less than 0.99, it increments the scale by 0.05.
        """
        self.volume = self.volume_slider.get_value()
        pygame.mixer.music.set_volume(self.volume)

        self.resolution = self.resolution_menu.get_value()

        if self.scale < 0.99:
            self.scale += 0.05

    def render(self) -> None:
        """
           Renders the settings screen.

           This method first calls the parent's render method to render the parent scene.
           Then, it overlays the settings screen on top of the parent scene.
        """
        self.parent_render()
        self.screen.blit(self.opacity, (0, 0))

        volume_text = pygame.font.Font(None, 36).render(
            f"Volume: {self.volume}", 1, (255, 255, 255)
        )
        self.volume_slider.render(self.screen)

        resolution_text = pygame.font.Font(None, 36).render(
            f"Resolution: {self.resolution}", 1, (255, 255, 255)
        )
        self.resolution_menu.render(self.screen)

        self.screen.blit(volume_text, (20, 20))
        self.screen.blit(resolution_text, (20, 60))

        self.apply_button.render(self.screen)
        self.cancel_button.render(self.screen)

        scaled_screen = pygame.transform.scale(
            self.screen,
            (
                int(self.screen.get_width() * self.scale),
                int(self.screen.get_height() * self.scale),
            ),
        )  # Scale the screen

        self.parent_render()
        self.screen.blit(
            scaled_screen,
            (
                (self.screen.get_width() - scaled_screen.get_width()) // 2,
                (self.screen.get_height() - scaled_screen.get_height()) // 2,
            ),
        )  # Draw the scaled screen onto the original screen

    @staticmethod
    def change_button_color(button: Button, hovered: bool) -> None:
        """
            Changes the color of the button when hovered.

            This method checks if the button is hovered. If it is, it changes the color of the button to a brighter shade.
            If the button is not hovered, it changes the color of the button to a darker shade.
            The color change depends on the text of the button. If the text is "Apply", the color is green. If the text is not "Apply", the color is red.

            Parameters:
            ----------
            button (Button): The button to change the color of.
            hovered (bool): Whether the button is hovered or not.
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
