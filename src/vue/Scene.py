import pygame
from abc import ABC, abstractmethod


class Scene(ABC):
    """
        Scene is an abstract base class that provides a template for defining game scenes.
        It provides methods for handling events, updating, and rendering scenes.

        Attributes:
            running (bool): A flag indicating whether the scene is running.
            screen (pygame.Surface): The screen to render the scene on.
            parameter (any): Parameters passed to the scene.
            core (any): The core game engine.
            event (pygame.event.Event): The event to handle.

        Methods:
            run(): Runs the scene loop.
            decorator_handle_events(): Decorator method for handling events.
            decorator_update(): Decorator method for updating the scene.
            decorator_render(): Decorator method for rendering the scene.
            handle_events(event): Abstract method for handling events.
            update(): Abstract method for updating the scene.
            render(): Abstract method for rendering the scene.
    """

    __slots__ = ["running", "screen", "parameter", "core", "event"]

    def __init__(self, core) -> None:
        """
            Initializes the Scene instance with the core game engine.

            Args:
                core (any): The core game engine.
        """
        self.running = False
        self.core = core
        self.screen = core.screen
        self.parameter = core.parameter
        self.event = self.core.event

    def run(self) -> None:
        """
            Runs the scene loop. This method handles events, updates the scene, and renders the scene in a loop until the scene is no longer running.
        """
        self.running = True
        while self.running:
            self.decorator_handle_events()
            self.decorator_update()
            self.decorator_render()

    def decorator_handle_events(self) -> None:
        """
            Decorator method for handling events. This method gets all the events from pygame and passes them to the handle_events method.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.handle_events(event)

    def decorator_update(self) -> None:
        """
            Decorator method for updating the scene. This method calls the update method.
        """
        self.update()

    def decorator_render(self) -> None:
        """
            Decorator method for rendering the scene. This method calls the render method and then updates the display.
        """
        self.render()

        pygame.display.flip()

    @abstractmethod
    def handle_events(self, event: pygame.event.Event) -> None:
        """
            Abstract method for handling events. This method should be implemented in subclasses to handle specific events.

            Args:
                event (pygame.event.Event): The event to handle.
        """
        pass

    @abstractmethod
    def update(self) -> None:
        """
            Abstract method for updating the scene. This method should be implemented in subclasses to update the scene.
        """
        pass

    @abstractmethod
    def render(self) -> None:
        """
            Abstract method for rendering the scene. This method should be implemented in subclasses to render the scene.
        """
        pass
