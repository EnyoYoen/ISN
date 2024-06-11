import os
import json
import subprocess

import pygame

from vue.GameTitle import GameTitle
from vue.GameVue import GameVue


class Core:
    """
    The Core class represents the core of the game. It is responsible for game initialization, configuration, and execution.

    Attributes:
        screen (pygame.Surface): The main screen of the game.
        title_screen (GameTitle): The title screen of the game.
        parameter (dict): The game parameters.
        save_name (str): The name of the save file.
        game_screen (GameVue): The main game screen.
        event (pygame.event.Event): The custom event type.

    Methods:
        __init__(): Initializes the Core instance.
        __del__(): Closes the game and exits pygame.
        window_setup(): Initializes the pygame module and sets up the window.
        setup_parameter(): Sets up the game parameters based on configuration.
        update_screen(): Updates the screen based on the game parameters.
        read_config() -> dict: Reads the game configuration from a file.
        default_config(): Writes the default configuration to a file.
        game_version() -> str: Returns the version of the game.
        update_parameter(dico: dict): Updates the game parameters if necessary.
        run(): Starts the game execution.
        start_game(): Starts the main game.
    """

    __slots__ = [
        "screen",
        "title_screen",
        "parameter",
        "save_name",
        "game_screen",
        "event",
    ]

    def __init__(self) -> None:
        """
        Initializes the Core instance. This includes initializing pygame and setting up the game screen, title screen, parameters, save name, and event.
        """
        self.game_screen = None
        self.screen = None
        self.title_screen = None
        self.parameter = None
        self.save_name = None
        self.event = pygame.event.custom_type()

        pygame.init()

    def __del__(self):
        """
        Closes the game and exits pygame. This is called when the Core instance is deleted.
        """
        pygame.quit()

    @staticmethod
    def window_setup() -> None:
        """
        Initializes the pygame module and sets up the window. This includes setting the window caption and icon.
        """
        pygame.display.set_caption("Exodus", "exodus icon")
        pygame.display.set_icon(pygame.image.load("assets/Textures/UI/exodus.png"))

    def setup_parameter(self) -> None:
        """
        Sets up the game parameters based on configuration. This includes setting up the window and reading the game configuration. If the configuration file does not exist, it creates a default configuration.
        """
        self.window_setup()

        if not os.path.isfile("config.json"):
            self.default_config()

        dico = self.read_config()

        if dico.get("version") != self.game_version():
            self.update_parameter(dico)
            dico = self.read_config()

        self.parameter = dico
        self.update_screen()

    def update_screen(self) -> None:
        """
        Updates the screen based on the game parameters. This includes setting the screen mode based on whether the game is in fullscreen mode or not.
        """
        if self.parameter["fullscreen"]:
            flags = pygame.FULLSCREEN | pygame.SCALED
        else:
            flags = pygame.SCALED
        self.screen = pygame.display.set_mode(
            (self.parameter["width"], self.parameter["height"]), flags
        )

    @staticmethod
    def read_config() -> dict:
        """
        Reads the game configuration from a file and returns it as a dictionary.
        """
        with open("config.json", "r") as configFile:
            dico = json.load(configFile)
        return dico

    def default_config(self) -> None:
        """
        Writes the default configuration to a file. The default configuration includes the game version, fullscreen mode, screen width and height, and volume.
        """
        with open("config.json", "w") as configFile:
            json.dump(
                dict(
                    version=self.game_version(),
                    fullscreen=True,
                    width=2560,
                    height=1600,
                    volume=0.1,
                ),
                configFile,
            )

    @staticmethod
    def game_version() -> str:
        """
        Returns the version of the game. The version is determined by counting the number of git revisions.
        """
        patch = (
            subprocess.run(["git", "rev-list", "--all", "--count"], capture_output=True)
            .stdout.decode("utf-8")
            .strip()
        )
        return "0.0." + str(patch)

    def update_parameter(self, dico: dict) -> None:
        """
        Updates the game parameters if necessary. This includes writing the updated parameters to the configuration file.
        """
        self.default_config()

        default_dico = self.read_config()

        with open("config.json", "w") as configFile:
            for key in dico.keys():
                if key != "version":
                    default_dico[key] = dico[key]
            json.dump(default_dico, configFile)

    def run(self) -> None:
        """
        Starts the game execution. This includes setting up and running the title screen, and starting the main game when the title screen is closed.
        """
        self.title_screen = GameTitle(self)
        self.title_screen.setup()
        self.title_screen.run()
        del self.title_screen
        for event in pygame.event.get(self.event):
            if event.dict.get("scene") == "game":
                self.start_game()

    def start_game(self) -> None:
        """
        Starts the main game. This includes setting up and running the main game screen.
        """
        self.game_screen = GameVue(self)
        self.game_screen.run()
        del self.game_screen
