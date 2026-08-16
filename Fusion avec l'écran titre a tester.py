import pygame
import pytmx
import pyscroll
pygame.init()

HAUTEUR = 800
LARGEUR = 800
HISTOIRE = "histoire"
SPEEDRUN = "speedrun"
TITRE = "meilleur jeu all time"

class Keylistener:
    def __init__(self):
        self.keys:list[int]=[]
    def add_key(self,key):
        if key not in self.keys:
            self.keys.append(key)

    def remove_key(self,key):
        if key in self.keys:
            self.keys.remove(key)

    def key_pressed(self,key):
        return key in self.keys

    def clear(self):
        self.keys.clear()
class tool:
    @staticmethod
    def split_image(spritesheet:pygame.Surface,x:int,y:int,width:int,height:int):
        return spritesheet.subsurface(pygame.Rect(x,y,width,height))
class entity(pygame.sprite.Sprite):
    def __init__(self):
        self.spritesheet = pygame.image.load("assets/princejeu.png")
class Screen:

    def __init__(self):
        self.display = pygame.display.set_mode((HAUTEUR,LARGEUR))
        pygame.display.set_caption("Blah")
        self.clock = pygame.time.Clock()
        self.framerate = 30


    def update(self):
        pygame.display.flip()
        pygame.display.update()
        self.clock.tick(self.framerate)


    def get_size(self):
        return self.display.get_size()

    def get_display(self):
        return self.display
class Map:

    def __init__(self,screen: Screen):
        self.screen = screen
        self.tmx_data  = None
        self.map_layer = None
        self.group = None
        self.player = None

    def switch_map(self,map):
        self.tmx_data = pytmx.load_pygame ("assets/map_1bienavancé.tmx")
        map_data= pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data,self.screen.get_size())
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer,default_layer=7)
        self.map_layer.zoom = 0.67

    def add_player(self,player):
        self.player = player
        self.group.add(player,layer = 8)

    def update(self):
        self.group.update()
        self.group.center(self.player.rect.center)
        self.group.draw(self.screen.get_display())
class Entity(pygame.sprite.Sprite):
    def __init__(self, keylistener: Keylistener):
        super().__init__()
        self.keylistener = keylistener

        self.sprites = {
            "bas":    pygame.image.load("assets/princejeu.png").convert_alpha(),
            "gauche": pygame.image.load("assets/princegauche.png").convert_alpha(),
            "haut":   pygame.image.load("assets/princededos.png").convert_alpha(),
            "droite": pygame.image.load("assets/princedroite.png").convert_alpha(),
        }

        self.direction = "bas"
        self.image = pygame.transform.scale(self.sprites[self.direction], (120, 120))
        self.rect = pygame.Rect(75, 80, 120, 120)

        self.move_cooldown = 150
        self.last_move_time = 0

    def update(self):
        self.check_move()

    def check_move(self):
        now = pygame.time.get_ticks()
        if now - self.last_move_time < self.move_cooldown:
            return

        moved = False

        if self.keylistener.key_pressed(pygame.K_q):
            self.rect.x -= 90
            self.direction = "gauche"
            moved = True
        elif self.keylistener.key_pressed(pygame.K_d):
            self.rect.x += 90
            self.direction = "droite"
            moved = True
        elif self.keylistener.key_pressed(pygame.K_z):
            self.rect.y -= 90
            self.direction = "haut"
            moved = True
        elif self.keylistener.key_pressed(pygame.K_s):
            self.rect.y += 90
            self.direction = "bas"
            moved = True

        if moved:
            # Met à jour le sprite selon la direction
            self.image = pygame.transform.scale(self.sprites[self.direction], (120, 120))
            self.last_move_time = now

class Game:

        def __init__(self):
            self.running = True
            self.screen = Screen()
            self.map= Map(self.screen)
            self.keylistener = Keylistener()
            self.entity= Entity(self.keylistener)
            self.map.switch_map("mapdebase")
            self.map.add_player(self.entity)

        def run(self):
            while self.running:
                self.handle_input()
                self.screen.display.fill((0,0,0))
                self.map.update()
                pygame.display.flip()
                self.screen.clock.tick(self.screen.framerate)

        def handle_input(self):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    self.keylistener.add_key(event.key)
                elif event.type == pygame.KEYUP:
                    self.keylistener.remove_key(event.key)


class Bouton:
    def __init__(self, texte, x, y, largeur, hauteur, action):
        self.text = texte
        self.action = action
        self.rect = pygame.Rect(x, y, largeur, hauteur)
        self.curseur = False
        self.police = pygame.font.SysFont("arial", 35)

    def draw(self, surface):
        if self.curseur:
            couleur_fond = (60, 60, 180)
            couleur_bord = (255, 255, 255)
        else:
            couleur_fond = (40, 40, 120)
            couleur_bord = (100, 100, 200)

        pygame.draw.rect(surface, couleur_fond, self.rect, border_radius=10)
        pygame.draw.rect(surface, couleur_bord, self.rect, width=3, border_radius=10)

        texte_surface = self.police.render(self.text, True, (255, 255, 255))
        surface.blit(texte_surface, texte_surface.get_rect(center=self.rect.center))

    def update(self, pos_souris):
        self.curseur = self.rect.collidepoint(pos_souris)

    def click(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


class Titlescreen:
    def __init__(self, screen):
        self.screen = screen
        self.police_titre = pygame.font.SysFont("arial", 80, bold=True)
        self.police_aide  = pygame.font.SysFont("arial", 35)

        largeur_fenetre = screen.get_size()[0]
        largeur_btn = 300
        hauteur_btn = 80
        centre_x = largeur_fenetre // 2 - largeur_btn // 2

        self.btn_histoire = Bouton("Mode Histoire", centre_x, 400, largeur_btn, hauteur_btn, HISTOIRE)
        self.btn_speedrun = Bouton("Mode Speedrun", centre_x, 510, largeur_btn, hauteur_btn, SPEEDRUN)

    def gerer_event(self, event):
        if self.btn_histoire.click(event):
            return HISTOIRE
        if self.btn_speedrun.click(event):
            return SPEEDRUN
        return None

    def update(self):
        souris = pygame.mouse.get_pos()
        self.btn_histoire.update(souris)
        self.btn_speedrun.update(souris)

    def draw(self):
        surface = self.screen.get_display()
        surface.fill((15, 15, 50))

        titre = self.police_titre.render("Dungeons Speedster", True, (255, 220, 50))
        surface.blit(titre, titre.get_rect(center=(400, 200)))

        aide = self.police_aide.render("Choisissez un mode de jeu", True, (180, 180, 255))
        surface.blit(aide, aide.get_rect(center=(400, 330)))

        self.btn_histoire.draw(surface)
        self.btn_speedrun.draw(surface)
if __name__ == '__main__':
    screen = Screen()
    titlescreen = Titlescreen(screen)
    mode = None

    while mode is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            result = titlescreen.gerer_event(event)
            if result is not None:
                mode = result

        titlescreen.update()
        titlescreen.draw()
        pygame.display.flip()
        screen.clock.tick(screen.framerate)

    game = Game()
    game.run()