# Créé par danan, le 26/05/2026 en Python 3.7
import pygame
import pytmx
import pyscroll
import sys

pygame.init()

HAUTEUR = 800
LARGEUR = 800
HISTOIRE = "histoire"
SPEEDRUN = "speedrun"
TITRE = "meilleur jeu all time"


MAPS = [
    {
        "fichier": "assets/map_1bienavancé.tmx",
        "tuiles_escalier": [1170, 1183],
    },
    {
        "fichier": "assets/map_2bienavancé.tmx",
        "tuiles_escalier": [125],
    },
    {
        "fichier": "assets/map_3bienavancé.tmx",
        "tuiles_escalier": [281, 294],
    },
    {
        "fichier": "assets/map_4bienavancé.tmx",
        "tuiles_escalier": [294],
    },
    {
        "fichier": "assets/map_5bienavancé.tmx",
        "tuiles_escalier": [119],
    },
    {
        "fichier": "assets/map_7bienavancé.tmx",
        "tuiles_escalier": [294],
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

    def switch_map(self, fichier_map: str, tuiles_escalier: list[int]):
        """Charge une nouvelle map depuis son fichier .tmx."""
        self.tuiles_escalier = tuiles_escalier

        self.tmx_data = pytmx.load_pygame(fichier_map)
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.screen.get_size())
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=7)
        self.map_layer.zoom = 0.67

        # Ré-ajoute le joueur si on en a déjà un
        if self.player is not None:
            self.group.add(self.player, layer=8)

    def add_player(self, player):
        self.player = player
        self.group.add(player, layer=8)

    def joueur_sur_escalier(self) -> bool:
        """
        Renvoie True si le joueur se trouve sur une tuile escalier.
        On vérifie toutes les couches de la map.
        """
        if self.player is None or self.tmx_data is None:
            return False

        # Taille d'une tuile en pixels
        tw = self.tmx_data.tilewidth
        th = self.tmx_data.tileheight

        # Centre du joueur en pixels
        cx = self.player.rect.centerx
        cy = self.player.rect.centery

        # Convertit en coordonnées de grille
        col = cx // tw
        ligne = cy // th

        # Cherche dans chaque couche de tuiles
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                gid = layer.data[ligne][col] if 0 <= ligne < layer.height and 0 <= col < layer.width else 0
                if gid in self.tuiles_escalier:
                    return True
        return False

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

    def teleporter_haut_gauche(self):
        """Place le joueur en haut à gauche de la map (après une transition)."""
        self.rect.x = 100   # légèrement à l'intérieur des murs
        self.rect.y = 100
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
    def __init__(self, mode):
        self.running = True
        self.screen = Screen()
        self.map = Map(self.screen)
        self.keylistener = Keylistener()
        self.entity = Entity(self.keylistener)
        self.mode = mode  # Sauvegarde du mode choisi (HISTOIRE ou SPEEDRUN)

        # Index de la map actuelle dans la liste MAPS
        self.map_actuelle_index = 0

        # Charge la première map
        infos = MAPS[self.map_actuelle_index]
        self.map.switch_map(infos["fichier"], infos["tuiles_escalier"])
        self.map.add_player(self.entity)

        # Petit délai pour éviter de changer de map dès l'apparition
        self.cooldown_transition = 1000   # en millisecondes
        self.dernier_changement = pygame.time.get_ticks()

        # Variables pour le Chronomètre (Speedrun)
        self.temps_debut_partie = pygame.time.get_ticks()
        self.temps_debut_map = pygame.time.get_ticks()
        self.temps_par_map = []  # Stocke le temps mis pour chaque map
        self.police_chrono = pygame.font.SysFont("arial", 28, bold=True)
        self.partie_terminee = False

    def formater_temps(self, ms):
        """Convertit des millisecondes en chaîne de caractères mm:ss.cc"""
        minutes = ms // 60000
        secondes = (ms % 60000) // 1000
        centiemes = (ms % 1000) // 10
        return f"{minutes:02d}:{secondes:02d}.{centiemes:02d}"

    def changer_map(self):
        """Passe à la map suivante et replace le joueur en haut à gauche."""
        maintenant = pygame.time.get_ticks()

        # Enregistrement du temps de la map actuelle (seulement en mode Speedrun)
        if self.mode == SPEEDRUN:
            temps_map = maintenant - self.temps_debut_map
            self.temps_par_map.append(temps_map)

        self.map_actuelle_index += 1

        if self.map_actuelle_index >= len(MAPS):
            # Plus de maps -> Fin de la partie
            self.partie_terminee = True
            return

        infos = MAPS[self.map_actuelle_index]
        self.map.switch_map(infos["fichier"], infos["tuiles_escalier"])
        self.entity.teleporter_haut_gauche()

        self.dernier_changement = maintenant
        self.temps_debut_map = maintenant  # Réinitialise le chrono pour la nouvelle map

    def afficher_chrono_jeu(self):
        """Affiche le chronomètre en haut au centre de l'écran pendant qu'on joue."""
        if self.mode != SPEEDRUN:
            return

        maintenant = pygame.time.get_ticks()
        temps_ecoule_map = maintenant - self.temps_debut_map
        temps_total = maintenant - self.temps_debut_partie

        texte_map = f"Map {self.map_actuelle_index + 1} : {self.formater_temps(temps_ecoule_map)}"
        texte_total = f"Total : {self.formater_temps(temps_total)}"

        # Rendu des textes
        surface_map = self.police_chrono.render(texte_map, True, (255, 255, 255))
        surface_total = self.police_chrono.render(texte_total, True, (255, 215, 0)) # Couleur dorée

        # Dessin d'un bandeau de fond pour la lisibilité
        pygame.draw.rect(self.screen.get_display(), (0, 0, 0, 150), (10, 10, 240, 70), border_radius=5)

        # Affichage des textes sur l'écran
        self.screen.get_display().blit(surface_map, (20, 15))
        self.screen.get_display().blit(surface_total, (20, 45))

    def afficher_ecran_fin(self):
        """Affiche le récapitulatif complet des temps une fois le jeu fini."""
        surface = self.screen.get_display()
        surface.fill((15, 15, 35))

        police_titre = pygame.font.SysFont("arial", 50, bold=True)
        police_texte = pygame.font.SysFont("arial", 30)

        titre = police_titre.render("GG ! SPEEDRUN TERMINÉ !", True, (255, 215, 0))
        surface.blit(titre, titre.get_rect(center=(LARGEUR // 2, 100)))

        # Affichage du temps de chaque map
        y_offset = 200
        temps_total = 0
        for i, temps in enumerate(self.temps_par_map):
            temps_total += temps
            txt = f"Map {i + 1} : {self.formater_temps(temps)}"
            surf = police_texte.render(txt, True, (200, 200, 250))
            surface.blit(surf, surf.get_rect(center=(LARGEUR // 2, y_offset)))
            y_offset += 40

        # Ligne de séparation
        pygame.draw.line(surface, (255, 255, 255), (200, y_offset + 10), (600, y_offset + 10), 2)

        # Temps total final
        txt_final = f"TEMPS TOTAL FINAL : {self.formater_temps(temps_total)}"
        surf_final = police_titre.render(txt_final, True, (50, 255, 50))
        surface.blit(surf_final, surf_final.get_rect(center=(LARGEUR // 2, y_offset + 50)))

        txt_quitter = police_texte.render("Pressez ÉCHAP pour quitter", True, (150, 150, 150))
        surface.blit(txt_quitter, txt_quitter.get_rect(center=(LARGEUR // 2, 700)))

    def run(self):
        # Initialisation des chronos juste au lancement de la boucle de jeu
        self.temps_debut_partie = pygame.time.get_ticks()
        self.temps_debut_map = pygame.time.get_ticks()
        self.dernier_changement = pygame.time.get_ticks()

        while self.running:
            self.handle_input()

            if not self.partie_terminee:
                self.screen.display.fill((0, 0, 0))
                self.map.update()

                # Gestion des chronos et vérification de l'escalier
                now = pygame.time.get_ticks()
                if now - self.dernier_changement > self.cooldown_transition:
                    if self.map.joueur_sur_escalier():
                        self.changer_map()

                # On dessine le chrono par-dessus le jeu
                self.afficher_chrono_jeu()
            else:
                # Si la partie est finie, on affiche l'écran des scores
                self.afficher_ecran_fin()

            pygame.display.flip()
            self.screen.clock.tick(self.screen.framerate)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and self.partie_terminee:
                    self.running = False
                    pygame.quit()
                    sys.exit()
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
                sys.exit()
            result = titlescreen.gerer_event(event)
            if result is not None:
                mode = result

        titlescreen.update()
        titlescreen.draw()
        pygame.display.flip()
        screen.clock.tick(screen.framerate)

    # On passe le "mode" sélectionné à la classe Game
    game = Game(mode)
    game.run()