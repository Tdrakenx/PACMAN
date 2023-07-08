################################################################################
#                                                                              #
#                      Classe Fantome pour le jeu paco                         #
#                                                                              # 
################################################################################
import pygame as pg
from pygame.locals import *
from constantes import *

class Fantome(pg.sprite.Sprite):
    """Classe qui crée un fantome qui se déplace en suivant un chemin déterminé par un objet propre de type 'PathFinder'."""
    def __init__(self,colonne=0,ligne=0,levelCourant=None,coordSheet=None,chiffre=0):
        pg.sprite.Sprite.__init__(self,self.containers)

        # coordonnées matricielles de départ
        self.ligneDepart = ligne
        self.colonneDepart = colonne

        # coordonnée matricielles actuelles        
        self.colonne = colonne
        self.ligne = ligne

        # un chiffre identifiant
        self.chiffre = chiffre

        # le level courant
        self.levelCourant = levelCourant

        # la direction courante
        self.direction = 'haut'

        self.etat = 'tueur'#vulnerable,tueur,retour

        # dictionnaire des image de l'animation en fonction de la direction choisie ou de l'état      
        self.dictionnaireAnimation = {'droite':(SPRITES_SHEET.subsurface((coordSheet[0][0][0]*32,coordSheet[0][0][1]*32,32,32)),SPRITES_SHEET.subsurface((coordSheet[0][1][0]*32,coordSheet[0][1][1]*32,32,32))),
                                      'gauche':(SPRITES_SHEET.subsurface((coordSheet[1][0][0]*32,coordSheet[1][0][1]*32,32,32)),SPRITES_SHEET.subsurface((coordSheet[1][1][0]*32,coordSheet[1][1][1]*32,32,32))),
                                      'haut':(SPRITES_SHEET.subsurface((coordSheet[2][0][0]*32,coordSheet[2][0][1]*32,32,32)),SPRITES_SHEET.subsurface((coordSheet[2][1][0]*32,coordSheet[2][1][1]*32,32,32))),
                                      'bas':(SPRITES_SHEET.subsurface((coordSheet[3][0][0]*32,coordSheet[3][0][1]*32,32,32)),SPRITES_SHEET.subsurface((coordSheet[3][1][0]*32,coordSheet[3][1][1]*32,32,32))),
                                      'vulnerable1':(SPRITES_SHEET.subsurface((12*32,0*32,32,32)),SPRITES_SHEET.subsurface((13*32,0*32,32,32))),
                                      'vulnerable2':(SPRITES_SHEET.subsurface((12*32,1*32,32,32)),SPRITES_SHEET.subsurface((13*32,1*32,32,32))),
                                      'retour':(SPRITES_SHEET.subsurface((12*32,2*32,32,32)),SPRITES_SHEET.subsurface((13*32,2*32,32,32)))}


        # vitesse du fantome
        self.vitesse = VITESSE_FANTOME
        # déplacement relatif unitaire 
        self.h = 0 # -1 : gauche, 1 : droite
        self.v = 0 # -1 : haut,   1 : bas
        self.directionArriere = None

        # surface de dessin de l'image courante de l'animation
        self.image = pg.Surface((LARGEUR_TILE,HAUTEUR_TILE)).convert()
        self.image.fill((0,0,0))
        self.image.set_colorkey((0,0,0))
        self.image.blit(SPRITES_SHEET.subsurface((COORDS_FANTOMES_SPRITES[self.chiffre][0][0][0]*32,COORDS_FANTOMES_SPRITES[self.chiffre][0][0][1]*32,32,32)),(0,0))        
        self.rect = self.image.get_rect(x=self.colonne*LARGEUR_TILE,y=self.ligne*HAUTEUR_TILE)

        #
        font = pg.font.Font(PATH_FONT2,18)
        self.texteMiam = font.render("MIAM",1,(255,0,0))
        self.rectTexteMiam = self.texteMiam.get_rect(x=self.rect.x+self.levelCourant.camera.etat.x,
                                                     y=self.rect.y+self.levelCourant.camera.etat.y)
        # un objet pathFinder propre qui trouvera le chemin le plus court pour atteindre une case d'arrivée
        # l'attribut path contiendra toutes les coordonnées des cases sur lesquelles se déplacer
        self.pathFinder = None
        self.path = []
        self.caseArrivee = None#[self.ligne,self.colonne]#None

        # attributs relatif à l'animation
        self.indiceAnimation = 0
        self.tempsDebutImage = 0        
        self.ms_image = 180
        # clignotement
        self.tempsDebutVulnerable = 0
        self.clignotement = False
        self.ms_avantCligno = 5000
        self.nbr_cyclesCligno = 5
        self.tempsDebutCycleCligno = 0
        self.ms_clignoHaut = 500
        self.ms_clignoBas = 250
        self.ms_cycleCligno = self.ms_clignoHaut + self.ms_clignoBas

    def update(self):
        """Mise à jour des coordonnées du fantome en mode jeu."""
        
        self.rect = self.rect.move((self.h*self.vitesse,self.v*self.vitesse))

        # prise en compte du changement de coté du level        
        if self.rect.right > self.levelCourant.rect.right:
            self.rect.left = self.levelCourant.rect.left
        elif self.rect.left < self.levelCourant.rect.left:
            self.rect.right = self.levelCourant.rect.right
        elif self.rect.top < self.levelCourant.rect.top:
            self.rect.bottom = self.levelCourant.rect.bottom
        elif self.rect.bottom > self.levelCourant.rect.bottom:
            self.rect.top = self.levelCourant.rect.top             
        # lorsque le fantome arrive sur une case
        if self.rect.y%HAUTEUR_TILE == 0 and self.rect.x%LARGEUR_TILE == 0:
            self.ligne = self.rect.y/HAUTEUR_TILE
            self.colonne = self.rect.x/LARGEUR_TILE
            # si son chemin n'est pas vide 
            if self.path:
                # calcul des déplacements relatifs unitaires en tenant compte des swap écran
                self.h = self.path[0][0]-self.colonne
                self.h = abs(self.h) == 1 and self.h or (self.h and (self.h > 0 and -1 or 1))
                self.v = self.path[0][1]-self.ligne
                self.v = abs(self.v) == 1 and self.v or (self.v and (self.v > 0 and -1 or 1))                
                self.directionArriere = [self.v*-1,self.h*-1]
                self.path.pop(0)

                # détermination des directions en fonction des déplacements relatifs unitaires
                if self.h > 0:
                    self.direction = 'droite'
                elif self.h < 0:
                    self.direction = 'gauche'
                if self.v > 0:
                    self.direction = 'bas'
                elif self.v < 0:
                    self.direction = 'haut'

            else:
                # si aucun chemin n'a été encore déterminé on stop le fantome en attendant
                self.h,self.v = 0,0

            # si le fantome a rejoint sa case de départ après s'être fait manger
            if self.ligne == self.ligneDepart and self.colonne == self.colonneDepart and self.etat == 'retour':
                self.etat_initial()

        # arrivé sur l'avant dernière case, on a vidé le chemin
        if not self.path:
            if not self.pathFinder.rechercheDemandee :
                # on calcule la ligne et la colonne du fantome par anticipation 
                # ce qui permet de chercher un chemin à partir de la dernière case
                # pendant le dernier déplacement vers celle-ci : gain en fluidité
                self.ligne += self.v
                self.colonne += self.h
                self.pathFinder.rechercheDemandee = True

        # on procède à l'animation
        self.animation()

    def animation(self):
        """Méthode d'animation."""

        cle = self.direction
        if self.etat == 'vulnerable':
            cle = 'vulnerable1'
            if not self.clignotement and pg.time.get_ticks() - self.tempsDebutVulnerable >= self.ms_avantCligno :
                self.clignotement = True
                self.tempsDebutCycleCligno = pg.time.get_ticks()
            if self.clignotement:
                if pg.time.get_ticks()-self.tempsDebutCycleCligno <= self.ms_clignoHaut:
                    cle = 'vulnerable2'
                elif pg.time.get_ticks()-self.tempsDebutCycleCligno <= self.ms_cycleCligno:
                    cle = 'vulnerable1'
                else:
                    self.tempsDebutCycleCligno = pg.time.get_ticks()                                
                    self.nbrCyclesCligno -= 1
                    if self.nbrCyclesCligno == 0:
                        self.etat = 'tueur'
        elif self.etat == 'retour':
            cle = 'retour'

        if self.vitesse :
            self.image.blit(self.dictionnaireAnimation[cle][self.indiceAnimation],(0,0))        
            if pg.time.get_ticks() - self.tempsDebutImage > self.ms_image :
                self.indiceAnimation = (self.indiceAnimation+1)%2
                self.tempsDebutImage = pg.time.get_ticks()        
                
    def etat_initial(self):
        """Méthode chargée de remettre le fantome à son état initial."""

        self.ligne = self.ligneDepart
        self.colonne = self.colonneDepart
        self.rect.topleft =(self.colonne*LARGEUR_TILE,self.ligne*HAUTEUR_TILE)
        self.pathFinder.marcheArrierePossible = False
        self.path = []
        self.caseArrivee = None
        self.etat = 'tueur'#'vulnerable'
        self.vitesse = VITESSE_FANTOME
        self.h, self.v = 0, 0
        self.direction = 'droite'

    def etat_vulnerable(self):
        """Méthode chargée de remettre le fantome à son état vulnérable."""
        
        self.etat = 'vulnerable'
        self.nbrCyclesCligno = 5
        self.clignotement = False
        self.tempsDebutVulnerable = pg.time.get_ticks()        
