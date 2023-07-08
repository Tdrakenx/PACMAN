################################################################################
#                                                                              #
#                      Classe PathFinder pour le jeu paco                      #
#                                                                              # 
################################################################################
import pygame as pg
from pygame.locals import *
import threading
from constantes import *
from random import randrange,choice

class Noeud(object):
    """Classe qui crée un noeud pour l'algorithme A star."""
    def __init__(self,ligne,colonne):

        self.parent = self
        self.ligne = ligne
        self.colonne = colonne
        # coût de ce noeud au noeud de départ
        self.g = 0
        # coût de ce noeud au noeud d'arrivée
        self.h = 0
        # coût total du noeud de départ au noeud d'arrivée en passant par ce noeud
        self.f = 0
        
class PathFinder(threading.Thread):
    """Classe héritée d'un objet de type Threading qui met en place un algorithme A star afin
        de trouver le plus court chemin entre une case de départ et une case d'arrivée d'un d'objet de type mobile
        se déplaçant dans une matrice de tiles.Le path(chemin) résultant sera attribué à sa variable d'objet 'path' du mobile.
        Quand le mobile est créé il faut d'abord lui attribuer un objet PathFinder (ex : mobile.pathFinder = PathFinder(mobile)
        Dans l'update du mobile créer 2 cas, 1 pour le cas où le path éxiste et donc déplacer le mobile en concéquence,
        1 second pour le cas où le path est vide et donc demander une recherche de chemin après avoir déterminé une case d'arrivée.
        Ne pas oublier de lancer les threads par une boucle dans les containers des mobiles par :
            for mobile in Mobile.containers:
                mobile.pathFinder.start()
            avant chaque level et de les couper par
            for t in threading.enumerate:
                t.stop = True.
            à la fin du level"""
    def __init__(self,mobile,marcheArrierePossible=True,swap=False):
        threading.Thread.__init__(self)

        # attribut de contrôle du thread
        self.stop = False

        # attribut d'appartenance du path
        self.mobile = mobile

        # détermine si l'algorithme doit trouver une case du côté opposé lorsque le noeud courant est sur un des 4 bords
        self.swap = swap

        # noeud de départ
        self.noeudDepart = None        

        # noeud d'arrivée
        self.noeudArrivee = None        

        # liste contenant tous les noeuds voisins non envisagés pour le momment
        self.listeOuverte = []

        # liste contenant tous les noeuds déja envisagés
        self.listeFermee = []

        # liste des directions envisageables par rapport au noeud courant
        self.directions = [[-1,0],[0,1],[1,0],[0,-1]]

        # attribut de contrôle de la recherche
        self.rechercheDemandee = False
        
        # noeud correspondant à la marche arrière par rapport au noeud de départ quand celle-ci n'est pas possible
        self.marcheArrierePossible = marcheArrierePossible
        self.noeudMarcheArriere = None

        self.clock = pg.time.Clock()
        
    def set_noeuds(self,caseDepart,caseArrivee):
        """Initialisation d'une recherche de chemin."""
        
        self.noeudDepart = Noeud(caseDepart[0],caseDepart[1])
        self.noeudArrivee = Noeud(caseArrivee[0],caseArrivee[1])
        self.listeOuverte = []
        self.listeFermee = []
        self.noeudMarcheArriere = None

    def run(self):
        """Boucle principale du thread."""
        
        while not self.stop:
            if self.rechercheDemandee:
                ligne = self.mobile.ligne
                colonne = self.mobile.colonne
                directionArriere = None
                if self.mobile.caseArrivee :
                    self.set_noeuds((ligne,colonne),(self.mobile.caseArrivee[0],self.mobile.caseArrivee[1]))
                else:
                    while ligne == self.mobile.ligne and colonne == self.mobile.colonne or self.mobile.levelCourant.matrice[int(ligne)][int(colonne)] == 1 or\
                          self.mobile.levelCourant.matrice[int(ligne)][int(colonne)] == 0:
                        ligne = randrange(self.mobile.levelCourant.nbrLignes)
                        colonne = randrange(self.mobile.levelCourant.nbrColonnes)
                        
                    self.set_noeuds((self.mobile.ligne,self.mobile.colonne),(ligne,colonne))

                self.calcul_g(self.noeudDepart)
                self.calcul_h(self.noeudDepart)
                self.calcul_f(self.noeudDepart)
                self.listeOuverte.append(self.noeudDepart)     
                while self.listeOuverte != []:
                    noeudCourant = self.meilleur_noeud()
                    self.listeFermee.append(noeudCourant)
                    self.listeOuverte.remove(noeudCourant)
                    if (noeudCourant.ligne == self.noeudArrivee.ligne and noeudCourant.colonne == self.noeudArrivee.colonne):
                        break

                    for direction in self.directions:
                        voisin = None
                        # mode de recherche ne prennant pas en compte le swap écran
                        if not self.swap:
                            if 0 <= noeudCourant.ligne+direction[0] < len(self.mobile.levelCourant.matrice) and \
                               0 <= noeudCourant.colonne+direction[1] < len(self.mobile.levelCourant.matrice[0]) and\
                               self.mobile.levelCourant.matrice[noeudCourant.ligne+direction[0]][noeudCourant.colonne+direction[1]] != 1 :
                                voisin = Noeud(noeudCourant.ligne+direction[0],noeudCourant.colonne+direction[1])
                                voisin.parent = noeudCourant
                        # mode de recherche prennant en compte le swap écran                                
                        else:
                            ligne = (noeudCourant.ligne+direction[0])%len(self.mobile.levelCourant.matrice)
                            colonne = (noeudCourant.colonne+direction[1])%len(self.mobile.levelCourant.matrice[0])
                            if self.mobile.levelCourant.matrice[int(ligne)][int(colonne)] != 1 :
                                voisin = Noeud(ligne,colonne)                                
                                voisin.parent = noeudCourant

                        if voisin:
                            if not self.deja_present_dans_liste(voisin,self.listeFermee):
                                self.calcul_g(voisin)
                                self.calcul_h(voisin)
                                self.calcul_f(voisin)
                                n = self.deja_present_dans_liste(voisin,self.listeOuverte)
                                if n!= False:
                                    if voisin.g < n.g:
                                        n.parent = noeudCourant
                                        n.g = voisin.g
                                        n.h = voisin.h
                                        n.f = voisin.f
                                elif noeudCourant == self.noeudDepart and direction == self.mobile.directionArriere:
                                    self.noeudMarcheArriere = voisin
                                    if self.marcheArrierePossible:
                                        self.listeOuverte.append(voisin)
                                        self.noeudMarcheArriere = None
                                else:
                                    self.listeOuverte.append(voisin)
                    # quand la liste ouverte est vide, aucun chemin n'est possile
                    if not self.listeOuverte:
                        # si le mobile a pour case de départ un cul-de-sac après un déplacement vers celui-ci, on met la marche arrière dans la liste ouverte
                        if len(self.listeFermee) == 1 and self.noeudMarcheArriere:
                            self.listeOuverte.append(self.noeudMarcheArriere)
                            self.noeudMarcheArriere = None
                        # sinon on choisi un noeud de la liste fermée bordé par au moins 2 murs consécutifs
                        else:
                            listeNoeuds = []
                            if len(self.listeFermee) > 1:
                                for noeud in self.listeFermee:
                                    if noeud != self.noeudDepart:
                                        nbrMurs = 0                                    
                                        murEnHaut = False
                                        murAGauche = False
                                        for direction in self.directions:
                                            if self.swap:
                                                if self.mobile.levelCourant.matrice[int((noeud.ligne+direction[0])%len(self.mobile.levelCourant.matrice))][int((noeud.colonne+direction[1])%len(self.mobile.levelCourant.matrice[0]))] == 1:
                                                    nbrMurs += 1
                                                    if direction == [-1,0] :
                                                        murEnHaut = True
                                                    elif direction == [0,-1]:
                                                        murAGauche = True
                                                else:
                                                    nbrMurs = 0
                                            else:
                                                if not (0 <= noeud.ligne+direction[0] < len(self.mobile.levelCourant.matrice)) or \
                                                    not (0 <= noeud.colonne+direction[1] < len(self.mobile.levelCourant.matrice[0])) or\
                                                    self.mobile.levelCourant.matrice[int(noeud.ligne+direction[0])][int(noeud.colonne+direction[1])] == 1 :
                                                    nbrMurs += 1
                                                    if direction == [-1,0] :
                                                        murEnHaut = True
                                                    elif direction == [0,-1]:
                                                        murAGauche = True
                                                else:
                                                    nbrMurs = 0
                                            if murEnHaut and murAGauche:
                                                listeNoeuds.append(noeud)

                                            elif nbrMurs > 1:
                                                listeNoeuds.append(noeud)
                                                break
                                noeudArrive = choice(listeNoeuds)
                                self.mobile.caseArrivee = [noeudArrive.ligne,noeudArrive.colonne]                            

                if (noeudCourant.ligne == self.noeudArrivee.ligne and noeudCourant.colonne == self.noeudArrivee.colonne):
                    self.mobile.caseArrivee = None
                    self.rechercheDemandee = False
                    
                    path = []                    
                    n = self.listeFermee[-1]
                    path.append((n.colonne,n.ligne))
                    n = n.parent
                    while n.parent != n:
                        path.append((n.colonne,n.ligne))
                        n = n.parent
                    
                    path.reverse()
                   # print path

                    self.mobile.path = path

    def calcul_g(self,noeud):
        """Calcul du coût entre le noeud courant et le noeud de départ."""
        
        noeud.g = noeud.parent.g + 1#self.distance(noeud,noeud.parent)

    def calcul_h(self,noeud):
        """Calcul du coût entre le noeud courant et le noeud d'arrivée."""
        
        noeud.h = self.distance(noeud,self.noeudArrivee)

    def calcul_f(self,noeud):
        """Calcul du coût total entre le noeud de départ et le noeud d'arrivée en passant par le noeud courant."""
        
        noeud.f = noeud.g + noeud.h
        
    def distance(self,noeud1,noeud2):
        """Evaluation des distances entre 2 noeuds."""

        diffLigne = noeud1.ligne - noeud2.ligne
        diffColonne = noeud1.colonne - noeud2.colonne
        # distance de manhattan
#        return (abs(diffLigne) + abs(diffColonne))
        # distance euclidienne
#        return sqrt((diffLigne*diffLigne)+(diffColonne*diffColonne))
        # carré de la distance euclidienne
        return ((diffLigne*diffLigne)+(diffColonne*diffColonne))    
    
    def meilleur_noeud(self):
        """Evaluation du meilleur noeud de la liste ouverte par rapport à son coût F."""
        f = 10000
        meilleurNoeud = None
        for noeud in self.listeOuverte:
            if noeud.f < f:
                f = noeud.f
                meilleurNoeud = noeud

        return meilleurNoeud

    def deja_present_dans_liste(self,noeud,liste):
        """Vérifie si un noeud est déjà présent dans une liste donnée."""
        
        for n in liste:
            if n.ligne == noeud.ligne and n.colonne == noeud.colonne:
                return n
        return False
