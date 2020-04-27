import pygame
from pygame.sprite import Sprite
import os
import sys
# import math
from pygame.sprite import Group
from random import randint


pygame.init()
clock = pygame.time.Clock()
os.environ['SDL_VIDEO_WINDOW_POS'] = '50, 50'
screen = pygame.display.set_mode((650, 650), pygame.RESIZABLE)
screen_rect = screen.get_rect()
pygame.display.set_caption("omg")
font = pygame.font.SysFont(None, 48)
font_20 = pygame.font.SysFont(None, 20)


class Player(Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.solid = False
        self.moved = True
        self.form = 'circle'
        self.radius = 25
        self.width = self.radius * 2
        self.hight = self.radius * 2
        self.pos_x = float(100)
        self.pos_y = float(10)
        self.image = pygame.Surface((self.width, self.hight), pygame.SRCALPHA)
        self.image.set_alpha(0)
        self.rect = self.image.get_rect()
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)
        pygame.draw.circle(self.image, (0, 200, 0), (int(
            self.width / 2), int(self.hight / 2)), int(self.width / 2))
        self.mask = pygame.mask.from_surface(self.image)

        self.mass = self.radius**2 * 3.14

        self.moving_right = False
        self.moving_left = False
        self.moving_top = False
        self.moving_bot = False
        self.max_speed = 8
        self.moving_accelerate = 0.5
        self.moving_speed = pygame.Vector2()
        self.moving_speed.x = float(0)
        self.moving_speed.y = float(0)
        self.goal_speed_vector = pygame.Vector2()
        self.goal_speed_vector.x = float(0)
        self.goal_speed_vector.y = float(0)
        self.goal_speed_vector_case = pygame.Vector2()


    def set_goal_speed_vector_case(self, case):
        if case == 'right':
            self.goal_speed_vector_case += (1, 0)
        elif case == 'left':
            self.goal_speed_vector_case += (-1, 0)
        elif case == 'top':
            self.goal_speed_vector_case += (0, -1)
        elif case == 'bot':
            self.goal_speed_vector_case += (0, 1)
        elif case == '-right':
            self.goal_speed_vector_case += (-1, 0)
        elif case == '-left':
            self.goal_speed_vector_case += (1, 0)
        elif case == '-top':
            self.goal_speed_vector_case += (0, 1)
        elif case == '-bot':
            self.goal_speed_vector_case += (0, -1)


    def moving(self):
        self.goal_speed_vector = self.max_speed * self.goal_speed_vector_case
        marginal_accel = pygame.Vector2()
        try:
            self.goal_speed_vector.scale_to_length(self.max_speed)
        except ValueError:
            pass
        marginal_accel = self.goal_speed_vector - self.moving_speed
        if marginal_accel.length() > self.moving_accelerate:
            try:
                marginal_accel.scale_to_length(self.moving_accelerate)
            except ValueError:
                pass
        self.moving_speed += marginal_accel
        if self.moving_speed.length() != 0: self.moved = True
        else: self.moved = False
        self.pos_x += self.moving_speed.x
        self.pos_y += self.moving_speed.y
        self.rect.centerx = self.pos_x
        self.rect.centery = self.pos_y

def collisions(pushing_sprites):
    for cheking_sprite in pushing_sprites:
        if cheking_sprite.solid: continue # если спрайт не двигается - нечего его проверять
        if not cheking_sprite.moved: continue # если он не двигался на прошлом шаге, то не надо его проверять
        for current_sprite in pushing_sprites:
            if cheking_sprite == current_sprite: continue
            additional_distance=0
            while pygame.sprite.collide_mask(cheking_sprite, current_sprite):
                if current_sprite.form == 'circle':
                    pushOut_vector = get_pushOut_vector(cheking_sprite.rect.center, current_sprite.rect.center, cheking_sprite.radius + current_sprite.radius + additional_distance)
                elif current_sprite.form == 'rect':
                    nearlest_point = get_nearlest_point(cheking_sprite, current_sprite)
                    pushOut_vector = get_pushOut_vector(cheking_sprite.rect.center, nearlest_point, cheking_sprite.radius + additional_distance)
                additional_distance += 1
                mass_effect = current_sprite.mass / (cheking_sprite.mass + current_sprite.mass)
                #mass_effect = 0.9
                #print(cheking_sprite.mass, current_sprite.mass, mass_effect)
                if current_sprite.solid: mass_effect = 1
                cheking_sprite.pos_x = cheking_sprite.pos_x + pushOut_vector.x * mass_effect
                cheking_sprite.pos_y = cheking_sprite.pos_y + pushOut_vector.y * mass_effect
                current_sprite.pos_x = current_sprite.pos_x - pushOut_vector.x * (1 - mass_effect)
                current_sprite.pos_y = current_sprite.pos_y - pushOut_vector.y * (1 - mass_effect)

                cheking_sprite.rect.centerx = cheking_sprite.pos_x
                cheking_sprite.rect.centery = cheking_sprite.pos_y
                current_sprite.rect.centerx = current_sprite.pos_x
                current_sprite.rect.centery = current_sprite.pos_y

                cheking_sprite.moved = False
                if not current_sprite.solid:
                    current_sprite.moved = True


                # collisions(pushing_sprites)


