from math import ceil
from time import time, time_ns

import pygame

from vue.Scene import Scene
from vue.BuildingChoice import BuildingChoice
from vue.BuildingInterface import BuildingInterface
from vue.Button import Button
from vue.Pause import Pause

from model.Tools import Colors, Directions
from model.Map import Map, Biomes
from model.Geometry import Point, Rectangle, Circle
from model.Perlin import Perlin
from model.Player import Player
from model.Ressource import RessourceType
from model.Structures import StructureType, BuildingType, BuildingState, OreType, BaseCamp, Farm, get_struct_class_from_type
from model.Human import Human, Colon, get_human_class_from_type
from model.HumanType import HumanType
from model.Saver import Saver

class GameVue(Scene):
    __slots__ = ["saver", "player", "map", "actual_chunks", "buildings", "frame_render", "render_until_event", "clicked_building", "camera_pos", "left_clicking", "right_clicking", "button_hovered", "start_click_pos", "mouse_pos", "select_start", "select_end", "selecting", "selected_humans", "building", "building_pos", "cell_pixel_size", "screen_width", "screen_height", "base_pos", "compass_center", "compass_width", "screen_size", "scale_factor", "cell_width_count", "cell_height_count", "ressource_font", "ressource_icons", "humans_textures", "tree_texture", "biomes_textures", "ore_textures", "building_textures", "missing_texture", "ressource_background", "ressource_background_size", "building_button", "home_button", "building_button_rect", "home_button_rect", "colors", "clock", "last_timestamp", "building_choice", "building_choice_displayed", "building_interface", "building_interface_displayed"]

    def __init__(self, core):
        super().__init__(core)

        self.colors = None
        self.ressource_background_size = None
        self.ressource_background = None
        self.clicked_building = None
        self.home_button = None
        self.building_button = None
        self.home_button_rect = None
        self.building_button_rect = None
        self.biomes_textures = None
        self.ressource_icons = None
        self.humans_textures = None
        self.tree_texture = None
        self.ore_textures = None
        self.building_textures = None
        self.missing_texture = None
        self.ressource_font = None
        self.building_pos = None
        self.building = None

        self.player = Player(self.ressource_update_callback)

        self.map = Map()
        self.actual_chunks = None
        self.buildings = []

        self.frame_render = False
        self.render_until_event = True
        self.left_clicking = False
        self.right_clicking = False
        self.button_hovered = False
        self.camera_pos = Point.origin()
        self.start_click_pos = Point.origin()
        self.mouse_pos = Point.origin()

        self.select_start = Point.origin()
        self.select_end = Point.origin()
        self.selecting = False
        self.selected_humans = []

        self.reset_building()

        self.screen_width, self.screen_height = self.screen.get_width(), self.screen.get_height()
        self.screen_size = Point(self.screen_width, self.screen_height)
        self.scale_factor = 1
        self.scale()
        self.cell_width_count = ceil(self.screen_size.x / Map.CELL_SIZE)
        self.cell_height_count = ceil(self.screen_height / Map.CELL_SIZE)
        
        self.base_pos = Point.origin()
        self.compass_center = Point(self.screen_width * 0.95, self.screen_height * 0.1)
        self.compass_width = int(self.screen_width * 0.04)

        self.load_ressources()

        self.building_choice = BuildingChoice(self.player, self.screen, self.screen_size, self.ressource_background_size, self.ressource_icons, self.scale_factor)
        self.building_choice_displayed = False

        self.building_interface = BuildingInterface(self.player, self.screen, self.screen_size, self.ressource_background_size, self.ressource_icons, self.scale_factor)
        self.building_interface_displayed = False

        self.initialize_camps()

        self.clock = pygame.time.Clock()

        self.saver = Saver(self, core.save_name)

        if core.save_name is not None:
            self.saver.load()

        self.initialize_music()

        self.last_timestamp = time_ns()

    def scale(self):
        max_length = max(self.screen_width, self.screen_height)
        if max_length <= 1200:
            Map.CELL_SIZE = 30
            self.scale_factor = 1
        elif max_length > 1200 and max_length <= 1800:
            Map.CELL_SIZE = 35
            self.scale_factor = 1.2
        else:
            Map.CELL_SIZE = 40
            self.scale_factor = 1.4

    def reset_building(self):
        self.building = None
        self.building_pos = Point.origin()

    def load_ressources(self):
        self.ressource_font = pygame.font.Font("assets/font/Junter.otf", 16)

        self.ressource_icons = {}
        for ressource_type in RessourceType:
            self.ressource_icons[ressource_type] = pygame.transform.scale(pygame.image.load("assets/icons/" + ressource_type.name.lower() + ".png").convert_alpha(), (26, 26))

        self.biomes_textures = {}
        for biome in Biomes:
            self.biomes_textures[biome] = pygame.transform.scale(pygame.image.load("assets/icons/" + biome.name.lower() + ".jpg").convert_alpha(), (Map.CELL_SIZE, Map.CELL_SIZE))

        self.tree_texture = pygame.transform.scale(pygame.image.load("assets/Textures/Tree.png").convert_alpha(), (Map.CELL_SIZE * 3, Map.CELL_SIZE * 3))

        self.humans_textures = {}
        orientation_filenames = {
            Directions.BOTTOM: "b.png",
            Directions.RIGHT: "r.png",
            Directions.LEFT: "l.png",
            Directions.TOP: "t.png"
        }
        for human_type in HumanType:
            self.humans_textures[human_type] = {}
            for orientation in Directions:
                self.humans_textures[human_type][orientation] = pygame.transform.scale(pygame.image.load("assets/Textures/Humans/" + human_type.name.lower() + "/" + orientation_filenames[orientation]).convert_alpha(), (Map.CELL_SIZE, Map.CELL_SIZE))

        self.building_textures = {}
        for building in BuildingType:
            try:
                building_struct = get_struct_class_from_type(building)(Point(0, 0), self.player, self.building_destroyed_callback, self.human_died_callback)
                self.building_textures[building] = pygame.transform.scale(pygame.image.load("assets/Textures/Buildings/" + building.name.lower() + ".png").convert_alpha(), (building_struct.rect_size.x * Map.CELL_SIZE, building_struct.rect_size.y * Map.CELL_SIZE))
            except Exception:
                self.building_textures[building] = None

        self.ore_textures = {}
        for ore in OreType:
            try:
                self.ore_textures[ore] = pygame.transform.scale(pygame.image.load("assets/Textures/Ores/" + ore.name.lower() + ".png").convert_alpha(), (Map.CELL_SIZE, Map.CELL_SIZE))
            except Exception:
                self.ore_textures[ore] = None

        self.missing_texture = pygame.transform.scale(pygame.image.load("assets/Textures/missing.png").convert_alpha(), (Map.CELL_SIZE, Map.CELL_SIZE))

        self.ressource_background = pygame.transform.scale(pygame.image.load("assets/Textures/UI/ui.png").convert_alpha(), (312 * self.scale_factor, 202 * self.scale_factor))
        self.ressource_background_size = Point(self.ressource_background.get_width(), self.ressource_background.get_height())
        self.home_button = Button("Base", self.ressource_background_size.x + 15 * self.scale_factor, self.screen_height - 95 * self.scale_factor, 70 * self.scale_factor, 70 * self.scale_factor, (46, 159, 228), None, 15)
        self.building_button = Button("Bâtiments", self.ressource_background_size.x + 15 * self.scale_factor, self.screen_height - 180 * self.scale_factor, 70 * self.scale_factor, 70 * self.scale_factor, (46, 159, 228), None, 15)
        self.home_button_rect = Rectangle(self.ressource_background_size.x + 15 * self.scale_factor, self.screen_height - 95 * self.scale_factor, self.ressource_background_size.x + 85 * self.scale_factor, self.screen_height - 25 * self.scale_factor)
        self.building_button_rect = Rectangle(self.ressource_background_size.x + 15 * self.scale_factor, self.screen_height - 180 * self.scale_factor, self.ressource_background_size.x + 85 * self.scale_factor, self.screen_height - 110 * self.scale_factor)

        self.colors = {
            Colors.BLACK: pygame.Color(pygame.color.THECOLORS["black"]),
            Colors.WHITE: pygame.Color(pygame.color.THECOLORS["white"]),
            Colors.ALICEBLUE: pygame.Color(pygame.color.THECOLORS["aliceblue"]),
            Colors.AQUA: pygame.Color(pygame.color.THECOLORS["aqua"]),
            Colors.BLUE: pygame.Color(pygame.color.THECOLORS["blue"]),
            Colors.BLUEVIOLET: pygame.Color(pygame.color.THECOLORS["blueviolet"]),
            Colors.RED: pygame.Color(pygame.color.THECOLORS["red"]),
            Colors.ORANGE: pygame.Color(pygame.color.THECOLORS["orange"]),
            Colors.YELLOW: pygame.Color(pygame.color.THECOLORS["yellow"])
        }

    def initialize_music(self):
        pygame.mixer.music.load("assets/music/titleScreen.mp3")
        pygame.mixer.music.set_volume(self.parameter["volume"])
        pygame.mixer.music.play()

    def handle_events(self, event):
        mouse_pos = pygame.mouse.get_pos()
        mouse_point = Point(mouse_pos[0], mouse_pos[1])
        home_button_hovered, building_button_hovered = self.home_button_rect.containsPoint(mouse_point), self.building_button_rect.containsPoint(mouse_point)

        if self.building_choice_displayed and self.building_choice.rect.containsPoint(mouse_point):
            result = self.building_choice.event_stream(event)
            if result is not None:
                self.building = get_struct_class_from_type(result)(self.camera_pos // Map.CELL_SIZE, self.player, self.building_destroyed_callback, self.human_died_callback)
                self.building_pos = mouse_point - self.screen_size // 2
                self.building_choice_displayed = False
            self.frame_render = True
        # Events for the building interface
        elif self.building_interface_displayed and self.building_interface.rect.containsPoint(mouse_point):
            if self.building_interface.event_stream(event):
                buttons = self.clicked_building.get_buttons(self)
                if len(buttons) > 0:
                    self.building_interface.create_buttons(buttons)
            self.frame_render = True
        # Events for the buttons
        elif home_button_hovered or building_button_hovered:
            self.button_hovered = True
            clicked_button = self.home_button if home_button_hovered else self.building_button
            clicked = clicked_button.is_clicked(event)
            if clicked:
                clicked_button.color = (115, 207, 255)
                if home_button_hovered:
                    self.camera_pos = Point.origin()
                else:
                    self.building_choice_displayed = not self.building_choice_displayed
                    self.frame_render = True
            if clicked_button.is_hovered(event):
                clicked_button.color = (101, 195, 255)
            elif not clicked:
                clicked_button.color = (46, 159, 228)
            self.frame_render = True
        else: # Events for the game
            # MOUSE BUTTON DOWN
            if event.type == pygame.MOUSEBUTTONDOWN:
                pressed_mouse_buttons = pygame.mouse.get_pressed()
                if pressed_mouse_buttons[0]:
                    self.left_clicking = True
                    self.select_start = mouse_point
                    self.select_end = self.select_start
                elif pressed_mouse_buttons[2]:
                    self.right_clicking = True
                    if self.building is None:
                        self.mouse_pos = mouse_point
                self.start_click_pos = mouse_point
            # MOUSE BUTTON UP
            elif event.type == pygame.MOUSEBUTTONUP:
                pressed_mouse_buttons = pygame.mouse.get_pressed()

                if not pressed_mouse_buttons[2] and self.right_clicking:
                    self.right_clicking = False
                elif not pressed_mouse_buttons[0]:
                    if self.building is not None:
                        self.building.coords = self.building_pos // Map.CELL_SIZE + self.camera_pos // Map.CELL_SIZE
                        if self.left_clicking and self.map.place_structure(self.building):
                            for ressource_type, ressource_number in self.building.costs.items():
                                self.player.add_ressource(ressource_type, -ressource_number)
                            self.reset_building()
                            self.left_clicking = False
                            self.frame_render = True
                    elif self.selecting:
                        self.frame_render = True
                        self.selecting = False
                        self.left_clicking = False
                        self.select_start = Point.origin()
                        self.select_end = Point.origin()
                    elif len(self.selected_humans) > 0:
                        self.left_clicking = False
                        cell = (mouse_point + self.camera_pos - self.screen_size // 2) // Map.CELL_SIZE
                        for human in self.selected_humans:
                            human.set_target_location(cell)
                        self.selected_humans.clear()
                        self.frame_render = True
                    else:
                        pos_point = mouse_point + self.camera_pos - self.screen_size // 2
                        cell_pos = pos_point // Map.CELL_SIZE
                        chunk_pos = cell_pos // Perlin.CHUNK_SIZE
                        chunk_humans = self.map.chunk_humans.get(chunk_pos, None)
                        if chunk_humans is not None:
                            for human in chunk_humans:
                                if Circle(human.current_location, Map.CELL_SIZE).contains(pos_point + self.camera_pos):
                                    self.selected_humans.append(human)
                                    self.selecting = False
                                    break
                            self.frame_render = len(self.selected_humans) > 0

                        building = self.map.occupied_coords.get(cell_pos, None)
                        if building is not None and building.structure_type == StructureType.BUILDING and building.state == BuildingState.BUILT:
                            if self.building_interface_displayed:
                                self.clicked_building = None
                                self.building_interface_displayed = False
                                self.frame_render = True
                            else:
                                buttons = building.get_buttons(self)
                                if len(buttons) > 0:
                                    self.clicked_building = building
                                    self.building_interface_displayed = True
                                    self.building_interface.create_buttons(buttons)
                                    self.frame_render = True
                        else:
                            if self.building_interface_displayed and self.left_clicking:
                                self.building_interface_displayed = False
                                self.frame_render = True
                            
                        self.left_clicking = False
            # MOUSE MOTION
            elif event.type == pygame.MOUSEMOTION:
                self.render_until_event = False
                if self.button_hovered:
                    self.button_hovered = False
                    self.building_button.color = (46, 159, 228)
                    self.home_button.color = (46, 159, 228)
                    self.frame_render = True

                if self.selecting:
                    self.select_end = mouse_point
                elif self.right_clicking:
                    self.camera_pos += (self.mouse_pos - mouse_point) * (2.8 / 2.0)
                    if (self.mouse_pos - mouse_point) != Point.origin():
                        self.frame_render = True
                elif self.building is not None:
                    if (self.mouse_pos - self.building_pos) // Map.CELL_SIZE != Point.origin():
                        self.building_pos = mouse_point - self.screen_size // 2
                        self.frame_render = True
                elif self.left_clicking and self.start_click_pos.distance(mouse_point) > 10:
                    self.selecting = True
                self.mouse_pos = mouse_point
            # KEY UP
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_p :
                    pause = Pause(
                        self.core, self.render, self.saver
                    )  # Create and run the settings scene
                    pause.run()
                if event.key == pygame.K_h: # TODO: For debug, remove for the final version
                    chunk_pos = self.camera_pos // Map.CELL_SIZE // Perlin.CHUNK_SIZE
                    if self.map.chunk_humans.get(chunk_pos, None) is None:
                        self.map.chunk_humans[chunk_pos] = []
                    human = Colon(self.map, self.camera_pos, self.player, self.human_died_callback)
                    self.map.chunk_humans[chunk_pos].append(human)
                    self.map.humans.append(human)
                    self.frame_render = True
                if event.key == pygame.K_r: # TODO: For debug, remove for the final version
                    self.player.add_ressource(RessourceType.WOOD, 1000)
                    self.player.add_ressource(RessourceType.FOOD, 1000)
                    self.player.add_ressource(RessourceType.STONE, 1000)
                    self.player.add_ressource(RessourceType.IRON, 1000)
                    self.player.add_ressource(RessourceType.COPPER, 1000)
                    self.player.add_ressource(RessourceType.GOLD, 1000)
                    self.player.add_ressource(RessourceType.CRYSTAL, 1000)
                    self.player.add_ressource(RessourceType.VULCAN, 1000)
                if event.key == pygame.K_ESCAPE:
                    self.reset_building()
                    self.selected_humans.clear()
                    self.frame_render = True

    def update(self):
        timestamp = time_ns()
        duration = (timestamp - self.last_timestamp) / 1000000000
        self.last_timestamp = timestamp

        if self.map.update(duration):
            self.frame_render = True

    def render(self):
        if self.selecting or self.frame_render or self.render_until_event:
            if self.frame_render:
                self.frame_render = False
            self.render_map()

            self.render_selection()

            self.render_interface()
            
            if self.building_choice_displayed:
                self.building_choice.render()

            if self.building_interface_displayed:
                self.building_interface.render()

        #print(self.clock.get_fps())

        #self.clock.tick()

    def render_map(self):
        camera_pos = Point(int(self.camera_pos.x), int(self.camera_pos.y))
        camera_cell = camera_pos // Map.CELL_SIZE
        camera_offset = camera_pos % Map.CELL_SIZE
        camera_chunk = camera_cell // Perlin.CHUNK_SIZE
        camera_chunk_cell = camera_cell % Perlin.CHUNK_SIZE

        screen_center = self.screen_size // 2
        screen_center_cell = screen_center // Map.CELL_SIZE
        screen_center_rounded = screen_center_cell * Map.CELL_SIZE
        chunk_tl = screen_center - camera_chunk_cell * Map.CELL_SIZE
        chunk_br = chunk_tl + Point(Perlin.CHUNK_SIZE * Map.CELL_SIZE, Perlin.CHUNK_SIZE * Map.CELL_SIZE) - camera_offset

        margin_tl = Point(max(0, chunk_tl.x), max(0, chunk_tl.y))
        margin_br = Point(max(0, self.screen_width - chunk_br.x), max(0, self.screen_height - chunk_br.y))
        cells_tl = Point(ceil(margin_tl.x / Map.CELL_SIZE), ceil(margin_tl.y / Map.CELL_SIZE))
        cells_br = Point(ceil(margin_br.x / Map.CELL_SIZE), ceil(margin_br.y / Map.CELL_SIZE))
        chunks_tl = Point(ceil(cells_tl.x / Perlin.CHUNK_SIZE), ceil(cells_tl.y / Perlin.CHUNK_SIZE))
        chunks_br = Point(ceil(cells_br.x / Perlin.CHUNK_SIZE), ceil(cells_br.y / Perlin.CHUNK_SIZE))

        cells_tl_signed = Point(chunk_tl.x / Map.CELL_SIZE, chunk_tl.y / Map.CELL_SIZE)
        cells_br_signed = Point((self.screen_width - chunk_br.x) / Map.CELL_SIZE, (self.screen_height - chunk_br.y) / Map.CELL_SIZE)
        cells_size = Point(ceil(cells_tl_signed.x + cells_br_signed.x) + Perlin.CHUNK_SIZE, ceil(cells_tl_signed.y + cells_br_signed.y) + Perlin.CHUNK_SIZE)

        chunks_size = chunks_br + chunks_tl

        ceiled_cells_tl = Point(ceil(cells_tl_signed.x), ceil(cells_tl_signed.y))
        cell_offset = Point(-ceiled_cells_tl.x if ceiled_cells_tl.x <= 0 else Perlin.CHUNK_SIZE - ceiled_cells_tl.x, -ceiled_cells_tl.y if ceiled_cells_tl.y <= 0 else Perlin.CHUNK_SIZE - ceiled_cells_tl.y)

        tl_chunk = camera_chunk - chunks_tl
        chunks = self.map.get_area_around_chunk(camera_chunk - chunks_tl, chunks_size.x + 1, chunks_size.y + 1)
        self.actual_chunks = chunks

        # RENDER MAP
        for i in range(0, cells_size.x):
            for j in range(0, cells_size.y):
                x = i + cell_offset.x
                y = j + cell_offset.y
                self.screen.blit(self.biomes_textures[Biomes(int(chunks[x][y]))], (i * Map.CELL_SIZE - camera_offset.x, j * Map.CELL_SIZE - camera_offset.y))

        # RENDER STRUCTURES
        shown_trees = {}
        shown_buildings = {}
        for x in range(tl_chunk.x, tl_chunk.x + chunks_size.x + 1):
            for y in range(tl_chunk.y, tl_chunk.y + chunks_size.y + 1):
                actual_chunk_occupied_coords = self.map.chunk_occupied_coords.get(Point(x, y), None)
                if actual_chunk_occupied_coords is not None:
                    for point in actual_chunk_occupied_coords:
                        struct = self.map.occupied_coords.get(point, None)
                        if struct is not None:
                            if struct.structure_type == StructureType.BUILDING and shown_buildings.get(struct, None) is None:
                                absolute_point = (struct.coords + struct.upper_left) * Map.CELL_SIZE - camera_pos + screen_center_rounded
                                self.screen.blit(self.building_textures[struct.type] if self.building_textures.get(struct.type, None) != None else self.missing_texture, (absolute_point.x, absolute_point.y))
                                shown_buildings[struct] = True
                                if struct.state == BuildingState.BUILDING or struct.state == BuildingState.PLACED:
                                    pygame.draw.rect(self.screen, self.colors[Colors.WHITE], (absolute_point.x + (struct.rect_size.x * Map.CELL_SIZE - Map.CELL_SIZE * 2) // 2, absolute_point.y - Map.CELL_SIZE, Map.CELL_SIZE * 2, Map.CELL_SIZE // 2))
                                    pygame.draw.rect(self.screen, self.colors[Colors.BLUE], (absolute_point.x + (struct.rect_size.x * Map.CELL_SIZE - Map.CELL_SIZE * 2) // 2, absolute_point.y - Map.CELL_SIZE, int(Map.CELL_SIZE * 2 * (struct.building_time / struct.building_duration)), Map.CELL_SIZE // 2))
                            elif struct.structure_type == StructureType.ORE:
                                absolute_point = point * Map.CELL_SIZE - camera_pos + screen_center_rounded
                                self.screen.blit(self.ore_textures[struct.type] if self.ore_textures.get(struct.type, None) != None else self.missing_texture, (absolute_point.x, absolute_point.y))
                            elif struct.structure_type == StructureType.TREE and shown_trees.get(struct, None) is None:
                                absolute_point = (struct.coords + Point(-1, -1)) * Map.CELL_SIZE - camera_pos + screen_center_rounded
                                self.screen.blit(self.tree_texture, (absolute_point.x, absolute_point.y))
                                shown_trees[struct] = True

        # RENDER PLACE BUILDING
        if self.building is not None:
            relative_center = self.building_pos // Map.CELL_SIZE
            relative_position = (self.building_pos) // Map.CELL_SIZE + camera_cell
            
            for point in self.building.points:
                absolute_point = (relative_center + point) * Map.CELL_SIZE + screen_center_rounded - camera_offset
                color = Colors.BLACK
                if self.map.occupied_coords.get(point + relative_position, None) is not None:
                    color = Colors.RED
                pygame.draw.rect(self.screen, self.colors[color], (absolute_point.x, absolute_point.y, Map.CELL_SIZE, Map.CELL_SIZE))

            absolute_point = (relative_center + self.building.upper_left) * Map.CELL_SIZE + screen_center_rounded - camera_offset
            self.screen.blit(self.building_textures[self.building.type] if self.building_textures.get(self.building.type, None) != None else self.missing_texture, (absolute_point.x, absolute_point.y))
            

        if self.selecting:
            self.selected_humans.clear()
            selection_rect = Rectangle.fromPoints(self.select_start, self.select_end)
        else:
            ids = [id(h) for h in self.selected_humans]
                
        # RENDER HUMANS
        for x in range(tl_chunk.x, tl_chunk.x + chunks_size.x + 1):
            for y in range(tl_chunk.y, tl_chunk.y + chunks_size.y + 1):
                actual_chunk_humans = self.map.chunk_humans.get(Point(x, y), None)
                if actual_chunk_humans is not None:
                    for human in actual_chunk_humans:
                        absolute_point = human.current_location - camera_pos + screen_center_rounded

                        if self.selecting:
                            selected = selection_rect.containsPoint(absolute_point)
                            if selected:
                                self.selected_humans.append(human)
                        else:
                            selected = id(human) in ids

                        if selected:
                            pygame.draw.circle(self.screen, self.colors[Colors.AQUA], (absolute_point.x + 1, absolute_point.y), 10)
                        self.screen.blit(self.humans_textures[human.type][human.orientation], (absolute_point.x - Map.CELL_SIZE // 2, absolute_point.y - Map.CELL_SIZE // 2))
                

    def render_selection(self):
        if self.selecting:
            s = pygame.Surface((abs(self.select_end.x - self.select_start.x), abs(self.select_end.y - self.select_start.y)))
            s.set_alpha(150)
            s.fill((0,127,127))
            self.screen.blit(s, (self.select_start.x if self.select_start.x < self.select_end.x else self.select_end.x, self.select_start.y if self.select_start.y < self.select_end.y else self.select_end.y))

    def render_interface(self):
        ressource_icons_texts = {}
        for ressource_type in RessourceType:
            text = self.render_ressource_text(ressource_type)
            icon = self.ressource_icons.get(ressource_type, None)
            ressource_icons_texts[ressource_type] = (icon, text)

        offset = self.screen_height - self.ressource_background_size.y

        self.screen.blit(self.ressource_background, (0, offset))

        i = 0
        for ressource_type in [(RessourceType.FOOD, RessourceType.COPPER), (RessourceType.WOOD, RessourceType.IRON), (RessourceType.STONE, RessourceType.CRYSTAL), (RessourceType.GOLD, RessourceType.VULCAN)]:
            ressource_1, ressource_2 = ressource_type

            ressource_icon_1, ressource_text_1 = ressource_icons_texts.get(ressource_1, (None, None))
            ressource_icon_2, ressource_text_2 = ressource_icons_texts.get(ressource_2, (None, None))

            self.screen.blit(ressource_text_1, (80 * self.scale_factor , offset + (50 + 30 * i) * self.scale_factor))
            self.screen.blit(ressource_text_2, (200 * self.scale_factor, offset + (50 + 30 * i) * self.scale_factor))

            self.screen.blit(ressource_icon_1, (40 * self.scale_factor , offset + (43 + 30 * i) * self.scale_factor))
            self.screen.blit(ressource_icon_2, (160 * self.scale_factor, offset + (43 + 30 * i) * self.scale_factor))

            i += 1

        # Boussole
        int_camera_pos = Point(int(self.camera_pos.x), int(self.camera_pos.y))
        distance = int_camera_pos.distance(self.base_pos) // Map.CELL_SIZE
        text = self.ressource_font.render(f"Distance: {int(distance)}", True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.compass_center.x, self.compass_center.y + self.compass_width + 30))
        self.screen.blit(text, text_rect)

        if int_camera_pos == self.base_pos:
            pygame.draw.circle(self.screen, (0, 0, 0), (self.compass_center.x, self.compass_center.y), self.compass_width, 10)
        else:
            vect_pos = Point(-(int_camera_pos.x / int_camera_pos.distance(self.base_pos)) * self.compass_width, -(int_camera_pos.y / int_camera_pos.distance(self.base_pos)) * self.compass_width)
            end_pos = vect_pos + self.compass_center

            pygame.draw.circle(self.screen, (0, 0, 0), (self.compass_center.x, self.compass_center.y), self.compass_width, 10)
            pygame.draw.line(self.screen, (255, 0, 0), (self.compass_center.x, self.compass_center.y), (end_pos.x, end_pos.y), 4)

        self.home_button.render(self.screen)
        self.building_button.render(self.screen)

    def render_ressource_text(self, ressource_type):
        return self.ressource_font.render(str(int(self.player.get_ressource(ressource_type))), True, self.colors[Colors.WHITE])

    def ressource_update_callback(self):
        self.frame_render = True

    def building_destroyed_callback(self, building):
        self.map.remove_building(building)

    def human_died_callback(self, human):
        self.map.remove_human(human)

    def initialize_camps(self):
        self.map.place_structure(BaseCamp(Point.origin(), self.player, self.building_destroyed_callback, self.human_died_callback))
        for point in [Point(-3, 1), Point(-3, 2), Point(-3, 3), Point(-2, 3), Point(-1, 3)]:
            postion = point * Map.CELL_SIZE + Human.CELL_CENTER
            human = Colon(self.map, postion, self.player, self.human_died_callback)
            self.map.place_human(human, postion)
            self.frame_render = True

    def add_human(self, human_type, position):
        human = get_human_class_from_type(human_type)(self.map, position * Map.CELL_SIZE, self.player, self.human_died_callback)
        chunk_pos = position // Perlin.CHUNK_SIZE
        if self.map.chunk_humans.get(chunk_pos, None) is None:
            self.map.chunk_humans[chunk_pos] = []
        self.map.chunk_humans[chunk_pos].append(human)
        self.map.humans.append(human)
        self.frame_render = True
