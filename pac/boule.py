################################################################################
#                                                                              #
#                       Classe Boule pour le jeu PACO                          #
#                                                                              # 
################################################################################
import pygame as pg
from pygame.locals import *
from constantes import *

class Boule(pg.sprite.Sprite):
    """Classe créant une surface contenant un petit cercle plein jaune,
        symbolisant une boule à manger par Paco pour finir le level."""
    
    listeBoules = []
    def __init__(self,colonne=0,ligne=0,image=None):
        pg.sprite.Sprite.__init__(self,self.containers)

        self.ligne = ligne
        self.colonne = colonne
        self.couleur = BOULE_COULEUR

        if image:
            self.image = image
        else:
            self.image = pg.Surface((LARGEUR_TILE,HAUTEUR_TILE)).convert()
            self.image = pg.Surface.convert(self.image)
            self.image.fill(COLOR_KEY)
            self.image.set_colorkey(COLOR_KEY)

        self.rect = Rect(colonne*LARGEUR_TILE,ligne*HAUTEUR_TILE,LARGEUR_TILE,HAUTEUR_TILE)

        self.rectSurface = self.image.get_rect()
        self.offset = -24
        self.rectSurface = self.rectSurface.inflate(self.offset,self.offset)

        if not image:
            pg.draw.circle(self.image,self.couleur,self.rectSurface.center,self.rectSurface.w/2)
