from enum import Enum
from math import inf
from random import uniform

from model.Entity import Entity
from model.Structures import StructureType, BuildingType, BuildingState, OreType, oreToRessourceType
from model.Ressource import RessourceType
from model.Geometry import Point
from model.Map import Map
from model.AStar import AStar
from model.HumanType import HumanType
from model.Tools import Directions

class HumanState(Enum):
    """
    Enumération des états possibles d'un humain.
    """
    IDLE = 0
    MOVING = 1
    WORKING = 2

class HumanWork(Enum):
    """
    Enumération des tâches possibles d'un humain.
    """
    IDLE = 0
    GATHERING = 1
    HUNTING = 2
    BUILDING = 3
    DESTROYING = 4
    FIGHTING = 5

class GatherState(Enum):
    """
    Enumération des états possibles de récolte d'un humain.
    """
    GATHERING = 1
    DEPOSITING = 2

class Human(Entity):
    """
    Un humain dans le jeu.

    Attributs:
    ----------
    hid : int
        L'identifiant unique de l'humain.
    current_location : Point
        La position actuelle de l'humain.
    target_location : Point
        La position cible de l'humain.
    building_location : Point
        La position du bâtiment cible de l'humain.
    path : list
        La liste des points du chemin de l'humain.
    resource_capacity : int
        La capacité de ressources de l'humain.
    gathering_speed : int
        La vitesse de récolte de l'humain.
    damage : int
        Les dégâts infligés par l'humain.
    ressource_type : RessourceType
        Le type de ressource récoltée par l'humain.
    deposit_speed : int
        La vitesse de dépôt des ressources de l'humain.
    speed : int
        La vitesse de déplacement de l'humain.
    progression : int
        La progression de l'humain sur son chemin.
    going_to_work : bool
        Indique si l'humain se rend à son lieu de travail.
    going_to_target : bool
        Indique si l'humain se rend à sa cible.
    going_to_deposit : bool
        Indique si l'humain se rend à son lieu de dépôt.
    state : HumanState
        L'état de l'humain.
    work : HumanWork
        La tâche de l'humain.
    gather_state : GatherState
        L'état de récolte de l'humain.
    map : Map
        La carte du jeu.
    player : Player
        Le joueur possédant l'humain.
    target_entity : Entity
        L'entité cible de l'humain.
    death_callback : function
        La fonction de callback appelée lors de la mort de l'humain.
    """

    __slots__ = ["hid", "current_location", "target_location", "building_location", "path", "resource_capacity", "gathering_speed", "damage", "ressource_type", "deposit_speed", "speed", "progression", "going_to_work", "going_to_target", "going_to_deposit", "state", "work", "gather_state", "map", "player", "target_entity", "death_callback"]

    CELL_CENTER = Point(Map.CELL_SIZE, Map.CELL_SIZE) // 2

    HID = 0

    def __init__(self, health, type, capacity, gathering_speed, damage, speed, map, location, player, death_callback):
        # Initialisation de l'entité
        super().__init__(health, {})

        # Initialisation des attributs
        Human.HID += 1
        self.hid = Human.HID
        self.type = type
        self.current_location = location - location % Map.CELL_SIZE + Human.CELL_CENTER
        self.target_location = None
        self.building_location = None
        self.path = None
        self.resource_capacity = capacity
        self.gathering_speed = gathering_speed
        self.damage = damage
        self.ressource_type = None
        self.deposit_speed = 2
        self.speed = speed
        self.progression = 0
        self.going_to_work = False
        self.going_to_target = False
        self.going_to_deposit = False
        self.state = HumanState.IDLE
        self.work = HumanWork.IDLE
        self.gather_state = GatherState.GATHERING
        self.map = map
        self.orientation = Directions.BOTTOM
        self.player = player
        self.target_entity = None
        self.death_callback = death_callback
        self.ressources = {}

    def find_nearest_building(self, building_types):
        """
        Trouve le bâtiment le plus proche de l'humain correspondant à un des types donnés.

        Paramètres:
        -----------
        building_types : list
            La liste des types de bâtiments à chercher.
        """
        # On récupère les bâtiments correspondant aux types donnés et construits
        buildings = []
        for building_type in building_types:
            actual_buildings = self.map.building_type.get(building_type, None)
            if actual_buildings is not None:
                for building in actual_buildings:
                    if building.state != BuildingState.PLACED and building.state != BuildingState.BUILDING:
                        buildings.append(building)

        # On cherche le bâtiment le plus proche par l'algorithme A*
        nearest_building = None
        min_path = None
        min_distance = +inf
        for building in buildings:
            path = AStar(self.current_location // Map.CELL_SIZE, building.coords, self.map)
            distance = +inf if path is None else len(path)
            if distance < min_distance:
                min_distance = distance
                nearest_building = building
                min_path = path

        # On retourne la position du bâtiment le plus proche et le chemin pour y accéder
        return nearest_building.coords, min_path

    def move(self, duration):
        """
        Déplace l'humain sur son chemin.

        Paramètres:
        -----------
        duration : int
            La durée du déplacement.
        """
        # On met à jour la progression de l'humain sur son chemin et on garde en mémoire l'ancienne progression
        old_progression = self.progression
        self.progression += duration * self.speed
        path_start = 0
        path_end = 0
        diff = None

        # On met à jour la position actuelle de l'humain
        if self.progression < len(self.path) - 1:
            # Si l'humain n'a pas atteint la fin de son chemin, on calcule sa position intermédiaire
            self.progression = min(self.progression, len(self.path) - 1)
            path_start = int(self.progression)
            path_end = path_start + 1
            diff = (self.path[path_end] - self.path[path_start])
            self.current_location = self.path[path_start] + diff * (self.progression % 1)
        else:
            # Si l'humain a atteint la fin de son chemin, on met à jour sa position 
            self.current_location = self.path[-1]
            self.progression = len(self.path) - 1
            if len(self.path) > 1:
                diff = (self.path[-2] - self.path[-1])
        
        # On met à jour l'orientation de l'humain
        if diff is not None:
            if diff.x > 0:
                self.orientation = Directions.RIGHT
            elif diff.x < 0:
                self.orientation = Directions.LEFT
            else:
                if diff.y > 0:
                    self.orientation = Directions.BOTTOM
                elif diff.y < 0:
                    self.orientation = Directions.TOP

        # On retourne la durée restante après le déplacement (0 si l'humain n'a pas atteint la fin de son chemin)
        return 0 if self.progression < len(self.path) - 1 else duration - (len(self.path) - 1 - old_progression) / self.speed
    
    def get_ressource_count(self, ressources):
        """
        Retourne le nombre total de ressources dans le dictionnaire donné.

        Paramètres:
        -----------
        ressources : dict
            Les ressources données.
        """
        count = 0
        for ressource in ressources.values():
            count += ressource
        return count

    def gather_resources(self, duration):
        """
        Récolte des ressources pendant une durée donnée.

        Paramètres:
        -----------
        duration : int
            La durée de récolte.
        """
        # On récupère les anciennes ressources de l'humain et on initialise les ressources si elles n'existent pas
        if self.ressources.get(self.ressource_type, None) is None:
            self.ressources[self.ressource_type] = 0
        old_ressources = self.ressources
        capacity = self.resource_capacity - self.get_ressource_count(old_ressources)

        # On met à jour la vitesse de récolte en fonction du type de ressource et de l'humain, et des améliorations du joueur
        gathering_speed = self.gathering_speed
        if self.ressource_type == RessourceType.FOOD:
            gathering_speed *= self.player.upgrades.FOOD_MULTIPLIER
        elif self.ressource_type in [RessourceType.STONE, RessourceType.IRON, RessourceType.COPPER, RessourceType.GOLD, RessourceType.CRYSTAL, RessourceType.VULCAN]:
            gathering_speed *= self.player.upgrades.MINING_MULTIPLIER
        if (self.type == HumanType.LUMBERJACK and self.ressource_type == RessourceType.WOOD
            or self.type == HumanType.FARMER and self.ressource_type == RessourceType.FOOD
            or self.type == HumanType.MINER and self.ressource_type in [RessourceType.STONE, RessourceType.IRON, RessourceType.COPPER, RessourceType.GOLD, RessourceType.CRYSTAL, RessourceType.VULCAN]):
            gathering_speed *= 2

        # On met à jour les ressources de l'humain en fonction de la durée de récolte et de la capacité de l'humain
        self.ressources[self.ressource_type] += min(duration * gathering_speed, capacity)

        # On met à jour la durée restante après la récolte
        duration_left = 0 if self.get_ressource_count(self.ressources) < self.resource_capacity else duration - capacity / gathering_speed
        
        struct =  self.map.occupied_coords.get(self.target_location, None)
        if struct is None or struct.structure_type == StructureType.ORE or struct.structure_type == StructureType.TREE:
            struct_destroyed = False
            if struct is not None:
                # On récupère les ressources de la structure si elle n'est pas détuite
                if struct.structure_type == StructureType.ORE:
                    struct_destroyed = struct.mine((duration - duration_left) * self.gathering_speed)
                else:
                    struct_destroyed = struct.chop_down((duration - duration_left) * self.gathering_speed)
                    
            if struct is None or struct_destroyed:
                # La structure a été détruite ou n'existe plus, on retourne au bâtiment cible
                self.gather_state = GatherState.DEPOSITING
                self.going_to_target = False
                self.go_to_location(self.building_location)
            
        return duration_left

    def deposit_resources(self, duration):
        """
        Dépose des ressources pendant une durée donnée.
        
        Paramètres:
        -----------
        duration : int
            La durée de dépôt.
        """
        total_deposit = 0
        for ressource, quantity in self.ressources.items():
            # On dépose les ressources dans le bâtiment cible tant que l'humain a des ressources à déposer et que la durée n'est pas écoulée
            deposit = min(duration * self.deposit_speed, quantity)
            self.player.add_ressource(ressource, deposit)
            self.ressources[ressource] -= deposit
            if quantity > deposit:
                total_deposit += deposit
                break
            else:
                total_deposit += quantity
                duration -= deposit / self.deposit_speed
                self.ressources[ressource] = 0
        
        # On renvoie la durée restante après le dépôt (0 si il reste des ressources à déposer)
        return 0 if self.get_ressource_count(self.ressources) > 0 else duration - total_deposit / self.deposit_speed

    def set_target_location(self, location):
        """
        Définit la position cible de l'humain.

        Paramètres:
        -----------
        location : Point
            La position cible de l'humain.
        """
        self.target_location = location
        self.go_to_location(self.target_location)

    def set_target_entity(self, entity):
        """
        Définit l'entité cible de l'humain.

        Paramètres:
        -----------
        entity : Entity
            L'entité cible de l'humain.
        """
        self.target_entity = entity
        self.go_to_location(self.target_entity.current_location)

    def create_path(self, location):
        """
        Crée un chemin entre la position actuelle de l'humain et une position donnée.

        Paramètres:
        -----------
        location : Point
            La position cible de l'humain.
        """
        self.path = AStar(self.current_location // Map.CELL_SIZE, location, self.map)
        if self.path is None:
            self.path = [self.current_location]
        else:
            if len(self.path) > 1:
                self.path[0] = self.current_location
            self.path[-1] = self.path[-1] + Point(uniform(-1, 1), uniform(-1, 1)) * Map.CELL_SIZE
        
    def go_to_location(self, location):
        """
        Déplace l'humain vers une position donnée et on met à jour ses statuts en fonction.

        Paramètres:
        -----------
        location : Point
            La position cible de l'humain.
        """
        # On enlève l'humain du bâtiment où il travaillait
        if self.work == HumanWork.BUILDING:
            building = self.map.occupied_coords.get(self.building_location, None)
            if building is not None:
                building.addWorkers(-1)

        self.progression = 0
        struct = self.map.occupied_coords.get(location, None)
        if struct is None:
            # Si la position cible est vide, on se déplace vers cette position, sans travail
            self.state = HumanState.MOVING
            self.work = HumanWork.IDLE
        else:
            # Si la position cible est occupée, on met à jour le travail de l'humain en fonction de la structure
            self.state = HumanState.WORKING
            self.going_to_work = True
            if struct.structure_type == StructureType.BUILDING:
                # Si la structure est un bâtiment
                self.going_to_target = False
                if struct.player == self.player:
                    # Si le bâtiment appartient au joueur, on construit le bâtiment si il n'est pas construit, sinon si il est construit, on travaille dedans si c'est une ferme
                    if struct.state == BuildingState.PLACED or struct.state == BuildingState.BUILDING:
                        self.work = HumanWork.BUILDING
                        self.building_location = location
                    else:
                        if struct.type == BuildingType.FARM:
                            self.work = HumanWork.GATHERING
                            self.gather_state = GatherState.GATHERING
                            self.ressource_type = RessourceType.FOOD
                            self.going_to_target = True
                            self.building_location, _ = self.find_nearest_building([BuildingType.BASE_CAMP, BuildingType.PANTRY])
                        else:
                            self.building_location = location
                else:
                    # Si le bâtiment n'appartient pas au joueur, on détruit le bâtiment
                    self.work = HumanWork.DESTROYING
                    self.target_location = location
            elif struct.structure_type == StructureType.ORE and (
                    (struct.type == OreType.VULCAN or struct.type == OreType.CRYSTAL) and self.player.upgrades.EXTRA_MATERIALS or 
                    (struct.type != OreType.VULCAN and struct.type != OreType.CRYSTAL)):
                # Si la structure est un minerai qu'il peut exploiter, on récolte le minerai
                self.work = HumanWork.GATHERING
                self.gather_state = GatherState.GATHERING
                self.ressource_type = oreToRessourceType[struct.type]
                self.going_to_target = True
                self.building_location, _ = self.find_nearest_building([BuildingType.BASE_CAMP, BuildingType.MINER_CAMP])
            elif struct.structure_type == StructureType.TREE:
                # Si la structure est un arbre, on récolte le bois
                self.work = HumanWork.GATHERING
                self.gather_state = GatherState.GATHERING
                self.ressource_type = RessourceType.WOOD
                self.going_to_target = True
                self.building_location, _ = self.find_nearest_building([BuildingType.BASE_CAMP, BuildingType.LUMBER_CAMP])
        self.create_path(location)

    def update(self, duration):
        """
        Met à jour l'humain pendant une durée donnée.

        Paramètres:
        -----------
        duration : int
            La durée de la mise à jour.
        """
        # On dépkace d'abord l'humain
        result = False
        if self.state != HumanState.IDLE:
            position = self.current_location
            if self.state == HumanState.MOVING or self.going_to_work:
                duration = self.move(duration)
                if duration > 0:
                    if self.work != HumanWork.IDLE:
                        self.going_to_work = False
                        if self.work == HumanWork.BUILDING:
                            building = self.map.occupied_coords.get(self.building_location, None)
                            if building is not None:
                                building.addWorkers(1)
                    else:
                        self.state = HumanState.IDLE
                        duration = 0

            # Boucle de travail jusqu'à ce que la durée soit écoulée
            while duration > 0:
                if self.state == HumanState.WORKING:
                    if self.going_to_deposit:
                        duration = self.move(duration)
                        if duration > 0:
                            self.going_to_deposit = False
                    elif self.work == HumanWork.GATHERING:
                        if self.gather_state == GatherState.GATHERING:
                            duration = self.gather_resources(duration)
                            if duration > 0:
                                self.going_to_deposit = True
                                self.gather_state = GatherState.DEPOSITING
                                self.going_to_target = False
                                self.go_to_location(self.building_location)
                        else:
                            duration = self.deposit_resources(duration)
                            if duration > 0:
                                self.gather_state = GatherState.GATHERING
                                self.going_to_target = True
                                self.go_to_location(self.target_location)
                    elif self.work == HumanWork.DESTROYING:
                        struct = self.map.occupied_coords.get(self.target_location, None)
                        if struct is not None and struct.structure_type == StructureType.BUILDING:
                            struct.destroy(duration * self.gathering_speed)
                            self.state = HumanState.IDLE
                            duration = 0                            
                    elif self.work == HumanWork.BUILDING:
                        duration = 0
                    elif self.work == HumanWork.HUNTING or self.work == HumanWork.FIGHTING:
                        if self.work == HumanWork.FIGHTING:
                            if self.target_entity.health > 0:
                                if self.target_entity.current_location.distance(self.current_location) <= Map.CELL_SIZE * 2:
                                    if self.target_entity.take_damage(self.damage):
                                        self.state = HumanState.IDLE
                                        self.work = HumanWork.IDLE
                                        self.target_entity = None
                                        duration = 0
                                else:
                                    self.create_path(self.target_entity.current_location)
                            else:
                                self.state = HumanState.IDLE
                                self.work = HumanWork.IDLE
                                self.target_entity = None
                                duration = 0
                else:
                    duration = self.move(duration)
                    if duration > 0 and self.work != HumanWork.IDLE:
                        self.go_to_location(self.target_location if self.going_to_target else self.building_location)
                        self.going_to_work = False
            result = self.current_location != position
        return result
    
    def stop(self):
        """
        Arrête l'humain.
        """
        self.state = HumanState.IDLE
        self.work = HumanWork.IDLE
        self.going_to_work = False
        self.going_to_target = False

    def take_damage(self, damage):
        """
        Inflige des dégâts à l'humain.

        Paramètres:
        -----------
        damage : int
            Les dégâts infligés.
        """
        self.health -= damage
        dead = self.health <= 0
        if dead:
            self.death_callback(self)
        return dead

# Différentes classes d'humains, héritant de la classe Human et sont spécialisées sauf pour la classe Colon
class Colon(Human):
    def __init__(self, map, location, player, death_callback):
        super().__init__(500, HumanType.COLON, 10, 2, 50, 2, map, location, player, death_callback)

class Miner(Human):
    def __init__(self, map, location, player, death_callback):
        super().__init__(600, HumanType.MINER, 10, 2, 50, 2, map, location, player, death_callback)

class Lumberjack(Human):
    def __init__(self, map, location, player, death_callback):
        super().__init__(600, HumanType.LUMBERJACK, 10, 2, 60, 2, map, location, player, death_callback)

class Farmer(Human):
    def __init__(self, map, location, player, death_callback):
        super().__init__(600, HumanType.FARMER, 10, 2, 50, 2, map, location, player, death_callback)

class Hunter(Human):
    def __init__(self, map, location, player, death_callback):
        super().__init__(600, HumanType.HUNTER, 10, 2, 75, 2, map, location, player, death_callback)

class Soldier(Human):
    def __init__(self, map, location, player, death_callback):
        super().__init__(600, HumanType.SOLDIER, 5, 1, 100, 3, map, location, player, death_callback)

human_type_class = {
    HumanType.COLON: Colon,
    HumanType.MINER: Miner,
    HumanType.LUMBERJACK: Lumberjack,
    HumanType.FARMER: Farmer,
    HumanType.HUNTER: Hunter,
    HumanType.SOLDIER: Soldier
}

def get_human_class_from_type(human_type):
    """
    Retourne la classe d'un humain en fonction de son type.

    Paramètres:
    -----------
    human_type : HumanType
        Le type de l'humain.
    """
    return human_type_class[human_type]