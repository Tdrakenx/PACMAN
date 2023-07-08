################################################################################
#                                                                              #
#               Classes Levels et Level pour le jeu paco                       #
#                                                                              # 
################################################################################
import pygame as pg
from pygame.locals import *
from camera import *
from constantes import *
from joueur import *
from fantome import *
from boule import *
from pacgomme import *
from mur import *
from path_finder import *
import glob,random

class Level(object):
    """Classe qui crée tous les objets initiaux d'un level en fonction de sa matrice de tiles,
        et qui permet de l'afficher."""
    def __init__(self,matrice=None,screen=None,modeEdition=False,modeDemo=False):

        #+- la matrice de tiles
        self.matrice = matrice

        #+- dimensions de la matrice 
        self.nbrLignes = len(self.matrice)
        self.nbrColonnes = len(self.matrice[0])
        
        #+- dimensions de la surface du level
        self.largeur = self.nbrColonnes*LARGEUR_TILE
        self.hauteur = self.nbrLignes*HAUTEUR_TILE
        self.rect = Rect(0,0,self.largeur,self.hauteur)

        #+- surface du display pour le blitting
        self.screen = screen

        #+- si le level est créé en mode edition
        self.modeEdition = modeEdition

        #+- pour chaque level on mémorise la position du curseur de déplacement du scrolling de l'editeur
        self.rectCurseurScrolling = None

        #+- surface transparente contenant la grille du level
        self.surfaceGrille = None
        #+- surface contenant tous les murs du level
        self.surfaceMurs = None
        #+- surface contenant la map du level
        self.surfaceMap = None
        self.rectMap = None

        #+- containers des objets propres au level
        self.joueurContainers = pg.sprite.GroupSingle()
        self.fantomeContainers = pg.sprite.RenderUpdates()
        self.murContainers = pg.sprite.RenderUpdates()
        self.bouleContainers = pg.sprite.RenderUpdates()
        self.pacgommeContainers = pg.sprite.RenderUpdates()

        Joueur.containers = self.joueurContainers
        Fantome.containers = self.fantomeContainers
        Boule.containers = self.bouleContainers
        Pacgomme.containers = self.pacgommeContainers
        Mur.containers = self.murContainers

        #+- création de la caméra pour le scrolling       
        if modeEdition :
            self.camera = Camera(WIN_WIDTH,WIN_HEIGHT,self.largeur,self.hauteur)
        else:
            self.camera = Camera(WIN_WIDTH,WIN_HEIGHT,self.largeur,self.hauteur,192,416,192,416)

        #+- si le level est créé en mode démo (cf:création objets)
        self.modeDemo = modeDemo

        #+- création des éléments propres au level
        self.creation_surfaces()
        self.creation_murs()
        self.creation_objets()
        
    def creation_surfaces(self):
        """Création des surfaces et mise à jour de la caméra du level."""
        
        # Grille
        self.surfaceGrille = pg.Surface((self.nbrColonnes*LARGEUR_TILE+1,self.nbrLignes*HAUTEUR_TILE+1)).convert()
        self.surfaceGrille.fill(COLOR_KEY)
        self.surfaceGrille.set_colorkey(COLOR_KEY)
        for x in range(self.nbrColonnes+1):
            if x%5 == 0:
                ep = 3
            else:
                ep = 1
            pg.draw.line(self.surfaceGrille,(255,255,255),(x*LARGEUR_TILE,0),(x*LARGEUR_TILE,self.nbrLignes*HAUTEUR_TILE),ep) 
        for y in range(self.nbrLignes+1):
            if y%5 == 0:
                ep = 3
            else:
                ep = 1
            pg.draw.line(self.surfaceGrille,(255,255,255),(0,y*HAUTEUR_TILE),(self.nbrColonnes*LARGEUR_TILE,y*HAUTEUR_TILE),ep)
        # Murs
        self.surfaceMurs = pg.Surface((self.nbrColonnes*LARGEUR_TILE,self.nbrLignes*HAUTEUR_TILE)).convert()
        self.surfaceMurs.fill(BG_COLOR)
        self.surfaceMurs.fill((200,140,25))

        # Map
        self.surfaceMap = pg.Surface((self.nbrColonnes*LARGEUR_TILE,self.nbrLignes*HAUTEUR_TILE)).convert()

        # mise à jour Camera
        self.camera.changement_Level(self.nbrColonnes*LARGEUR_TILE,self.nbrLignes*HAUTEUR_TILE)

    def update(self,modeDemo=False):
        """Méthode de mise à jour des éléments du level."""
        
        if Joueur.containers.sprite :
            if modeDemo:
                Joueur.containers.sprite.update_demo()
            else:
                Joueur.containers.sprite.update()
            self.camera.update(Joueur.containers.sprite.rect)
            
            if Joueur.containers.sprite.fantomesManges:
                pg.time.wait(250)
                for fantome in Joueur.containers.sprite.fantomesManges:
                    fantome.rect.topleft = (fantome.colonne*LARGEUR_TILE,fantome.ligne*HAUTEUR_TILE)
                Joueur.containers.sprite.fantomesManges = []            
            else:
                Fantome.containers.update()
            Joueur.containers.sprite.collision_boule()
            Joueur.containers.sprite.collision_pacgomme()
            Joueur.containers.sprite.collision_fantome()

    def draw(self,mapOn=False,grilleOn=False):
        """Méthode chargée de déssiner toutes les surfaces et éléments du level."""
        
        if mapOn :
            self.screen.fill(BG_COLOR)
            self.screen.blit(self.surfaceMap,self.rectMap)
        else:
            self.screen.fill(BG_COLOR)
            self.screen.blit(self.surfaceMurs,self.camera.etat.topleft)

            for boule in Boule.containers:
                self.screen.blit(boule.image,self.camera.apply(boule.rect))
            for pacgomme in Pacgomme.containers:
                self.screen.blit(pacgomme.image,self.camera.apply(pacgomme.rect))
            for fantome in Fantome.containers:
                self.screen.blit(fantome.image,self.camera.apply(fantome.rect))
            if Joueur.containers.sprite:
                self.screen.blit(Joueur.containers.sprite.image,self.camera.apply(Joueur.containers.sprite.rect))
                if not self.modeEdition:                
                    for fantome in Joueur.containers.sprite.fantomesManges:
                        self.screen.blit(fantome.texteMiam,fantome.rectTexteMiam)
            if grilleOn:
                self.screen.blit(self.surfaceGrille,self.camera.etat.topleft)

    def creation_murs(self):
        """création des murs sur une surface indépendante compte tenu de leur caractère statique.
            A chaque frame on blittera cette surface et non pas chaque mur du level."""
        
        self.murContainers.empty()
        self.surfaceMurs.fill(BG_COLOR_LEVEL)
        for ligne in range(len(self.matrice)):
            for colonne in range(len(self.matrice[0])):
                if self.matrice[ligne][colonne] == 1:
                    mur = Mur(colonne,ligne)
                    jointureDroite = False
                    jointureBasse = False
                    if colonne < len(self.matrice[0])-1:
                        if self.matrice[ligne][colonne+1] == 1:
                            jointureDroite = True
                            murJointureDroite = Mur(colonne,ligne,jointureDroite=True)
                    if ligne < len(self.matrice)-1:
                        if self.matrice[ligne+1][colonne] == 1:
                            jointureBasse = True                            
                            murJointureBasse = Mur(colonne,ligne,jointureBasse=True)
                    if jointureDroite and jointureBasse and self.matrice[ligne+1][colonne+1] == 1:
                        pg.draw.rect(self.surfaceMurs,MUR_COULEUR,(mur.rect.centerx,mur.rect.centery,32,32),0)
        self.murContainers.draw(self.surfaceMurs)                            
        
    def creation_objets(self):
        """Méthode chargée de créer tous les éléments du level."""
        
        self.bouleContainers.empty()
        self.pacgommeContainers.empty()
        self.fantomeContainers.empty()
        self.joueurContainers.empty()

        for ligne in range(len(self.matrice)):
            for colonne in range(len(self.matrice[0])):
                if self.matrice[ligne][colonne] == 10:
                    joueur = Joueur(colonne,ligne,self,coordSheet=COORDS_JOUEUR_SPRITES[self.matrice[ligne][colonne]],modeDemo=self.modeDemo,modeEdition=self.modeEdition)
                    if self.modeDemo:
                        Joueur.containers.sprite.pathFinder = PathFinder(Joueur.containers.sprite,marcheArrierePossible=False,swap=True)
                if  self.matrice[ligne][colonne] >= 11 :
                    fantome = Fantome(colonne,ligne,self,coordSheet=COORDS_FANTOMES_SPRITES[self.matrice[ligne][colonne]],chiffre=self.matrice[ligne][colonne])                    
                    fantome.pathFinder = PathFinder(fantome,marcheArrierePossible=False,swap=True)
                    boule = Boule(colonne,ligne)
                elif self.matrice[ligne][colonne] == 2:
                    boule = Boule(colonne,ligne)
                elif self.matrice[ligne][colonne] == 3:
                    pacgomme = Pacgomme(colonne,ligne)
        if self.joueurContainers.sprite and not self.modeEdition:
            self.camera.update(self.joueurContainers.sprite.rect)
        
    def creation_map(self,grilleOn=False):
        """Création de la carte du level."""
        
        self.surfaceMap = pg.Surface((self.nbrColonnes*LARGEUR_TILE,self.nbrLignes*HAUTEUR_TILE)).convert()        
        self.surfaceMap.fill(BG_COLOR_LEVEL)
        self.surfaceMap.blit(self.surfaceMurs,(0,0))
        
        Boule.containers.draw(self.surfaceMap)
        Pacgomme.containers.draw(self.surfaceMap)
        Joueur.containers.draw(self.surfaceMap)
        Fantome.containers.draw(self.surfaceMap)
        if grilleOn:
            self.surfaceMap.blit(self.surfaceGrille,(0,0))
        rect = Rect(self.rect.x-self.camera.etat.x,
                    self.rect.y-self.camera.etat.y,
                    WIN_WIDTH,WIN_HEIGHT)
        pg.draw.rect(self.surfaceMap,(255,0,0),rect,4)

        # dans le cas d'un level non carré on s'assure que la carte n'apparaîtra pas applatie
        rapportReductionHauteur = WIN_WIDTH/(self.largeur*1.0)
        rapportReductionLargeur = WIN_HEIGHT/(self.hauteur*1.0)

        rapportReduction = min(rapportReductionHauteur,rapportReductionLargeur)
        self.surfaceMap = pg.transform.smoothscale(self.surfaceMap,(int(rapportReduction*self.largeur),
                                                                   int(rapportReduction*self.hauteur)))

        self.rectMap = self.surfaceMap.get_rect()
        self.rectMap.center = (WIN_WIDTH/2,WIN_HEIGHT/2)

    def ajouter_colonne(self):
        """Ajoute une colonne à la matrice du level."""
        
        for ligne in self.matrice:
            ligne.append(2)
        self.nbrColonnes = len(self.matrice[0])
        self.largeur = self.nbrColonnes * LARGEUR_TILE

        self.rect = Rect(0,0,self.largeur,self.hauteur)
        self.creation_surfaces()
        self.creation_murs()
        self.creation_objets()

    def supprimer_colonne(self):
        """Supprime une colonne à la matrice du level."""
        
        if len(self.matrice[0]) > 4:
            for ligne in self.matrice:
                del ligne[-1]
            self.nbrColonnes = len(self.matrice[0])
            self.largeur = self.nbrColonnes * LARGEUR_TILE
         
        self.rect = Rect(0,0,self.largeur,self.hauteur)
        self.creation_surfaces()
        self.creation_murs()
        self.creation_objets()

    def ajouter_ligne(self):
        """Ajoute une ligne à la matrice du level."""
        
        self.matrice.append([2]*self.nbrColonnes)
        self.nbrLignes = len(self.matrice)
        self.hauteur = self.nbrLignes * HAUTEUR_TILE

        self.rect = Rect(0,0,self.largeur,self.hauteur)
        self.creation_surfaces()
        self.creation_murs()
        self.creation_objets()

    def supprimer_ligne(self):
        """Supprime une ligne à la matrice du level."""
        
        if len(self.matrice) > 4:
            del self.matrice[-1]
            self.nbrLignes = len(self.matrice)
            self.hauteur = self.nbrLignes * HAUTEUR_TILE

        self.rect = Rect(0,0,self.largeur,self.hauteur)
        self.creation_surfaces()
        self.creation_murs()
        self.creation_objets()
