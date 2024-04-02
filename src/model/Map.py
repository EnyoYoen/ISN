from enum import Enum
import random

import numpy as np
import matplotlib.pyplot as plt

from Perlin import Perlin

class Biomes(Enum):
    LAVA = 1
    VOLCANO = 2
    PLAIN = 3
    MUSHROOM_FOREST = 4
    DESOLATED_FOREST = 5
    SNOW = 6

class Ores(Enum):
    IRON = 1
    COPPER = 2
    GOLD = 3
    VULCAN = 4
    CRYSTAL = 5

class Map:
    __slots__ = ["perlin", "map_chunks", "ores", "area_size", "x_chunk", "y_chunk"]

    def __init__(self, seed = 1) -> None:
        self.perlin = Perlin(seed, 4, 2, 2, 100, 1)
        self.map_chunks = {}
        self.ores = {} # {(x_chunk, y_chunk): {type: (x, y)}}
        self.area_size = 5 # The size (in chunks) of the area generated by get_area_around_chunk
        self.x_chunk = 0 # TODO : initialize with saved data (if it exists)
        self.y_chunk = 0
    
    def change_chunk_coords(self, x, y):
        self.x_chunk = x
        self.y_chunk = y

    def try_generate_ore(self, x_chunk, y_chunk, x, y, treshold, search_area_size, search_ores, ores_count_treshold, ore_type):
        if random.random() < treshold:
            ores_count = 0
            values = [0]
            for i in range(1, search_area_size // 2 + 1):
                values.append(-i)
                values.append(i)
            for i in range(search_area_size * search_area_size):
                chunk_ores = self.ores.get((x_chunk + values[i // search_area_size], y_chunk + values[i % search_area_size]), None)
                if chunk_ores != None:
                    for search_ore in search_ores:
                        actual_chunk_ores = chunk_ores.get(search_ore, None)
                        if actual_chunk_ores != None:
                            ores_count += len(actual_chunk_ores)
            if ores_count < ores_count_treshold:
                if self.ores.get((x_chunk, y_chunk), None) == None:
                    self.ores[(x_chunk, y_chunk)] = {}
                if self.ores[(x_chunk, y_chunk)].get(ore_type, None) == None:
                    self.ores[(x_chunk, y_chunk)][ore_type] = []
                self.ores[(x_chunk, y_chunk)][ore_type].append((x, y))

    def process_chunk(self, chunk_data, min_height, max_height, x_chunk, y_chunk):
        processed_chunk = np.empty((Perlin.CHUNK_SIZE, Perlin.CHUNK_SIZE))
        for i in range(Perlin.CHUNK_SIZE):
            for j in range(Perlin.CHUNK_SIZE):
                normalized_height = chunk_data[i][j]#(chunk_data[i][j] - min_height) / (max_height - min_height)
                if normalized_height > 3.5:
                    processed_chunk[i][j] = Biomes.SNOW.value
                    self.try_generate_ore(x_chunk, y_chunk, i, j, 0.005, 3, [Ores.CRYSTAL], 3, Ores.CRYSTAL)
                elif normalized_height > 2:
                    processed_chunk[i][j] = Biomes.DESOLATED_FOREST.value
                    self.try_generate_ore(x_chunk, y_chunk, i, j, 0.01, 1, [Ores.COPPER], 2, Ores.COPPER)
                elif normalized_height > 1:
                    processed_chunk[i][j] = Biomes.MUSHROOM_FOREST.value
                elif normalized_height > -2:
                    processed_chunk[i][j] = Biomes.PLAIN.value
                    self.try_generate_ore(x_chunk, y_chunk, i, j, 0.015, 1, [Ores.IRON], 2, Ores.IRON)
                elif normalized_height > -3:
                    processed_chunk[i][j] = Biomes.VOLCANO.value
                    self.try_generate_ore(x_chunk, y_chunk, i, j, 0.005, 5, [Ores.VULCAN], 1, Ores.VULCAN)
                else:
                    processed_chunk[i][j] = Biomes.LAVA.value
        return processed_chunk

    def get_area_around_chunk(self):
        # Get an area of <area_size> x <area_size> chunks around the current chunk, concatenated into one 2D array
        rows = []
        chunks = []
        for i in range(self.area_size * self.area_size):
            actual_chunk_x = self.x_chunk + i // self.area_size - 1
            actual_chunk_y = self.y_chunk + i % self.area_size - 1
            if self.map_chunks.get((actual_chunk_x, actual_chunk_y), None) == None:
                chunk = self.perlin.get_chunk(actual_chunk_x, actual_chunk_y)
                processed_chunk = self.process_chunk(chunk[0], chunk[1], chunk[2], actual_chunk_x, actual_chunk_y)
                self.map_chunks[actual_chunk_x, actual_chunk_y] = processed_chunk

            # Temporary
            complete_chunk = self.map_chunks[(actual_chunk_x, actual_chunk_y)]
            if self.ores.get((actual_chunk_x, actual_chunk_y)) != None:
                for type, coords in self.ores[(actual_chunk_x, actual_chunk_y)].items():
                    for coord in coords:
                        complete_chunk[coord[0]][coord[1]] = type.value + 5

            chunks.append(complete_chunk)
            if i % self.area_size == self.area_size - 1:
                rows.append(np.concatenate(chunks, axis = 1))
                chunks.clear()
        
        return np.concatenate(rows, axis = 0)

if __name__ == "__main__":
    map = Map()
    area = map.get_area_around_chunk()
    fig, ax = plt.subplots()
    ax.imshow(area)
    plt.show()