import pygame
import os

TILE_SIZE = 50


class GameObject:
    def __init__(self):
        self.rect = pygame.Rect(TILE_SIZE, TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def collide_with_sth(self, object_type=None):
        for i in all_sprites:
            if object_type is None:
                if self.rect.colliderect(i) and i is not self:
                    return True, type(i)
            else:
                if self.rect.colliderect(i) and i is not self and type(i) == object_type:
                    return True, (i.rect.x, i.rect.y)
        return False, None


class Player(pygame.sprite.Sprite, GameObject):
    def __init__(self, x, y):
        super().__init__(player_group, all_sprites)
        self.ready_to_change_gravity = True
        self.g = 1.1
        self.direction = 1
        self.vy = 0
        self.rect = pygame.Rect(TILE_SIZE * x, TILE_SIZE * y, TILE_SIZE, TILE_SIZE)

    def move(self, x, y):
        old_x, old_y, w, h = self.rect
        self.rect = pygame.Rect(old_x, old_y + y, w, h)
        if self.collide_with_sth(Wall)[0]:
            collision_coords = self.collide_with_sth(Wall)[1]
            self.rect.y = collision_coords[1] + -(TILE_SIZE * self.direction)
            self.ready_to_change_gravity = True
            self.vy = 0
        else:
            self.rect.x += x
        if self.collide_with_sth(Wall)[0]:
            self.rect = pygame.Rect(old_x, old_y, w, h)

    def update(self, *args):
        self.vy *= self.g
        if self.vy != 0:
            self.ready_to_change_gravity = False
            self.move(0, self.vy)
        if self.collide_with_sth(Wall)[0]:
            self.vy = 0
        pygame.draw.rect(screen, pygame.Color('white'), self.rect)

    def change_gravity(self):
        self.direction *= -1
        self.vy = 5 * self.direction


class Spike(pygame.sprite.Sprite, GameObject):
    def __init__(self, x, y):
        super().__init__(spikes, all_sprites)
        self.rect = pygame.Rect(TILE_SIZE * x, TILE_SIZE * y, TILE_SIZE, TILE_SIZE)

    def update(self, *args):
        pygame.draw.rect(screen, pygame.Color('red'), self.rect)


class Wall(pygame.sprite.Sprite, GameObject):
    def __init__(self, x, y):
        super().__init__(walls, all_sprites)
        self.rect = pygame.Rect(TILE_SIZE * x, TILE_SIZE * y, TILE_SIZE, TILE_SIZE)

    def update(self, *args):
        pygame.draw.rect(screen, pygame.Color('black'), self.rect)


class Exit(pygame.sprite.Sprite, GameObject):
    def __init__(self, x, y):
        super().__init__(exits, all_sprites)
        self.rect = pygame.Rect(TILE_SIZE * x, TILE_SIZE * y, TILE_SIZE, TILE_SIZE)

    def update(self, *args):
        pygame.draw.rect(screen, pygame.Color('green'), self.rect)


class Light(pygame.sprite.Sprite, GameObject):
    def __init__(self, x, y):
        super().__init__(light_beam, all_sprites)
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 1
        self.beam_path = [(TILE_SIZE * x, TILE_SIZE * y)]
        self.rect = pygame.Rect(TILE_SIZE * x, TILE_SIZE * y, TILE_SIZE, TILE_SIZE)

    def update(self, *args):
        for light_piece in self.beam_path:
            pygame.draw.rect(screen, pygame.Color('violet'),
                             pygame.Rect(light_piece, (TILE_SIZE, TILE_SIZE)))
        if self.vx > 0 or self.vy > 0 and (TILE_SIZE * (self.x + self.vx),
                                           TILE_SIZE * (self.y + self.vy)) not in self.beam_path:
            self.beam_path.append((TILE_SIZE * (self.x + self.vx), TILE_SIZE * (self.y + self.vy)))


def load_image(name, trans=0):
    full_name = os.path.join('data', name)
    image = pygame.image.load(full_name).convert()
    if trans is not None:
        if trans == -1:
            trans = image.get_at((0, 0))
        image.set_colorkey(trans)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                pass
            elif level[y][x] == '#':
                Wall(x, y)
            elif level[y][x] == '^':
                Spike(x, y)
            elif level[y][x] == '@':
                new_player = Player(x, y)
            elif level[y][x] == '$':
                Exit(x, y)
            elif level[y][x] == '|':
                Light(x, y)
    return new_player, x, y


all_sprites = pygame.sprite.Group()
spikes = pygame.sprite.Group()
walls = pygame.sprite.Group()
exits = pygame.sprite.Group()
player_group = pygame.sprite.Group()
light_beam = pygame.sprite.Group()


pygame.init()
screen = pygame.display.set_mode((1300, 750))
clock = pygame.time.Clock()
player, level_x, level_y = generate_level(load_level('lvl.txt'))

running = True
while running:
    screen.fill(pygame.Color('aquamarine'))
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1 and player.ready_to_change_gravity:
                player.change_gravity()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
        player.move(10, 0)
    elif keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
        player.move(-10, 0)
    all_sprites.update()
    for elem in all_sprites:
        res = elem.collide_with_sth()
        if res[0]:
            if res[1] == Wall:
                elem.rect.x += 10 if elem.rect.x <= TILE_SIZE else -10
            elif res[1] == Exit:
                print('norm')
            elif res[1] == Spike:
                print('loh')
    clock.tick(60)
    pygame.display.flip()
