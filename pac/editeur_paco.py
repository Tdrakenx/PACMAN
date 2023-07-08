################################################################################
#                                                                              #
#                      Classe Editeur pour le jeu paco                         #
#                                                                              #
################################################################################
import pygame as pg
from pygame.locals import *
import os,sys,string
from all_levels import *
from joueur import *
from constantes import *
from ecran_dialogue import *

class ElementInterface(pg.sprite.Sprite):
    """Création des éléments qui seront dessinés dans l'interface de l'éditeur."""
    
    def __init__(self,x=0,y=0,chiffre=0,paco=False,fantome=False,boule=False,pacgomme=False,mur=False):
        pg.sprite.Sprite.__init__(self,self.containers)

        self.x = x
        self.y = y

        self.image = pg.Surface((LARGEUR_TILE,HAUTEUR_TILE)).convert()
        self.image.fill(COLOR_KEY)
        self.image.set_colorkey(COLOR_KEY)
        self.rect = self.image.get_rect()

        self.chiffre = chiffre

        if paco:
            self.image.blit(SPRITES_SHEET.subsurface((COORDS_JOUEUR_SPRITES[10][0][0][0]*32,COORDS_JOUEUR_SPRITES[10][0][0][1]*32,32,32)),(0,0))
        elif boule:
            pg.draw.circle(self.image,BOULE_COULEUR,self.rect.center,(self.rect.w-24)/2,0)
        elif pacgomme:
            pg.draw.circle(self.image,PACGOMME_COULEUR,self.rect.center,(self.rect.w-12)/2,0)
        elif mur:
            pg.draw.circle(self.image,MUR_COULEUR,self.rect.center,(self.rect.w-6)/2,0)
        elif fantome:
            self.image.blit(SPRITES_SHEET.subsurface((COORDS_FANTOMES_SPRITES[self.chiffre][0][0][0]*32,COORDS_FANTOMES_SPRITES[self.chiffre][0][0][1]*32,32,32)),(0,0))

        self.rect.topleft = (self.x,self.y)

