import MV
import logging

logger = logging.getLogger('anasyn')

class Pile(object):
    "Representation d'une pile pour representer la pile d'execution des instructions dans la MV"
    p = [] # Simulation de la pile avec une liste Python

    def __init__(self):
        self.p = []

    def getP(self):
        return self.p

    def setP(self,pile):
        self.p = pile

    def empiler(self,x):
        self.p.append(x)

    def depiler(self):
        return self.p.pop(-1)

    def lire(self):
        return self.p[-1]

class MachineVirtuelle(object):
    "Descripteur d'une instance de machine virtuelle qui executera une suite d'instructions (donnees sous forme de code objet)"
    etat = "" # Pas fondamentalement utile, mais simule l'etat d'arret ou de marche de la MV
    codeObjet = [] # Programme = liste d'instructions a executer
    compteurO = 0 # Adresse de la prochaine instruction
    pileDonnees = None # pile d'execution
    regIp = -1 # Registre IP pour sauvegarder l'adresse de sommet de pile ("pointeur de la pile")
    regBase = -1 # Registre Base pour sauvegarder l'adresse du premiere element du bloc de liaison de l'operation en cours d'execution

    def __init__(self):
        self.etat = "ARRET" # La MV est arretee tant qu'on n'a pas demarre l'execution

    def getCodeObjet(self):
        return self.codeObjet

    def getPileDonnees(self):
        return self.pileDonnees

    def getRegBase(self):
        return self.regBase

    def getCompteurO(self):
        return self.compteurO

    def setCodeObjet(self,codeObj):
        self.codeObjet = codeObj

    def setPileDonnees(self, pileD):
        self.pileDonnees = pileD

    def setRegBase(self,regB):
        self.regBase = regB

    def setCompteurO(self,compO):
        self.compteurO = compO


    def debutProg(self):
        "Debut du programme NilNovi"
        self.etat = "MARCHE"
        self.pileDonnees = MV.Pile()
        self.compteurO += 1
        self.regIp = -1

    def finProg(self):
        "Fin du programme NilNovi"
        self.etat = "ARRET"
        self.codeObjet = []
        self.compteurO = 0
        self.pileDonnees = MV.Pile()
        self.regBase = None
        self.regIp = -1

    def reserver(self,n):
        "Reserve n emplacements dans la pile d'execution"
        self.regIp += n
        for i in range(n):
            self.pileDonnees.empiler(-1) # la MV empile '-1' pour chaque case qu'elle veut reserver
        self.compteurO += 1

    def empiler(self,v):
        "Empile val dans la pile d'execution"
        self.pileDonnees.empiler(v)
        self.regIp += 1
        self.compteurO += 1

    def empilerAd(self,ad):
        "Empile l'adresse d'un emplacement de la pile"
        self.pileDonnees.empiler(ad)
        self.regIp += 1
        self.compteurO += 1

    def affectation(self):
        "Affecte la valeur au sommet de pile a la variable designee par l'emplacement sous le sommet"
        l = len(self.pileDonnees.getP())
        v = self.pileDonnees.depiler()
        ad = self.pileDonnees.depiler()
        if l-2 == ad:                             # Gestion d'un cas d'affectation particulier
            self.pileDonnees.empiler(v)
        else:
            if len(self.pileDonnees.getP()) == 0: # Gestion d'une autre configuration particuliere
                self.pileDonnees.empiler(v)
            else:
                self.pileDonnees.getP()[ad] = v
        self.regIp -= 2
        self.compteurO += 1

    def valeurPile(self):
        "Remplace le sommet de pile par la valeur designee par ce sommet"
        ad = self.pileDonnees.depiler()
        if len(self.pileDonnees.getP()) == 0: # Gestion d'une configuration particuliere
            v = ad
        else:
            v = self.pileDonnees.getP()[ad]
        self.pileDonnees.empiler(v)
        self.compteurO += 1

    def get(self):
        "Place la valeur lue (donnee par l'utilisateur) dans la variable designee par le sommet"
        ad = self.pileDonnees.depiler()
        print("Entrez une valeur")
        v = input()
        if len(self.pileDonnees.getP()) == 0: # Gestion d'une configuration particuliere
            self.pileDonnees.empiler(int(v))
        else:
            self.pileDonnees.getP()[ad] = int(v)
        self.regIp -= 1
        self.compteurO += 1

    def put(self):
        "Affiche la valeur en sommet de pile"
        v = self.pileDonnees.depiler()
        print("Put : "+str(v))
        self.regIp -= 1
        self.compteurO += 1

    def moins(self):
        "Calcule l'oppose de la valeur en sommet de pile"
        v = self.pileDonnees.getP()[-1]
        v = -v
        self.pileDonnees.empiler(v)
        self.compteurO += 1

    def sous(self):
        "Calcule la difference entre les 2 valeurs en sommet de pile"
        op2 = self.pileDonnees.depiler()
        op1 = self.pileDonnees.depiler()
        self.pileDonnees.empiler(op1-op2)
        self.regIp -= 1
        self.compteurO += 1

    def add(self):
        "Calcule la somme des 2 valeurs en sommet de pile"
        op2 = self.pileDonnees.depiler()
        op1 = self.pileDonnees.depiler()
        self.pileDonnees.empiler(op1 + op2)
        self.regIp -= 1
        self.compteurO += 1

    def mult(self):
        "Calcule le produit des 2 valeurs en sommet de pile"
        op2 = self.pileDonnees.depiler()
        op1 = self.pileDonnees.depiler()
        self.pileDonnees.empiler(op1 * op2)
        self.regIp -= 1
        self.compteurO += 1

    def div(self):
        "Divise la valeur sous le sommet par la valeur en sommet de pile"
        op2 = self.pileDonnees.depiler()
        op1 = self.pileDonnees.depiler()
        self.pileDonnees.empiler(op1 // op2)
        self.regIp -= 1
        self.compteurO += 1

    def egal(self):
        "Empile 1 si les 2 valeurs en sommet de pile sont egales, 0 sinon"
        v1 = self.pileDonnees.depiler()
        v2 = self.pileDonnees.depiler()
        if v1 == v2:
            b = 1
        else:
            b = 0
        self.pileDonnees.empiler(b)
        self.regIp -= 1
        self.compteurO += 1

    def diff(self):
        "Empile 0 si les 2 valeurs en sommet de pile sont egales, 1 sinon"
        v1 = self.pileDonnees.depiler()
        v2 = self.pileDonnees.depiler()
        if v1 != v2:
            b = 1
        else:
            b = 0
        self.pileDonnees.empiler(b)
        self.regIp -= 1
        self.compteurO += 1

    def inf(self):
        "Empile 1 si la valeur sous le sommet de la pile est inferieure a la valeur au sommet, 0 sinon"
        v1 = self.pileDonnees.depiler()
        v2 = self.pileDonnees.depiler()
        if v2 < v1:
            b = 1
        else:
            b = 0
        self.pileDonnees.empiler(b)
        self.regIp -= 1
        self.compteurO += 1

    def infeg(self):
        "Empile 1 si la valeur sous le sommet de la pile est inferieure ou egale a la valeur au sommet, 0 sinon"
        v1 = self.pileDonnees.depiler()
        v2 = self.pileDonnees.depiler()
        if v2 <= v1:
            b = 1
        else:
            b = 0
        self.pileDonnees.empiler(b)
        self.regIp -= 1
        self.compteurO += 1

    def sup(self):
        "Empile 1 si la valeur sous le sommet de la pile est superieure a la valeur au sommet, 0 sinon"
        v1 = self.pileDonnees.depiler()
        v2 = self.pileDonnees.depiler()
        if v2 > v1:
            b = 1
        else:
            b = 0
        self.pileDonnees.empiler(b)
        self.regIp -= 1
        self.compteurO += 1

    def supeg(self):
        "Empile 1 si la valeur sous le sommet de la pile est superieure ou egale a la valeur au sommet, 0 sinon"
        v1 = self.pileDonnees.depiler()
        v2 = self.pileDonnees.depiler()
        if v2 >= v1:
            b = 1
        else:
            b = 0
        self.pileDonnees.empiler(b)
        self.regIp -= 1
        self.compteurO += 1

    def et(self):
        "Empile 1 si les 2 valeurs en sommet de pile sont 1, 0 sinon"
        v1 = self.pileDonnees.depiler()
        v2 = self.pileDonnees.depiler()
        self.pileDonnees.empiler(v1 and v2)
        self.regIp -= 1
        self.compteurO += 1

    def ou(self):
        "Empile 1 si au moins l'une des 2 valeurs en sommet de pile est 1, 0 sinon"
        v1 = self.pileDonnees.depiler()
        v2 = self.pileDonnees.depiler()
        self.pileDonnees.empiler(v1 or v2)
        self.regIp -= 1
        self.compteurO += 1

    def non(self):
        "Empile 1 si la valeur en sommet de pile est 0, 0 sinon"
        b = self.pileDonnees.depiler()
        self.pileDonnees.empiler(not b)
        self.compteurO += 1

    def tra(self,ad):
        "Donne le controle a l'instruction situee a l'adresse ad (dans la partie programme)"
        self.compteurO = ad

    def tze(self,ad):
        "Donne le controle a l'instruction a l'adresse ad si le sommet de pile conient 0. Continue en sequence sinon"
        b = self.pileDonnees.depiler()
        if b == 1:
            self.compteurO += 1
        else:
            self.compteurO = ad
        self.regIp -= 1

    def reserverBloc(self):
        "Au moment de l'appel d'une operation, reserve et initialise un bloc de liaison"
        self.pileDonnees.empiler(self.regBase)
        self.pileDonnees.empiler(-1) # assurer la reservation de la case (meme si regIp pourrait aussi l'assurer)
        self.regIp += 2
        self.compteurO += 1

    
    def retourFonct(self):
        "Instruction generee a rencontre d'un return dans une fonction. Assure le retour"
        self.regIp = self.regBase
        adR = self.pileDonnees.getP()[self.regBase+1]
        regBasePre = self.pileDonnees.getP()[self.regBase]
        v = self.pileDonnees.depiler()
        for i in range(self.regBase,len(self.pileDonnees.getP())):
            if len(self.pileDonnees.getP()) > 0:
                self.pileDonnees.depiler()
        self.pileDonnees.empiler(v)
        self.regBase = regBasePre
        self.compteurO = adR

    def retourProc(self):
        "Instruction generee a la fin d'une procedure. Assure le retour"
        self.regIp = self.regBase-1
        adR = self.pileDonnees.getP()[self.regBase+1]
        regBasePre = self.pileDonnees.getP()[self.regBase]
        for i in range(self.regBase,len(self.pileDonnees.getP())+1):
            if len(self.pileDonnees.getP()) > 0:
                self.pileDonnees.depiler()
        self.regBase = regBasePre
        self.compteurO = adR

    def empilerParam(self,ad):
        "Instruction pour la gestion des parametres effectifs"
        v = self.pileDonnees.getP()[self.regBase+2+ad]
        self.pileDonnees.empiler(v)
        self.regIp += 1

    def traStat(self,ad,nbP):
        """ Instruction permettant l'appel d'une operation. Lors de l'execution, elle complete la structure creee par l'execution
            de l'instrucion reserverBloc, structure (situee a nbp positions sous le sommet de pile) en introduisant l'adresse de
            retour (qui est l'adresse suivant l'adresse de cette instruction). Cette structure est promue (nouveau) bloc de liaison.
            Enfin le CO avec la valeur ad """
        self.regBase = self.regIp - nbP - 1
        self.pileDonnees.getP()[self.regIp-nbP] = self.compteurO + 1
        self.compteurO = ad


    def mVExecution(self,listeCodeObj):
        "Methode principale de la MV : Lance l'execution de la MV sur le programme decrit par la liste d'instrucions 'listeCodeObj'"

        self.codeObjet = listeCodeObj

        if len(self.codeObjet) > 0:      # Verification que la liste d'instruction est non-vide
            instruct = self.codeObjet[0]
        else:
            logger.debug("Code objet vide")

        while instruct != "finProg()":   # Execution iterative de chacune des instruction reconnues
            logger.debug("Instruction : " + instruct)
            i = instruct.index(')')

            if instruct == "debutProg()":
                self.debutProg()
            elif instruct[:9] == "reserver(":
                self.reserver(int(instruct[9:i]))
            elif instruct[:8] == "empiler(":
                self.empiler(int(instruct[8:i]))
            elif instruct[:10] == "empilerAd(":
                self.empilerAd(int(instruct[10:i]))
            elif instruct == "affectation()":
                self.affectation()
            elif instruct == "valeurPile()":
                self.valeurPile()
            elif instruct == "get()":
                self.get()
            elif instruct == "put()":
                self.put()
            elif instruct == "moins()":
                self.moins()
            elif instruct == "sous()":
                self.sous()
            elif instruct == "add()":
                self.add()
            elif instruct == "mult()":
                self.mult()
            elif instruct == "div()":
                self.div()
            elif instruct == "egal()":
                self.egal()
            elif instruct == "diff()":
                self.diff()
            elif instruct == "inf()":
                self.inf()
            elif instruct == "infeg()":
                self.infeg()
            elif instruct == "sup()":
                self.sup()
            elif instruct == "supeg()":
                self.supeg()
            elif instruct == "et()":
                self.et()
            elif instruct == "ou()":
                self.ou()
            elif instruct == "non()":
                self.non()
            elif instruct[:4] == "tra(":
                self.tra(int(instruct[4:i]))
            elif instruct[:4] == "tze(":
                self.tze(int(instruct[4:i]))
            elif instruct == "reserverBloc()":
                self.reserverBloc()
            elif instruct == "retourFonct()":
                self.retourFonct()
            elif instruct == "retourProc()":
                self.retourProc()
            elif instruct[:13] == "empilerParam(":
                self.empilerParam(int(instruct[13:i]))
            elif instruct[:8] == "traStat(":
                j = instruct.index(',')
                self.traStat(int(instruct[8:j]),int(instruct[j+1:i]))
            else:
                logger.debug("Unknown instruction")

            logger.debug("contenu pile apres instruction : " + str((self.pileDonnees).getP()))
            logger.debug("cO = "+str(self.compteurO))
            logger.debug("base = "+str(self.regBase))
            logger.debug("ip = "+str(self.regIp))

            instruct = self.codeObjet[self.compteurO]

        if instruct == "finProg()":  # Execution de la fin du programme NilNovi
            print("Contenu pile finale : " + str((self.pileDonnees).getP()))
            self.finProg()
        else:
            logger.debug("Erreur : Pas d'instruction de fin de programme")

