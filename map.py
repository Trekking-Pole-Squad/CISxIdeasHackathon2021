from os import path
import pygame
import random
from pygame import freetype


class Map:
    def __init__(self, file_name):
        map_file = open(path.join(".", "maps", file_name), "r")

        self.render_offset = (672, 0)
        self.pixel_size = (16, 16)
        self.total_map_size = (48, 48)
        # total map size in pixels will be 16x48 and 16x48

        self.done = False

        self.win_frames = 0

        file_data = map_file.readlines()
        # first line is map size, truncated to a maximum size of 46 (plus walls becomes 48)
        width = int(file_data[0].split(",")[0])
        height = int(file_data[0].split(",")[1])
        file_data.pop(0)
        width = (self.total_map_size[0] - 2) if width > (self.total_map_size[0] - 2) else width
        height = (self.total_map_size[1] - 2) if height > (self.total_map_size[1] - 2) else height

        self.map_size = (width, height)

        # initialize map with only air
        self.map = [[0 for column in range(width)] for row in range(height)]
        self.spawnpoint = (0, 0)

        # map data is sorted in <x>,<y>,<type>
        # types are as follows:
        # 0 - air
        # 1 - floor
        # 2 - target
        # 3 - spawnpoint
        for file_line in file_data:
            # skip empty lines
            if file_line != "\n":
                point_info = file_line.split(",")
                # set the location using the information
                # remove spawnpoint
                if int(point_info[0]) < self.map_size[0] and int(point_info[1]) < self.map_size[1]:
                    if int(point_info[2]) == 3:
                        self.spawnpoint = [int(point_info[0]), int(point_info[1])]
                    else:
                        self.map[int(point_info[1])][int(point_info[0])] = int(point_info[2])

        # render initialization
        # int() is built-in floor() function
        self.x_block_offset = int((self.total_map_size[0] - self.map_size[0]) / 2)
        self.y_block_offset = int((self.total_map_size[1] - self.map_size[1]) / 2)

        self.render_map = [[1 for column in range(self.total_map_size[0])] for row in range(self.total_map_size[1])]

        # place map on render_map
        for y in range(self.map_size[1]):
            for x in range(self.map_size[0]):
                self.render_map[y + self.y_block_offset][x + self.x_block_offset] = self.map[y][x]

        # init textures
        self.textures = [0] * 4
        self.textures[1] = []
        for frame in range(3):
            self.textures[1].append(pygame.image.load(path.join(".", "images", "floor", str(frame)+".png")))

        for texture_index in range(len(self.textures[1])):
            self.textures[1][texture_index] = pygame.transform.scale(self.textures[1][texture_index], self.pixel_size)

        self.textures[2] = pygame.image.load(path.join(".", "images", "target", "grounded.png"))
        self.textures[2] = pygame.transform.scale(self.textures[2], self.pixel_size)

        self.textures[3] = pygame.image.load(path.join(".", "images", "target", "aerial.png"))
        self.textures[3] = pygame.transform.scale(self.textures[3], self.pixel_size)

        self.background = pygame.image.load(path.join(".", "images", "background.png"))
        self.background = pygame.transform.scale(self.background, (self.total_map_size[0] * self.pixel_size[0],
                                                                   self.total_map_size[1] * self.pixel_size[1]))

        pygame.init()

        self.font = pygame.freetype.Font(path.join(".", "fonts", "Menlo.ttc"))
        self.font.size = 32
        self.font.fgcolor = (156, 170, 255)

    def run(self, screen):
        # render over gameplay, and stop gameplay (follow through)
        self._render(screen)
        if self.done:
            self._render_win_screen(screen)

    def reset_map(self):
        self.win_frames = 0
        self.render_map = [[1 for column in range(self.total_map_size[0])] for row in range(self.total_map_size[1])]

        # place map on render_map
        for y in range(self.map_size[1]):
            for x in range(self.map_size[0]):
                self.render_map[y + self.y_block_offset][x + self.x_block_offset] = self.map[y][x]

    def break_target(self, x, y):
        # assume the sword hitbox intersection was checked already
        self.render_map[y][x] = 0

        # check if all targets are gone and end game when all are gone
        end_game = True
        for row in self.render_map:
            if 2 in row:
                end_game = False
        self.done = end_game

    def _render(self, screen):
        # render background
        screen.blit(self.background, self.render_offset)

        # render foreground
        for y in range(self.total_map_size[1]):
            for x in range(self.total_map_size[0]):
                block_rect = pygame.Rect((self.render_offset[0] + x * self.pixel_size[0],
                                          self.render_offset[1] + y * self.pixel_size[1],
                                          self.pixel_size[0],
                                          self.pixel_size[1]))
                # don't render air
                if self.render_map[y][x] != 0:
                    # if texture has list, randomize based on seed (constant output for specified x,y)
                    if type(self.textures[self.render_map[y][x]]) == list:
                        # some random equation. Originally was x * y but that would make the textures mirrored in y = x
                        random.seed((5 * x) ** 2 + (3 * y))
                        texture = random.choice(self.textures[self.render_map[y][x]])
                    else:
                        if self.render_map[y][x] == 2:
                            if self.render_map[y+1][x] == 1:
                                texture = self.textures[2]
                            else:
                                texture = self.textures[3]
                        else:
                            texture = self.textures[self.render_map[y][x]]
                    screen.blit(texture, block_rect)

    def _render_win_screen(self, screen):
        background = pygame.Surface((600,660))
        background.fill((46, 42, 54))
        screen.blit(background,pygame.Rect(36, 72, 600, 660))

        font_surface, font_rect = self.font.render("time: "+str(self.win_frames)+" frames")
        font_rect.center = (336, 384)
        screen.blit(font_surface, font_rect)