def get_nearlest_point(obj1, obj2):
    # ogj1 должен быть кругом. obj2 - ректом. Возвращает точку на ректе ближайшую к центру круга.

    nearlest_point = [0,0]

    if obj1.rect.centerx <= obj2.rect.left and obj1.rect.centery <= obj2.rect.top:
        nearlest_point = obj2.rect.topleft

    elif obj1.rect.centerx > obj2.rect.left and obj1.rect.centerx <= obj2.rect.right and obj1.rect.centery < obj2.rect.y:
        nearlest_point[0] = obj1.rect.centerx
        nearlest_point[1] = obj2.rect.top

    elif obj1.rect.centerx > obj2.rect.right and obj1.rect.centery <= obj2.rect.top:
        nearlest_point = obj2.rect.topright

    elif obj1.rect.centerx > obj2.rect.right and obj2.rect.top < obj1.rect.centery <= obj2.rect.bottom:
        nearlest_point[0] = obj2.rect.right
        nearlest_point[1] = obj1.rect.centery

    elif obj1.rect.centerx > obj2.rect.right and obj1.rect.centery > obj2.rect.top:
        nearlest_point = obj2.rect.bottomright

    elif obj2.rect.left < obj1.rect.centerx <= obj2.rect.right and obj1.rect.centery > obj2.rect.bottom:
        nearlest_point[0] = obj1.rect.centerx
        nearlest_point[1] = obj2.rect.bottom

    elif obj1.rect.centerx <= obj2.rect.left  and obj1.rect.centery >= obj2.rect.bottom:
        nearlest_point = obj2.rect.bottomleft

    elif obj1.rect.centerx < obj2.rect.left and obj2.rect.top < obj1.rect.centery < obj2.rect.bottom:
        nearlest_point[0] = obj2.rect.left
        nearlest_point[1] = obj1.rect.centery

    return nearlest_point
                

def get_pushOut_vector(point1, point2, distance):
    collide_vector = pygame.Vector2(float(0), float(0))
    collide_vector.x = point1[0] - point2[0]
    collide_vector.y = point1[1] - point2[1]
    pushOut_vector = pygame.Vector2(collide_vector)
    if pushOut_vector.length() == 0:
        pushOut_vector.xy = randint(-1, 1), randint(-1, 1)
        return pushOut_vector
    pushOut_vector.scale_to_length(distance)
    pushOut_vector -= collide_vector
    return pushOut_vector






class Obstacle(Sprite):
    def __init__(self, radius, pos_x, pos_y):
        super(Obstacle, self).__init__()
        self.solid = True
        self.moved = False
        self.form = 'circle'
        self.radius = radius
        self.width = self.radius * 2
        self.hight = self.radius * 2
        self.mass = self.radius**2 * 3.14
        self.pos_x = float(pos_x)
        self.pos_y = float(pos_y)
        self.image = pygame.Surface((self.width, self.hight), pygame.SRCALPHA)
        self.image.set_alpha(0)
        self.rect = self.image.get_rect()
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)
        pygame.draw.circle(self.image, (0, 200, 150), (int(
            self.width / 2), int(self.hight / 2)), int(self.width / 2))
        self.mask = pygame.mask.from_surface(self.image)

class Obstacle_light(Sprite):
    def __init__(self, radius, pos_x, pos_y):
        super(Obstacle_light, self).__init__()
        self.solid = False
        self.moved = True
        self.form = 'circle'
        self.radius = radius
        self.width = self.radius * 2
        self.hight = self.radius * 2
        self.mass = self.radius**2 * 3.14
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = pygame.Surface((self.width, self.hight), pygame.SRCALPHA)
        self.image.set_alpha(0)
        self.rect = self.image.get_rect()
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)
        pygame.draw.circle(self.image, (100, 0, 150), (int(self.width / 2), int(self.hight / 2)), int(self.width / 2))
        self.mask = pygame.mask.from_surface(self.image)

class Obstacle_solid_rect(Sprite):
    def __init__(self, width, height, pos_x, pos_y):
        super(Obstacle_solid_rect, self).__init__()
        self.solid = True
        self.moved = False
        self.form = 'rect'
        self.width = width
        self.height = height
        self.mass = self.width*self.height
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.image.set_alpha(0)
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image, (0, 0, 0), self.rect)
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)



        self.mask = pygame.mask.from_surface(self.image)



player = Player()
pushing_sprites = Group()
player.add(pushing_sprites)



def spawn_rect():
    for x in range(1):
        obstacle = Obstacle_solid_rect(100,150, 200, 200)
        obstacle.add(pushing_sprites)

def spawn_one_big_solid():
    for x in range(1):
        obstacle = Obstacle(min(screen_rect.width, screen_rect.height)/2-100, screen_rect.centerx, screen_rect.centery)
        obstacle.add(pushing_sprites)

