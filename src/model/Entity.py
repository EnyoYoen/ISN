class Entity:
    """
    Classe représentant une entité (animal ou humain) dans le jeu

    Attributs:
    ----------
    health : int
        La santé de l'entité.
    ressources : dict
        Les ressources dans l'"inventaire" de l'entité.
    """
    __slots__ = ["health", "ressources"]

    def __init__(self, health, ressources) -> None:
        """
        Initialise une entité dans le jeu

        Paramètres:
        -----------
        health : int
            La santé de l'entité.
        ressources : dict
            Les ressources dans l'"inventaire" de l'entité.
        """
        self.health = health
        self.ressources = ressources