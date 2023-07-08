# -*- coding: Utf-8 -*

import pygame as pg
from pygame.locals import *
from constantes import *

class Ecran_Options(object):
    """Classe qui crée écran de dialogue à choix multiple en transparence sur le level courant.
        l'argument 'options' doit être une liste de listes contenant chacune le nom de l'option,
        la variable concernée(contenue dans le fichier 'variables' et sa plage de valeurs."""
    def __init__(self,screen,levels,options):

        self.screen = screen
        self.screen_rect = self.screen.get_rect()

        self.levels = levels
        self.options = options

        #+- Attribut de l'horloge de pygame
        self.clock = pg.time.Clock()        

        self.font = pg.font.Font(PATH_FONT2,40)

        self.texteTitre = self.font.render('OPTIONS',1,(0,255,255))
        self.rectTitre = self.texteTitre.get_rect(centerx=self.screen_rect.w/2,y=100)

        self.optionChoisie = self.options[0]

        self.surface = pg.Surface((self.screen_rect.size)).convert()
        self.surface.set_alpha(200)
        self.rectSurface = self.surface.get_rect()

        font = pg.font.Font(PATH_FONT2,20)
        self.texteQuitter = font.render("Echap pour quitter",1,(255,255,255))
        
        self.main_loop()
            
    def main_loop(self):

        indice = 0
        while 1 :
            for event in pg.event.get():
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        return
                    
                    elif event.key == K_UP:
                        indice = (indice-1)%len(self.options)
                        self.optionChoisie = self.options[indice]
                    elif event.key == K_DOWN:
                        indice = (indice+1)%len(self.options)
                        self.optionChoisie = self.options[indice]
                    elif event.key == K_RIGHT:
                        ind = self.optionChoisie[2].index(self.optionChoisie[1][0])
                        ind = (ind+1)%len(self.options[indice][2])
                        self.options[indice][1][0] = self.options[indice][2][ind]
                        if self.optionChoisie[0] == "Plein Ecran : ":
                            pg.display.set_mode((WIN_WIDTH,WIN_HEIGHT),MODE_ECRAN[0])
                            self.screen = pg.display.get_surface()
                        elif self.optionChoisie[0] == "Volume Musique : ":
                            pg.mixer.music.set_volume(VOLUME_MUSIQUE[0]/10.)
                        elif self.optionChoisie[0] == "Volume Son : ":
                            SON_BOULE1.set_volume(VOLUME_SON[0]/10.)
                            SON_BOULE2.set_volume(VOLUME_SON[0]/10.)
                            SON_PACGOMME.set_volume(VOLUME_SON[0]/10.)
                            SON_FANTOME.set_volume(VOLUME_SON[0]/10.)
                            SON_MORT.set_volume(VOLUME_SON[0]/10.)
                            SON_BOULE1.play()                            

                    elif event.key == K_LEFT:
                        ind = self.optionChoisie[2].index(self.optionChoisie[1][0])
                        ind = (ind-1)%len(self.options[indice][2])
                        self.options[indice][1][0] = self.options[indice][2][ind]
                        if self.optionChoisie[0] == "Plein Ecran : ":
                            pg.display.set_mode((WIN_WIDTH,WIN_HEIGHT),MODE_ECRAN[0])
                            self.screen = pg.display.get_surface()
                        elif self.optionChoisie[0] == "Volume Musique : ":
                            pg.mixer.music.set_volume(VOLUME_MUSIQUE[0]/10.)
                        elif self.optionChoisie[0] == "Volume Son : ":
                            SON_BOULE1.set_volume(VOLUME_SON[0]/10.)
                            SON_BOULE2.set_volume(VOLUME_SON[0]/10.)
                            SON_PACGOMME.set_volume(VOLUME_SON[0]/10.)
                            SON_FANTOME.set_volume(VOLUME_SON[0]/10.)
                            SON_MORT.set_volume(VOLUME_SON[0]/10.)
                            SON_BOULE1.play()                                                        

            self.levels.levelCourant.draw()
            self.surface.fill((0,0,0))
            self.surface.blit(self.texteTitre,self.rectTitre)
            self.surface.blit(self.texteQuitter,(0,0))            

            posx = 120
            posy = 200
            for option in self.options:
                if self.options.index(option) == indice:
                    couleur = (255,0,0)
                else:
                    couleur = (255,255,255)
                if option[0] == 'Plein Ecran : ':
                    if option[1][0] == FULLSCREEN:
                        texte = self.font.render(option[0]+'oui',1,couleur)
                    else:
                        texte = self.font.render(option[0]+'non',1,couleur)
                else:
                    texte = self.font.render(option[0]+str(option[1][0]),1,couleur)
                    
                rectTexte = texte.get_rect(x=posx,y=posy)
                self.surface.blit(texte,rectTexte)
                posy += 50
            self.screen.blit(self.surface,self.rectSurface)
            pg.display.flip()
            self.clock.tick(25)
