import pygame
pygame.init()
from classes import joueur
from classes import game



pygame.display.set_caption("test")
screen = pygame.display.set_mode((1000,1000))
background = pygame.image.load('assets/mapdebase.png')
running = True
jeu = game()
while running :
    screen.blit(background,(0,0))
    screen.blit(jeu.joueur.image,jeu.joueur.rect)
    #verification déplacements
    """if jeu.pressed.get(pygame.K_RIGHT) and background.colour != rgba(33, 51, 0):
        jeu.joueur.move_right()
    elif jeu.pressed.get(pygame.K_LEFT):
        jeu.joueur.move_left()
    elif jeu.pressed.get(pygame.K_UP):
        jeu.joueur.move_up()
    elif jeu.pressed.get(pygame.K_DOWN):
        jeu.joueur.move_down()"""
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False
            pygame.quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT and background.colour != rgba(33, 51, 0):
                jeu.joueur.move_right()
            elif event.key == pygame.K_LEFT:
                jeu.joueur.move_left()
            elif event.key == pygame.K_UP:
                jeu.joueur.move_up()
            elif event.key == pygame.K_DOWN:
                jeu.joueur.move_down()

        couleur = background.get_at((jeu.joueur.rect.centerx, jeu.joueur.rect.centery))
        print(jeu.joueur.rect.centerx,jeu.joueur.rect.centery)
        print(couleur)