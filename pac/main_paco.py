# -*- coding: Utf-8 -*
import pygame as pg
from pygame.locals import *
from constantes import *
from variables import *
from all_levels import *
from interface import *
from editeur_paco import *
from ecran_dialogue import *
from ecran_options import *

class Paco(object):
    def __init__(self):
        """Class principale préparant le jeu avant son lancement."""

        #+- Display et sa surface associée
        pg.display.set_mode((WIN_WIDTH,WIN_HEIGHT),MODE_ECRAN[0])        
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()

        #+- Attributs de contrôle du jeu
        self.quitterJeu = False
        self.retourMenu = False

        #+- Attribut contenant un objet 'levels' lui-même contenant tous les levels
        self.all_levels = None

        #+- Attribut contenant le nom levels
        self.nomLevels = NOM_TABLEAUX_DEFAUT
        
        #+- Attribut contrôlant l'affichage ou non de la map
        self.mapOn = False

        #+- Attribut contenant l'affichage des info en haut et en bas
        self.interface = None

        #+- Attribut de l'horloge de pygame
        self.clock = pg.time.Clock()

    def event_loop(self):
        """Récupération des événements utilisateur."""

        for event in pg.event.get():
            if event.type == KEYUP:
                # touche 'echapement' : retour                
                if event.key == K_ESCAPE:
                    if Ecran_Dialogue(self.screen,self.all_levels,"Retour Menu ?",['OUI','NON']).optionChoisie == 'OUI':
                        self.retourMenu = True
                # affichage de la map
                elif event.key == K_SPACE or event.key == K_RCTRL:
                    self.mapOn = False
                       
            if event.type == KEYDOWN:
                if event.key == K_SPACE or event.key == K_RCTRL:
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
                # touche menu
                elif event.key == K_o:
                    menu = Ecran_Options(self.screen,self.all_levels,[['Plein Ecran : ',MODE_ECRAN,[0,FULLSCREEN]],['Volume Musique : ',VOLUME_MUSIQUE,range(11)],['Volume Son : ',VOLUME_SON,range(11)]])
                    
    def update(self):
        """Méthode de mise à jour des éléments du jeu."""

        if not self.mapOn:
            # si le nombre de boule est nul
            if len(Boule.containers) == 0 :
                nbrVie = Joueur.containers.sprite.nbrVie
                pg.mixer.music.fadeout(3000)
                pg.time.wait(1000)
                # si on ne peut pas changer de level
                if not self.all_levels.changement_level(1):
                    if Ecran_Dialogue(self.screen,self.all_levels,'FELICITATIONS !!!',['Appuyez sur Entrer']).optionChoisie == 'Appuyez sur Entrer':
                        self.retourMenu = True
                # sinon on met à jour le nombre de vies du joueur
                else:
                    pg.mixer.music.play(-1)
                    Joueur.containers.sprite.nbrVie = nbrVie
            # si il reste des boules
            else:
                self.all_levels.levelCourant.update()

                # si paco est mort et qu'il vient de finir sa rotation sur lui-même
                if Joueur.containers.sprite.etat == 'mort' and Joueur.containers.sprite.comptRotation90 == -1 :
                    pg.time.wait(1000)
                    Joueur.containers.sprite.nbrVie -= 1
                    if Joueur.containers.sprite.nbrVie == 0:
                        pg.mixer.music.fadeout(3000)
                        if Ecran_Dialogue(self.screen,self.all_levels,'GAME OVER',['Appuyez sur Entrer']).optionChoisie == 'Appuyez sur Entrer':
                            self.retourMenu = True
                    else:
                        Joueur.containers.sprite.etat_initial()

            # mise à jour de l'interface
            self.interface.update()
  
    def draw(self):
        """Dessine le level courant et l'interface."""

        if not self.retourMenu:
            self.all_levels.levelCourant.draw(self.mapOn)
            if not self.mapOn:
                self.interface.draw()
        
    def display_fps(self):
        """Montre le taux de FPS."""
        
        caption = "{} - FPS: {:.0f}/{}".format(TITRE, self.clock.get_fps(),FPS)
        pg.display.set_caption(caption)

    def main_loop(self):
        """Boucle principale."""
        
        self.retourMenu = False        
        while not self.retourMenu:
            self.event_loop()
            self.update()
            self.draw()
            pg.display.flip()
            self.clock.tick(FPS)
            self.display_fps()

    def credits(self):
        """Affichage des crédits du jeu."""
        
        surface = pg.Surface((WIN_WIDTH,WIN_HEIGHT)).convert()
        surface.set_alpha(200)
        rectSurface = surface.get_rect()
        font = pg.font.Font(PATH_FONT2,60)
        titre = font.render(TITRE,1,(255,255,100))
        rectTitre = titre.get_rect(centerx=WIN_WIDTH/2,centery=100)
        surface.blit(titre,rectTitre)
        font = pg.font.Font(PATH_FONT2,20)
        texteQuitter = font.render("Echap pour quitter",1,(255,255,255))
        surface.blit(texteQuitter,(0,0))        
        credit=[('Programmeur','DRAKE'),('Idee originale',' TEENY ME'),('Musique Menu','Nils 505 Feske - Once'),('Musique Jeu',"L'homme Manete - Epic Champ")]
        posy = 180
        font = pg.font.Font(PATH_FONT2,40)        
        for c in credit:
            texte = font.render(c[0],1,(255,0,0))
            rectTexte = texte.get_rect(centerx=WIN_WIDTH/2,centery=posy)
            surface.blit(texte,rectTexte)
            texte = font.render(c[1],1,(255,255,255))
            rectTexte = texte.get_rect(centerx=WIN_WIDTH/2,centery=posy+40)
            surface.blit(texte,rectTexte)
            posy += 100
        retourMenu = False
        while not retourMenu:
            for event in pg.event.get():
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        retourMenu = True
            self.all_levels.levelCourant.draw()
            self.screen.blit(surface,rectSurface)
            pg.display.update()
            self.clock.tick(25)
        
    def menu(self):
        """"Menu principal."""

        pg.mouse.set_visible(False)
        if MODE_ECRAN[0] == FULLSCREEN:
            pg.time.wait(2000)
        pg.mixer.music.load(MUSIQUE_MENU)
        pg.mixer.music.play(-1)
        
        surfaceMenu = pg.Surface((WIN_WIDTH,WIN_HEIGHT)).convert()
        surfaceMenu.set_alpha(160)
        rectSurfaceMenu = surfaceMenu.get_rect()
        
        font = pg.font.Font(PATH_FONT1,94)
        texteTitre = font.render("PACO",1,(255,255,100))
        rectTexteTitre = texteTitre.get_rect(centerx=WIN_WIDTH/2,centery=100)
        font = pg.font.Font(PATH_FONT1,48)        
        texteOpt1 = font.render("1 : Jeu",1,(255,255,255))
        rectTexteOpt1 = texteOpt1.get_rect(x=WIN_WIDTH/4,centery=220)
        font = pg.font.Font(PATH_FONT1,16)                
        texteListeLevels = font.render(self.nomLevels,1,(255,255,255))
        rectTexteListeLevels = texteListeLevels.get_rect(x=WIN_WIDTH/4+58,centery=245)
        font = pg.font.Font(PATH_FONT1,48)        
        texteOpt2 = font.render("2 : Chargement",1,(255,255,255))
        rectTexteOpt2 = texteOpt2.get_rect(x=WIN_WIDTH/4,centery=280)
        texteOpt3 = font.render("3 : Editeur",1,(255,255,255))
        rectTexteOpt3 = texteOpt3.get_rect(x=WIN_WIDTH/4,centery=340)
        texteOpt4 = font.render("4 : Options",1,(255,255,255))
        rectTexteOpt4 = texteOpt4.get_rect(x=WIN_WIDTH/4,centery=400)
        texteOpt5 = font.render("5 : Credits",1,(255,255,255))
        rectTexteOpt5 = texteOpt5.get_rect(x=WIN_WIDTH/4,centery=460)

        surfaceMenu.blit(texteTitre,rectTexteTitre)
        surfaceMenu.blit(texteListeLevels,rectTexteListeLevels)
        surfaceMenu.blit(texteOpt1,rectTexteOpt1)
        surfaceMenu.blit(texteOpt2,rectTexteOpt2)
        surfaceMenu.blit(texteOpt3,rectTexteOpt3)
        surfaceMenu.blit(texteOpt4,rectTexteOpt4)
        surfaceMenu.blit(texteOpt5,rectTexteOpt5)        

        self.all_levels = All_Levels(self.screen,self.nomLevels,modeDemo=True)
        while not self.quitterJeu:
            for event in pg.event.get():
                if event.type == KEYUP:
                    # Quitter le jeu
                    if event.key == K_ESCAPE:
                        self.quitterJeu = True
                    # Nouvelle partie
                    if event.key == K_KP1:
                        surfaceChargement = pg.Surface((WIN_WIDTH,WIN_HEIGHT)).convert()
                        surfaceChargement.set_alpha(160)
                        rectSurfaceChargement = surfaceChargement.get_rect()
                        font = pg.font.Font(PATH_FONT2,26)
                        texteChargement = font.render("Veuillez patienter pendant le chargement...",1,(255,255,100))
                        rectTexteChargement = texteChargement.get_rect(centerx=WIN_WIDTH/2,centery=200)
                        surfaceChargement.blit(texteChargement,rectTexteChargement)
                        self.screen.blit(surfaceChargement,(0,0))
                        pg.display.update()
                        
                        pg.mixer.music.fadeout(2000)
                        self.all_levels = All_Levels(self.screen,self.nomLevels)
                        self.interface = Interface(self.all_levels)
                        
                        if Joueur.containers.sprite:
                            self.grilleOn = False
                            pg.mixer.music.load(MUSIQUE_JEU)
                            pg.mixer.music.play(-1)
                            self.main_loop() # <- appel de la main loop du jeu
                            pg.mixer.music.fadeout(2000)
                            
                        self.all_levels = All_Levels(self.screen,self.nomLevels,modeDemo=True)
                        pg.mixer.music.load(MUSIQUE_MENU)
                        pg.mixer.music.play(-1)
                    # Chargement
                    elif event.key == K_KP2:
                        listeNomsLevels = []
                        listeChemins = glob.glob(PATH_LEVELS)
                        for chemin in listeChemins:
                            (filepath,filename) = os.path.split(chemin)
                            listeNomsLevels.append(filename.split('.txt')[0])
                        listeNomsLevels.append("ANNULER")

                        nomLevels = Ecran_Dialogue(self.screen,self.all_levels,"CHARGEMENT",listeNomsLevels).optionChoisie
                        if nomLevels != "ANNULER":
                            self.nomLevels = nomLevels
                            self.all_levels = All_Levels(self.screen,self.nomLevels,modeDemo=True)
                            
                            font = pg.font.Font(PATH_FONT1,20)
                            texteListeLevels = font.render(nomLevels,1,(255,255,255))
                            surfaceMenu.fill((0,0,0))
                            surfaceMenu.blit(texteTitre,rectTexteTitre)
                            surfaceMenu.blit(texteListeLevels,rectTexteListeLevels)
                            surfaceMenu.blit(texteOpt1,rectTexteOpt1)
                            surfaceMenu.blit(texteOpt2,rectTexteOpt2)
                            surfaceMenu.blit(texteOpt3,rectTexteOpt3)
                            surfaceMenu.blit(texteOpt4,rectTexteOpt4)
                            surfaceMenu.blit(texteOpt5,rectTexteOpt5)                            
                    # Editeur
                    elif event.key == K_KP3:
                        pg.mixer.music.stop()
                        pg.mouse.set_visible(True)
                        editeur = EditeurPaco()
                        editeur.main_loop()
                        pg.display.set_mode((WIN_WIDTH,WIN_HEIGHT),MODE_ECRAN[0])
                        self.screen = pg.display.get_surface()
                        self.screen_rect = self.screen.get_rect()
                        self.all_levels = All_Levels(self.screen,self.nomLevels,modeDemo=True)
                        pg.mixer.music.load(MUSIQUE_MENU)
                        pg.mixer.music.play(-1)
                        pg.mouse.set_visible(False)
                    # Options
                    elif event.key == K_KP4:
                        options = Ecran_Options(self.screen,self.all_levels,[['Plein Ecran : ',MODE_ECRAN,[0,FULLSCREEN]],['Volume Musique : ',VOLUME_MUSIQUE,range(11)],['Volume Son : ',VOLUME_SON,range(11)]])
                        pg.mouse.set_visible(False)
                    # Credits
                    elif event.key == K_KP5:
                        self.credits()

            # démonstration en arrière plan
            if len(Boule.containers) == 0 :
                self.all_levels = All_Levels(self.screen,self.nomLevels,modeDemo=True)
            elif Joueur.containers.sprite.etat == 'mort' and Joueur.containers.sprite.comptRotation90 == 0 :
                pg.time.wait(1000)
                Joueur.containers.sprite.etat_initial()
            self.all_levels.levelCourant.update(modeDemo=True)                
            self.all_levels.levelCourant.draw()
            self.screen.blit(surfaceMenu,(0,0))
            pg.display.flip()
                
            self.clock.tick(FPS)
            self.display_fps()            

if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    try:
        fichier = open(os.path.join(SCRIPT_PATH,"ressources","levels",NOM_TABLEAUX_DEFAUT+'.txt'),'r')
    except:
        print("Le fichier contenant les levels par défaut est manquant.Veuillez en créer un via le module 'editeur_paco.py' et le nommer "+NOM_TABLEAUX_DEFAUT)
    else:
        fichier.close()
        pg.init()
        
        pg.key.set_repeat(20,100)
        
        pg.display.set_caption(TITRE)
        paco = Paco()
        paco.menu()
        pg.quit()
        for t in threading.enumerate():
            t.stop = True
    try:
        sys.exit()
    except:
        pass
