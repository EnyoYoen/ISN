from enum import Enum
from math import inf
import random

import matplotlib.pyplot as plt
import numpy as np

from model.Perlin import Perlin
from model.Structures import BuildingState, StructureType, Tree, Ore, OreType
from model.Geometry import Point, Rectangle


class Biomes(Enum):
    """
    Enumération des biomes
    """
    LAVA = 1
    VOLCANO = 2
    DESERT = 3
    PLAIN = 4
    TUNDRA = 5
    MUSHROOM_FOREST = 6
    OASIS = 7
    SWAMP = 8
    FOREST = 9
    MOUNTAIN = 10
    SNOWY_PEAK = 11
    OCEAN = 12
    BEACH = 13
    ICE_FLOE = 14

class Map:
    """
    La carte du jeu.

    Attributs:
    ----------
    perlin_temperature : Perlin
        Le générateur de bruit de Perlin pour la température.
    perlin_humidity : Perlin
        Le générateur de bruit de Perlin pour l'humidité.
    map_chunks : dict
        Les chunks de la carte.
    trees : dict
        Les arbres sur la carte.
    ores : dict
        Les minerais sur la carte.
    buildings : list
        Les bâtiments sur la carte.
    building_type : dict
        Les bâtiments par type.
    occupied_coords : dict
        Les coordonnées occupées sur la carte.
    chunk_humans : dict
        Les humains par chunk.
    humans : list
        Les humains sur la carte.
    chunk_occupied_coords : dict
        Les coordonnées occupées par chunk.
    temp_humi_biomes : dict
        Les biomes par température et humidité.
    """

    __slots__ = ["perlin_temperature", "perlin_humidity", "map_chunks", "trees", "ores", "buildings", "building_type", "structures", "occupied_coords", "chunk_humans", "humans", "chunk_occupied_coords", "temp_humi_biomes"]

    CELL_SIZE = 30

    def __init__(self, seed = 1) -> None:
        # Initialisation des générateurs de bruit de Perlin
        self.perlin_temperature = Perlin(seed, 4, 2, 1, 50, 1)
        self.perlin_humidity = Perlin(seed + 10, 4, 2, 1, 50, 1)

        # Initialisation des attributs
        self.map_chunks = {}
        self.trees = {} # {Point (chunk coords): [Point]}
        self.ores = {} # {Point (chunk coords): {OreType: [Point]}}
        self.buildings = []
        self.building_type = {} # {StructureType: Structure}
        self.occupied_coords = {} # {Point: Structure}
        self.chunk_humans = {} # {Point (chunk coords): [Humans]}
        self.humans = []
        self.chunk_occupied_coords = {} # {Point (chunk coords): [Point]}

        self.temp_humi_biomes = { # Rectangle(min_humi, min_temp, max_humi, max_temp): Biome
            Rectangle(-inf,  3  , -2  ,  inf): Biomes.LAVA,
            Rectangle(-inf,  2  , -2  ,  3  ): Biomes.VOLCANO,
            Rectangle(-inf,  0.5, -2  ,  2  ): Biomes.DESERT,
            Rectangle(-inf, -2.5, -2  ,  0.5): Biomes.PLAIN,
            Rectangle(-inf, -inf, -2  , -2.5): Biomes.TUNDRA,
            Rectangle(-2  ,  2.5,  3  ,  inf): Biomes.MUSHROOM_FOREST,
            Rectangle(-2  ,  1  ,  1  ,  2.5): Biomes.OASIS,
            Rectangle( 1  ,  1  ,  3  ,  2.5): Biomes.SWAMP,
            Rectangle(-2  , -1  ,  2  ,  1  ): Biomes.FOREST,
            Rectangle(-2  , -2.5,  2  , -1  ): Biomes.MOUNTAIN,
            Rectangle(-2  , -inf,  2  , -2.5): Biomes.SNOWY_PEAK,
            Rectangle( 3  , -2.5,  inf,  inf): Biomes.OCEAN,
            Rectangle( 2  , -2.5,  3  ,  1  ): Biomes.BEACH,
            Rectangle( 2  , -inf,  inf, -2.5): Biomes.ICE_FLOE
        }
    
    def try_generate_tree(self, chunk_coords, position, treshold, search_area_size, tree_count_treshold):
        """
        Essaie de générer un arbre à une position donnée.

        Paramètres:
        -----------
        chunk_coords (Point):
            Les coordonnées du chunk.
        position (Point):
            La position de l'arbre dans le chunk.
        treshold (float):
            Le seuil pour générer un arbre.
        search_area_size (int):
            La taille (en chunks) de la zone de recherche.
        tree_count_treshold (int):
            Le nombre d'arbres maximum dans la zone de recherche.
        """
        # On génére un nombre et si il est inférieur au seuil, on continue de voir si on peut générer un arbre
        if random.random() < treshold:
            # On compte le nombre d'arbres dans la zone de recherche
            trees_count = 0
            values = [0]
            for i in range(1, search_area_size // 2 + 1):
                values.append(-i)
                values.append(i)

            for i in range(search_area_size * search_area_size):
                chunk_trees = self.trees.get(Point(chunk_coords.x + values[i // search_area_size], chunk_coords.y + values[i % search_area_size]), None)
                if chunk_trees != None:
                    trees_count += len(chunk_trees)

            # Si le nombre d'arbres est inférieur au nombre maximal, on génère un arbre
            if trees_count < tree_count_treshold:
                if self.trees.get(chunk_coords, None) == None:
                    self.trees[chunk_coords] = []

                # On vériie si l'arbre peut être placé
                absolute_position = chunk_coords * Perlin.CHUNK_SIZE + position
                tree = Tree(absolute_position, self.tree_chopped_callback)
                found = False
                i = 0
                while not found and i < len(tree.points):
                    if self.occupied_coords.get(tree.points[i] + absolute_position, None) is not None:
                        # Il y a déjà une structure à cet endroit
                        found = True
                    i += 1

                # Si l'arbre peut être placé, on l'ajoute à la carte
                if not found:
                    self.trees[chunk_coords].append(absolute_position)
                    for point in tree.points:
                        self.occupied_coords[absolute_position + point] = tree
                        chunk_pos = (absolute_position + point) // Perlin.CHUNK_SIZE
                        if self.chunk_occupied_coords.get(chunk_pos, None) is None:
                            self.chunk_occupied_coords[chunk_pos] = []
                        self.chunk_occupied_coords[chunk_pos].append(absolute_position + point)

    def try_generate_ore(self, chunk_coords, position, treshold, search_area_size, search_ores, ores_count_treshold, ore_type):
        """
        Essaie de générer un minerai à une position donnée.

        Paramètres:
        -----------
        chunk_coords (Point):
            Les coordonnées du chunk.
        position (Point):
            La position du minerai dans le chunk.
        treshold (float):
            Le seuil pour générer un minerai.
        search_area_size (int):
            La taille (en chunks) de la zone de recherche.
        search_ores (list):
            Les minerais à chercher.
        ores_count_treshold (int):
            Le nombre de minerais maximum dans la zone de recherche.
        ore_type (OreType):
            Le type de minerai à générer.
        """
        # On génére un nombre et si il est inférieur au seuil, on continue de voir si on peut générer un minerai
        if random.random() < treshold:
            # On compte le nombre de minerais dans la zone de recherche
            ores_count = 0
            values = [0]
            for i in range(1, search_area_size // 2 + 1):
                values.append(-i)
                values.append(i)
                
            for i in range(search_area_size * search_area_size):
                chunk_ores = self.ores.get(Point(chunk_coords.x + values[i // search_area_size], chunk_coords.y + values[i % search_area_size]), None)
                if chunk_ores != None:
                    for search_ore in search_ores:
                        actual_chunk_ores = chunk_ores.get(search_ore, None)
                        if actual_chunk_ores != None:
                            ores_count += len(actual_chunk_ores)

            # Si le nombre de minerais est inférieur au nombre maximal, on génère un minerai
            if ores_count < ores_count_treshold:
                if self.ores.get(chunk_coords, None) == None:
                    self.ores[chunk_coords] = {}
                if self.ores[chunk_coords].get(ore_type, None) == None:
                    self.ores[chunk_coords][ore_type] = []

                # On vériie si le minerai peut être placé
                absolute_position = chunk_coords * Perlin.CHUNK_SIZE + position
                ore = Ore(ore_type, absolute_position, self.ore_mined_callback)
                found = False
                i = 0
                while not found and i < len(ore.points):
                    if self.occupied_coords.get(ore.points[i] + absolute_position, None) is not None:
                        # Il y a déjà une structure à cet endroit
                        found = True
                    i += 1

                # Si le minerai peut être placé, on l'ajoute à la carte
                if not found:
                    self.ores[chunk_coords][ore_type].append(absolute_position)
                    for point in ore.points:
                        self.occupied_coords[absolute_position + point] = ore
                        chunk_pos = (absolute_position + point) // Perlin.CHUNK_SIZE
                        if self.chunk_occupied_coords.get(chunk_pos, None) is None:
                            self.chunk_occupied_coords[chunk_pos] = []
                        self.chunk_occupied_coords[chunk_pos].append(absolute_position + point)


    def process_chunk(self, chunk_temperature_data, chunk_humidity_data, chunk_coords):
        """
        Traite un chunk de la carte.

        Paramètres:
        -----------
        chunk_temperature_data (np.array):
            Les données de température du chunk.
        chunk_humidity_data (np.array):
            Les données d'humidité du chunk.
        chunk_coords (Point):
            Les coordonnées du chunk.
        """
        processed_chunk = np.empty((Perlin.CHUNK_SIZE, Perlin.CHUNK_SIZE), dtype=int)
        # On parcourt chaque case du chunk
        for i in range(Perlin.CHUNK_SIZE):
            for j in range(Perlin.CHUNK_SIZE):
                # Ne pas mettre un seuil supérieur à 0.015, cela générera des structures uniquement au début du chunk
                position = Point(i, j)
                height = chunk_temperature_data[i][j]
                # On génère les biomes en fonction de la "température" et on génére les arbres et minerais en fonction du biome
                if height > 4.5:
                    processed_chunk[i][j] = Biomes.SNOWY_PEAK.value
                    self.try_generate_ore(chunk_coords, position, 0.005, 3, [OreType.CRYSTAL], 3, OreType.CRYSTAL)
                elif height > 2.5:
                    processed_chunk[i][j] = Biomes.MOUNTAIN.value
                    self.try_generate_ore(chunk_coords, position, 0.01, 1, [OreType.COPPER], 2, OreType.COPPER)
                elif height > 0:
                    processed_chunk[i][j] = Biomes.FOREST.value
                    self.try_generate_ore(chunk_coords, position, 0.015, 1, [OreType.IRON, OreType.STONE], 2, OreType.IRON)
                    self.try_generate_ore(chunk_coords, position, 0.010, 2, [OreType.COPPER, OreType.IRON, OreType.STONE], 2, OreType.GOLD)
                    self.try_generate_tree(chunk_coords, position, 0.015, 1, 15)
                elif height > -2.75:
                    processed_chunk[i][j] = Biomes.PLAIN.value
                    self.try_generate_ore(chunk_coords, position, 0.015, 1, [OreType.STONE], 2, OreType.STONE)
                    self.try_generate_tree(chunk_coords, position, 0.01, 2, 5)
                elif height > -4:
                    processed_chunk[i][j] = Biomes.VOLCANO.value
                    self.try_generate_ore(chunk_coords, position, 0.005, 5, [OreType.VULCAN], 1, OreType.VULCAN)
                else:
                    processed_chunk[i][j] = Biomes.LAVA.value
        return processed_chunk

    def get_chunk(self, chunk_coords):
        """
        Récupère un chunk de la carte.

        Paramètres:
        -----------
        chunk_coords (Point):
            Les coordonnées du chunk.
        """
        if self.map_chunks.get(chunk_coords, None) is None:
            # On génère le chunk si il n'existe pas
            chunk_temperature = self.perlin_temperature.get_chunk(chunk_coords.x, chunk_coords.y)
            #chunk_humidity = self.perlin_humidity.get_chunk(chunk_coords.x, chunk_coords.y)
            processed_chunk = self.process_chunk(chunk_temperature[0], None, chunk_coords)#chunk_humidity[0], chunk_coords)
            self.map_chunks[chunk_coords] = processed_chunk
        return self.map_chunks[chunk_coords]

    def get_area_around_chunk(self, chunk_coords, width, height):
        """
        Récupère une zone autour d'un chunk.

        Paramètres:
        -----------
        chunk_coords (Point):
            Les coordonnées du chunk.
        width (int):
            La largeur de la zone.
        height (int):
            La hauteur de la zone.
        """
        rows = []
        chunks = []
        for i in range(width):
            for j in range(height):
                # On récupère les chunks autour du chunk
                actual_chunk_coords = Point(chunk_coords.x + i, chunk_coords.y + j)
                chunks.append(self.get_chunk(actual_chunk_coords))
            # On concatène les chunks pour obtenir une ligne
            rows.append(np.concatenate(chunks, axis = 1))
            chunks.clear()

        # On concatène les lignes pour obtenir la zone
        return np.concatenate(rows, axis = 0)

    def try_place_structure(self, structure):
        """
        Essaie de placer une structure sur la carte.

        Paramètres:
        -----------
        structure (Structure):
            La structure à placer.
        """
        center = structure.coords
        i = 0
        l = len(structure.points)
        while i < l and self.occupied_coords.get(center + structure.points[i], None) is None:
            # Il n'y a pas de structure à cet endroit
            i += 1

        # Si i == l, cela signifie qu'il n'y a pas de structure à l'endroit où on veut placer la structure
        return i == l

    def place_structure(self, structure):
        """
        Place une structure sur la carte.

        Paramètres:
        -----------
        structure (Structure):
            La structure à placer.
        """
        # On vérifie si la structure peut être placée
        can_place = self.try_place_structure(structure)
        if can_place:
            # On place la structure
            center = structure.coords
            for relative_point in structure.points:
                absolute_point = center + relative_point
                self.occupied_coords[absolute_point] = structure
                chunk_coords = absolute_point // Perlin.CHUNK_SIZE
                if self.chunk_occupied_coords.get(chunk_coords, None) is None:
                    self.chunk_occupied_coords[chunk_coords] = []
                self.chunk_occupied_coords[chunk_coords].append(absolute_point)

            if structure.structure_type == StructureType.BUILDING:
                self.buildings.append(structure)
                type = structure.type
                if self.building_type.get(type, None) is None:
                    self.building_type[type] = []
                self.building_type[type].append(structure)

        return can_place
    
    def place_human(self, human, map_position):
        """
        Place un humain sur la carte.

        Paramètres:
        -----------
        human (Human):
            L'humain à placer.
        map_position (Point):
            La position de l'humain sur la carte.
        """
        chunk_pos = map_position // Map.CELL_SIZE // Perlin.CHUNK_SIZE
        if self.chunk_humans.get(chunk_pos, None) is None:
            self.chunk_humans[chunk_pos] = []
        self.chunk_humans[chunk_pos].append(human)
        self.humans.append(human)

    def tree_chopped_callback(self, tree):
        """
        Callback appelé lorsqu'un arbre est coupé.

        Paramètres:
        -----------
        tree (Tree):
            L'arbre coupé.
        """
        # On retire l'arbre de la carte
        try:
            self.trees[tree.coords // Perlin.CHUNK_SIZE].remove(tree.coords)
        except ValueError:
            pass

        for point in tree.points:
            try:
                actual_chunk_pos = (tree.coords + point) // Perlin.CHUNK_SIZE
                self.occupied_coords.pop(tree.coords + point)
                self.chunk_occupied_coords[actual_chunk_pos].remove(tree.coords + point)
            except Exception:
                pass
    
    def ore_mined_callback(self, ore):
        """
        Callback appelé lorsqu'un minerai est miné entièrement.

        Paramètres:
        -----------
        ore (Ore):
            Le minerai miné.
        """
        # On retire le minerai de la carte
        try:
            self.ores[ore.coords // Perlin.CHUNK_SIZE][ore.type].remove(ore.coords)
        except ValueError:
            pass

        for point in ore.points:
            try:
                actual_chunk_pos = (ore.coords + point) // Perlin.CHUNK_SIZE
                self.occupied_coords.pop(ore.coords + point)
                self.chunk_occupied_coords[actual_chunk_pos].remove(ore.coords + point)
            except Exception:
                pass

    def remove_building(self, building):
        """
        Supprime un bâtiment de la carte.

        Paramètres:
        -----------
        building (Building):
            Le bâtiment à supprimer.
        """
        self.buildings.remove(building)
        self.building_type[building.type].remove(building)
        for point in building.points:
            self.occupied_coords.pop(building.coords + point)
            actual_chunk_pos = (building.coords + point) // Perlin.CHUNK_SIZE
            self.chunk_occupied_coords[actual_chunk_pos].remove(building.coords + point)

    def remove_human(self, human):
        """
        Supprime un humain de la carte.

        Paramètres:
        -----------
        human (Human):
            L'humain à supprimer.
        """
        self.humans.remove(human)
        self.chunk_humans[human.current_location // Map.CELL_SIZE // Perlin.CHUNK_SIZE].remove(human)

    def update(self, duration):
        """
        Met à jour la carte.

        Paramètres:
        -----------
        duration (float):
            La durée de la mise à jour.
        """
        need_render = False

        # On met à jour les bâtiments
        for building in self.buildings:
            if building.update(duration):
                need_render = True

        # On met à jour les humains
        chunk_humans = self.chunk_humans.copy()
        for chunk_coords, humans in self.chunk_humans.items():
            for human in humans:
                if human.update(duration):
                    need_render = True
                    new_chunk_coords = human.current_location // Map.CELL_SIZE // Perlin.CHUNK_SIZE
                    if new_chunk_coords != chunk_coords:
                        if chunk_humans.get(new_chunk_coords, None) is None:
                            chunk_humans[new_chunk_coords] = []
                        chunk_humans[new_chunk_coords].append(human)
                        chunk_humans[chunk_coords].remove(human)
        self.chunk_humans = chunk_humans

        return need_render
