import pygame
from tool import tool
from keylistener import Keylistener
class Entity(pygame.sprite.Sprite):

    def __init__ (self,keylistener: Keylistener):
        super().__init__()
        self.keylistener = keylistener
        self.spritesheet = pygame.image.load()
        self.image=tool.split_image(self.spritesheet, 0, 0, 16, 32)
        self.position= [0,0]
        self.rect:pygame.Rect=pygame.Rect(0,0,16,32)

    def update (self):
        self.check_move()
        self.rect.topleft= self.position

    def check_move(self):
        if self.keylistener.key_pressed(pygame.K_q):
            self.move_left()
        elif self.keylistener.key_pressed(pygame.K_d):
            self.move_right()
        elif self.keylistener.key_pressed(pygame.K_z):
            self.move_up()
        elif self.keylistener.key_pressed(pygame.K_s):
            self.move_down()

    def move_left(self):
        self.position[0] -= 1

    def move_right(self):
        self.position[0] += 1

    def move_up(self):
        self.position[1] -= 1

    def move_down(self):
        self.position[1] -= 1