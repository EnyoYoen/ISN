from enum import Enum

class Technologies(Enum):
    """
    Enumération des technologies
    """
    FORESTRY = 1
    AGRICULTURE = 2
    MINING = 3
    HUNT = 4
    COMBAT = 5
    BUILDING_HEALTH = 6
    BUILDING_TIME = 7
    EXTRA_MATERIALS = 8

class Upgrades:
    """
    Classe des améliorations

    Attributs:
    BUILDING_HEALTH_MULTIPLIER (int):
        Le multiplicateur de santé des bâtiments.
    BUILDING_TIME_MULTIPLIER (int):
        Le multiplicateur de temps de construction des bâtiments.
    FOOD_MULTIPLIER (int):
        Le multiplicateur de production de nourriture.
    MINING_MULTIPLIER (int):
        Le multiplicateur de production de minerais.
    WOOD_MULTIPLIER (int):
        Le multiplicateur de production de bois.
    HUNT_MULTIPLIER (int):
        Le multiplicateur de production de viande.
    COMBAT_MULTIPLIER (int):
        Le multiplicateur de combat.
    EXTRA_MATERIALS (bool):
        Si le joueur peut obtenir des matériaux supplémentaires (vulcain et crystal).
    """

    __slots__ = ["BUILDING_HEALTH_MULTIPLIER", "BUILDING_TIME_MULTIPLIER", "FOOD_MULTIPLIER", "MINING_MULTIPLIER", "WOOD_MULTIPLIER", "HUNT_MULTIPLIER", "COMBAT_MULTIPLIER", "EXTRA_MATERIALS"]

    def __init__(self) -> None:
        self.BUILDING_HEALTH_MULTIPLIER = 1
        self.BUILDING_TIME_MULTIPLIER = 1

        self.FOOD_MULTIPLIER = 1
        self.MINING_MULTIPLIER = 1
        self.WOOD_MULTIPLIER = 1
        self.HUNT_MULTIPLIER = 1
        self.COMBAT_MULTIPLIER = 1
        self.EXTRA_MATERIALS = False