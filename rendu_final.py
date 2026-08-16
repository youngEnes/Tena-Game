import pygame
import pytmx
import pyscroll
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
pygame.init()
 
Hauteur = 800
Largeur = 800
Histoire = "histoire"
Speedrun = "speedrun"
Titre = "meilleur jeu all time"
 
 
Maps = [
    {
        "fichier": "assets/map_1bienavancé.tmx",
        "tuiles_escalier": [4],
        "escalier_pos": None,
        "bouton": (5, 5),
        "pieges_rythme": True,
    },
    {
        "fichier": "assets/map_2bienavancé.tmx",
        "tuiles_escalier": [14, 2],
        "escalier_pos": [(11, 11), (11, 7)],
        "bouton": (5, 5),
        "pieges_rythme": False,
    },
    {
        "fichier": "assets/Map_3bienavancé.tmx",
        "tuiles_escalier": [4],
        "escalier_pos": [(11, 10), (11, 11)],
        "bouton": None,
        "pieges_rythme": False,
    },
    {
        "fichier": "assets/map_4bienavancé.tmx",
        "tuiles_escalier": [3],
        "escalier_pos": [(11, 1), (11, 3), (11, 5), (11, 7), (11, 9), (11, 11)],
        "bouton": None,
        "pieges_rythme": False,
    },
    {
        "fichier": "assets/map_5bienavancé.tmx",
        "tuiles_escalier": [7],
        "escalier_pos": [(11, 10)],
        "bouton": None,
        "pieges_rythme": False,
    },
    {
        "fichier": "assets/map_6bienavancé.tmx",
        "tuiles_escalier": [294],
        "escalier_pos": [(11, 2), (11, 6), (11, 10)],
        "bouton": None,
        "pieges_rythme": False,
        "victoire": True,
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
        self.display = pygame.display.set_mode((Largeur, Hauteur))
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
        self.rects_collision: list[pygame.Rect] = []
 
    def switch_map(self, fichier_map: str, tuiles_escalier: list, escalier_pos=None):
        self.tuiles_escalier = tuiles_escalier
        self.escalier_pos = escalier_pos
        self.tmx_data = pytmx.load_pygame(fichier_map)
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.screen.get_size())
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=7)
        self.map_layer.zoom = 0.67
        self.charger_collisions()
        if self.player is not None:
            self.group.add(self.player, layer=8)
 
    def charger_collisions(self):
        self.rects_collision = []
        if self.tmx_data is None:
            return
        for layer in self.tmx_data.layers:
            if isinstance(layer, pytmx.TiledObjectGroup) and "collision" in layer.name.lower():
                for obj in layer:
                    rect = pygame.Rect(
                        int(obj.x), int(obj.y),
                        int(obj.width), int(obj.height)
                    )
                    self.rects_collision.append(rect)
 
    def add_player(self, player):
        self.player = player
        self.group.add(player, layer=8)
 
    def en_collision(self, rect: pygame.Rect) -> bool:
        for r in self.rects_collision:
            if rect.colliderect(r):
                return True
        return False
 
    def joueur_sur_escalier(self) -> bool:
        if self.player is None or self.tmx_data is None:
            return False
 
        tw = self.tmx_data.tilewidth
        th = self.tmx_data.tileheight
 
        offset = self.map_layer.get_center_offset()
        map_x = self.player.hitbox.centerx - offset[0]
        map_y = self.player.hitbox.centery - offset[1]
 
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
 
        self.taille_sprite = 120
        self.taille_hitbox = 40
        self.direction = "bas"
 
        self.rect = pygame.Rect(90, 90, 90, 90)
        self.hitbox = pygame.Rect(
            self.rect.centerx - self.taille_hitbox // 2,
            self.rect.centery - self.taille_hitbox // 2,
            self.taille_hitbox, self.taille_hitbox
        )
        self.image = self._make_image(self.direction)
 
        self.move_cooldown = 150
        self.last_move_time = 0
        self.map: Map | None = None
 
    def _make_image(self, direction):
        ts = self.taille_sprite
        tuile = 90
        offset = (ts - tuile) // 2
        surface = pygame.Surface((tuile, tuile), pygame.SRCALPHA)
        sprite = pygame.transform.scale(self.sprites[direction], (ts, ts))
        surface.blit(sprite, (-offset, -offset))
        return surface
 
    def _sync_hitbox(self):
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.centery = self.rect.centery
 
    def teleporter_haut_gauche(self):
        self.rect.x = 90
        self.rect.y = 90
        self._sync_hitbox()
        self.direction = "bas"
        self.image = self._make_image(self.direction)
 
    def respawn(self):
        self.rect.x = 90
        self.rect.y = 90
        self._sync_hitbox()
        self.direction = "bas"
        self.image = self._make_image(self.direction)
 
    def update(self):
        self.check_move()
 
    def check_move(self):
        now = pygame.time.get_ticks()
        if now - self.last_move_time < self.move_cooldown:
            return
 
        pas = 90
        dx, dy = 0, 0
        new_direction = self.direction
 
        if self.keylistener.key_pressed(pygame.K_q):
            dx = -pas
            new_direction = "gauche"
        elif self.keylistener.key_pressed(pygame.K_d):
            dx = pas
            new_direction = "droite"
        elif self.keylistener.key_pressed(pygame.K_z):
            dy = -pas
            new_direction = "haut"
        elif self.keylistener.key_pressed(pygame.K_s):
            dy = pas
            new_direction = "bas"
 
        if dx != 0 or dy != 0:
            if self.map is not None:
                pas_x = 1 if dx > 0 else -1 if dx < 0 else 0
                pas_y = 1 if dy > 0 else -1 if dy < 0 else 0
                restant_x = abs(dx)
                restant_y = abs(dy)
 
                while restant_x > 0 or restant_y > 0:
                    if restant_x > 0:
                        future = self.hitbox.move(pas_x, 0)
                        if not self.map.en_collision(future):
                            self.rect.move_ip(pas_x, 0)
                            self._sync_hitbox()
                        else:
                            restant_x = 0
                        restant_x -= 1
                    if restant_y > 0:
                        future = self.hitbox.move(0, pas_y)
                        if not self.map.en_collision(future):
                            self.rect.move_ip(0, pas_y)
                            self._sync_hitbox()
                        else:
                            restant_y = 0
                        restant_y -= 1
            else:
                self.rect.move_ip(dx, dy)
                self._sync_hitbox()
 
            self.direction = new_direction
            self.image = self._make_image(self.direction)
            self.last_move_time = now
 
 
