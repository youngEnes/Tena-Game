import pygame
pygame.init()

tir = pygame.USEREVENT + 1
pygame.time.set_timer(tir, 1000)
Lazer = (153,0,48)
Sol_Mort = (145,0,15)


class game:
    def __init__(self):
        self.joueur = joueur()

class joueur(pygame.sprite.Sprite) :
    def __init__(self):
        super().__init__()
        self.life = 10
        self.health = 1
        self.max_life = 10
        self.image = pygame.image.load('assets/princejeu.png')
        self.image_haut = pygame.image.load("assets/princededos.png")
        self.image_bas = pygame.image.load('assets/princejeu.png')
        self.image_gauche = pygame.image.load("assets/princegauche.png")
        self.image_droite = pygame.image.load("assets/princedroite.png")
        self.image_mort = pygame.image.load("assets/Mort.png")
        self.image_mort = pygame.transform.scale(self.image_mort,(100,100))
        self.image = pygame.transform.scale(self.image,(100,100))
        self.image_haut = pygame.transform.scale(self.image_haut,(100,100))
        self.image_bas = pygame.transform.scale(self.image_bas,(100,100))
        self.image_gauche = pygame.transform.scale(self.image_gauche,(100,100))
        self.image_droite = pygame.transform.scale(self.image_droite,(100,100))
        self.rect = self.image.get_rect()
        self.rect.x = 45
        self.rect.y = 35
    def move_right(self):
        self.rect.x += 80
    def move_left(self):
        self.rect.x -= 80
    def move_up(self):
        self.rect.y -= 80
    def move_down(self):
        self.rect.y += 80

    def degat(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0


class Boulet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/Boulet.png")
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = 10

    def update(self):
        self.rect.x -= self.velocity
        if self.rect.x > 1000:
            self.kill()


class Canon:
    def __init__(self):
        self.image = pygame.image.load("assets/Canon.png")
        self.rect = self.image.get_rect()
        self.rect.x = 800
        self.rect.y = 800
        self.projectiles = pygame.sprite.Group()

    def launch_projectile(self):
        boulet = Boulet(self.rect.centerx, self.rect.centery)
        self.projectiles.add(boulet)


class Laser:

    def __init__(self):
        self.image= pygame.image.load('assets/laser.png')
        self.rect = self.image.get_rect()
        self.rect.x = 385
        self.rect.y = 710


screen = pygame.display.set_mode((1000, 1000))
pygame.display.set_caption("blah")
background = pygame.image.load("assets/map_7.png")


canon = Canon()
laser = Laser()
clock = pygame.time.Clock()
jeu = game()
running = True



while running:
    couleur = background.get_at((jeu.joueur.rect.centerx, jeu.joueur.rect.centery))[:3]
    screen.blit(background, (0, 0))
    screen.blit(canon.image, canon.rect)
    screen.blit(jeu.joueur.image,jeu.joueur.rect)
    screen.blit(laser.image,laser.rect)
    canon.projectiles.update()
    canon.projectiles.draw(screen)

    for boulet in canon.projectiles:
        if (boulet.rect.centerx // 80 == jeu.joueur.rect.centerx // 80 and
    boulet.rect.centery // 80 == jeu.joueur.rect.centery // 80):
            jeu.joueur.degat(jeu.joueur.health)
            boulet.kill()
            jeu.joueur.life -=1
            jeu.joueur.rect.x = 445
            jeu.joueur.rect.y = 43
            if jeu.joueur.life == 0:
                running= False

    if couleur == Lazer:
        jeu.joueur.image = jeu.joueur.image_mort
        jeu.joueur.life -=1
        jeu.joueur.rect.x = 445
        jeu.joueur.rect.y = 43
        if jeu.joueur.life == 0:
             running = False

    if couleur == Sol_Mort:
        jeu.joueur.image = jeu.joueur.image_mort
        jeu.joueur.life -=1
        jeu.joueur.rect.x = 445
        jeu.joueur.rect.y = 43
        if jeu.joueur.life == 0:
             running = False


    pygame.display.flip()



    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == tir :
            canon.launch_projectile()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT and jeu.joueur.rect.x<800:
                jeu.joueur.move_right()
                jeu.joueur.image= jeu.joueur.image_droite
            elif event.key == pygame.K_LEFT and jeu.joueur.rect.x>80:
                jeu.joueur.move_left()
                jeu.joueur.image = jeu.joueur.image_gauche
            elif event.key == pygame.K_UP and jeu.joueur.rect.y>80:
                jeu.joueur.move_up()
                jeu.joueur.image = jeu.joueur.image_haut
            elif event.key == pygame.K_DOWN and jeu.joueur.rect.y < 800:
                jeu.joueur.move_down()
                jeu.joueur.image = jeu.joueur.image_bas

clock.tick(60)

pygame.quit()
