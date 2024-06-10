from model.Human import HumanState
from model.Map import Map
from model.Player import Player
from model.QLearningAgent import QLearningAgent
from model.Ressource import RessourceType
from model.Structures import BuildingType

LEARN = True


class AiPlayer(Player):
    """
    The AiPlayer class represents an AI player in the game. It is a subclass of the Player class.

    Attributes:
        actions (list): The list of possible actions the AI player can take.
        model (QLearningAgent): The Q-Learning agent used by the AI player.

    Methods:
        __init__(ressource_update_callback): Initializes the AiPlayer instance.
        calculate_state(map): Calculates the current state of the game.
        step(map): Performs a step in the game.
        get_structures(map): Gets the structures owned by the AI player.
        get_technology(map): Gets the technology upgrades of the AI player.
        get_craft(map): Gets the craftable items of the AI player.
        get_human(map): Gets the humans owned by the AI player.
        get_ennemi(map): Gets the enemies of the AI player.
    """

    __slots__ = ["actions", "model"]

    def __init__(
        self,
        ressource_update_callback,
    ):
        """
        Initializes the AiPlayer instance.

        Parameters:
            ressource_update_callback (function): The callback function to update resources.
        """
        super().__init__(ressource_update_callback)

        self.actions = []

        self.model = QLearningAgent(self.actions)

    def calculate_state(self, map: Map):
        """
        Calculates the current state of the game. The state includes the resources, technology, craft, humans, and enemies.

        Parameters:
            map (Map): The current game map.

        Returns:
            tuple: The current state of the game.
        """
        ressource = self.get_structures(map)
        technology = self.get_technology(map)
        craft = self.get_craft(map)
        human = self.get_human(map)
        ennemi = self.get_ennemi(map)
        return ressource, technology, craft, human, ennemi

    def step(self, map: Map):
        """
        Performs a step in the game. This includes calculating the current state, choosing an action, performing the action, and updating the Q-table.

        Parameters:
            map (Map): The current game map.
        """
        state = self.calculate_state(map)
        id_action = self.model.choose_action(state)
        reward = self.actions[id_action]()
        next_state = self.calculate_state(map)

        if LEARN:
            self.model.update_q_table(state, id_action, reward, next_state)

    def get_structures(self, map: Map):
        """
        Gets the structures owned by the AI player. This includes the pantry, farm, and mine.

        Parameters:
            map (Map): The current game map.

        Returns:
            tuple: The number of each type of structure owned by the AI player.
        """
        pantry = 0
        farm = 0
        mine = 0
        for building in map.buildings:
            if building.player == self:
                if building.type == BuildingType.PANTRY:
                    pantry += 1
                if building.type == BuildingType.FARM:
                    farm += 1
                if building.type == BuildingType.MINER_CAMP:
                    mine += 1
        return pantry, farm, mine

    def get_technology(self, map: Map):
        """
        Gets the technology upgrades of the AI player. This includes the building health multiplier, building time multiplier, food multiplier, and mining multiplier.

        Parameters:
            map (Map): The current game map.

        Returns:
            tuple: The technology upgrades of the AI player.
        """
        if self.upgrades.BUILDING_HEALTH_MULTIPLIER == 2:
            base_updatehealth = 1
        else:
            base_updatehealth = 0
        if self.upgrades.BUILDING_TIME_MULTIPLIER == 2:
            base_update_time = 2
        else:
            base_update_time = 0
        if self.upgrades.FOOD_MULTIPLIER == 2:
            food_update = 1
        else:
            food_update = 0
        if self.upgrades.MINING_MULTIPLIER == 2:
            mining_update = 1
        else:
            mining_update = 0
        return base_updatehealth, base_update_time, food_update, mining_update

    def get_craft(self, map: Map):
        """
        Gets the craftable items of the AI player. This includes whether the AI player can colonize, farm, or mine/pantry.

        Parameters:
            map (Map): The current game map.

        Returns:
            tuple: The craftable items of the AI player.
        """
        farm_able = 0
        mine_pantry_able = 0
        colon_able = 0
        if self.ressources[RessourceType.FOOD] >= 150:
            colon_able = 1
        if (
            self.ressources[RessourceType.WOOD] >= 75
            and self.ressources[RessourceType.STONE] >= 25
        ):
            mine_pantry_able = 1
        if self.ressources[RessourceType.WOOD] >= 50:
            farm_able = 1
        return colon_able, farm_able, mine_pantry_able

    def get_human(self, map: Map):
        """
        Gets the humans owned by the AI player.

        Parameters:
            map (Map): The current game map.

        Returns:
            int: The number of humans owned by the AI player.
        """
        human = 0
        for human in map.humans:
            if human.player == self:
                if human.state == HumanState.IDLE:
                    human += 1
        return human

    def get_ennemi(self, map: Map):
        """
        Gets the enemies of the AI player.

        Parameters:
            map (Map): The current game map.

        Returns:
            int: The number of enemies of the AI player.
        """
        return 0