class EditeurPaco(object):
    """Editeur."""
    def __init__(self):
        self.clock = pg.time.Clock()
        largeurInterface = 180

        # création du display et de sa surface associée
        pg.display.set_mode((WIN_WIDTH+largeurInterface,WIN_HEIGHT),MODE_ECRAN[0])
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        
        # interface du mode catalogue
        self.surfaceInterface1 = pg.Surface((largeurInterface,WIN_HEIGHT))
        self.surfaceInterface1.fill(BG_COLOR_INTERFACE)
        self.surfaceInterface1.set_alpha(190)
        self.rectInterface1 = self.surfaceInterface1.get_rect(x=WIN_WIDTH)
        font = pg.font.Font(None,21)
        textes = (('5 : entrer edition',200),
                  ('6 : level suivant',240),
                  ('4 : level precedant',260),
                  ('9 : ajouter colonne',300),
                  ('Maj+9 : retirer colonne',320),
                  ('7 : ajouter ligne',340),
                  ('Maj+7 : retirer ligne',360),                  
                  ('+ : inserer level',400),
                  ('- : supprimer level',420),
                  ('c : charger',480),
                  ('s : sauvegarder',500),
                  ('Echap : retour menu',540))
        for texte,posy in textes:
            surfaceTexte = font.render(texte,1,(255,255,255))
            self.surfaceInterface1.blit(surfaceTexte,(10,posy))

        # interface du mode édition
        self.surfaceInterface2 = pg.Surface((largeurInterface,WIN_HEIGHT))
        self.surfaceInterface2.fill(BG_COLOR_INTERFACE)
        self.surfaceInterface2.set_alpha(190)
        self.rectInterface2 = self.surfaceInterface2.get_rect(x=WIN_WIDTH)
        font = pg.font.Font(None,21)
        textes = (('5 : sortir edition',200),
                  ('t : test on/off',240),
                  ('fleches : camera',280),
                  ('espace : carte',300),
                  ('p : vide = boules',320),
                  ('g : grille',340),
                  ('c : charger',480),
                  ('s : sauvegarder',500),
                  ('Echap : retour menu',540))
        for texte,posy in textes:
            surfaceTexte = font.render(texte,1,(255,255,255))
            self.surfaceInterface2.blit(surfaceTexte,(10,posy))

        ElementInterface.containers = pg.sprite.LayeredUpdates()
        ElementInterface.containers.empty()
        paco = ElementInterface(x=WIN_WIDTH+73,y=10,chiffre=10,paco=True)

        boule = ElementInterface(x=WIN_WIDTH+74,y=52,chiffre=2,boule=True)
        pacgomme = ElementInterface(x=WIN_WIDTH+127,y=52,chiffre=3,pacgomme=True)
        mur = ElementInterface(x=WIN_WIDTH+21,y=52,chiffre=1,mur=True)

        f = ElementInterface(x=WIN_WIDTH+10,y=100,chiffre=11,fantome=True)
        f = ElementInterface(x=WIN_WIDTH+10,y=142,chiffre=15,fantome=True)
        
        f = ElementInterface(x=WIN_WIDTH+52,y=100,chiffre=12,fantome=True)
        f = ElementInterface(x=WIN_WIDTH+52,y=142,chiffre=16,fantome=True)
        
        f = ElementInterface(x=WIN_WIDTH+94,y=100,chiffre=13,fantome=True)
        f = ElementInterface(x=WIN_WIDTH+94,y=142,chiffre=17,fantome=True)        

        f = ElementInterface(x=WIN_WIDTH+136,y=100,chiffre=14,fantome=True)
        f = ElementInterface(x=WIN_WIDTH+136,y=142,chiffre=18,fantome=True)
        
        # l'élément actuel de l'interface sélectionné et son carré rouge l'entourant (le mur par défaut)
        self.selectionElement = ElementInterface.containers.sprites()[3]
        self.rectCarreSelection = ElementInterface.containers.sprites()[3].rect.copy()
        # 
        self.rectCarreSelectionFantome = Rect(-1,-1,0,0)

        # rectangle contenant la partie visible du level dans le display pour le clic souris
        self.rectEditeur = None

        # curseur central de la caméra qui se déplace via les touches de direction
        self.rectCurseurScrolling = Rect(0,0,32,32)
        self.rectCurseurScrolling.center = (WIN_WIDTH/2,WIN_HEIGHT/2)

        # mode édition ou mode catalogue
        self.modeEdition = False
        # carte du level demandé ou non
        self.mapOn = True
        # grille demandée
        self.grilleOn = False

        # nom du fichier contenant les levels
        self.nomLevels = "sans nom"
        self.texteNomLevels = None
        self.texteNbrLignes_NbrColonnes = None
        self.fontTexteLigneColonneSouris = pg.font.Font(None,24)
        self.texteLigneColonneSouris = None
        
        self.fontFPS = pg.font.Font(None,24)
        # l'objets levels correspondant au fichier chargé
        self.all_levels = None

        self.chargement_levels(self.nomLevels)

    def chargement_levels(self,nomLevels=None):
        """Chargement de la liste des levels."""

        if nomLevels != "sans nom":
            self.modeEdition = False
            self.nomLevels = nomLevels
            surfaceChargement = pg.Surface((WIN_WIDTH,WIN_HEIGHT)).convert()
            surfaceChargement.set_alpha(160)
            rectSurfaceChargement = surfaceChargement.get_rect()
            font = pg.font.Font(None,35)
            texteChargement = font.render("Veuillez patienter pendant le chargement...",1,(255,255,100))
            rectTexteChargement = texteChargement.get_rect(centerx=WIN_WIDTH/2,centery=150)                            
            surfaceChargement.blit(texteChargement,rectTexteChargement)
            self.screen.blit(surfaceChargement,(0,0))
            pg.display.update() 
        
        self.all_levels = All_Levels(self.screen,nomLevels,modeEdition=True)
        for level in self.all_levels.listeLevels:
            level.rectCurseurScrolling = self.rectCurseurScrolling
        self.rectEditeur = Rect(max((self.all_levels.levelCourant.camera.largeurFocus-self.all_levels.levelCourant.camera.largeurLevel)/2,0),
                                max((self.all_levels.levelCourant.camera.hauteurFocus-self.all_levels.levelCourant.camera.hauteurLevel)/2,0),
                                min(self.all_levels.levelCourant.largeur,WIN_WIDTH),min(self.all_levels.levelCourant.hauteur,WIN_HEIGHT))

        self.fontNomLevels = pg.font.Font(None,12)
        self.texteNomLevels = self.fontNomLevels.render(self.nomLevels,1,(255,255,255))

        self.fontNbrLignesNbrColonnes = pg.font.Font(None,16)
        self.texteNbrLignes_NbrColonnes = self.fontNbrLignesNbrColonnes.render('Lignes x Colonnes : '+str(self.all_levels.levelCourant.nbrLignes)+'x'+str(self.all_levels.levelCourant.nbrColonnes),1,(255,255,255))

    def main_loop(self):
        """Boucle principale de l'éditeur."""

        # vitesse horizontale et verticale de la caméra
        h_vittCamera, v_vittCamera = 0, 0
        quitter = False
        while not quitter:
            for event in pg.event.get():
                # Touches relevées
                if event.type == KEYUP:
                    # Echap : quitter éditeur
                    if event.key == K_ESCAPE:
                        if not self.all_levels.sauvegardeOk :
                            ed = Ecran_Dialogue(self.screen,self.all_levels,'Sauvegarder les changements ?',['OUI','NON','ANNULER'])
                            if ed.optionChoisie == 'OUI':
                                if self.all_levels.nomLevels != "sans nom":
                                    self.all_levels.sauver_levels()
                                    quitter = True                                    
                                else:
                                   nomLevels = self.recup_nom_levels()
                                   if nomLevels:
                                       self.all_levels.nomLevels = nomLevels
                                       self.nomLevels = nomLevels
                                       self.texteNomLevels = self.fontNomLevels.render(self.nomLevels,1,(255,255,255))
                                       self.all_levels.sauver_levels()
                                       quitter = True
                            elif ed.optionChoisie == 'NON':
                                quitter = True
                        else:
                            quitter = True                            
                    # C : charger liste
                    if event.key == K_c:
                        chargement = True
                        if not self.all_levels.sauvegardeOk :
                            ed = Ecran_Dialogue(self.screen,self.all_levels,'Sauvegarder les changements ?',['OUI','NON','ANNULER'])
                            if ed.optionChoisie == 'OUI':
                                if self.all_levels.nomLevels != "sans nom":
                                    self.all_levels.sauver_levels()
                                else:
                                    nomLevels = self.recup_nom_levels()
                                    if nomLevels:
                                        self.all_levels.nomLevels = nomLevels
                                        self.nomLevels = nomLevels                                        
                                        self.texteNomLevels = self.fontNomLevels.render(self.nomLevels,1,(255,255,255))
                                        self.all_levels.sauver_levels()
                                    else:
                                        chargement = False
                            elif ed.optionChoisie == 'ANNULER':
                                chargement = False

                        if chargement:
                            listeNomsLevels = []
                            listeChemins = glob.glob(PATH_LEVELS)
                            for chemin in listeChemins:
                                (filepath,filename) = os.path.split(chemin)
                                listeNomsLevels.append(filename.split('.txt')[0])
                            listeNomsLevels.append('ANNULER')
                            
                            nomLevels = Ecran_Dialogue(self.screen,self.all_levels,"CHARGEMENT",listeNomsLevels).optionChoisie
                            if nomLevels != 'ANNULER':
                                self.mapOn = True
                                self.texteNomLevels = self.fontNomLevels.render(self.nomLevels,1,(255,255,255))                                
                                self.rectCarreSelectionFantome = Rect(-1,-1,0,0)
                                self.selectionElement = ElementInterface.containers.sprites()[3]
                                self.rectCarreSelection = ElementInterface.containers.sprites()[3].rect.copy()
                                self.chargement_levels(nomLevels)
                                self.rectEditeur = Rect(max((self.all_levels.levelCourant.camera.largeurFocus-self.all_levels.levelCourant.camera.largeurLevel)/2,0),
                                                        max((self.all_levels.levelCourant.camera.hauteurFocus-self.all_levels.levelCourant.camera.hauteurLevel)/2,0),
                                                        min(self.all_levels.levelCourant.largeur,WIN_WIDTH),min(self.all_levels.levelCourant.hauteur,WIN_HEIGHT))
                    # S : sauvegarder liste
                    if event.key == K_s:
                        if self.all_levels.nomLevels != "sans nom":
                            self.all_levels.sauver_levels()
                        else:
                            nomLevels = self.recup_nom_levels()
                            if nomLevels:
                                self.all_levels.nomLevels = nomLevels
                                self.nomLevels = nomLevels                                
                                self.texteNomLevels = self.fontNomLevels.render(self.nomLevels,1,(255,255,255))
                                self.all_levels.sauver_levels()
                                
                    # 5 : entrer sortir mode édition
                    if event.key == K_KP5 :
                        self.mapOn = not self.mapOn
                        self.modeEdition = not self.modeEdition
                        if not self.modeEdition:
                            self.all_levels.levelCourant.creation_map()
                            self.all_levels.animation_level(vitesse=WIN_WIDTH)

                    if not self.modeEdition:
                        # 6 : tableau suivant (mode catalogue)
                        if event.key == K_KP6:
                            self.all_levels.changement_level(1)
                            self.rectCarreSelectionFantome = Rect(-1,-1,0,0)
                            self.selectionElement = ElementInterface.containers.sprites()[3]
                            self.rectCarreSelection = ElementInterface.containers.sprites()[3].rect.copy()
                            self.rectEditeur = Rect(max((self.all_levels.levelCourant.camera.largeurFocus-self.all_levels.levelCourant.camera.largeurLevel)/2,0),
                                                    max((self.all_levels.levelCourant.camera.hauteurFocus-self.all_levels.levelCourant.camera.hauteurLevel)/2,0),
                                                    min(self.all_levels.levelCourant.largeur,WIN_WIDTH),min(self.all_levels.levelCourant.hauteur,WIN_HEIGHT))
                        # 4 : tableau précédent (mode catalogue)
                        if event.key == K_KP4:
                            self.all_levels.changement_level(-1)
                            self.rectCarreSelectionFantome = Rect(-1,-1,0,0)
                            self.selectionElement = ElementInterface.containers.sprites()[3]
                            self.rectCarreSelection = ElementInterface.containers.sprites()[3].rect.copy()
                            self.rectEditeur = Rect(max((self.all_levels.levelCourant.camera.largeurFocus-self.all_levels.levelCourant.camera.largeurLevel)/2,0),
                                                    max((self.all_levels.levelCourant.camera.hauteurFocus-self.all_levels.levelCourant.camera.hauteurLevel)/2,0),
                                                    min(self.all_levels.levelCourant.largeur,WIN_WIDTH),min(self.all_levels.levelCourant.hauteur,WIN_HEIGHT))

                        # + : ajouter tableau
                        if event.key == K_KP_PLUS:
                            self.all_levels.nouveau_level()
                            self.all_levels.levelCourant.rectCurseurScrolling = self.rectCurseurScrolling
                            self.rectCarreSelectionFantome = Rect(-1,-1,0,0)
                            self.selectionElement = ElementInterface.containers.sprites()[3]
                            self.rectCarreSelection = ElementInterface.containers.sprites()[3].rect.copy()
                            self.rectEditeur = Rect(max((self.all_levels.levelCourant.camera.largeurFocus-self.all_levels.levelCourant.camera.largeurLevel)/2,0),
                                                    max((self.all_levels.levelCourant.camera.hauteurFocus-self.all_levels.levelCourant.camera.hauteurLevel)/2,0),
                                                    min(self.all_levels.levelCourant.largeur,WIN_WIDTH),min(self.all_levels.levelCourant.hauteur,WIN_HEIGHT))

                        # - : supprimer tableau
                        if event.key == K_KP_MINUS:
                            if Ecran_Dialogue(self.screen,self.all_levels,"SUPPRIMER CE TABLEAU ?",('OUI','NON',)).optionChoisie == 'OUI':
                                self.all_levels.supprimer_level()
                                self.rectCarreSelectionFantome = Rect(-1,-1,0,0)
                                self.selectionElement = ElementInterface.containers.sprites()[3]
                                self.rectCarreSelection = ElementInterface.containers.sprites()[3].rect.copy()
                                self.rectEditeur = Rect(max((self.all_levels.levelCourant.camera.largeurFocus-self.all_levels.levelCourant.camera.largeurLevel)/2,0),
                                                        max((self.all_levels.levelCourant.camera.hauteurFocus-self.all_levels.levelCourant.camera.hauteurLevel)/2,0),
                                                        min(self.all_levels.levelCourant.largeur,WIN_WIDTH),min(self.all_levels.levelCourant.hauteur,WIN_HEIGHT))

                        # 9 : ajouter/retirer colonne
                        if event.key == K_KP9:
                            mods = pg.key.get_mods()
                            if mods & KMOD_LSHIFT:
                                self.all_levels.levelCourant.supprimer_colonne()
                            else:
                                self.all_levels.levelCourant.ajouter_colonne()
                            self.all_levels.sauvegardeOk = False
                            self.rectEditeur = Rect(max((self.all_levels.levelCourant.camera.largeurFocus-self.all_levels.levelCourant.camera.largeurLevel)/2,0),
                                                    max((self.all_levels.levelCourant.camera.hauteurFocus-self.all_levels.levelCourant.camera.hauteurLevel)/2,0),
                                                    min(self.all_levels.levelCourant.largeur,WIN_WIDTH),min(self.all_levels.levelCourant.hauteur,WIN_HEIGHT))
                            self.all_levels.animation_level(WIN_WIDTH)
                            self.texteNbrLignes_NbrColonnes = self.fontNbrLignesNbrColonnes.render('Lignes x Colonnes : '+str(self.all_levels.levelCourant.nbrLignes)+'x'+str(self.all_levels.levelCourant.nbrColonnes),1,(255,255,255))                            
                        # 7 : ajouter/retirer ligne
                        if event.key == K_KP7:
                            mods = pg.key.get_mods()
                            if mods & KMOD_LSHIFT:
                                self.all_levels.levelCourant.supprimer_ligne()                                
                            else:
                                self.all_levels.levelCourant.ajouter_ligne()
                            self.all_levels.sauvegardeOk = False
                            self.rectEditeur = Rect(max((self.all_levels.levelCourant.camera.largeurFocus-self.all_levels.levelCourant.camera.largeurLevel)/2,0),
                                                    max((self.all_levels.levelCourant.camera.hauteurFocus-self.all_levels.levelCourant.camera.hauteurLevel)/2,0),
                                                    min(self.all_levels.levelCourant.largeur,WIN_WIDTH),min(self.all_levels.levelCourant.hauteur,WIN_HEIGHT))
                            self.all_levels.animation_level(WIN_WIDTH)
                            self.texteNbrLignes_NbrColonnes = self.fontNbrLignesNbrColonnes.render('Lignes x Colonnes : '+str(self.all_levels.levelCourant.nbrLignes)+'x'+str(self.all_levels.levelCourant.nbrColonnes),1,(255,255,255))
                    if self.modeEdition:
                        # m : enlever la carte
                        if event.key == K_SPACE or event.key == K_RCTRL:
                            self.mapOn = False
                        # g : grille on/off
                        if event.key == K_g:
                            self.grilleOn = not self.grilleOn
                        # touche droite : stop scrolling droit 
                        if event.key == K_RIGHT:
                            h_vittCamera, v_vittCamera = 0, 0
                        # touche gauche : stop scrolling gauche
                        if event.key == K_LEFT:
                            h_vittCamera, v_vittCamera = 0, 0
                        # touche haut : stop scrolling haut
                        if event.key == K_UP:
                            h_vittCamera, v_vittCamera = 0, 0
                        # touche bas : stop scrolling bas
                        if event.key == K_DOWN:
                            h_vittCamera, v_vittCamera = 0, 0
                        # p : les espaces sont comblés par des boules
                        if event.key == K_p:
                            for l in range(len(self.all_levels.levelCourant.matrice)):
                                for c in range(len(self.all_levels.levelCourant.matrice[0])):
                                    if self.all_levels.levelCourant.matrice[l][c] == 0:
                                        self.all_levels.levelCourant.matrice[l][c] = 2
                                        boule = Boule(c,l)
                        # t : test on/off
                        if event.key == K_t:
                            if Joueur.containers.sprite:
                                self.test_level()                            
                # Touches préssées
                if event.type == KEYDOWN and self.modeEdition:
                    # m : affichage de la carte
                    if event.key == K_SPACE or event.key == K_RCTRL:
                        self.mapOn = True
                        self.all_levels.levelCourant.creation_map(self.grilleOn)
                    # touche droite : scrolling droit
                    if event.key == K_RIGHT:
                        if self.all_levels.levelCourant.rectCurseurScrolling.centerx < self.all_levels.levelCourant.largeur - WIN_WIDTH/2:
                            h_vittCamera, v_vittCamera = 32, 0
                        else:
                            h_vittCamera, v_vittCamera = 0, 0
                    # touche gauche : scrolling gauche                            
                    if event.key == K_LEFT:
                        if self.all_levels.levelCourant.rectCurseurScrolling.centerx > WIN_WIDTH/2:
                            h_vittCamera, v_vittCamera = -32, 0
                        else:
                            h_vittCamera, v_vittCamera = 0, 0
                    # touche haut : scrolling haut                            
                    if event.key == K_UP:
                        if self.all_levels.levelCourant.rectCurseurScrolling.centery > WIN_HEIGHT/2:
                            h_vittCamera, v_vittCamera = 0, -32
                        else:
                            h_vittCamera, v_vittCamera = 0, 0
                    # touche bas : scrolling bas
                    if event.key == K_DOWN:
                        if self.all_levels.levelCourant.rectCurseurScrolling.centery < self.all_levels.levelCourant.hauteur - WIN_HEIGHT/2:
                            h_vittCamera, v_vittCamera = 0, 32
                        else:
                            h_vittCamera, v_vittCamera = 0, 0

                # Clique souris gauche
                if pg.mouse.get_pressed() == (1,0,0) and not self.mapOn:
                    # dans l'interface
                    if self.rectInterface1.collidepoint(pg.mouse.get_pos()):
                        try:
                            sp = ElementInterface.containers.get_sprites_at(pg.mouse.get_pos())[0]
                            self.rectCarreSelection = sp.rect
                            self.selectionElement = sp
                            if sp.chiffre in range(11,20):
                                for fantome in Fantome.containers:
                                    if fantome.chiffre == sp.chiffre:
                                        self.rectCarreSelectionFantome = fantome.rect
                                        break
                                    else:
                                        self.rectCarreSelectionFantome = Rect(-1,-1,0,0)
                            else:
                                self.rectCarreSelectionFantome = Rect(-1,-1,0,0)
                        except:
                            pass
                            
                    # dans le level
                    elif self.rectEditeur.collidepoint(pg.mouse.get_pos()):
                        ligne = ((pg.mouse.get_pos()[1]-self.all_levels.levelCourant.camera.etat.y)/HAUTEUR_TILE)
                        colonne = ((pg.mouse.get_pos()[0]-self.all_levels.levelCourant.camera.etat.x)/LARGEUR_TILE)
                        
                        if not self.all_levels.levelCourant.matrice[ligne][colonne] == self.selectionElement.chiffre and \
                           self.all_levels.levelCourant.matrice[ligne][colonne] not in range(10,21):
                            # impression du chiffre de l'élément dans la matrice
                            self.all_levels.levelCourant.matrice[ligne][colonne] = self.selectionElement.chiffre
                            self.all_levels.sauvegardeOk = False
                            # mur
                            if self.selectionElement.chiffre == 1:
                                Boule.containers.remove([boule for boule in Boule.containers if boule.ligne == ligne and boule.colonne == colonne])
                                Pacgomme.containers.remove([pacgomme for pacgomme in Pacgomme.containers if pacgomme.ligne == ligne and pacgomme.colonne == colonne])
                                self.all_levels.levelCourant.creation_murs()
                            # boule
                            elif self.selectionElement.chiffre == 2:
                                boule = Boule(colonne,ligne)
                                Pacgomme.containers.remove([pacgomme for pacgomme in Pacgomme.containers if pacgomme.ligne == ligne and pacgomme.colonne == colonne])
                                self.all_levels.levelCourant.creation_murs()
                            # pacgomme
                            elif self.selectionElement.chiffre == 3:
                                pacgomme = Pacgomme(colonne,ligne)
                                Boule.containers.remove([boule for boule in Boule.containers if boule.ligne == ligne and boule.colonne == colonne])
                                self.all_levels.levelCourant.creation_murs()
                            # joueur
                            elif self.selectionElement.chiffre == 10:
                                if Joueur.containers:
                                    self.all_levels.levelCourant.matrice[Joueur.containers.sprite.ligne][Joueur.containers.sprite.colonne] = 0
                                    Joueur.containers.sprite.rect.topleft = (colonne*LARGEUR_TILE,ligne*HAUTEUR_TILE)
                                    Joueur.containers.sprite.ligne = ligne
                                    Joueur.containers.sprite.colonne = colonne
                                else:
                                    joueur = Joueur(colonne,ligne,levelCourant=self.all_levels.levelCourant,coordSheet=COORDS_JOUEUR_SPRITES[self.all_levels.levelCourant.matrice[ligne][colonne]],modeEdition=True)
                                Boule.containers.remove([boule for boule in Boule.containers if boule.ligne == ligne and boule.colonne == colonne])
                                Pacgomme.containers.remove([pacgomme for pacgomme in Pacgomme.containers if pacgomme.ligne == ligne and pacgomme.colonne == colonne])
                                self.all_levels.levelCourant.creation_murs()
                            # fantomes
                            elif self.selectionElement.chiffre in range(11,20):
                                fantomeTrouve = False
                                for fantome in Fantome.containers:
                                    if fantome.chiffre == self.selectionElement.chiffre:
                                        fantomeTrouve = True
                                        self.all_levels.levelCourant.matrice[fantome.ligne][fantome.colonne] = 0
                                        Boule.containers.remove([boule for boule in Boule.containers if boule.ligne == fantome.ligne and boule.colonne == fantome.colonne])                                        
                                        fantome.rect.topleft = (colonne*LARGEUR_TILE,ligne*HAUTEUR_TILE)
                                        fantome.ligne = ligne
                                        fantome.colonne = colonne
                                        break
                                if not fantomeTrouve:
                                    fantome = Fantome(colonne,ligne,levelCourant=self.all_levels.levelCourant,coordSheet=COORDS_FANTOMES_SPRITES[self.all_levels.levelCourant.matrice[ligne][colonne]],chiffre=self.selectionElement.chiffre)
                                    fantome.pathFinder = PathFinder(fantome,False,True)
                                    self.rectCarreSelectionFantome = fantome.rect                                    
                                self.all_levels.levelCourant.matrice[fantome.ligne][fantome.colonne] = fantome.chiffre
                                Boule.containers.remove([boule for boule in Boule.containers if boule.ligne == ligne and boule.colonne == colonne])
                                Pacgomme.containers.remove([pacgomme for pacgomme in Pacgomme.containers if pacgomme.ligne == ligne and pacgomme.colonne == colonne])
                                self.all_levels.levelCourant.creation_murs()

                # Clique souris droit : effacement de l'élément de la matrice et de l'écran
                if pg.mouse.get_pressed() == (0,0,1) and not self.mapOn:
                    if self.rectEditeur.collidepoint(pg.mouse.get_pos()):
                        ligne = ((pg.mouse.get_pos()[1]-self.all_levels.levelCourant.camera.etat.y)/HAUTEUR_TILE)
                        colonne = ((pg.mouse.get_pos()[0]-self.all_levels.levelCourant.camera.etat.x)/LARGEUR_TILE)
                        
                        if self.all_levels.levelCourant.matrice[int(ligne)][int(colonne)] != 0 :
                            self.all_levels.levelCourant.matrice[int(ligne)][int(colonne)] = 0
                            self.all_levels.sauvegardeOk = False
                            Joueur.containers.remove([joueur for joueur in Joueur.containers if joueur.ligne == ligne and joueur.colonne == colonne])
                            Boule.containers.remove([boule for boule in Boule.containers if boule.ligne == ligne and boule.colonne == colonne])
                            Pacgomme.containers.remove([pacgomme for pacgomme in Pacgomme.containers if pacgomme.ligne == ligne and pacgomme.colonne == colonne])
                            fantome = [fantome for fantome in Fantome.containers if fantome.ligne == ligne and fantome.colonne == colonne]
                            Fantome.containers.remove(fantome)                            
                            if fantome:
                                if fantome[0].rect == self.rectCarreSelectionFantome:
                                    self.rectCarreSelectionFantome = Rect(-1,-1,0,0)
                            self.all_levels.levelCourant.creation_murs()

            # Blitting
            self.all_levels.levelCourant.draw(grilleOn=self.grilleOn,mapOn=self.mapOn)
            if self.modeEdition:
                self.screen.blit(self.surfaceInterface2,self.rectInterface2)
                ElementInterface.containers.draw(self.screen)
                self.all_levels.levelCourant.rectCurseurScrolling = self.all_levels.levelCourant.rectCurseurScrolling.move(h_vittCamera,v_vittCamera)
                self.all_levels.levelCourant.camera.update(self.all_levels.levelCourant.rectCurseurScrolling)
                pg.draw.rect(self.screen,(255,0,0),self.rectCarreSelection,2)
                if not self.mapOn:
                    pg.draw.rect(self.screen,(255,0,0),self.all_levels.levelCourant.camera.apply(self.rectCarreSelectionFantome),2)
                if self.rectEditeur.collidepoint(pg.mouse.get_pos()) and not self.mapOn:
                    ligne = ((pg.mouse.get_pos()[1]-self.all_levels.levelCourant.camera.etat.y)/HAUTEUR_TILE)
                    colonne = ((pg.mouse.get_pos()[0]-self.all_levels.levelCourant.camera.etat.x)/LARGEUR_TILE)
                    self.texteLigneColonneSouris = self.fontTexteLigneColonneSouris.render('L:'+str(ligne+1)+' C:'+str(colonne+1),1,(255,255,255))
                    self.screen.blit(self.texteLigneColonneSouris,(pg.mouse.get_pos()[0]+20,pg.mouse.get_pos()[1]))
            else:
                ElementInterface.containers.draw(self.screen)                
                self.screen.blit(self.surfaceInterface1,self.rectInterface1)

            self.screen.blit(self.texteNomLevels,(WIN_WIDTH+10,WIN_HEIGHT-30))
            self.screen.blit(self.texteNbrLignes_NbrColonnes,(WIN_WIDTH+10,WIN_HEIGHT-20))

            pg.display.flip()
            self.clock.tick(FPS)

    def test_level(self):
        """Méthode qui met en oeuvre une boucle principale comparable à celle du jeu."""

        # limites de la caméra en mode jeu
        self.all_levels.levelCourant.camera = Camera(WIN_WIDTH,WIN_HEIGHT,self.all_levels.levelCourant.largeur,self.all_levels.levelCourant.hauteur,192,416,192,416)        
       
        # départ des threads de recherche des fantomes
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

        texteInterface = "FPS : "+str(int(self.clock.get_fps()))+'/'+str(FPS)
        texteFps = self.fontFPS.render(texteInterface,1,(255,255,255))
        retour = False
        while not retour:
            for event in pg.event.get():
                # touche relevé
                if event.type == KEYUP:
                    # t : test off
                    if event.key == K_t:
                        retour = True
                    # m : carte off
                    elif event.key == K_SPACE or event.key == K_RCTRL:
                        self.mapOn = False
                # touche pressée
                if event.type == KEYDOWN:
                    # m : carte on
                    if event.key == K_SPACE or event.key == K_RCTRL:
                        if not self.mapOn:
                            self.mapOn = True
                            self.all_levels.levelCourant.creation_map()
                    # touche droite
                    elif event.key == K_RIGHT:
                        Joueur.containers.sprite.directionVoulue = 'droite'
                    # touche gauche
                    elif event.key == K_LEFT:
                        Joueur.containers.sprite.directionVoulue = 'gauche'
                    # touche haut
                    elif event.key == K_UP:
                        Joueur.containers.sprite.directionVoulue = 'haut'
                    # touche bas
                    elif event.key == K_DOWN:
                        Joueur.containers.sprite.directionVoulue = 'bas'

            if not self.mapOn:
                if Joueur.containers.sprite.fantomesManges:
                    for fantome in Joueur.containers.sprite.fantomesManges:
                        fantome.rect.topleft = (fantome.colonne*LARGEUR_TILE,fantome.ligne*HAUTEUR_TILE)
                    Joueur.containers.sprite.fantomesManges = []
                
            if Joueur.containers.sprite.etat == 'mort' :
                pg.time.wait(1000)
                Joueur.containers.sprite.etat_initial()

            # mise à jour des éléments du jeu
            if not self.mapOn:
                self.all_levels.levelCourant.update()
            # blitting  
            self.all_levels.levelCourant.draw(self.mapOn)
            self.screen.blit(self.surfaceInterface2,(WIN_WIDTH+1,0))
            ElementInterface.containers.draw(self.screen)                

            texteInterface = "FPS : "+str(int(self.clock.get_fps()))+'/'+str(FPS)
            texteFps = self.fontFPS.render(texteInterface,1,(255,255,255))
            self.screen.blit(texteFps,(0,0))            

            pg.display.flip()                            
            self.clock.tick(FPS)
            self.display_fps()              

        # arret des threads
        for t in threading.enumerate():
            t.stop = True
        # on recré le level 
        self.all_levels.levelCourant.creation_objets()
        # on remet les limite de la caméra en mode édition
        self.all_levels.levelCourant.camera = Camera(WIN_WIDTH,WIN_HEIGHT,self.all_levels.levelCourant.largeur,self.all_levels.levelCourant.hauteur)
        self.all_levels.levelCourant.camera.update(self.all_levels.levelCourant.rectCurseurScrolling)

    def display_fps(self):
        """Montre le taux de FPS."""
        
        caption = "{} - FPS: {:.0f}/{}".format(TITRE, self.clock.get_fps(),FPS)
        pg.display.set_caption(caption)

    def recup_nom_levels(self):
        """Méthode créant un écran de dialogue dans le display invitant l'utilisateur
          à entrer un nom fichier."""
        
        font = pg.font.Font(PATH_FONT2,40)    
        texteTitre = font.render('Nom de sauvegarde',1,(255,0,0))
        rectTitre = texteTitre.get_rect(centerx=WIN_WIDTH/2,y=200)
        surface = pg.Surface((WIN_WIDTH,WIN_HEIGHT)).convert()
        surface.set_alpha(200)
        rectSurface = surface.get_rect()
        surface.blit(texteTitre,rectTitre)

        font = pg.font.Font(PATH_FONT2,20)
        texteRetour = font.render('Echap : annuler',1,(255,255,255))
        rectRetour = texteRetour.get_rect()

        font = pg.font.Font(PATH_FONT2,40)
        listeFichiers = glob.glob('*.txt')
        nomExistant = False
        nom = ''
        retour = False
        while not retour:
            for event in pg.event.get():
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        retour = True
                        return False
                    if pg.key.name(event.key) in string.ascii_letters or pg.key.name(event.key).isdigit():
                        nom += pg.key.name(event.key)
                        texteNom = font.render(nom,1,(255,255,255))
                        rectNom = texteNom.get_rect(centerx=WIN_WIDTH/2,y=260)
                        surface.fill((0,0,0))
                        surface.blit(texteTitre,rectTitre)
                        surface.blit(texteNom,rectNom)                        
                    if pg.key.name(event.key) == 'backspace':
                        nom = nom[:-1]
                        texteNom = font.render(nom,1,(255,255,255))
                        rectNom = texteNom.get_rect()
                        rectNom.centerx = WIN_WIDTH/2
                        rectNom.y = 260
                        surface.fill((0,0,0))
                        surface.blit(texteTitre,rectTitre)
                        surface.blit(texteNom,rectNom)                          
                    if event.key == K_RETURN:
                        if nom+'.txt' in listeFichiers:
                            texteNomExistant = font.render('Nom de fichier existant !',1,(255,0,0))
                            rectNomExistant = texteNomExistant.get_rect(centerx=WIN_WIDTH/2,y=400)
                            self.screen.blit(texteNomExistant,rectNomExistant)
                            pg.display.update()
                            pg.time.wait(1000)
                        else:
                            return nom
            
            self.all_levels.levelCourant.draw()
            if self.modeEdition:
                self.screen.blit(self.surfaceInterface2,(WIN_WIDTH,0))
                ElementInterface.containers.draw(self.screen)                
            else:
                ElementInterface.containers.draw(self.screen)                
                self.screen.blit(self.surfaceInterface1,(WIN_WIDTH,0))

            self.screen.blit(surface,(0,0))

            pg.display.update()
            self.clock.tick(40)
    
if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.mixer.pre_init(22050,16,2,512)
    pg.init()

    pg.key.set_repeat(20,100)

    pg.display.set_caption("Editeur")
    SCRIPT_PATH=sys.path[0]

    editeurPaco = EditeurPaco()
    editeurPaco.main_loop()
    pg.quit()

    sys.exit()
