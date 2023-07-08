################################################################################
#                                                                              #
#                        Classe Mur pour le jeu paco                           #
#                                                                              # 
################################################################################
import pygame as pg
from pygame.locals import *
from constantes import *

class Mur(pg.sprite.Sprite):
    listeMurs = []
    def __init__(self,colonne=0,ligne=0,jointureDroite=False,jointureBasse=False,image=None):
        pg.sprite.Sprite.__init__(self,self.containers)

        self.ligne = ligne
        self.colonne = colonne
        self.couleur = MUR_COULEUR
        self.jointureDroite = jointureDroite
        self.jointureBasse = jointureBasse

        if image:
            self.image = image
        else:
            self.image = pg.Surface((LARGEUR_TILE,HAUTEUR_TILE)).convert()
            self.image.fill(COLOR_KEY)
            self.image.set_colorkey(COLOR_KEY)

        self.rect = self.image.get_rect()
        self.rayon = 11
        self.epaisseur = 0

        if self.jointureDroite:
            if not image:
                pg.draw.rect(self.image,self.couleur,self.rect.inflate(0,(2*self.rayon)-self.rect.h),self.epaisseur)
            self.rect = self.rect.move(colonne*LARGEUR_TILE+LARGEUR_TILE/2,ligne*HAUTEUR_TILE)
        elif self.jointureBasse:
            if not image:            
                pg.draw.rect(self.image,self.couleur,self.rect.inflate((2*self.rayon)-self.rect.w,0),self.epaisseur)
            self.rect = self.rect.move(colonne*LARGEUR_TILE,ligne*HAUTEUR_TILE+HAUTEUR_TILE/2)
        else:
            if not image:            
                pg.draw.circle(self.image,self.couleur,self.rect.center,self.rayon,self.epaisseur)
            self.rect = self.rect.move(colonne*LARGEUR_TILE,ligne*HAUTEUR_TILE)
