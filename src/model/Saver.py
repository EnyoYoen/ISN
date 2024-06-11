import struct
import os
from datetime import datetime
import numpy as np

from model.Perlin import Perlin
from model.Map import Map
from model.Structures import Structure, StructureType, OreType, Building, BuildingType, BuildingState, Tree, Ore, Orientation, typeToClass
from model.Geometry import Point
from model.Player import Player
from model.Human import Human, HumanType, HumanState, HumanWork, GatherState, RessourceType, get_human_class_from_type
from model.Upgrades import Upgrades
from model.Tools import Directions

class Saver:
    """
    Classe permettant de sauvegarder et de charger une partie.

    Attributs:
    ----------
    game_vue : GameVue
        L'objet du jeu.
    save_name : str
        Le nom de la sauvegarde.
    """

    __slots__ = ["game_vue", "save_name"]

    def __init__(self, game_vue, save_name = None) -> None:
        # On initialise les attributs de la sauvegarde
        self.game_vue = game_vue
        # On initialise le nom de la sauvegarde si il n'est pas donné
        if save_name is None:
            self.save_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        else:
            self.save_name = save_name

    def save(self):
        """
        Sauvegarde de la partie.
        """

        # On crée le dossier de sauvegarde si il n'existe pas
        saves_directory = "saves"
        if not os.path.exists(saves_directory):
            os.makedirs(saves_directory)

        # On crée le dossier de sauvegarde de la partie
        save_dir = os.path.join(saves_directory, self.save_name)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # On sauvegarde les données dans un fichier binaire
        map = self.game_vue.map
        signature = [77, 65, 80, 00] # 'MAP_' in ASCII
        with open(f"saves/{self.save_name}/map.exd", "wb") as f:
            ## MAP
            # Signature
            for b in signature:
                f.write(struct.pack('B', b))
            
            # Map seed
            f.write(struct.pack('i', map.perlin_temperature.seed))
            
            # Chunks
            f.write(struct.pack('i', Perlin.CHUNK_SIZE))
            f.write(struct.pack('i', len(map.map_chunks)))
            for chunk_coords, chunk in map.map_chunks.items():
                f.write(struct.pack('ii', chunk_coords.x, chunk_coords.y))
                f.write(struct.pack('i', len(chunk)))
                for row in chunk:
                    for value in row:
                        f.write(struct.pack('B', value))

            # Player
            self.save_player(f, self.game_vue.player)

            # Trees
            f.write(struct.pack('i', len(map.trees)))
            for chunk_coords, trees in map.trees.items():
                f.write(struct.pack('ii', chunk_coords.x, chunk_coords.y))
                f.write(struct.pack('i', len(trees)))
                for tree in trees:
                    f.write(struct.pack('ii', tree.x, tree.y))
            
            # Ores
            f.write(struct.pack('i', len(map.ores)))
            for chunk_coords, ores in map.ores.items():
                f.write(struct.pack('ii', chunk_coords.x, chunk_coords.y))
                f.write(struct.pack('i', len(ores)))
                for ore_type, ore in ores.items():
                    f.write(struct.pack('B', ore_type.value))
                    f.write(struct.pack('i', len(ore)))
                    for point in ore:
                        f.write(struct.pack('ii', point.x, point.y))

            structs = {}

            # Buildings
            f.write(struct.pack('i', len(map.buildings)))
            for building in map.buildings:
                self.save_building(f, building)
                structs[building.sid] = True

            # Buildings by types
            f.write(struct.pack('i', len(map.building_type)))
            for building_type, buildings in map.building_type.items():
                f.write(struct.pack('B', building_type.value))
                f.write(struct.pack('i', len(buildings)))
                for building in buildings:
                    f.write(struct.pack('i', building.sid))

            # Occupied coords
            f.write(struct.pack('i', len(map.occupied_coords)))
            for coord, structure in map.occupied_coords.items():
                f.write(struct.pack('ii', int(coord.x), int(coord.y)))
                f.write(struct.pack('i', structure.sid))
                if not structs.get(structure.sid, False): 
                    structs[structure.sid] = True

                    f.write(struct.pack('B', structure.structure_type.value))
                    if structure.structure_type == StructureType.BUILDING:
                        self.save_building(f, structure)
                    elif structure.structure_type == StructureType.TREE:
                        self.save_tree(f, structure)
                    elif structure.structure_type == StructureType.ORE:
                        self.save_ore(f, structure)

            # Chunk occupied coords
            f.write(struct.pack('i', len(map.chunk_occupied_coords)))
            for coord, points in map.chunk_occupied_coords.items():
                f.write(struct.pack('ii', coord.x, coord.y))
                f.write(struct.pack('i', len(points)))
                for point in points:
                    f.write(struct.pack('ii', int(point.x), int(point.y)))
            
            # Humans
            f.write(struct.pack('i', len(map.humans)))
            for human in map.humans:
                    self.save_human(f, human)

            # Humans by chunks
            f.write(struct.pack('i', len(map.chunk_humans)))
            for chunk_coords, humans in map.chunk_humans.items():
                f.write(struct.pack('ff', int(chunk_coords.x), int(chunk_coords.y)))
                f.write(struct.pack('i', len(humans)))
                for human in humans:
                    f.write(struct.pack('i', human.hid))

            ## GAMEVUE
            f.write(struct.pack('ff', self.game_vue.camera_pos.x, self.game_vue.camera_pos.y))

    def save_sructure(self, f, structure):
        """
        Sauvegarde une structure dans un fichier binaire.

        Parametres:
        -----------
        f : file
            Le fichier binaire.
        structure : Structure
            La structure à sauvegarder.
        """
        f.write(struct.pack('i', structure.sid))
        f.write(struct.pack('B', structure.structure_type.value))
        f.write(struct.pack('ii', int(structure.coords.x), int(structure.coords.y)))
        f.write(struct.pack('B', structure.orientation.value))
        f.write(struct.pack('i', len(structure.points)))
        for point in structure.points:
            f.write(struct.pack('ii', point.x, point.y))

    def save_typed_structure(self, f, structure):
        """
        Sauvegarde une structure typée dans un fichier binaire.

        Parametres:
        -----------
        f : file
            Le fichier binaire.
        structure : Structure
            La structure à sauvegarder.
        """
        self.save_sructure(f, structure)
        f.write(struct.pack('B', structure.type.value))

    def save_building(self, f, building):
        """
        Sauvegarde un bâtiment dans un fichier binaire.

        Parametres:
        -----------
        f : file
            Le fichier binaire.
        building : Building
            Le bâtiment à sauvegarder.
        """
        self.save_typed_structure(f, building)
        f.write(struct.pack('i', building.player.pid))
        f.write(struct.pack('f', building.health))
        f.write(struct.pack('f', building.building_time))
        f.write(struct.pack('f', building.building_duration))
        f.write(struct.pack('i', building.workers))
        f.write(struct.pack('ii', building.upper_left.x, building.upper_left.y))
        f.write(struct.pack('ii', building.rect_size.x, building.rect_size.y))
        f.write(struct.pack('B', building.state.value))
        f.write(struct.pack('B', building.gamevue is not None))

    def save_tree(self, f, tree):
        """
        Sauvegarde un arbre dans un fichier binaire.

        Parametres:
        -----------
        f : file
            Le fichier binaire.
        tree : Tree
            L'arbre à sauvegarder.
        """
        self.save_sructure(f, tree)
        f.write(struct.pack('f', tree.health))

    def save_ore(self, f, ore):
        """
        Sauvegarde une veine de minerai dans un fichier binaire.

        Parametres:
        -----------
        f : file
            Le fichier binaire.
        ore : Ore
            La veine de minerai à sauvegarder.
        """
        self.save_typed_structure(f, ore)

    def save_human(self, f, human):
        """
        Sauvegarde un humain dans un fichier binaire.
        
        Parametres:
        -----------
        f : file
            Le fichier binaire.
        human : Human
            L'humain à sauvegarder.
        """
        f.write(struct.pack('B', human.type.value))
        f.write(struct.pack('ff', human.current_location.x, human.current_location.y))
        f.write(struct.pack('i', human.player.pid))
        f.write(struct.pack('B', human.state.value))
        f.write(struct.pack('B', human.work.value))
        f.write(struct.pack('B', human.gather_state.value))
        f.write(struct.pack('B', human.orientation.value))
        f.write(struct.pack('B', human.going_to_work))
        f.write(struct.pack('B', human.going_to_target))
        f.write(struct.pack('B', human.going_to_deposit))
        
        f.write(struct.pack('B', human.target_location is not None))
        if human.target_location is not None:
            f.write(struct.pack('ff', human.target_location.x, human.target_location.y))
        else:
            f.write(struct.pack('ff', -1, -1))
        
        f.write(struct.pack('B', human.building_location is not None))
        if human.building_location is not None:
            f.write(struct.pack('ff', human.building_location.x, human.building_location.y))
        else:
            f.write(struct.pack('ff', -1, -1))
        
        f.write(struct.pack('B', human.target_entity is not None))
        if human.target_entity is not None:
            f.write(struct.pack('i', human.target_entity.hid))
        else:
            f.write(struct.pack('i', -1))
        
        f.write(struct.pack('B', human.path is not None))
        if human.path is None:
            f.write(struct.pack('i', 0))
        else:
            f.write(struct.pack('i', len(human.path)))
            for point in human.path:
                f.write(struct.pack('ff', point.x, point.y))
        
        f.write(struct.pack('i', human.resource_capacity))
        f.write(struct.pack('i', human.gathering_speed))
        f.write(struct.pack('i', human.damage))
        f.write(struct.pack('i', human.ressource_type.value if human.ressource_type is not None else 0))
        f.write(struct.pack('i', human.deposit_speed))
        f.write(struct.pack('i', human.speed))
        f.write(struct.pack('f', human.progression))
        f.write(struct.pack('i', human.hid))
        f.write(struct.pack('i', len(human.ressources)))
        for ressource_type, quantity in human.ressources.items():
            f.write(struct.pack('B', ressource_type.value))
            f.write(struct.pack('f', quantity))

    def save_player(self, f, player):
        """
        Sauvegarde un joueur dans un fichier binaire.

        Parametres:
        -----------
        f : file
            Le fichier binaire.
        player : Player
            Le joueur à sauvegarder.
        """
        f.write(struct.pack('i', player.pid))
        f.write(struct.pack('i', len(player.ressources)))
        for ressource_type, quantity in player.ressources.items():
            f.write(struct.pack('B', ressource_type.value))
            f.write(struct.pack('f', quantity))
        self.save_upgrades(f, player.upgrades)

    def save_upgrades(self, f, upgrades):
        """
        Sauvegarde les améliorations d'un joueur dans un fichier binaire.

        Parametres:
        -----------
        f : file
            Le fichier binaire.
        upgrades : Upgrades
            Les améliorations du joueur à sauvegarder.
        """
        f.write(struct.pack('B', upgrades.EXTRA_MATERIALS))
        f.write(struct.pack('B', upgrades.FOOD_MULTIPLIER))
        f.write(struct.pack('B', upgrades.MINING_MULTIPLIER))
        f.write(struct.pack('B', upgrades.WOOD_MULTIPLIER))
        f.write(struct.pack('B', upgrades.HUNT_MULTIPLIER))
        f.write(struct.pack('B', upgrades.COMBAT_MULTIPLIER))
        f.write(struct.pack('B', upgrades.BUILDING_HEALTH_MULTIPLIER))
        f.write(struct.pack('B', upgrades.BUILDING_TIME_MULTIPLIER))



    def load(self):
        """
        Charge une partie.
        """
        signature = [77, 65, 80, 00] # 'MAP_' in ASCII
        with open(f"saves/{self.save_name}/map.exd", "rb") as f:
            # On vérifie la signature
            file_signature = list(struct.unpack('BBBB', f.read(4)))
            if file_signature != signature:
                raise ValueError("Invalid file format")
            
            map = self.game_vue.map
            
            # Map seed
            map.perlin_temperature.set_seed(struct.unpack('i', f.read(4))[0])

            # Chunks
            Perlin.CHUNK_SIZE = struct.unpack('i', f.read(4))[0]
            for _ in range(struct.unpack('i', f.read(4))[0]):
                chunk_coords = Point(struct.unpack('i', f.read(4))[0], struct.unpack('i', f.read(4))[0])
                len_chunk = struct.unpack('i', f.read(4))[0]
                chunk = np.empty((Perlin.CHUNK_SIZE, Perlin.CHUNK_SIZE), dtype=int)
                for i in range(Perlin.CHUNK_SIZE):
                    for j in range(Perlin.CHUNK_SIZE):
                        chunk[i, j] = struct.unpack('B', f.read(1))[0]
                map.map_chunks[chunk_coords] = chunk

            players = {}

            # Player
            self.load_player(f, self.game_vue.player)
            players[self.game_vue.player.pid] = self.game_vue.player

            # Trees
            for _ in range(struct.unpack('i', f.read(4))[0]):
                chunk_coords = Point(struct.unpack('i', f.read(4))[0], struct.unpack('i', f.read(4))[0])
                trees = []
                for _ in range(struct.unpack('i', f.read(4))[0]):
                    tree = Point(struct.unpack('i', f.read(4))[0], struct.unpack('i', f.read(4))[0])
                    trees.append(tree)
                map.trees[chunk_coords] = trees

            # Ores
            for _ in range(struct.unpack('i', f.read(4))[0]):
                chunk_coords = Point(struct.unpack('i', f.read(4))[0], struct.unpack('i', f.read(4))[0])
                ores = {}
                for _ in range(struct.unpack('i', f.read(4))[0]):
                    ore_type = OreType(struct.unpack('B', f.read(1))[0])
                    ore = []
                    for _ in range(struct.unpack('i', f.read(4))[0]):
                        point = Point(struct.unpack('i', f.read(4))[0], struct.unpack('i', f.read(4))[0])
                        ore.append(point)
                    ores[ore_type] = ore
                map.ores[chunk_coords] = ores

            structs = {}

            # Buildings
            for _ in range(struct.unpack('i', f.read(4))[0]):
                building = self.load_building(f, players)
                map.buildings.append(building)
                structs[building.sid] = building

            # Buildings by types
            for _ in range(struct.unpack('i', f.read(4))[0]):
                building_type = BuildingType(struct.unpack('B', f.read(1))[0])
                buildings = []
                for _ in range(struct.unpack('i', f.read(4))[0]):
                    building = structs[struct.unpack('i', f.read(4))[0]]
                    buildings.append(building)
                map.building_type[building_type] = buildings
            
            # Occupied coords
            l = struct.unpack('i', f.read(4))[0]
            for _ in range(l):
                coords = Point(struct.unpack('i', f.read(4))[0], struct.unpack('i', f.read(4))[0])
                sid = struct.unpack('i', f.read(4))[0]
                if sid in structs:
                    structure = structs[sid]
                else:
                    structure_type = StructureType(struct.unpack('B', f.read(1))[0])
                    if structure_type == StructureType.BUILDING:
                        structure = self.load_building(f, players)
                    elif structure_type == StructureType.TREE:
                        structure = self.load_tree(f)
                    elif structure_type == StructureType.ORE:
                        structure = self.load_ore(f)
                    structs[sid] = structure
                map.occupied_coords[coords] = structure

            # Chunk occupied coords
            for _ in range(struct.unpack('i', f.read(4))[0]):
                coords = Point(struct.unpack('i', f.read(4))[0], struct.unpack('i', f.read(4))[0])
                points = []
                for _ in range(struct.unpack('i', f.read(4))[0]):
                    point = Point(struct.unpack('i', f.read(4))[0], struct.unpack('i', f.read(4))[0])
                    points.append(point)
                map.chunk_occupied_coords[coords] = points

            humans = {}

            # Humans
            l = struct.unpack('i', f.read(4))[0]
            for _ in range(l):
                human = self.load_human(f, players)
                map.humans.append(human)
                humans[human.hid] = human
            
            # Humans by chunks
            for _ in range(struct.unpack('i', f.read(4))[0]):
                chunk_coords = Point(struct.unpack('f', f.read(4))[0], struct.unpack('f', f.read(4))[0])
                humans_map = []
                for _ in range(struct.unpack('i', f.read(4))[0]):
                    human = humans[struct.unpack('i', f.read(4))[0]]
                    humans_map.append(human)
                map.chunk_humans[chunk_coords] = humans_map

            ## GAMEVUE
            self.game_vue.camera_pos = Point(struct.unpack('f', f.read(4))[0], struct.unpack('f', f.read(4))[0])

    def load_structure(self, f):
        """
        Charge une structure depuis un fichier binaire.

        Parametres:
        -----------
        f : file
            Le fichier binaire.
        """
        sid = struct.unpack('i', f.read(4))[0]
        structure_type = StructureType(struct.unpack('B', f.read(1))[0])
        coords = Point(struct.unpack('i', f.read(4))[0], struct.unpack('i', f.read(4))[0])
        orientation = struct.unpack('B', f.read(1))[0]
        points = []
        for _ in range(struct.unpack('i', f.read(4))[0]):
            point = Point(struct.unpack('i', f.read(4))[0], struct.unpack('i', f.read(4))[0])
            points.append(point)
        return [sid, structure_type, coords, orientation, points]

    def load_typed_structure(self, f):
        """
        Charge une structure typée depuis un fichier binaire.

        Parametres:
        -----------
        f : file
            Le fichier binaire.
        """
        ts = self.load_structure(f)
        ts.append(struct.unpack('B', f.read(1))[0])
        return ts

    def load_building(self, f, players):
        """
        Charge un bâtiment depuis un fichier binaire.

        Parametres:
        -----------
        f : file
            Le fichier binaire.
        players : dict
            Les joueurs de la partie.
        """
        b = self.load_typed_structure(f)
        player = players[struct.unpack('i', f.read(4))[0]]
        type = BuildingType(b[5])
        building = typeToClass[type](b[2], player, self.game_vue.building_destroyed_callback, self.game_vue.human_died_callback, Orientation(b[3]))
        building.sid = b[0]
        building.type = type
        building.health = struct.unpack('f', f.read(4))[0]
        building.building_time = struct.unpack('f', f.read(4))[0]
        building.building_duration = struct.unpack('f', f.read(4))[0]
        building.workers = struct.unpack('i', f.read(4))[0]
        building.upper_left = Point(struct.unpack('i', f.read(4))[0], struct.unpack('i', f.read(4))[0])
        building.rect_size = Point(struct.unpack('i', f.read(4))[0], struct.unpack('i', f.read(4))[0])
        building.state = BuildingState(struct.unpack('B', f.read(1))[0])
        building.gamevue = self.game_vue if struct.unpack('B', f.read(1))[0] else None

        return building

    def load_tree(self, f):
        """
        Charge un arbre depuis un fichier binaire.

        Parametres:
        -----------
        f : file
            Le fichier binaire.
        """
        t = self.load_structure(f)
        tree = Tree(t[2], self.game_vue.map.tree_chopped_callback, Orientation(t[3]))
        tree.sid = t[0]
        tree.health = struct.unpack('f', f.read(4))[0]
        return tree
    
    def load_ore(self, f):
        """
        Charge une veine de minerai depuis un fichier binaire.

        Parametres:
        -----------
        f : file
            Le fichier binaire.
        """
        o = self.load_typed_structure(f)
        ore = Ore(OreType(o[5]), o[2], self.game_vue.map.ore_mined_callback, Orientation(o[3]))
        ore.sid = o[0]
        return ore
    
    def load_human(self, f, players):
        """
        Charge un humain depuis un fichier binaire.

        Parametres:
        -----------
        f : file
            Le fichier binaire.
        players : dict
            Les joueurs de la partie.
        """
        type = HumanType(struct.unpack('B', f.read(1))[0])
        location = Point(struct.unpack('f', f.read(4))[0], struct.unpack('f', f.read(4))[0])
        player = players[struct.unpack('i', f.read(4))[0]]

        h = get_human_class_from_type(type)(self.game_vue.map, location, player, self.game_vue.human_died_callback)
        h.current_location = location
        h.state = HumanState(struct.unpack('B', f.read(1))[0])
        h.work = HumanWork(struct.unpack('B', f.read(1))[0])
        h.gather_state = GatherState(struct.unpack('B', f.read(1))[0])
        h.orientation = Directions(struct.unpack('B', f.read(1))[0])
        h.going_to_work = struct.unpack('B', f.read(1))[0]
        h.going_to_target = struct.unpack('B', f.read(1))[0]
        h.going_to_deposit = struct.unpack('B', f.read(1))[0]

        if struct.unpack('B', f.read(1))[0]:
            h.target_location = Point(struct.unpack('f', f.read(4))[0], struct.unpack('f', f.read(4))[0])
        else:
            f.read(8)
            h.target_location = None
        
        if struct.unpack('B', f.read(1))[0]:
            h.building_location = Point(struct.unpack('f', f.read(4))[0], struct.unpack('f', f.read(4))[0])
        else:
            f.read(8)
            h.building_location = None
        
        if struct.unpack('B', f.read(1))[0]:
            # TODO : loop over the humans to find the target entity after loading them
            h.target_entity = struct.unpack('i', f.read(4))[0]
        else:
            f.read(4)
            h.target_entity = None
        
        if struct.unpack('B', f.read(1))[0]:
            h.path = []
            l = struct.unpack('i', f.read(4))[0]
            for _ in range(l):
                point = Point(struct.unpack('f', f.read(4))[0], struct.unpack('f', f.read(4))[0])
                h.path.append(point)
            if len(h.path) == 0:
                h.path = None
        else:
            h.path = None
            f.read(4)
        h.resource_capacity = struct.unpack('i', f.read(4))[0]
        h.gathering_speed = struct.unpack('i', f.read(4))[0]
        h.damage = struct.unpack('i', f.read(4))[0]
        ressource_type = struct.unpack('i', f.read(4))[0]
        h.ressource_type = RessourceType(ressource_type) if ressource_type != 0 else None
        h.deposit_speed = struct.unpack('i', f.read(4))[0]
        h.speed = struct.unpack('i', f.read(4))[0]
        h.progression = struct.unpack('f', f.read(4))[0]
        h.hid = struct.unpack('i', f.read(4))[0]
        for _ in range(struct.unpack('i', f.read(4))[0]):
            ressource_type = RessourceType(struct.unpack('B', f.read(1))[0])
            quantity = struct.unpack('f', f.read(4))[0]
            h.ressources[ressource_type] = quantity

        return h

    def load_upgrades(self, f, upgrades):
        """
        Charge les améliorations d'un joueur depuis un fichier binaire.

        Parametres:
        -----------
        f : file
            Le fichier binaire.
        upgrades : Upgrades
            Les améliorations du joueur à charger.
        """
        upgrades.EXTRA_MATERIALS = struct.unpack('B', f.read(1))[0]
        upgrades.FOOD_MULTIPLIER = struct.unpack('B', f.read(1))[0]
        upgrades.MINING_MULTIPLIER = struct.unpack('B', f.read(1))[0]
        upgrades.WOOD_MULTIPLIER = struct.unpack('B', f.read(1))[0]
        upgrades.HUNT_MULTIPLIER = struct.unpack('B', f.read(1))[0]
        upgrades.COMBAT_MULTIPLIER = struct.unpack('B', f.read(1))[0]
        upgrades.BUILDING_HEALTH_MULTIPLIER = struct.unpack('B', f.read(1))[0]
        upgrades.BUILDING_TIME_MULTIPLIER = struct.unpack('B', f.read(1))[0]

    def load_player(self, f, player):
        """
        Charge un joueur depuis un fichier binaire.

        Parametres:
        -----------
        f : file
            Le fichier binaire.
        player : Player
            Le joueur à charger.
        """
        player.pid = struct.unpack('i', f.read(4))[0]
        for _ in range(struct.unpack('i', f.read(4))[0]):
            ressource_type = struct.unpack('B', f.read(1))[0]
            quantity = struct.unpack('f', f.read(4))[0]
            player.ressources[RessourceType(ressource_type)] = quantity
        self.load_upgrades(f, player.upgrades)