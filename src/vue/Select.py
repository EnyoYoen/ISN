import pygame


class Select:
    """
    The Select class represents a selectable dropdown menu in a pygame application.

    Attributes:
        x (int): The x-coordinate of the top left corner of the dropdown menu.
        y (int): The y-coordinate of the top left corner of the dropdown menu.
        width (int): The width of the dropdown menu.
        height (int): The height of the dropdown menu.
        options (list): The list of options in the dropdown menu.
        value (any): The currently selected value in the dropdown menu.
        is_open (bool): A flag indicating whether the dropdown menu is open.

    Methods:
        __init__(x, y, width, height, options, default_value): Initializes the Select instance.
        render(screen): Renders the dropdown menu on the screen.
        handle_event(event): Handles a pygame event.
        get_value(): Returns the currently selected value.
    """

    __slots__ = ["x", "y", "width", "height", "options", "value", "is_open"]

    def __init__(self, x, y, width, height, options, default_value=None):
        """
        Initializes the Select instance.

        Parameters:
            x (int): The x-coordinate of the top left corner of the dropdown menu.
            y (int): The y-coordinate of the top left corner of the dropdown menu.
            width (int): The width of the dropdown menu.
            height (int): The height of the dropdown menu.
            options (list): The list of options in the dropdown menu.
            default_value (any, optional): The default selected value in the dropdown menu. Defaults to the first option if not provided.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.options = options
        self.value = default_value if default_value in options else options[0]
        self.is_open = False

    def render(self, screen):
        """
        Renders the dropdown menu on the screen.

        Parameters:
            screen (pygame.Surface): The surface to render the dropdown menu on.
        """
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            pygame.Rect(self.x, self.y, self.width, self.height),
        )
        text = pygame.font.Font(None, 36).render(str(self.value), 1, (0, 0, 0))
        screen.blit(
            text, pygame.Rect(self.x, self.y, self.width, self.height).move(5, 5)
        )
        if self.is_open:
            for i, option in enumerate(self.options):
                rect = pygame.Rect(
                    self.x, self.y + (i + 1) * self.height, self.width, self.height
                )
                pygame.draw.rect(screen, (255, 255, 255), rect)
                text = pygame.font.Font(None, 36).render(str(option), 1, (0, 0, 0))
                screen.blit(text, rect.move(5, 5))

    def handle_event(self, event):
        """
        Handles a pygame event. If the event is a left mouse button down event, it toggles the open state of the dropdown menu or selects an option.

        Parameters:
            event (pygame.event.Event): The event to handle.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if pygame.Rect(self.x, self.y, self.width, self.height).collidepoint(
                event.pos
            ):
                self.is_open = not self.is_open
            elif self.is_open:
                for i, option in enumerate(self.options):
                    rect = pygame.Rect(
                        self.x, self.y + (i + 1) * self.height, self.width, self.height
                    )
                    if rect.collidepoint(event.pos):
                        self.value = option
                        self.is_open = False

    def get_value(self):
        """
        Returns the currently selected value.

        Returns:
            any: The currently selected value.
        """
        return self.value
