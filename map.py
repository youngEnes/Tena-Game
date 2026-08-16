import pygame
import pytmx
import pyscroll
from joueur import entity
from Ecran import Screen

class Map:

    def __init__(self,screen: Screen):
        self.screen = screen
        self.tmx_data  = None
        self.map_layer = None
        self.group = None
        self.player = None

    def switch_map(self,map):
        self.tmx_data = pytmx.load_pygame ("assets"/"mapdebase.tmx")
        map_data= pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.Buffered(map_data,self.screen.get_size())
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer,default_layer=7)

    def add_player(self,player):
        self.group.add(player)

    def update(self):
        self.group.update()
        self.group.center(self.player)
        self.group.draw(self.screen.get_display())
