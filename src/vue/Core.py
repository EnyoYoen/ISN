import os
import json
import subprocess

import pygame

from vue.GameTitle import GameTitle
from vue.GameVue import GameVue


class Core:
    """
    Represents the core of the game.
    Handles game initialization, configuration, and execution.

    Methods:
        __init__(): Initializes the Core instance.
        __del__(): Closes the game and exits pygame.
        setup_parameter(): Sets up the game parameters based on configuration.
        default_config() -> dict: Returns default configuration parameters.
        game_version(): Returns the version of the game.
        update_parameter(): Updates the game parameters if necessary.
        run(): Starts the game execution.
    """

    __slots__ = ["screen", "title_screen", "parameter", "save_name", "game_screen", "event"]

    def __init__(self) -> None:
        """
        Initializes the Core instance.
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
        Close the game and exit pygame.
        """
        pygame.quit()

    @staticmethod
    def window_setup() -> None:
        """
        Initializes the pygame module.
        """
        pygame.display.set_caption("Exodus", "exodus icon")
        pygame.display.set_icon(pygame.image.load("assets/Textures/UI/exodus.png"))
        # TODO : add an icon for the window in the task manager

    def setup_parameter(self) -> None:
        """
        Sets up the game parameters based on configuration.
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
        if self.parameter["fullscreen"]:
            flags = pygame.FULLSCREEN | pygame.SCALED
        else:
            flags = pygame.SCALED
        self.screen = pygame.display.set_mode(
            (self.parameter["width"], self.parameter["height"]), flags
        )

    @staticmethod
    def read_config() -> dict:
        with open("config.json", "r") as configFile:
            dico = json.load(configFile)
        return dico

    def default_config(self) -> None:
        """
        Returns default configuration parameters.
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
        Returns the version of the game.
        """
        patch = (
            subprocess.run(["git", "rev-list", "--all", "--count"], capture_output=True)
            .stdout.decode("utf-8")
            .strip()
        )
        return "0.0." + str(patch)

    def update_parameter(self, dico: dict) -> None:
        """
        Updates the game parameters if necessary.
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
        Starts the game execution.
        """
        self.title_screen = GameTitle(self)
        self.title_screen.setup()
        self.title_screen.run()
        del self.title_screen
        for event in pygame.event.get(self.event):
            if event.dict.get("scene") == "game":
                self.start_game()

    def start_game(self) -> None:
        self.game_screen = GameVue(self)
        # TODO : self.game_screen.setup()
        self.game_screen.run()
        del self.game_screen
        # TODO : self.run()
