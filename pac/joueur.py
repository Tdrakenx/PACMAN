################################################################################
#                                                                              #
#                      Classe Joueur pour le jeu paco                          #
#                                                                              # 
################################################################################
import pygame as pg
from pygame.locals import *
from constantes import *
from fantome import *
from boule import *
from pacgomme import *
from random import randrange

class Joueur(pg.sprite.Sprite):
    """Classe qui crée un personnage Paco contrôlable par le joueur ou suivant un chemin
        déterminé par un objet propre du type 'PathFinder'."""
    def __init__(self,colonne=0,ligne=0,levelCourant=None,coordSheet=None,chiffre=10,modeDemo=False,modeEdition=False):
        pg.sprite.Sprite.__init__(self,self.containers)

        # coordonnées matricielles de départ
        self.ligneDepart = ligne
        self.colonneDepart = colonne

        # coordonnée matricielles actuelles
        self.ligne = ligne
        self.colonne = colonne

        # un chiffre identifiant
        self.chiffre = chiffre

        # le level courant 
        self.levelCourant = levelCourant

        # la direction courante
        self.direction = 'droite'
        
        # la direction voulue dès que le terrain le permet
        self.directionVoulue = None
        
        # l'état de paco
        self.etat = 'vivant' # ou 'mort'

        # mode démo ou non
        self.modeDemo = modeDemo

        # mode édition ou non 
        self.modeEdition = modeEdition
        
        # son nombre de vie
        self.nbrVie = NBR_VIE_INITIAL
        
        # dictionnaire des image de l'animation en fonction de la direction choisie
        self.dictionnaireAnimation = {'droite':(SPRITES_SHEET.subsurface((coordSheet[0][0][0]*32,coordSheet[0][0][1]*32,32,32)),SPRITES_SHEET.subsurface((coordSheet[0][1][0]*32,coordSheet[0][1][1]*32,32,32))),
                                      'gauche':(SPRITES_SHEET.subsurface((coordSheet[1][0][0]*32,coordSheet[1][0][1]*32,32,32)),SPRITES_SHEET.subsurface((coordSheet[1][1][0]*32,coordSheet[1][1][1]*32,32,32))),
                                      'haut':(pg.transform.flip(SPRITES_SHEET.subsurface((coordSheet[2][0][0]*32,coordSheet[2][0][1]*32,32,32)),True,False),
                                             pg.transform.flip(SPRITES_SHEET.subsurface((coordSheet[2][1][0]*32,coordSheet[2][1][1]*32,32,32)),True,False)),
                                      'bas':(SPRITES_SHEET.subsurface((coordSheet[3][0][0]*32,coordSheet[3][0][1]*32,32,32)),SPRITES_SHEET.subsurface((coordSheet[3][1][0]*32,coordSheet[3][1][1]*32,32,32)))}


        # surface de dessin de l'image courante de l'animation
        self.image = pg.Surface((LARGEUR_TILE,HAUTEUR_TILE)).convert()
        self.image = pg.Surface.convert(self.image)
        self.image.set_colorkey((0,0,0))
        self.image.blit(SPRITES_SHEET.subsurface((COORDS_JOUEUR_SPRITES[10][0][0][0]*32,COORDS_JOUEUR_SPRITES[10][0][0][1]*32,32,32)),(0,0))        
        self.rect = self.image.get_rect(x=self.colonne*LARGEUR_TILE,y=self.ligne*HAUTEUR_TILE)  

        # vitesse de Paco
        self.vitesse = VITESSE_JOUEUR
        # déplacement relatif unitaire 
        self.h = 0 # -1 : gauche, 1 : droite
        self.v = 0 # -1 : haut,   1 : bas
        self.directionArriere = None
        
        # passage de l'autre côté du level ou pas
        self.swap = False

        # un objet pathFinder propre qui trouvera le chemin le plus court pour atteindre une case d'arrivée (mode démo)
        # l'attribut path contiendra toutes les coordonnées des cases sur lesquelles se déplacer
        self.pathFinder = None
        self.path = []
        self.caseArrivee = None

        # liste contenant les boules et les pacgommes du level courant mélangées pour en choisir une au hasard en case d'arrivée dans la démo
        self.listeBoulesPacgommes = pg.sprite.Group()

        # après avoir manger une boule doit-on jouer le son 1 ,si oui on jouera le son 2 pour la suivante
        self.joueSonBoule1 = True

        # les fantomes mangés par paco
        self.fantomesManges = []
        
        # attributs relatif à l'animation
        self.indiceAnimation = 0
        self.tempsDebutImage = 0        
        self.ms_image = 100
        self.comptRotation90 = 12
        self.imageRotation = None
        
    def update(self):
        """Mise à jour des coordonnées du joueur en mode jeu."""
        
        self.rect = self.rect.move((self.h*self.vitesse,self.v*self.vitesse))

        # prise en compte du changement de coté du level
        self.swap = False
        if self.rect.right > self.levelCourant.rect.right:
            self.swap = True
            self.rect.left = self.levelCourant.rect.left
        elif self.rect.left < self.levelCourant.rect.left:
            self.swap = True            
            self.rect.right = self.levelCourant.rect.right
        elif self.rect.top < self.levelCourant.rect.top:
            self.swap = True            
            self.rect.bottom = self.levelCourant.rect.bottom
        elif self.rect.bottom > self.levelCourant.rect.bottom:
            self.swap = True            
            self.rect.top = self.levelCourant.rect.top
        
        # prise en compte du changement de direction unilatérale entre 2 tiles
        if self.directionVoulue == 'droite' and self.h == -1:
            self.h = 1
            self.v = 0
            self.direction = 'droite'
            self.animation()                    
            return            
        elif self.directionVoulue == 'gauche' and self.h == 1:
            self.h = -1
            self.v = 0            
            self.direction = 'gauche'
            self.animation()                    
            return            
        elif self.directionVoulue == 'haut' and self.v == 1:
            self.h = 0            
            self.v = -1
            self.direction = 'haut'
            self.animation()                    
            return            
        elif self.directionVoulue == 'bas' and self.v == -1:
            self.h = 0
            self.v = 1            
            self.direction = 'bas'
            self.animation()                    
            return            
            
        # lorsque le joueur est sur un tile 
        if self.rect.y%HAUTEUR_TILE == 0 and self.rect.x%LARGEUR_TILE == 0:
            # on évalue si il peut prendre la direction voulue quand par exemple elle est différente de la direction actuelle
            self.ligne = self.rect.y/HAUTEUR_TILE
            self.colonne = self.rect.x/LARGEUR_TILE
            if self.directionVoulue == 'droite' :
                colonne = (self.colonne+1)%len(self.levelCourant.matrice[0])
                if self.levelCourant.matrice[int(self.ligne)][int(colonne)] != 1:
                    self.direction = 'droite'
                    self.h = 1
                    self.v = 0
                    self.animation()                    
                    return
            elif self.directionVoulue == 'gauche':
                colonne = (self.colonne-1)%len(self.levelCourant.matrice[0])
                if self.levelCourant.matrice[int(self.ligne)][int(colonne)] != 1:
                    self.direction = 'gauche'
                    self.h = -1
                    self.v = 0
                    self.animation()                    
                    return                    
            elif self.directionVoulue == 'haut':
                ligne = (self.ligne-1)%len(self.levelCourant.matrice)
                if self.levelCourant.matrice[int(ligne)][int(self.colonne)] != 1:
                    self.direction = 'haut'
                    self.h = 0
                    self.v = -1
                    self.animation()
                    return                    
            elif self.directionVoulue == 'bas':
                ligne = (self.ligne+1)%len(self.levelCourant.matrice)
                if self.levelCourant.matrice[int(ligne)][int(self.colonne)] != 1:
                    self.direction = 'bas'                    
                    self.h = 0
                    self.v = 1
                    self.animation()                    
                    return

            # si le joueur ne peut pas prendre la direction voulue, on évalue si il peut se déplacer dans sa direction actuelle
            colonne = (self.colonne+self.h)%len(self.levelCourant.matrice[0])
            ligne = (self.ligne+self.v)%len(self.levelCourant.matrice)

            if self.levelCourant.matrice[int(ligne)][int(colonne)] == 1:
                self.h = 0
                self.v = 0

        # on procède à l'animation                
        self.animation()

    def update_demo(self):
        """Mise à jour des coordonnées du joueur en mode démo."""

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
        # lorsque paco arrive sur une case      
        if self.rect.y%HAUTEUR_TILE == 0 and self.rect.x%LARGEUR_TILE == 0:
            self.ligne = self.rect.y/HAUTEUR_TILE
            self.colonne = self.rect.x/LARGEUR_TILE
            # si son chemin n'est pas vide            
            if self.path:
                self.h = self.path[0][0]-self.colonne
                # calcul des déplacements relatifs unitaires en tenant compte des swap écran
                self.h = abs(self.h) == 1 and self.h or (self.h and (self.h > 1 and -1 or 1))
                self.v = self.path[0][1]-self.ligne
                self.v = abs(self.v) == 1 and self.v or (self.v and (self.v > 1 and -1 or 1))                
                self.directionArriere = [self.v*-1,self.h*-1]                
                self.path.pop(0)

                # détermination des direction en fonction des déplacements relatifs unitaires
                if self.h > 0:
                    self.direction = 'droite'
                elif self.h < 0:
                    self.direction = 'gauche'
                if self.v > 0:
                    self.direction = 'bas'
                elif self.v < 0:
                    self.direction = 'haut'

            else:
                # si aucun chemin n'a été encore déterminé on stop paco en attendant                
                self.h,self.v = 0,0

        # arrivé sur l'avant dernière case, on a vidé le chemin
        if not self.path:
            # on choisi une boule au hasard et on initialise la case d'arrivée avec celle-ci
            boule = Joueur.containers.sprite.listeBoulesPacgommes.sprites()[randrange(len(Joueur.containers.sprite.listeBoulesPacgommes))]
            self.caseArrivee = (boule.ligne,boule.colonne)
            if not self.pathFinder.rechercheDemandee :
                # on calcule la ligne et la colonne de paco par anticipation 
                # ce qui permet de chercher un chemin à partir de la dernière case
                # pendant le dernier déplacement vers celle-ci : gain en fluidité
                self.ligne += self.v
                self.colonne += self.h
                self.pathFinder.rechercheDemandee = True

        # on procède à l'animation
        self.animation()
        
    def animation(self):
        """Méthode d'animation."""
        
        if self.etat == 'mort':
            if not self.modeEdition:
                if pg.time.get_ticks() - self.tempsDebutImage > self.ms_image:
                    self.imageRotation = pg.transform.rotate(self.imageRotation,-90)
                    self.image.blit(self.imageRotation,(0,0))                
                    self.tempsDebutImage = pg.time.get_ticks()
                    self.comptRotation90 -= 1
            else:
                self.comptRotation90 = 0
                    
        else:
            self.image.blit(self.dictionnaireAnimation[self.direction][self.indiceAnimation],(0,0))
            if pg.time.get_ticks() - self.tempsDebutImage > self.ms_image :
                self.indiceAnimation = (self.indiceAnimation+1)%2
                self.tempsDebutImage = pg.time.get_ticks()        
        
    def collision_pacgomme(self):
        """Méthode chargée de gerer la collision entre le joueur et une pacgomme."""
        
        if pg.sprite.spritecollide(self,Pacgomme.containers,1):
            if not self.modeDemo and not self.modeEdition:
                SON_PACGOMME.play()
            for fantome in Fantome.containers.sprites():
                if fantome.etat != 'retour':
                    fantome.etat_vulnerable()
        
    def collision_boule(self):
        """Méthode chargée de gerer la collision entre le joueur et une boule."""

        if pg.sprite.spritecollide(self,Boule.containers,1) and not self.swap:
            if not self.modeDemo and not self.modeEdition:            
                if self.joueSonBoule1 :
                        SON_BOULE1.play()
                else:
                    if not self.modeDemo and not self.modeEdition:
                        SON_BOULE2.play()
                self.joueSonBoule1 = not self.joueSonBoule1
        
    def collision_fantome(self):
        """Méthode chargée de gerer la collision entre le joueur et un fantome."""
        
        for fantome in pg.sprite.spritecollide(self,Fantome.containers,0):
            if fantome.etat == 'vulnerable':
                self.fantomesManges.append(fantome)
                if not self.modeDemo and not self.modeEdition:
                    SON_FANTOME.play()
                fantome.rectTexteMiam = fantome.texteMiam.get_rect(x=fantome.rect.x+self.levelCourant.camera.etat.x,
                                                                   y=fantome.rect.y+self.levelCourant.camera.etat.y)
                
                fantome.path = []
                fantome.caseArrivee = (fantome.ligneDepart,fantome.colonneDepart)
                fantome.pathFinder.marcheArrierePossible = True
                fantome.etat = 'retour'
                fantome.vitesse = 8
                
            elif fantome.etat == 'tueur' and self.etat != 'mort':
                if not self.modeDemo and not self.modeEdition:
                    SON_MORT.play()
                self.etat = 'mort'
                self.path = []
                self.vitesse = 0
                self.h = 0
                self.v = 0
                for fantome in Fantome.containers:
                    fantome.vitesse = 0

                self.tempsDebutAnimation = pg.time.get_ticks()
                self.comptRotation90 = 12
                self.imageRotation = self.dictionnaireAnimation[self.direction][1]
                break

    def etat_initial(self):
        """Méthode chargée de remettre le joueur à son état initial."""
        
        self.etat = 'vivant'
        self.vitesse = VITESSE_JOUEUR
        self.ligne = self.ligneDepart
        self.colonne = self.colonneDepart
        self.rect.topleft = (self.colonne*LARGEUR_TILE,self.ligne*HAUTEUR_TILE)
        self.path = []        
        self.h = 0
        self.v = 0
        self.direction = 'droite'                        
        self.directionVoulue = None
        self.caseArrivee = None        
        self.fantomesManges = []
        for fantome in Fantome.containers:
            fantome.etat_initial()