def spawn_light_obst():
    obstacle = Obstacle_light(min(screen_rect.width, screen_rect.height)/2-100, screen_rect.centerx, screen_rect.centery)
    obstacle.add(pushing_sprites)

def spawn():
    for x in range(10):
        obstacle = Obstacle(randint(10, 80), randint(0, screen_rect.width - 80), randint(0, screen_rect.height - 80))
        obstacle.add(pushing_sprites)
    for x in range(10):
        obstacle_light = Obstacle_light(randint(10, 80), randint(0, screen_rect.width - 80), randint(0, screen_rect.height - 80))
        obstacle_light.add(pushing_sprites)

def spawn_2():
    for x in range(20):
        obstacle_light = Obstacle_light(5, screen_rect.centerx, screen_rect.centery)
        obstacle_light.add(pushing_sprites)

def spawn_3():
    for x in range(8):
        obstacle_light = Obstacle_light(60, screen_rect.centerx, screen_rect.centery)
        obstacle_light.add(pushing_sprites)

def del_all():
    pushing_sprites.empty()
    player.add(pushing_sprites)


def collide_obstacle(obj1, obj2):
    collide_vector = pygame.Vector2(float(0), float(0))
    collide_vector.x = obj2.rect.centerx - obj1.rect.centerx
    collide_vector.y = obj2.rect.centery - obj1.rect.centery
    collade_angle = (player.moving_speed).angle_to(collide_vector)
    pushOut_vector = pygame.Vector2(collide_vector)
    pushOut_vector.scale_to_length(obj2.radius + obj1.radius)
    pushOut_vector -= collide_vector
    obj1.rect.x -= pushOut_vector.x
    obj1.rect.y -= pushOut_vector.y
    if -360 < collade_angle < -270 or 0 < collade_angle < 90:
        player.moving_speed.rotate_ip(-(90 - collade_angle))
    if 270 < collade_angle < 360 or -90 < collade_angle < 0:
        player.moving_speed.rotate_ip(90 + collade_angle)

def pushing(obj1, obj2):
    collide_vector = pygame.Vector2(float(0), float(0))
    collide_vector.x = obj1.rect.centerx - obj2.rect.centerx
    collide_vector.y = obj1.rect.centery - obj2.rect.centery
    collade_angle = (player.moving_speed).angle_to(collide_vector)
    pushOut_vector = pygame.Vector2(collide_vector)
    pushOut_vector.scale_to_length(obj2.radius + obj1.radius)
    pushOut_vector -= collide_vector
    obj2.rect.x -= pushOut_vector.x
    obj2.rect.y -= pushOut_vector.y



def chek_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                player.set_goal_speed_vector_case('top')
            elif event.key == pygame.K_s:
                player.set_goal_speed_vector_case('bot')
            elif event.key == pygame.K_a:
                player.set_goal_speed_vector_case('left')
            elif event.key == pygame.K_d:
                player.set_goal_speed_vector_case('right')

            elif event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

            elif event.key == pygame.K_e:
                spawn()
            elif event.key == pygame.K_t:
                spawn_one_big_solid()
            elif event.key == pygame.K_r:
                del_all()
            elif event.key == pygame.K_f:
                spawn_rect()
            elif event.key == pygame.K_g:
                spawn_light_obst()
            elif event.key == pygame.K_c:
                spawn_2()
            elif event.key == pygame.K_v:
                spawn_3()

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                player.set_goal_speed_vector_case('-top')
            elif event.key == pygame.K_s:
                player.set_goal_speed_vector_case('-bot')
            elif event.key == pygame.K_a:
                player.set_goal_speed_vector_case('-left')
            elif event.key == pygame.K_d:
                player.set_goal_speed_vector_case('-right')

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()

        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            global screen_rect 
            screen_rect = screen.get_rect()
        


def update_screen():
    screen.fill((100, 100, 100))
    pushing_sprites.draw(screen)
    screen.blit(player.image, player.rect)
    pygame.draw.line(screen, (0, 0, 0), player.rect.center,
                     player.rect.center + player.moving_speed * 10, 3)
    screen.blit(FPS, (screen_rect.right-110,screen_rect.top +10))
    screen.blit(objects_count, (screen_rect.left+10,screen_rect.top +10))
    screen.blit(info_hotkeys, (screen_rect.left+10,screen_rect.top +50))
    pygame.display.flip()

spawn_2()
spawn_3()

while True:
    clock.tick(60)
    #clock.tick_busy_loop(60)
    #clock.get_fps()
    FPS = font.render('FPS '+str(int(clock.get_fps())), True, (30, 30, 30))
    objects_count = font.render('объектов: '+ str(len(pushing_sprites)), True, (30, 30, 30))
    info_hotkeys = font_20.render('R - удалить всё. Спавить на C, V, F, G, E, T', True, (30, 30, 30))
    chek_events()
    player.moving()
    collisions(pushing_sprites)

    update_screen()
