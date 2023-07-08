################################################################################
#                                                                              #
#                        Classe Caméra pour le jeu paco                        #
#                                                                              # 
################################################################################
import pygame as pg
from pygame.locals import *
from constantes import *

class Camera(object):
    """Classe qui crée un objet caméra qui permet de simuler son déplacement dans un level
        quand celui-ci est plus grand que le focus dans lequel apparaissent les éléments du jeu
        à l'écran quand la cible(obj de type Rect) de cette caméra se déplace."""
    def __init__(self, largeurFocus, hauteurFocus,
                 largeurLevel, hauteurLevel,
                 limiteHaute=None, limiteBasse=None, limiteGauche=None, limiteDroite=None):

        self.largeurFocus = largeurFocus
        self.hauteurFocus = hauteurFocus
        
        self.largeurLevel = largeurLevel
        self.hauteurLevel = hauteurLevel

        # position de la caméra par rapport au display
        self.etat = Rect(max((self.largeurFocus-self.largeurLevel),0)/2, max((self.hauteurFocus-self.hauteurLevel),0)/2, self.largeurLevel, self.hauteurLevel)

        if limiteHaute:
            self.limiteHaute = limiteHaute
        else:
            self.limiteHaute = hauteurFocus/2
        if limiteBasse:
            self.limiteBasse = limiteBasse
        else:
            self.limiteBasse = hauteurFocus/2
        if limiteGauche:
            self.limiteGauche = limiteGauche
        else:
            self.limiteGauche = largeurFocus/2
        if limiteDroite:
            self.limiteDroite = limiteDroite
        else:
            self.limiteDroite = largeurFocus/2

    def changement_Level(self,largeurLevel,hauteurLevel):
        """Mise à jour des dimensions du level."""
        
        self.largeurLevel = largeurLevel
        self.hauteurLevel = hauteurLevel
        self.etat = Rect(max((self.largeurFocus-self.largeurLevel),0)/2, max((self.hauteurFocus-self.hauteurLevel),0)/2, self.largeurLevel, self.hauteurLevel)

    def apply(self, cible):
        """Méthode qui renvoie la nouvelle position de la cible de type Rect reçue en fonction de la position courante de la caméra.
            A faire dans la boucle draw du programme principal."""
        return cible.move(self.etat.topleft)

    def update(self, cible):
        """Mise à jour de la position de la caméra en fonction de la position de la cible(obj Rect) par rapport aux limites de scrolling.
            A faire dans la boucle d'update du programme principal."""
        
        decalageX = self.etat.x
        decalageY = self.etat.y

        if self.largeurLevel > self.largeurFocus:
            if cible.centerx > self.limiteDroite-self.etat.x :
                decalageX = self.limiteDroite-cible.centerx
                decalageX = max(-(self.largeurLevel-self.largeurFocus), decalageX)

            if cible.centerx < self.limiteGauche-self.etat.x:
                decalageX = self.limiteGauche-cible.centerx
                decalageX = min(0, decalageX)

        if self.hauteurLevel > self.hauteurFocus:
            if cible.centery > self.limiteBasse-self.etat.y:
                decalageY = self.limiteBasse-cible.centery
                decalageY = max(-(self.hauteurLevel-self.hauteurFocus), decalageY)

            if cible.centery < self.limiteHaute-self.etat.y:
                decalageY = self.limiteHaute-cible.centery
                decalageY = min(0, decalageY)


        self.etat = Rect(decalageX, decalageY, self.largeurLevel, self.hauteurLevel)

    ###########################  PARTIE TEST #################################################
    def display_fps(self):
        """Montre le taux de FPS."""
        caption = "{} - FPS: {:.2f}".format("Camera", clock.get_fps())
        pg.display.set_caption(caption)

    def main_loop(self):
        global rectJoueur,h,v
        
        quitter = False
        while not quitter:
            for event in pg.event.get():
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        quitter = True
                if event.type == KEYUP:                        
                    if event.key == K_RIGHT:
                        h = 0
                        v = 0
                    elif event.key == K_LEFT:
                        h = 0
                        v = 0
                    elif event.key == K_UP:
                        h = 0
                        v = 0
                    elif event.key == K_DOWN:
                        h = 0
                        v = 0
                        
                if event.type == KEYDOWN:
                    if event.key == K_RIGHT:
                        h = 1
                        v = 0
                    elif event.key == K_LEFT:
                        h = -1
                        v = 0
                    elif event.key == K_UP:
                        h = 0
                        v = -1
                    elif event.key == K_DOWN:
                        h = 0
                        v = 1

            rectJoueur = rectJoueur.move(h*vitesse,v*vitesse)
            if rectJoueur.right > rectLevel.right:
                rectJoueur.right = rectLevel.right
            elif rectJoueur.left < 0:
                rectJoueur.left = 0
            elif rectJoueur.top < 0:
                rectJoueur.top = 0
            elif rectJoueur.bottom > rectLevel.bottom:
                rectJoueur.bottom = rectLevel.bottom
            camera.update(rectJoueur)
            screen.blit(surfaceLevel,camera.apply(rectLevel))
            screen.blit(surfaceJoueur,camera.apply(rectJoueur))
            pg.draw.line(screen,(255,0,0),(0,camera.limiteHaute),(LARGEUR_ECRAN,camera.limiteHaute),2)
            pg.draw.line(screen,(255,0,0),(0,camera.limiteBasse),(LARGEUR_ECRAN,camera.limiteBasse),2)
            pg.draw.line(screen,(255,0,0),(camera.limiteGauche,0),(camera.limiteGauche,HAUTEUR_ECRAN),2)
            pg.draw.line(screen,(255,0,0),(camera.limiteDroite,0),(camera.limiteDroite,HAUTEUR_ECRAN),2)
            pg.display.update()
            self.display_fps()
            clock.tick(40)
 
if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    
    pg.key.set_repeat(20,100)
    
    pg.display.set_caption("Camera")
    clock = pg.time.Clock()

    LARGEUR_TILE = 32
    HAUTEUR_TILE = 32
    LARGEUR_ECRAN = 32*19
    HAUTEUR_ECRAN = 32*19

    pg.display.set_mode((LARGEUR_ECRAN,HAUTEUR_ECRAN),0)
    
    screen = pg.display.get_surface()
    screen_rect = screen.get_rect()
    
    surfaceJoueur = pg.Surface((32,32))
    surfaceJoueur.fill((0,0,255))
    rectJoueur = surfaceJoueur.get_rect(x=9*32,y=9*32)
    h = 0
    v = 0
    vitesse = 8
    surfaceLevel = pg.Surface((32*38,32*38))
    rectLevel = surfaceLevel.get_rect()
    surfaceDamier = pg.Surface((32,32))                
    rectDamier = surfaceDamier.get_rect()
    for ligne in range(38):
        for colonne in range(38):
            if (ligne+colonne)%2 == 0:
                surfaceDamier.fill((200,200,200))
            else:
                surfaceDamier.fill((150,150,150))

            rectDamier.topleft = (colonne*32,ligne*32)
            surfaceLevel.blit(surfaceDamier,rectDamier)
    

#    camera = Camera(LARGEUR_ECRAN,HAUTEUR_ECRAN,rectLevel.w,rectLevel.h)
    camera = Camera(LARGEUR_ECRAN,HAUTEUR_ECRAN,rectLevel.w,rectLevel.h,96,512,96,512)    
    camera.main_loop()
    pg.quit()
        