class Game:
    def __init__(self):
        self.running = True
        self.screen = Screen()
        self.map = Map(self.screen)
        self.keylistener = Keylistener()
        self.entity = Entity(self.keylistener)
        self.entity.map = self.map
 
        self.map_actuelle_index = 0
 
        infos = Maps[self.map_actuelle_index]
        self.map.switch_map(infos["fichier"], infos["tuiles_escalier"], infos.get("escalier_pos"))
        self.map.add_player(self.entity)
 
        self.cooldown_transition = 1000
        self.dernier_changement = pygame.time.get_ticks()
 
        self.pieges_actifs = False
        self.dernier_rythme = pygame.time.get_ticks()
        self.intervalle_rythme = 2000
        self.bouton_appuye = False
        self.joueur_etait_sur_bouton = False
        self.joueur_etait_sur_piege = False
 
        self.cases_pieges_visitees = set()
        self.derniere_case_joueur = None
 
        self.ecran_gg = False
        self.mode = Histoire
        self.timer_debut = None
        self.temps_final = 0
 
    def changer_map(self):
        self.map_actuelle_index += 1
        if self.map_actuelle_index >= len(Maps):
            print("Félicitations !")
            self.map_actuelle_index = 0
 
        infos = Maps[self.map_actuelle_index]
        self.map.switch_map(
            infos["fichier"],
            infos["tuiles_escalier"],
            infos.get("escalier_pos")
        )
        self.entity.teleporter_haut_gauche()
        self.dernier_changement = pygame.time.get_ticks()
        self.pieges_actifs = False
        self.bouton_appuye = False
        self.joueur_etait_sur_bouton = False
        self.joueur_etait_sur_piege = False
        self.dernier_rythme = pygame.time.get_ticks()
 

        self.cases_pieges_visitees = set()
        self.derniere_case_joueur = None
 
    def get_position_joueur(self):
        tw = self.map.tmx_data.tilewidth
        th = self.map.tmx_data.tileheight
        offset = self.map.map_layer.get_center_offset()
        map_x = self.entity.hitbox.centerx - offset[0]
        map_y = self.entity.hitbox.centery - offset[1]
        col = int(map_x // tw)
        ligne = int(map_y // th)
        return col, ligne
 
    def verifier_victoire(self):
        if self.map.tmx_data is None:
            return
        for layer in self.map.tmx_data.layers:
            if isinstance(layer, pytmx.TiledObjectGroup) and layer.name.lower() == "fin":
                for obj in layer:
                    obj_rect = pygame.Rect(int(obj.x), int(obj.y), int(obj.width), int(obj.height))
                    offset = self.map.map_layer.get_center_offset()
                    hitbox_map = pygame.Rect(
                        self.entity.hitbox.x - offset[0],
                        self.entity.hitbox.y - offset[1],
                        self.entity.hitbox.width,
                        self.entity.hitbox.height
                    )
                    if hitbox_map.colliderect(obj_rect):
                        if self.mode == Speedrun and self.timer_debut is not None:
                            self.temps_final = (pygame.time.get_ticks() - self.timer_debut) / 1000
                        self.ecran_gg = True
 
    def afficher_gg(self):
        surface = self.screen.get_display()
        surface.fill((55, 35, 70))
        police = pygame.font.SysFont("arial", 160, bold=True)
        texte = police.render("GG", True, (180, 180, 180))
        surface.blit(texte, texte.get_rect(center=(Largeur // 2, Hauteur // 2 - 80)))
        if self.mode == Speedrun:
            police_temps = pygame.font.SysFont("arial", 60, bold=True)
            minutes = int(self.temps_final // 60)
            secondes = int(self.temps_final % 60)
            centi = int((self.temps_final * 100) % 100)
            texte_temps = police_temps.render(f"Temps : {minutes:02d}:{secondes:02d}.{centi:02d}", True, (200, 200, 200))
            surface.blit(texte_temps, texte_temps.get_rect(center=(Largeur// 2, Hauteur // 2 + 80)))
 
    def verifier_pieges(self):
        col, ligne = self.get_position_joueur()
        infos = Maps[self.map_actuelle_index]
        bouton_pos = infos.get("bouton")
        pieges_rythme = infos.get("pieges_rythme", False)
 
        sur_bouton = (bouton_pos is not None and col == bouton_pos[0] and ligne == bouton_pos[1])
 
        if pieges_rythme:

            self.bouton_appuye = sur_bouton
        else:

            if sur_bouton and not self.joueur_etait_sur_bouton:
                self.bouton_appuye = not self.bouton_appuye
        self.joueur_etait_sur_bouton = sur_bouton
 
        if self.bouton_appuye:
            return
 

        if pieges_rythme:
            pieges_dangereux = self.pieges_actifs
        else:
            pieges_dangereux = True
 
        if not pieges_dangereux:
            return
 
        sur_piege = False
        for layer in self.map.tmx_data.layers:
            if isinstance(layer, pytmx.TiledTileLayer) and "piège" in layer.name:
                if 0 <= ligne < layer.height and 0 <= col < layer.width:
                    gid = layer.data[ligne][col]
                    if gid != 0:
                        sur_piege = True
                        break
 
        if sur_piege:
            if self.map_actuelle_index == 2:
                pos_actuelle = (col, ligne)
                if pos_actuelle != self.derniere_case_joueur:
                    self.derniere_case_joueur = pos_actuelle
                    if pos_actuelle in self.cases_pieges_visitees:
                        self.entity.respawn()
                        self.cases_pieges_visitees = set()
                        self.derniere_case_joueur = None
                        return
                    else:
                        self.cases_pieges_visitees.add(pos_actuelle)
            else:
                if not self.joueur_etait_sur_piege:
                    self.entity.respawn()
        else:
            if self.map_actuelle_index != 2:
                pass
 
        self.joueur_etait_sur_piege = sur_piege
 
    def run(self):
        while self.running:
            if self.ecran_gg:
                self.afficher_gg()
                pygame.display.flip()
                self.screen.clock.tick(self.screen.framerate)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        pygame.quit()
                        return
                continue
 
            self.handle_input()
            self.screen.display.fill((0, 0, 0))
            self.map.update()
 
            now = pygame.time.get_ticks()
            infos = Maps[self.map_actuelle_index]
 
            if infos.get("pieges_rythme"):
                if now - self.dernier_rythme > self.intervalle_rythme:
                    self.pieges_actifs = not self.pieges_actifs
                    self.dernier_rythme = now
 
            if infos.get("bouton") is not None:
                if infos.get("pieges_rythme"):
                    couleur = (0, 200, 0) if not self.pieges_actifs or self.bouton_appuye else (200, 0, 0)
                else:
                    couleur = (0, 200, 0) if self.bouton_appuye else (200, 0, 0)
                pygame.draw.rect(self.screen.get_display(), couleur, (20, 20, 40, 40))
 
            self.verifier_pieges()

            if self.mode == Speedrun and self.timer_debut is not None:
                elapsed = (pygame.time.get_ticks() - self.timer_debut) / 1000
                minutes = int(elapsed // 60)
                secondes = int(elapsed % 60)
                centimes = int((elapsed * 100) % 100)
                police_timer = pygame.font.SysFont("arial", 36, bold=True)
                texte_timer = police_timer.render(f"{minutes:02d}:{secondes:02d}.{centimes:02d}", True, (0, 0, 0))
                self.screen.get_display().blit(texte_timer, (Largeur - texte_timer.get_width() - 20, 20))

            if infos.get("victoire"):
                self.verifier_victoire()
 
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
            couleur_fond = (120, 120, 120)
            couleur_bord = (200, 200, 200)
        else:
            couleur_fond = (80, 80, 80)
            couleur_bord = (140, 140, 140)
 
        pygame.draw.rect(surface, couleur_fond, self.rect, border_radius=10)
        pygame.draw.rect(surface, couleur_bord, self.rect, width=3, border_radius=10)
 
        texte_surface = self.police.render(self.text, True, (210, 210, 210))
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
 
        self.btn_histoire = Bouton("Mode Histoire", centre_x, 400, largeur_btn, hauteur_btn, Histoire)
        self.btn_speedrun = Bouton("Mode Speedrun", centre_x, 510, largeur_btn, hauteur_btn, Speedrun)
 
    def gerer_event(self, event):
        if self.btn_histoire.click(event):
            return Histoire
        if self.btn_speedrun.click(event):
            return Speedrun
        return None
 
    def update(self):
        souris = pygame.mouse.get_pos()
        self.btn_histoire.update(souris)
        self.btn_speedrun.update(souris)
 
    def draw(self):
        surface = self.screen.get_display()
        surface.fill((55, 35, 70))
 
        titre = self.police_titre.render("Dungeons Speedster", True, (180, 180, 180))
        surface.blit(titre, titre.get_rect(center=(400, 200)))
 
        aide = self.police_aide.render("Choisissez un mode de jeu", True, (150, 150, 150))
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
    game.mode = mode
    if mode == Speedrun:
        game.timer_debut = pygame.time.get_ticks()
    game.run()
