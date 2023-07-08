################################################################################
#                                                                              #
#                        Constantes pour le jeu paco                           #
#                                                                              # 
################################################################################
import pygame as pg
from pygame.locals import *
import os,sys,glob
from variables import *

SCRIPT_PATH=sys.path[0]
pg.mixer.pre_init(22050,16,2,512)    
pg.init()

#MODE_ECRAN = [FULLSCREEN]
MODE_ECRAN = [0]
TITRE = "PACO v1.4"
FPS = 25
NOM_TABLEAUX_DEFAUT = 'liste1'

NBR_VIE_INITIAL = 3

VITESSE_JOUEUR = 8
VITESSE_FANTOME = 4

LARGEUR_TILE = 32
HAUTEUR_TILE = 32

NBR_LIGNES = 19
NBR_COLONNES = 19
WIN_WIDTH = (NBR_COLONNES * LARGEUR_TILE)
WIN_HEIGHT = NBR_LIGNES * HAUTEUR_TILE
#BG_COLOR = (63,34,4)
BG_COLOR = (48,48,48)
BG_COLOR_LEVEL = (45,36,30)
BOULE_COULEUR = (250,250,100)
PACGOMME_COULEUR = (250,250,100)
MUR_COULEUR = ((58,142,186))
BG_COLOR_INTERFACE = (28,28,28)
COLOR_KEY = (0,0,0)

# Coordonnées colonne x ligne des sprites des fantomes dans le sprite_sheet dans leur 2 états
# ex   11:( ((0,0),(1,0)), ((0,2),(1,2)), ((0,3),(1,3)), ((0,1),(1,1)))
#              droite          gauche         monter        descente

COORDS_FANTOMES_SPRITES = {11:(((0,0),(1,0)),((0,2),(1,2)),((0,3),(1,3)),((0,1),(1,1))),
                           12:(((2,0),(3,0)),((2,2),(3,2)),((2,3),(3,3)),((2,1),(3,1))),
                           13:(((4,0),(5,0)),((4,2),(5,2)),((4,3),(5,3)),((4,1),(5,1))),
                           14:(((6,0),(7,0)),((6,2),(7,2)),((6,3),(7,3)),((6,1),(7,1))),
                           15:(((0,0),(1,0)),((0,2),(1,2)),((0,3),(1,3)),((0,1),(1,1))),
                           16:(((2,0),(3,0)),((2,2),(3,2)),((2,3),(3,3)),((2,1),(3,1))),
                           17:(((4,0),(5,0)),((4,2),(5,2)),((4,3),(5,3)),((4,1),(5,1))),
                           18:(((6,0),(7,0)),((6,2),(7,2)),((6,3),(7,3)),((6,1),(7,1)))}

PATH_LEVELS = os.path.join(SCRIPT_PATH,"ressources","levels","*.txt")
PATH_FONT1 = os.path.join(SCRIPT_PATH,"ressources","font","budmo jigglish.ttf")
PATH_FONT2 = os.path.join(SCRIPT_PATH,"ressources","font","budmo jiggler.ttf")

# Coordonnées ligne x colonne des sprites de Paco dans le sprite_sheet
COORDS_JOUEUR_SPRITES = {10:(((10,0),(11,0)),((10,2),(11,2)),((10,3),(11,3)),((10,1),(11,1)))}
SPRITES_SHEET = pg.image.load(os.path.join(SCRIPT_PATH,"ressources","images","spritesheetpaco2.bmp"))

# Musique
MUSIQUE_JEU = os.path.join(SCRIPT_PATH,"ressources","sons","musique3Paco.mp3")
MUSIQUE_MENU = os.path.join(SCRIPT_PATH,"ressources","sons","musique2Paco.mp3")
pg.mixer.music.set_volume(VOLUME_MUSIQUE[0]/10.)
    
# Sons
SON_BOULE1 = pg.mixer.Sound(os.path.join(SCRIPT_PATH,"ressources","sons","mange_boule1.wav"))
SON_BOULE2 = pg.mixer.Sound(os.path.join(SCRIPT_PATH,"ressources","sons","mange_boule2.wav"))
SON_PACGOMME = pg.mixer.Sound(os.path.join(SCRIPT_PATH,"ressources","sons","mange_pacgomme.wav"))
SON_FANTOME = pg.mixer.Sound(os.path.join(SCRIPT_PATH,"ressources","sons","mange_fantome.wav"))
SON_MORT = pg.mixer.Sound(os.path.join(SCRIPT_PATH,"ressources","sons","paco_mort.wav"))
SON_SWAP = pg.mixer.Sound(os.path.join(SCRIPT_PATH,"ressources","sons","swap.wav"))

SON_BOULE1.set_volume(VOLUME_SON[0]/10.)
SON_BOULE2.set_volume(VOLUME_SON[0]/10.)
SON_PACGOMME.set_volume(VOLUME_SON[0]/10.)
SON_FANTOME.set_volume(VOLUME_SON[0]/10.)
SON_MORT.set_volume(VOLUME_SON[0]/10.)
