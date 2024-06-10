import pygame


class Slider:
    """
        A class to represent a slider UI element.

        ...

        Attributes
        ----------
        x : int
            x-coordinate of the slider
        y : int
            y-coordinate of the slider
        width : int
            width of the slider
        height : int
            height of the slider
        min_val : int
            minimum value of the slider
        max_val : int
            maximum value of the slider
        value : int
            current value of the slider
        dragging : bool
            state of the slider (whether it's being dragged or not)

        Methods
        -------
        render(screen):
            Draws the slider on the given screen.
        handle_event(event):
            Handles the given event (mouse button down, up, and motion).
        get_value():
            Returns the current value of the slider.
    """

    __slots__ = ["x", "y", "width", "height", "min_val", "max_val", "value", "dragging"]

    def __init__(self, x, y, width, height, min_val, max_val, initial_val):
        """
            Constructs all the necessary attributes for the slider object.

            Parameters
            ----------
                x : int
                    x-coordinate of the slider
                y : int
                    y-coordinate of the slider
                width : int
                    width of the slider
                height : int
                    height of the slider
                min_val : int
                    minimum value of the slider
                max_val : int
                    maximum value of the slider
                initial_val : int
                    initial value of the slider
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.dragging = False

    def render(self, screen):
        """
            Draws the slider on the given screen.

            Parameters
            ----------
                screen : Surface
                    The surface to draw the slider on.
        """
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            pygame.Rect(self.x, self.y, self.width, self.height),
        )
        handle_x = (
            self.x
            + (self.value - self.min_val) / (self.max_val - self.min_val) * self.width
        )
        pygame.draw.rect(
            screen, (255, 0, 0), pygame.Rect(handle_x - 5, self.y, 10, self.height)
        )

    def handle_event(self, event):
        """
            Handles the given event (mouse button down, up, and motion).

            Parameters
            ----------
                event : Event
                    The event to handle.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if (
                self.x <= event.pos[0] <= self.x + self.width
                and self.y <= event.pos[1] <= self.y + self.height
            ):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.value = (event.pos[0] - self.x) / self.width * (
                self.max_val - self.min_val
            ) + self.min_val
            self.value = max(min(self.value, self.max_val), self.min_val)

    def get_value(self):
        """
            Returns the current value of the slider.

            Returns
            -------
            int
                The current value of the slider.
        """
        return self.value
