################################################################################
#                                                                              #
#               Classes Levels et Level pour le jeu paco                       #
#                                                                              # 
################################################################################
import pygame as pg
from pygame.locals import *
from constantes import *
from level import *
from joueur import *
from fantome import *
from boule import *
from pacgomme import *
import glob,random

class All_Levels(object):
    """Classe qui charge un fichier level,liste de matrices de tiles, et crée une liste d'objets level correspondants
        à chaque matrice."""
    def __init__(self,surface,nomLevels=None,modeEdition=False,modeDemo=False):

        self.surface = surface
        self.nomLevels = nomLevels
        self.modeEdition = modeEdition
        self.modeDemo = modeDemo
        self.sauvegardeOk = True
        self.clock = pg.time.Clock()
        self.levelCourant = None
        self.indiceLevel = -1
        if self.nomLevels != "sans nom":
            self.fichier = open(os.path.join(SCRIPT_PATH,"ressources","levels",self.nomLevels+'.txt'),'r')
            self.listeMatrices = eval(self.fichier.read())
            self.fichier.close
            
            self.listeLevels = []
            if self.modeDemo:
                self.listeLevels.append(Level(self.listeMatrices[randrange(len(self.listeMatrices))],self.surface,self.modeEdition,self.modeDemo))
            else:
                for matrice in self.listeMatrices:
                    self.listeLevels.append(Level(matrice,self.surface,self.modeEdition,self.modeDemo))
            self.nbrLevels = len(self.listeLevels)
            self.changement_level(1)
        else:
            self.listeMatrices = []
            self.listeLevels = []
            self.nouveau_level()

    def sauver_levels(self):
        """Sauvegarde du fichier contenant les matrices."""
        
        if self.nomLevels:
            fichier = open(os.path.join(SCRIPT_PATH,"ressources","levels",self.nomLevels+'.txt'),'w')
            fichier.write(str(self.listeMatrices))
            fichier.close
        self.sauvegardeOk = True            
        
    def nouveau_level(self):
        """Crée un nouveau level."""
        
        matrice = []
        for l in range(NBR_LIGNES):
            matrice.append([2]*NBR_COLONNES)
        self.listeMatrices.insert(self.indiceLevel+1,matrice)
        level = Level(matrice,self.surface,self.modeEdition)
        self.listeLevels.insert(self.indiceLevel+1,level)
        self.nbrLevels = len(self.listeMatrices)
        if self.modeEdition:
            self.changement_level(1)

    def supprimer_level(self):
        """Supprime un level."""
        
        del self.listeMatrices[self.indiceLevel]
        del self.listeLevels[self.indiceLevel]
        self.nbrLevels = len(self.listeMatrices)
        if self.nbrLevels > 0:        
            if self.indiceLevel == 0:
                self.changement_level(0)
            else:
                self.changement_level(-1)
        else:
            self.indiceLevel = -1
            self.nouveau_level()
        self.sauvegardeOk = False                        

    def changement_level(self,inc):
        """Change de level courant si possible sinon renvoie 'False'."""

        if not self.modeEdition and self.indiceLevel+inc == self.nbrLevels:
            return False
        else:
            self.indiceLevel = (self.indiceLevel+inc)%self.nbrLevels
            self.levelCourant = self.listeLevels[self.indiceLevel]
            Joueur.containers = self.levelCourant.joueurContainers
            Fantome.containers = self.levelCourant.fantomeContainers
            Boule.containers = self.levelCourant.bouleContainers
            Pacgomme.containers = self.levelCourant.pacgommeContainers
            Mur.containers = self.levelCourant.murContainers
            # si le level ne contient pas de Paco en mode jeu on test le suivant
            if not Joueur.containers.sprite and not self.modeEdition:
                return self.changement_level(1)

            if self.modeEdition:
                self.animation_level(32)
            else:
                for t in threading.enumerate():
                    t.stop = True
                for fantome in Fantome.containers:
                    fantome.pathFinder.start()
                    fantome.pathFinder.rechercheDemandee = True
                demarrage = False
                while not demarrage:
                    demarrage = True                    
                    for f in Fantome.containers:
                        if f.path == []:
                            demarrage = False
                pg.time.wait(1000)                            
                            
                if not self.modeDemo:
                    self.animation_level()
                if self.modeDemo:
                    Joueur.containers.sprite.listeBoulesPacgommes.add(Boule.containers.sprites())
                    Joueur.containers.sprite.listeBoulesPacgommes.add(Pacgomme.containers.sprites())
                    Joueur.containers.sprite.pathFinder.start()
                
                return True
        
    def animation_level(self,vitesse=8):
        """Animation de l'apparition du level par scrolling droite-gauche."""
        
        self.levelCourant.creation_map()
        font = pg.font.Font(PATH_FONT1,48)
        textLevel = font.render("LEVEL "+str(self.indiceLevel+1)+'/'+str(self.nbrLevels),1,(255,255,255))
        rectText = textLevel.get_rect(center=(self.levelCourant.rectMap.w/2,self.levelCourant.rectMap.h/2))
        self.levelCourant.surfaceMap.blit(textLevel,rectText)

        memRectMap = self.levelCourant.rectMap.copy()
        self.levelCourant.rectMap.center = (WIN_WIDTH+WIN_WIDTH/2,WIN_HEIGHT/2)
        finAnim = False
        while not finAnim:
            self.levelCourant.rectMap.x -= vitesse
            if self.levelCourant.rectMap.x <= memRectMap.x:
                self.levelCourant.rectMap.x = memRectMap.x
                finAnim = True
            self.surface.fill(BG_COLOR)                
            self.surface.blit(self.levelCourant.surfaceMap,self.levelCourant.rectMap)
            pg.display.update()
            self.clock.tick(40)
        if not self.modeEdition:
            pg.time.wait(1000)
