################################################################################
#                                                                              #
#                        Classe Interface pour le jeu paco                     #
#                                                                              # 
################################################################################
import pygame as pg
from pygame.locals import *
from constantes import *

class Interface(object):
    def __init__(self,all_levels):
        """Classe qui crée 2 surfaces transparentes,1 en haut 1 en bas et qui contient des informations de jeu."""

        self.all_levels = all_levels

        self.surfaceInfosJeu = pg.Surface((WIN_WIDTH,20)).convert()
        self.surfaceInfosJeu.set_alpha(160)
        self.rectSurfaceInfosJeu = self.surfaceInfosJeu.get_rect()
        
        self.surfaceMenu = pg.Surface((WIN_WIDTH,20)).convert()
        self.surfaceMenu.set_alpha(160)
        self.rectSurfaceMenu = self.surfaceMenu.get_rect()

        self.image = pg.Surface((LARGEUR_TILE,HAUTEUR_TILE)).convert()
        self.image.fill(COLOR_KEY)
        self.image.set_colorkey(COLOR_KEY)
        self.rectImage = self.image.get_rect(x=2*(self.rectSurfaceInfosJeu.w/3)-32)

        paco = SPRITES_SHEET.subsurface(COORDS_JOUEUR_SPRITES[10][0][1][0]*32,COORDS_JOUEUR_SPRITES[10][0][1][1]*32,32,32)
        self.image.blit(pg.transform.smoothscale(paco,(20,20)),(0,0))

        self.nomLevels = ''
        self.font1 = pg.font.Font(PATH_FONT2,18)
        self.font2 = pg.font.Font(PATH_FONT2,14)

        self.texteNomLevels = self.font1.render(' '+self.all_levels.nomLevels[:15],1,(255,255,255))
        self.rectTexteNomLevels = self.texteNomLevels.get_rect(x=self.rectSurfaceInfosJeu.left,y=2)

        self.texteBoules = self.font1.render("BOULES : "+str(len(self.all_levels.levelCourant.bouleContainers)),1,(255,255,100))
        self.rectTexteBoules = self.texteBoules.get_rect(x=self.rectTexteNomLevels.right+60,y=2)
        
        if self.all_levels.levelCourant.joueurContainers.sprite:
            self.texteVie = self.font1.render(" x "+str(self.all_levels.levelCourant.joueurContainers.sprite.nbrVie),1,(255,255,100))
            self.rectTexteVie = self.texteVie.get_rect(y=2)
            self.rectTexteVie.centerx = 2*(self.rectSurfaceInfosJeu.w/3)

        self.texteLevel = self.font1.render("LEVEL : "+str(self.all_levels.indiceLevel+1)+'/'+str(self.all_levels.nbrLevels),1,(255,255,255))
        self.rectTexteLevel = self.texteLevel.get_rect(right=self.rectSurfaceInfosJeu.right,y=2)

        self.texteMenuJeu = self.font2.render("  Echap : Quitter                    Espace : Map           Fleches : Deplacements                    O : Options",1,(255,255,255))
        self.surfaceMenu.blit(self.texteMenuJeu,(0,2))
          
    def update(self):
        """Mise à jour des informations."""

        self.texteBoules = self.font1.render("BOULES : "+str(len(self.all_levels.levelCourant.bouleContainers)),1,(255,255,100))
        self.texteVie = self.font1.render(" x "+str(self.all_levels.levelCourant.joueurContainers.sprite.nbrVie),1,(255,255,100))
        self.texteLevel = self.font1.render("LEVEL : "+str(self.all_levels.indiceLevel+1)+'/'+str(self.all_levels.nbrLevels),1,(255,255,255))
        self.rectTexteLevel = self.texteLevel.get_rect(right=self.rectSurfaceInfosJeu.right,y=2)        

        self.surfaceInfosJeu.fill((0,0,0))
        self.surfaceInfosJeu.blit(self.texteNomLevels,self.rectTexteNomLevels)
        self.surfaceInfosJeu.blit(self.texteBoules,self.rectTexteBoules)
        self.surfaceInfosJeu.blit(self.image,self.rectImage)
        self.surfaceInfosJeu.blit(self.texteVie,self.rectTexteVie)
        self.surfaceInfosJeu.blit(self.texteLevel,self.rectTexteLevel)        

    def draw(self):
        self.all_levels.levelCourant.screen.blit(self.surfaceInfosJeu,(0,0))
        self.all_levels.levelCourant.screen.blit(self.surfaceMenu,(0,WIN_HEIGHT-20))
