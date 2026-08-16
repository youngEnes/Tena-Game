import pygame
pygame.init()

from Ecran import Screen
from map import Map
from Entity import Entity
from keylistener import Keylistener
class Game:

        def __init__(self):
            self.running = True
            self.screen = Screen()
            self.map= Map(self.screen)
            self.keylistener = Keylistener()
            self.Entity= Entity(self.keylistener)
            self.map.add_player(self.Entity)

        def run(self):
            while self.running:
                self.handle_input()
                self.map_update()
                self.screen.update()

        def handle_input(self):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    self.keylistener.add_key(event.key)
                elif event.type == pygame.KEYUP:
                    self.keylistener.remove_key(event.key)
#19:19 vidéo

