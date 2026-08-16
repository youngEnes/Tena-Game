import pygame
import pytmx
import pyscroll
pygame.init()

HAUTEUR = 800
LARGEUR = 800
HISTOIRE = "histoire"
SPEEDRUN = "speedrun"
TITRE = "meilleur jeu all time"


MAPS = [
    {
        "fichier": "assets/map_1murcollision.tmx",
        "tuiles_escalier": [4],
        "escalier_pos": None,
        "spawn": (100, 100),
    },
    {
        "fichier": "assets/map_2bienavancé.tmx",
        "tuiles_escalier": [14, 2],
        "escalier_pos": [(11, 11), (11, 7)],
    },
    {
        "fichier": "assets/map_3bienavancé.tmx",
        "tuiles_escalier": [4],
        "escalier_pos": [(11, 10), (11, 11)],
    },
    {
        "fichier": "assets/map_4bienavancé.tmx",
        "tuiles_escalier": [3],
        "escalier_pos": [(11, 1), (11, 3), (11, 5), (11, 7), (11, 9), (11, 11)],
    },
    {
        "fichier": "assets/map_5bienavancé.tmx",
        "tuiles_escalier": [7],
        "escalier_pos": [(11, 10)],
    },
    {
        "fichier": "assets/map_6bienavancé.tmx",
        "tuiles_escalier": [28],
        "escalier_pos": [(11, 2), (11, 6), (11, 10)],
    },
]


class Keylistener:
    def __init__(self):
        self.keys: list[int] = []

    def add_key(self, key):
        if key not in self.keys:
            self.keys.append(key)

    def remove_key(self, key):
        if key in self.keys:
            self.keys.remove(key)

    def key_pressed(self, key):
        return key in self.keys

    def clear(self):
        self.keys.clear()


class Screen:
    def __init__(self):
        self.display = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Dungeons Speedster")
        self.clock = pygame.time.Clock()
        self.framerate = 30

    def update(self):
        pygame.display.flip()
        self.clock.tick(self.framerate)

    def get_size(self):
        return self.display.get_size()

    def get_display(self):
        return self.display


class Map:
    def __init__(self, screen: Screen):
        self.screen = screen
        self.tmx_data = None
        self.map_layer = None
        self.group = None
        self.player = None
        self.tuiles_escalier = []
        self.escalier_pos = None

    def switch_map(self, fichier_map: str, tuiles_escalier: list, escalier_pos=None):
        self.tuiles_escalier = tuiles_escalier
        self.escalier_pos = escalier_pos
        self.tmx_data = pytmx.load_pygame(fichier_map)
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.screen.get_size())
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=7)
        self.map_layer.zoom = 0.67
        if self.player is not None:
            self.group.add(self.player, layer=8)

    def add_player(self, player):
        self.player = player
        self.group.add(player, layer=8)

    def joueur_sur_escalier(self) -> bool:
        if self.player is None or self.tmx_data is None:
            return False

        tw = self.tmx_data.tilewidth
        th = self.tmx_data.tileheight

        offset = self.map_layer.get_center_offset()
        map_x = self.player.rect.centerx - offset[0]
        map_y = self.player.rect.centery - offset[1]

        col = int(map_x // tw)
        ligne = int(map_y // th)

        for layer in self.tmx_data.layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                if 0 <= ligne < layer.height and 0 <= col < layer.width:
                    gid = layer.data[ligne][col]
                    if gid in self.tuiles_escalier and (self.escalier_pos is None or (col, ligne) in self.escalier_pos):
                        return True
        return False

    def update(self):
        if self.group is None:
            return
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

    def teleporter_haut_gauche(self):
        self.rect.x = 75
        self.rect.y = 75
        self.direction = "bas"
        self.image = pygame.transform.scale(self.sprites[self.direction], (120, 120))

    def respawn(self):
        self.rect.x = 75
        self.rect.y = 80
        self.direction = "bas"
        self.image = pygame.transform.scale(self.sprites[self.direction], (120, 120))

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
            self.image = pygame.transform.scale(self.sprites[self.direction], (120, 120))
            self.last_move_time = now


class Game:
    def __init__(self):
        self.running = True
        self.screen = Screen()
        self.map = Map(self.screen)
        self.keylistener = Keylistener()
        self.entity = Entity(self.keylistener)

        self.map_actuelle_index = 0

        infos = MAPS[self.map_actuelle_index]
        self.map.switch_map(infos["fichier"], infos["tuiles_escalier"], infos.get("escalier_pos"))
        self.map.add_player(self.entity)

        self.cooldown_transition = 1000
        self.dernier_changement = pygame.time.get_ticks()

        self.pieges_actifs = False
        self.dernier_rythme = pygame.time.get_ticks()
        self.intervalle_rythme = 2000
        self.bouton_appuye = False

    def changer_map(self):
        self.map_actuelle_index += 1
        if self.map_actuelle_index >= len(MAPS):
            print("Félicitations !")
            self.map_actuelle_index = 0

        infos = MAPS[self.map_actuelle_index]
        self.map.switch_map(
            infos["fichier"],
            infos["tuiles_escalier"],
            infos.get("escalier_pos")
        )
        self.entity.teleporter_haut_gauche()
        self.dernier_changement = pygame.time.get_ticks()

    def verifier_pieges(self):
        tw = self.map.tmx_data.tilewidth
        th = self.map.tmx_data.tileheight
        offset = self.map.map_layer.get_center_offset()
        map_x = self.entity.rect.centerx - offset[0]
        map_y = self.entity.rect.centery - offset[1]
        col = int(map_x // tw)
        ligne = int(map_y // th)

        print(f"col={col} ligne={ligne}")

        if self.map_actuelle_index == 0:
            sur_bouton = (col == 5 and ligne == 5)
            self.bouton_appuye = sur_bouton

            if sur_bouton:
                return

            if self.pieges_actifs:
                for layer in self.map.tmx_data.layers:
                    if isinstance(layer, pytmx.TiledTileLayer) and "piège" in layer.name:
                        if 0 <= ligne < layer.height and 0 <= col < layer.width:
                            gid = layer.data[ligne][col]
                            if gid != 0:
                                self.entity.respawn()
                                return
        else:
            for layer in self.map.tmx_data.layers:
                if isinstance(layer, pytmx.TiledTileLayer) and "piège" in layer.name:
                    if 0 <= ligne < layer.height and 0 <= col < layer.width:
                        gid = layer.data[ligne][col]
                        if gid != 0:
                            self.entity.respawn()
                            return

    def run(self):
        while self.running:
            self.handle_input()
            self.screen.display.fill((0, 0, 0))
            self.map.update()

            now = pygame.time.get_ticks()

            if self.map_actuelle_index == 0:
                if now - self.dernier_rythme > self.intervalle_rythme:
                    self.pieges_actifs = not self.pieges_actifs
                    self.dernier_rythme = now

                if self.bouton_appuye:
                    couleur_feu = (0, 200, 0)
                else:
                    couleur_feu = (200, 0, 0) if self.pieges_actifs else (0, 200, 0)
                pygame.draw.circle(self.screen.get_display(), (30, 30, 30), (40, 40), 28)
                pygame.draw.circle(self.screen.get_display(), couleur_feu, (40, 40), 20)

            self.verifier_pieges()

            if now - self.dernier_changement > self.cooldown_transition:
                if self.map.joueur_sur_escalier():
                    self.changer_map()

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
        self.police_aide = pygame.font.SysFont("arial", 35)

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