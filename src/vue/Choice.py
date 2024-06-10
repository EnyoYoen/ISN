class Choice:
    """
        Represents a choice in the game.

        Attributes:
        ----------
        choice : int
            The current choice.
        max_choice : int
            The maximum number of choices.

        Methods:
        -------
        __init__(choice=1, max_choice=3):
            Initializes the Choice instance with the choice and max_choice.
        __add__(de):
            Increments the current choice by de and checks the bounds.
        __sub__(de):
            Decrements the current choice by de and checks the bounds.
        check():
            Checks and adjusts the current choice to ensure it's within the valid range.
        get_choix():
            Returns the current choice.
    """

    __slots__ = ["choice", "max_choice"]

    def __init__(self, choice=1, max_choice=5):
        """
            Initializes the Choice instance with the choice and max_choice.

            Parameters:
            ----------
            choice : int, optional
                The current choice. Defaults to 1.
            max_choice : int, optional
                The maximum number of choices. Defaults to 3.
        """
        self.choice = choice
        self.max_choice = max_choice

    def __add__(self, de):
        """
            Increments the current choice by de and checks the bounds.

            Parameters:
            ----------
            de : int
                The amount to increment the current choice by.
        """
        self.choice += de
        self.check()
        return self

    def __sub__(self, de):
        """
            Decrements the current choice by de and checks the bounds.

            Parameters:
            ----------
            de : int
                The amount to decrement the current choice by.
        """
        self.choice -= de
        self.check()
        return self

    def check(self):
        """
            Checks and adjusts the current choice to ensure it's within the valid range.
            If the current choice is less than 1, it's adjusted to be within the range by adding 3.
            If the current choice is greater than the maximum choice, it's adjusted to be within the range by subtracting 3.
        """
        while self.choice < 1:
            self.choice += self.max_choice
        while self.choice > self.max_choice:
            self.choice -= self.max_choice

    def get_choice(self):
        """
            Returns the current choice.

            Returns:
            -------
            int
                The current choice.
        """
        return self.choice

    def set_choice(self, de):
        """
            Sets the current choice to the given value.

            Parameters:
            ----------
            de : int
                The new choice value.
        """
        self.choice = de
