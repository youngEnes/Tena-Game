import pygame

class game:
    def __init__(self):
        self.joueur = joueur()

class joueur(pygame.sprite.Sprite) :
    def __init__(self):
        super().__init__()
        self.health = 10
        self.max_health = 10
        self.image = pygame.image.load('assets/princejeu.png')
        self.image = pygame.transform.scale(self.image,(100,100))
        self.rect = self.image.get_rect()
        self.rect.x = 445
        self.rect.y = 43
    def move_right(self):
        self.rect.x += 80
    def move_left(self):
        self.rect.x -= 80
    def move_up(self):
        self.rect.y -= 80
    def move_down(self):
        self.rect.y += 80