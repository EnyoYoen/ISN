import pygame

from vue.Button import Button
from vue.Choice import Choice
from vue.Scene import Scene
from vue.SettingScene import SettingsScene
from vue.SavesScene import SavesScene
from vue.ControlScene import ControlScene


class GameTitle(Scene):
    """
    Represents the title screen of the game.
    Inherits from the Scene class.

    Methods:
        __init__(screen): Initializes the GameTitle instance with the screen.
        handle_events(): Handles events specific to the title screen.
        update(): Updates the title screen.
        render(): Renders the title screen.
    """

    __slots__ = ["bg", "choice", "options", "font", "buttons"]

    def __init__(self, core) -> None:
        """
        Initializes the GameTitle instance with the screen.

        Parameters:
            screen (pygame.Surface): The surface to render the title screen on.
        """
        super().__init__(core)

        self.bg = None
        self.buttons = None

        pygame.mixer.music.load("assets/music/titleScreen.mp3")
        pygame.mixer.music.set_volume(self.parameter["volume"])
        pygame.mixer.music.play()

        self.choice = Choice()
        self.options = ["jouer", "sauvegardes", "explications", "option", "quitter"]

    def setup(self) -> None:
        self.core.update_screen()

        pygame.mixer.music.set_volume(self.parameter["volume"])

        self.bg = pygame.transform.smoothscale(
            pygame.image.load("assets/Textures/UI/background.jpg"),
            (self.screen.get_width(), self.screen.get_height()),
        )

        font_size = int(self.screen.get_height() * 0.065)
        button_width = self.screen.get_width() * 0.270
        button_height = self.screen.get_height() * 0.062
        self.buttons = [
            Button(
                option,
                (self.screen.get_width() - button_width) // 2,
                int(self.screen.get_height() * 0.45)
                + i * (self.screen.get_height() * 0.1),
                button_width,
                button_height,
                (255, 255, 255),
                "assets/font/Space-Laser-BF65f80ab15c082.otf",
                font_size,
            )
            for i, option in enumerate(self.options)
        ]

    def __del__(self) -> None:
        pygame.mixer.music.stop()

    def handle_events(self, event: pygame.event.Event) -> None:
        """
        Handles events specific to the title screen.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_KP_ENTER:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.key == pygame.K_UP:
                self.choice -= 1
            elif event.key == pygame.K_DOWN:
                self.choice += 1
            elif event.key == pygame.K_RETURN:
                self.choice_handler(self.choice.get_choice())
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i, button in enumerate(self.buttons):
                if button.is_clicked(event):
                    self.choice_handler(i + 1)
        elif event.type == pygame.MOUSEMOTION:
            for i, button in enumerate(self.buttons):
                if button.is_hovered(event):
                    self.choice.set_choice(i + 1)
        elif event.type == self.event:
            if event.dict.get("scene") == "quit":
                pygame.event.post(
                    pygame.event.Event(pygame.QUIT)
                )  # Close the game and exit

    def update(self) -> None:
        """
        Updates the title screen.
        """
        pass

    def render(self) -> None:
        """
        Renders the title screen.

        This method is responsible for drawing the title screen on the pygame surface. It first draws the background image
        onto the screen. Then, it iterates over the list of options and renders each one as a text object on the screen.

        The text is centered horizontally on the screen. The vertical position of the text is calculated as 80% of the
        screen height plus an offset based on the index of the option in the list, which creates a vertical list of options.

        The color of the text is determined by whether the current option is the selected choice. If it is, the text is
        rendered in red. Otherwise, it is rendered in white.
        """
        self.screen.blit(self.bg, (0, 0))  # Draw the background image onto the screen

        choice = self.choice.get_choice()
        for i, button in enumerate(self.buttons):  # Iterate over the list of options
            if choice == i + 1:  # Check if the current option is the selected choice
                button.color = (196, 158, 33)  # If it is, set the color to yellow
            else:
                button.color = (1, 6, 138)  # If it's not, set the color to blue
            button.render(self.screen)  # Render the button object onto the screen

            # Calculate the position of the text
            button_width, button_height = (
                button.get_size()
            )  # Get the size of the text object
            x = (
                self.screen.get_width() - button_width
            ) // 2  # Calculate the horizontal position (centered)
            y = int(self.screen.get_height() * 0.45) + i * (
                self.screen.get_height() * 0.1
            )  # Calculate the vertical position (80% from the top plus an offset)

            # Draw a triangle around the current choice
            if choice == i + 1:
                offset = button_height / 2

                x -= 20
                points = [
                    (x - offset, y + offset * 2),
                    (x - offset, y),
                    (x, y + offset),
                ]
                pygame.draw.polygon(self.screen, button.color, points)

                x += 40 + button_width
                points = [
                    (x + offset, y + offset * 2),
                    (x + offset, y),
                    (x, y + offset),
                ]
                pygame.draw.polygon(self.screen, button.color, points)

    def choice_handler(self, choice: Choice) -> None:
        """
        Handles the choice of the player.
        """
        if choice == 1:
            pygame.event.post(pygame.event.Event(self.event, {"scene": "game"}))
            self.running = False
        elif choice == 2:
            saves_scene = SavesScene(
                self.core, self.render
            )  # Create and run the saves scene
            saves_scene.run()
            self.setup()
        elif choice == 3:
            controls_scene = ControlScene(
                self.core, self.render
            )
            controls_scene.run()
            self.setup()
        elif choice == 4:
            settings_scene = SettingsScene(
                self.core, self.render
            )  # Create and run the settings scene
            settings_scene.run()
            self.setup()
        elif choice == 5:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
