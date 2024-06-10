import pygame


class Button:
    """
    The Button class represents a clickable button in a pygame application.

    Attributes:
        text (str): The text displayed on the button.
        x (int): The x-coordinate of the top left corner of the button.
        y (int): The y-coordinate of the top left corner of the button.
        width (int): The width of the button.
        height (int): The height of the button.
        color (tuple): The color of the button in RGB format.
        font (pygame.font.Font): The font used for the text on the button.

    Methods:
        __init__(text, x, y, width, height, color, font, font_size): Initializes the Button instance.
        render(screen): Renders the button on the screen.
        is_clicked(event): Checks if the button is clicked.
        get_size(): Returns the size of the button.
        is_hovered(event): Checks if the mouse is hovering over the button.
    """

    __slots__ = ["text", "x", "y", "width", "height", "color", "font"]

    def __init__(self, text, x, y, width, height, color, font=None, font_size=36):
        """
        Initializes the Button instance.

        Parameters:
            text (str): The text displayed on the button.
            x (int): The x-coordinate of the top left corner of the button.
            y (int): The y-coordinate of the top left corner of the button.
            width (int): The width of the button.
            height (int): The height of the button.
            color (tuple): The color of the button in RGB format.
            font (str, optional): The path to the font file. Defaults to the pygame default font.
            font_size (int, optional): The size of the font. Defaults to 36.
        """
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.font = pygame.font.Font(font, font_size)

    def render(self, screen):
        """
        Renders the button on the screen.

        Parameters:
            screen (pygame.Surface): The surface to render the button on.
        """
        pygame.draw.rect(
            screen, self.color, pygame.Rect(self.x, self.y, self.width, self.height)
        )
        text = self.font.render(self.text, 1, (255, 255, 255))
        text_width, text_height = text.get_size()
        screen.blit(
            text,
            (
                self.x + self.width // 2 - text_width // 2,
                self.y + self.height // 2 - text_height // 2.5,
            ),
        )

    def is_clicked(self, event):
        """
        Checks if the button is clicked.

        Parameters:
            event (pygame.event.Event): The event to check.

        Returns:
            bool: True if the button is clicked, False otherwise.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            return (
                self.x <= mouse_pos[0] <= self.x + self.width
                and self.y <= mouse_pos[1] <= self.y + self.height
            )
        return False

    def get_size(self):
        """
        Returns the size of the button.

        Returns:
            tuple: The width and height of the button.
        """
        return self.width, self.height

    def is_hovered(self, event):
        """
        Checks if the mouse is hovering over the button.

        Parameters:
            event (pygame.event.Event): The event to check.

        Returns:
            bool: True if the mouse is hovering over the button, False otherwise.
        """
        if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = pygame.mouse.get_pos()
            return (
                self.x <= mouse_pos[0] <= self.x + self.width
                and self.y <= mouse_pos[1] <= self.y + self.height
            )
