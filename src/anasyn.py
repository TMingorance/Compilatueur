#!/usr/bin/python

## 	@package anasyn
# 	Syntactical Analyser package. 
#

import sys, argparse, re
import logging

import analex
import MV

logger = logging.getLogger('anasyn')

DEBUG = False
LOGGING_LEVEL = logging.DEBUG


class AnaSynException(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

#########################################################################
#### Table des Identificateurs
#########################################################################

class Identificateur:
	nom = ''
	type = ''
	adresse = ''
	contexte = ''  #Deux identificateurs peuvent avoir le meme nom si ils ne sont pas dans le meme contexte, c'est-a-dire
	#si ils ne sont pas declares dans la meme fonction/procedure
	paramMode = ''
	nbParam = ''
	callLine = ''  #ligne a laquelle les tra et autres doivent envoyer pour appeler la fonction/procedure
	instancie = False  #Indique si une variable a ete assignee une valeur ou pas encore

	def __init__(self, nom, type, adresse, contexte, paramMode, nbParam, callLine):
		self.nom = nom
		self.type = type
		self.adresse = adresse
		self.contexte = contexte
		self.paramMode = paramMode
		self.nbParam = nbParam
		self.callLine = callLine

#y en a surement d'autres

class Contexte: #pour mettre dans contexteActuel, le numero sert d indice au tableau des compteurs d'adresses
	nom = ''
	numero = ''

	def __init__(self, nom, numero):
		self.nom = nom
		self.numero = numero


tabId = []  #table des identificateurs
tabIdSecondaire = []  #table permettant de gerer les declarations multiples de parametres et de variables
contexteActuel = []  #on va empiler les contextes : quand on entre dans une fct/proc on met le nom en queue de liste, et quand
##on sort d'une fonction, on depile, quand on met le contexte dans un identificateur, on prend la queue de liste

compteurAdresse = [0]  #Permet d'assigner une adresse a chaque variable dans son contexte : par exemple la premiere variable
#de la procedure principale aura 0 comme adresse, et le premier parametre, ou la premiere variable si il n'y a pas de parametre
#d'une sous-procedure aura egalement 0 comme adresse

tabInstr = []  #tableau qui contiendra en fin d'execution la suite d'instructions machine generee par la compilation

nbParam = 0  #Permet de compter le nombre de parametre d'une fonction/procedure

########################################################################
#### Syntactical Diagrams
########################################################################				 	

##Sont enregistres dans la table des identificateurs:
#Le programme principal
#les procedures et fonctions declares dans la partie declarations du prog princ
#leurs parametres
#les variables declarees dans n'importe quelle procedure ou fonction

def program(lexical_analyser):
	specifProgPrinc(lexical_analyser)
	lexical_analyser.acceptKeyword("is")
	corpsProgPrinc(lexical_analyser)

	
def specifProgPrinc(lexical_analyser):
	global compteurAdresse	#un prog princ peut pas avoir de param
	global tabId
	global contexteActuel
	lexical_analyser.acceptKeyword("procedure")
	ident = lexical_analyser.acceptIdentifier()

	##Remplissage de la table des identificateurs
	contexteActuel.append(Contexte(ident, 0))
	identificateur = Identificateur(ident, "procedure", '', contexteActuel[-1].nom,'','','')
	#compteurAdresse[contexteActuel[-1].numero] += 1
	tabId.append(identificateur)
	##

	logger.debug("Name of program : "+ident)

	
def corpsProgPrinc(lexical_analyser):
	global tabId
	global contexteActuel
	tabInstr.append("debutProg()")  #generation de code
	if not lexical_analyser.isKeyword("begin"):
		logger.debug("Parsing declarations")
		partieDecla(lexical_analyser)
		logger.debug("End of declarations")
	lexical_analyser.acceptKeyword("begin")

	if not lexical_analyser.isKeyword("end"):
		logger.debug("Parsing instructions")
		suiteInstr(lexical_analyser)
		logger.debug("End of instructions")

	lexical_analyser.acceptKeyword("end")
	lexical_analyser.acceptFel()
	tabInstr.append("finProg()")  # generation de code
	logger.debug("End of program")
	contexteActuel.pop(-1)
	logger.debug("\nTable des identificateurs \n")
	for identi in tabId:
		string = "nom : "+str(identi.nom)+" type : "+str(identi.type)+" adresse : "+str(identi.adresse)+" contexte : "+str(identi.contexte) + \
				 " paramMode : " + str(identi.paramMode)+" nbParam: " + str(identi.nbParam) + "\n"
		logger.debug(string)

	'''logger.debug("\n Commandes \n")
	for instr in tabInstr :
		logger.debug(instr)
	logger.debug ("\n")'''

def partieDecla(lexical_analyser):
		if lexical_analyser.isKeyword("procedure") or lexical_analyser.isKeyword("function") :
			listeDeclaOp(lexical_analyser)
			if not lexical_analyser.isKeyword("begin"):
				listeDeclaVar(lexical_analyser)
		else:
			listeDeclaVar(lexical_analyser)

def listeDeclaOp(lexical_analyser):
	declaOp(lexical_analyser)
	lexical_analyser.acceptCharacter(";")
	if lexical_analyser.isKeyword("procedure") or lexical_analyser.isKeyword("function") :
		listeDeclaOp(lexical_analyser)

def declaOp(lexical_analyser):
	if lexical_analyser.isKeyword("procedure"):
		procedure(lexical_analyser)
	if lexical_analyser.isKeyword("function"):
		fonction(lexical_analyser)

def procedure(lexical_analyser):
	global compteurAdresse
	global tabId
	global contexteActuel
	global nbParam
	lexical_analyser.acceptKeyword("procedure")
	ident = lexical_analyser.acceptIdentifier()

	##Remplissage de la table des identificateurs
	identificateur = Identificateur(ident, "procedure", '', contexteActuel[-1].nom, '', '', len(tabInstr) + 1)  #len(tabInstr) + 1 : on saute le tra du debut des lignes de fonctions
	contexte = contexteActuel[-1].nom
	#compteurAdresse[contexteActuel[-1].numero] += 1
	for identi in tabId:  #verification des doublons
		if identi.nom == ident and identi.contexte == contexteActuel[-1].nom :
			logger.error("Identificator already used <" + lexical_analyser.get_value() + ">!")
			raise AnaSynException("Identificator already used <" + lexical_analyser.get_value() + ">!")

	tabId.append(identificateur)
	##

	logger.debug("Name of procedure : "+ident)

	contexteActuel.append(Contexte(ident, len(compteurAdresse)))
	compteurAdresse.append(0)

	partieFormelle(lexical_analyser)

	for identi in tabId: #ajout du nbParam
		if identi.nom == ident and identi.contexte == contexte :
			identi.nbParam = nbParam
			nbParam = 0
			break  #on a verifie les doublons dans la table des id

	lexical_analyser.acceptKeyword("is")
	corpsProc(lexical_analyser)


def fonction(lexical_analyser):
	global compteurAdresse
	global tabId
	global contexteActuel
	global nbParam
	lexical_analyser.acceptKeyword("function")
	ident = lexical_analyser.acceptIdentifier()

	##Remplissage de la table des identificateurs
	identificateur = Identificateur(ident, "fonction", '', contexteActuel[-1].nom, '', '', len(tabInstr) + 1)  #len(tabInstr) + 1 : on saute le tra du debut des lignes de fonctions
	contexte = contexteActuel[-1].nom
	#compteurAdresse[contexteActuel[-1].numero] += 1

	for identi in tabId:  #verification des doublons
		if identi.nom == ident and identi.contexte == contexteActuel[-1].nom :
			logger.error("Identificator already used <" + lexical_analyser.get_value() + ">!")
			raise AnaSynException("Identificator already used <" + lexical_analyser.get_value() + ">!")

	tabId.append(identificateur)
	##

	logger.debug("Name of function : "+ident)
	contexteActuel.append(Contexte(ident, len(compteurAdresse)))
	compteurAdresse.append(0)

	partieFormelle(lexical_analyser)

	for identi in tabId:  #ajout du nbParam
		if identi.nom == ident and identi.contexte == contexte :
			identi.nbParam = nbParam
			nbParam = 0
			break  #on a verifie les doublons dans la table des id

	lexical_analyser.acceptKeyword("return")
	nnpType(lexical_analyser)

	lexical_analyser.acceptKeyword("is")
	corpsFonct(lexical_analyser)

def corpsProc(lexical_analyser):

	#generation de code
	tabInstr.append("tra(")
	address = len(tabInstr) - 1
	##

	if not lexical_analyser.isKeyword("begin"):
		partieDeclaProc(lexical_analyser)
	lexical_analyser.acceptKeyword("begin")
	suiteInstr(lexical_analyser)
	lexical_analyser.acceptKeyword("end")

	#generation de code
	tabInstr.append("retourProc()")
	tabInstr[address] += str(len(tabInstr)) + ")"
	contexteActuel.pop(-1)
	##

def corpsFonct(lexical_analyser):

	# generation de code
	tabInstr.append("tra(")
	address = len(tabInstr)-1
	##

	if not lexical_analyser.isKeyword("begin"):
		partieDeclaProc(lexical_analyser)
	lexical_analyser.acceptKeyword("begin")
	suiteInstrNonVide(lexical_analyser)
	lexical_analyser.acceptKeyword("end")

	# generation de code
	tabInstr.append("retourFonct()")
	tabInstr[address] += str(len(tabInstr)) + ")"
	contexteActuel.pop(-1)
	##

def partieFormelle(lexical_analyser):
	lexical_analyser.acceptCharacter("(")
	if not lexical_analyser.isCharacter(")"):
		listeSpecifFormelles(lexical_analyser)
	lexical_analyser.acceptCharacter(")")

def listeSpecifFormelles(lexical_analyser):  #gestion du parsing des parametres
	specif(lexical_analyser)
	if not lexical_analyser.isCharacter(")"):
		lexical_analyser.acceptCharacter(";")
		listeSpecifFormelles(lexical_analyser)

def specif(lexical_analyser):
	global tabId
	global tabIdSecondaire
	listeIdent(lexical_analyser)
	lexical_analyser.acceptCharacter(":")
	if lexical_analyser.isKeyword("in"):
		mode(lexical_analyser)

	nnpType(lexical_analyser)

	##Remplissage de la table des id
	for identi in tabIdSecondaire:
		if identi.paramMode == '':
			identi.paramMode = 'in'

	tabId = tabId + tabIdSecondaire
	tabIdSecondaire = []
	##


def mode(lexical_analyser):
	lexical_analyser.acceptKeyword("in")
	if lexical_analyser.isKeyword("out"):
		lexical_analyser.acceptKeyword("out")
		logger.debug("in out parameter")

		##Ajout du mode des parametres
		for identi in tabIdSecondaire :
			identi.paramMode = "in out"
		##

	else:
		logger.debug("in parameter")

		##Ajout du mode des parametres
		for identi in tabIdSecondaire:
			identi.paramMode = "in"
		##


def nnpType(lexical_analyser):
	global tabIdSecondaire
	if lexical_analyser.isKeyword("integer"):
		lexical_analyser.acceptKeyword("integer")

		##Ajout du type des parametres
		for identi in tabIdSecondaire :
			identi.type = "integer"
		##

		logger.debug("integer type")
	elif lexical_analyser.isKeyword("boolean"):
		lexical_analyser.acceptKeyword("boolean")

		##Ajout du type des parametres
		for identi in tabIdSecondaire :
			identi.type = "boolean"
		##

		logger.debug("boolean type")
	else:
		logger.error("Unknown type found <"+ lexical_analyser.get_value() +">!")
		raise AnaSynException("Unknown type found <"+ lexical_analyser.get_value() +">!")

def partieDeclaProc(lexical_analyser):
	listeDeclaVar(lexical_analyser)

def listeDeclaVar(lexical_analyser):
	declaVar(lexical_analyser)
	if lexical_analyser.isIdentifier():
		listeDeclaVar(lexical_analyser)

def declaVar(lexical_analyser):
	global tabId
	global tabIdSecondaire
	listeIdent(lexical_analyser)

	lexical_analyser.acceptCharacter(":")
	logger.debug("now parsing type...")
	nnpType(lexical_analyser)
	lexical_analyser.acceptCharacter(";")

	tabInstr.append("reserver(" + str(len(tabIdSecondaire))+ ")")  #generation de code

	#remplissage de la table des id
	tabId = tabId + tabIdSecondaire
	tabIdSecondaire = []

def listeIdent(lexical_analyser):
	global compteurAdresse
	global contexteActuel
	global tabIdSecondaire
	global nbParam
	ident = lexical_analyser.acceptIdentifier()
	logger.debug("identifier found: "+str(ident))

	##Remplissage de la table des identificateurs
	id = Identificateur(ident, "", compteurAdresse[contexteActuel[-1].numero], contexteActuel[-1].nom, '', '', '')

	for identi in tabId:  #verification des doublons
		if identi.nom == ident and identi.contexte == contexteActuel[-1].nom :
			logger.error("Identificator already used <" + lexical_analyser.get_value() + ">!")
			raise AnaSynException("Identificator already used <" + lexical_analyser.get_value() + ">!")

	for identi in tabIdSecondaire:  #verification des doublons
		if identi.nom == ident and identi.contexte == contexteActuel[-1].nom :
			logger.error("Identificateur déjà utilisé : " + lexical_analyser.traceback())
			raise AnaSynException("Identificateur déjà utilisé : " + lexical_analyser.traceback())

	tabIdSecondaire.append(id)
	nbParam += 1
	compteurAdresse[contexteActuel[-1].numero] += 1
	##

	if lexical_analyser.isCharacter(","):
		lexical_analyser.acceptCharacter(",")
		listeIdent(lexical_analyser)

def suiteInstrNonVide(lexical_analyser):
	instr(lexical_analyser)
	if lexical_analyser.isCharacter(";"):
		lexical_analyser.acceptCharacter(";")
		suiteInstrNonVide(lexical_analyser)

def suiteInstr(lexical_analyser):
	if not lexical_analyser.isKeyword("end"):
		suiteInstrNonVide(lexical_analyser)

def instr(lexical_analyser):
	global contexteActuel
	global tabId
	if lexical_analyser.isKeyword("while"):
		boucle(lexical_analyser)
	elif lexical_analyser.isKeyword("if"):
		altern(lexical_analyser)
	elif lexical_analyser.isKeyword("get") or lexical_analyser.isKeyword("put"):
		es(lexical_analyser)
	elif lexical_analyser.isKeyword("return"):
		retour(lexical_analyser)
	elif lexical_analyser.isIdentifier():
		ident = lexical_analyser.acceptIdentifier()
		if lexical_analyser.isSymbol(":="):  ##affectation
			lexical_analyser.acceptSymbol(":=")

			##
			#verification du type
			for identi in tabId:
				if ident == identi.nom and contexteActuel[-1].nom == identi.contexte :
					if (lexical_analyser.isKeyword("true") or lexical_analyser.isKeyword("false")) and \
							identi.type != "boolean":
						traceback = lexical_analyser.traceback()
						logger.error("Variable booléenne non trans-typable en entier :" + traceback)
						raise AnaSynException("Variable booléenne non trans-typable en entier : "+traceback)
					identi.instancie = True
					tabInstr.append("empilerAd(" + str(identi.adresse) + ")")  #generation de code
			##

			expression(lexical_analyser)
			# ensuite on append la valeur finale de l'expression (fait dans expression)

			##
			tabInstr.append("affectation()")  #Generation de code
			##

			logger.debug("parsed affectation")
		elif lexical_analyser.isCharacter("("):
			genererBloc(lexical_analyser,ident)
		else:
			logger.error("Expecting procedure call or affectation!")  #c'est l'erreur apparaissant quand on met un nom de variable tout seul sur une ligne
			raise AnaSynException("Expecting procedure call or affectation!")
		
	else:
		logger.error("Unknown Instruction <" + lexical_analyser.get_value() + ">!")
		raise AnaSynException("Unknown Instruction <" + lexical_analyser.get_value() + ">!")


def genererBloc(lexical_analyser, ident):
	lexical_analyser.acceptCharacter("(")

	##generation de code
	tabInstr.append("reserverBloc()")
	##

	if not lexical_analyser.isCharacter(")"):
		listePe(lexical_analyser)

	lexical_analyser.acceptCharacter(")")

	# generation de code
	for identi in tabId:
		if ident == identi.nom and contexteActuel[-1].nom == identi.contexte:
			tabInstr.append("traStat(" + str(identi.callLine) + "," + str(identi.nbParam) + ")")
	##

	logger.debug("parsed procedure call")


def listePe(lexical_analyser):  #liste des parametres d'entree d'une procedure ou fonction
	expression(lexical_analyser)
	if lexical_analyser.isCharacter(","):
		lexical_analyser.acceptCharacter(",")
		listePe(lexical_analyser)


def expression(lexical_analyser):
	logger.debug("parsing expression: " + str(lexical_analyser.get_value()))

	test = exp1(lexical_analyser)
	if lexical_analyser.isKeyword("or"):
		lexical_analyser.acceptKeyword("or")
		test = exp1(lexical_analyser) and test

		##generation de code
		tabInstr.append("ou()")
		##

	return test

def exp1(lexical_analyser):
	logger.debug("parsing exp1")
	
	test = exp2(lexical_analyser)
	if lexical_analyser.isKeyword("and"):
		lexical_analyser.acceptKeyword("and")
		test = exp2(lexical_analyser) and test

		##generation de code
		tabInstr.append("et()")
		##

	return test


def exp2(lexical_analyser):
	logger.debug("parsing exp2")
	test = exp3(lexical_analyser)
	if lexical_analyser.isSymbol("<"):
		opRel(lexical_analyser)
		exp3(lexical_analyser)

		##generation de code
		tabInstr.append("inf()")
		##
		return True
	elif lexical_analyser.isSymbol("<="):
		opRel(lexical_analyser)
		exp3(lexical_analyser)

		##generation de code
		tabInstr.append("infeg()")
		##

		return True
	elif lexical_analyser.isSymbol(">"):
		opRel(lexical_analyser)
		exp3(lexical_analyser)

		##generation de code
		tabInstr.append("sup()")
		##

		return True
	elif lexical_analyser.isSymbol(">="):
		opRel(lexical_analyser)
		exp3(lexical_analyser)

		##generation de code
		tabInstr.append("supeg()")
		##

		return True
	elif lexical_analyser.isSymbol("="):
		opRel(lexical_analyser)
		exp3(lexical_analyser)

		##generation de code
		tabInstr.append("egal()")
		##

		return True
	elif lexical_analyser.isSymbol("/="):
		opRel(lexical_analyser)
		exp3(lexical_analyser)

		##generation de code
		tabInstr.append("diff()")
		##

		return True

	return test

def opRel(lexical_analyser):
	logger.debug("parsing relationnal operator: " + lexical_analyser.get_value())
	if lexical_analyser.isSymbol("<"):
		lexical_analyser.acceptSymbol("<")
	elif lexical_analyser.isSymbol("<="):
		lexical_analyser.acceptSymbol("<=")
	elif lexical_analyser.isSymbol(">"):
		lexical_analyser.acceptSymbol(">")
	elif lexical_analyser.isSymbol(">="):
		lexical_analyser.acceptSymbol(">=")
	elif lexical_analyser.isSymbol("="):
		lexical_analyser.acceptSymbol("=")
	elif lexical_analyser.isSymbol("/="):
		lexical_analyser.acceptSymbol("/=")
	else:
		msg = "Unknown relationnal operator <"+ lexical_analyser.get_value() +">!"
		logger.error(msg)
		raise AnaSynException(msg)

def exp3(lexical_analyser):
	logger.debug("parsing exp3")
	test = exp4(lexical_analyser)
	if lexical_analyser.isCharacter("+"):
		opAdd(lexical_analyser)
		test = exp4(lexical_analyser)

		##generation de code
		tabInstr.append("add()")
		##

	elif lexical_analyser.isCharacter("-"):
		opAdd(lexical_analyser)
		test = exp4(lexical_analyser)

		##generation de code
		tabInstr.append("sous()")
		##
	return test

def opAdd(lexical_analyser):
	logger.debug("parsing additive operator: " + lexical_analyser.get_value())
	if lexical_analyser.isCharacter("+"):
		lexical_analyser.acceptCharacter("+")
	elif lexical_analyser.isCharacter("-"):
		lexical_analyser.acceptCharacter("-")
	else:
		msg = "Unknown additive operator <" + lexical_analyser.get_value() + ">!"
		logger.error(msg)
		raise AnaSynException(msg)

def exp4(lexical_analyser):
	logger.debug("parsing exp4")
	test = prim(lexical_analyser)
	if lexical_analyser.isCharacter("*"):
		opMult(lexical_analyser)
		prim(lexical_analyser)

		##generation de code
		tabInstr.append("mult()")
		##

	elif lexical_analyser.isCharacter("/"):
		opMult(lexical_analyser)
		prim(lexical_analyser)

		##generation de code
		tabInstr.append("div()")
		##
	return test

def opMult(lexical_analyser):
	logger.debug("parsing multiplicative operator: " + lexical_analyser.get_value())
	if lexical_analyser.isCharacter("*"):
		lexical_analyser.acceptCharacter("*")
	elif lexical_analyser.isCharacter("/"):
		lexical_analyser.acceptCharacter("/")
	else:
		msg = "Unknown multiplicative operator <" + lexical_analyser.get_value() + ">!"
		logger.error(msg)
		raise AnaSynException(msg)


operateur = "" 		#variable stockant l'operateur utilise
def prim(lexical_analyser):
	logger.debug("parsing prim")
	global operateur
	operateur = ""
	if lexical_analyser.isCharacter("+") or lexical_analyser.isCharacter("-") or lexical_analyser.isKeyword("not"):
		opUnaire(lexical_analyser)
	test = elemPrim(lexical_analyser)
	if operateur == "-":
		tabInstr.append("moins()")
	if operateur == "not":
		tabInstr.append("non()")
	return test

def opUnaire(lexical_analyser):
	logger.debug("parsing unary operator: " + lexical_analyser.get_value())
	global operateur
	if lexical_analyser.isCharacter("+"):
		lexical_analyser.acceptCharacter("+")
		operateur = "+"
	elif lexical_analyser.isCharacter("-"):
		lexical_analyser.acceptCharacter("-")
		operateur = "-"
	elif lexical_analyser.isKeyword("not"):
		lexical_analyser.acceptKeyword("not")
		operateur = "not"
	else:
		msg = "Unknown additive operator <" + lexical_analyser.get_value() + ">!"
		logger.error(msg)
		raise AnaSynException(msg)

def elemPrim(lexical_analyser):
	logger.debug("parsing elemPrim: " + str(lexical_analyser.get_value()))
	if lexical_analyser.isCharacter("("):
		lexical_analyser.acceptCharacter("(")
		test = expression(lexical_analyser)
		lexical_analyser.acceptCharacter(")")
		return test
	elif lexical_analyser.isInteger() or lexical_analyser.isKeyword("true") or lexical_analyser.isKeyword("false"):
		valeur(lexical_analyser)
		if lexical_analyser.isInteger():
			return True
		else:
			return False
	elif lexical_analyser.isIdentifier():

		##
		ident = lexical_analyser.acceptIdentifier()  #En fait l'identifiant ici est forcement un identifiant de fonction
		##

		if lexical_analyser.isCharacter("("):			# Appel fonct
			genererBloc(lexical_analyser, ident)

			logger.debug("Call to function: " + ident)
			return False
		else:
			logger.debug("Use of an identifier as an expression: " + ident)  #ici on met une variable pour faire appel a sa valeur
			test = False
			##
			for identi in tabId:
				if ident == identi.nom and contexteActuel[-1].nom == identi.contexte:
					#gestion d'erreurs
					if identi.type == "boolean" and not identi.instancie:
						traceback = lexical_analyser.traceback()
						logger.error("Variable booléenne non instanciée : " + traceback)
						raise AnaSynException("Variable booléenne non instanciée : " + traceback)
					if identi.type == "boolean":
						test = True
					else:
						test = False
					#generation de code
					tabInstr.append("empilerAd(" + str(identi.adresse) + ")")
			tabInstr.append("valeurPile()")
			##
			return test
	else:
		logger.error("Unknown Value!")
		raise AnaSynException("Unknown Value!")

def valeur(lexical_analyser):
	if lexical_analyser.isInteger():
		entier = lexical_analyser.acceptInteger()

		#generation de code
		tabInstr.append("empiler(" + str(entier) + ")")
		##

		logger.debug("integer value: " + str(entier))
		return "integer"
	elif lexical_analyser.isKeyword("true") or lexical_analyser.isKeyword("false"):
		vtype = valBool(lexical_analyser)
		return vtype
	else:
		logger.error("Unknown Value! Expecting an integer or a boolean value!")
		raise AnaSynException("Unknown Value ! Expecting an integer or a boolean value!")

def valBool(lexical_analyser):
	if lexical_analyser.isKeyword("true"):
		lexical_analyser.acceptKeyword("true")

		#generation de code
		tabInstr.append("empiler(1)")
		##

		logger.debug("boolean true value")
	else:
		logger.debug("boolean false value")
		lexical_analyser.acceptKeyword("false")

		#genration de code
		tabInstr.append("empiler(0)")
		##
	return "boolean"

def es(lexical_analyser):
	logger.debug("parsing E/S instruction: " + lexical_analyser.get_value())
	if lexical_analyser.isKeyword("get"):
		lexical_analyser.acceptKeyword("get")
		lexical_analyser.acceptCharacter("(")

		##
		ident = lexical_analyser.acceptIdentifier()
		for identi in tabId:
			if ident == identi.nom and contexteActuel[-1].nom == identi.contexte:
				#gestion d'erreur : get ne reçoit qu'un entier
				if not identi.type == "integer":
					traceback = lexical_analyser.traceback()
					logger.error("Variable non entière : " + traceback)
					raise AnaSynException("Variable non entière : " + traceback)
				#generation de code
				tabInstr.append("empilerAd(" + str(identi.adresse) + ")")
		##

		lexical_analyser.acceptCharacter(")")

		#generation de code
		tabInstr.append("get()")
		##

		logger.debug("Call to get "+ident)
	elif lexical_analyser.isKeyword("put"):
		lexical_analyser.acceptKeyword("put")
		lexical_analyser.acceptCharacter("(")
		expression(lexical_analyser)

		#generation de code
		tabInstr.append("put()")
		##

		lexical_analyser.acceptCharacter(")")
		logger.debug("Call to put")
	else:
		logger.error("Unknown E/S instruction!")
		raise AnaSynException("Unknown E/S instruction!")

def boucle(lexical_analyser):
	#gen term
	logger.debug("parsing while loop: ")
	lexical_analyser.acceptKeyword("while")

	adresseTra = len(tabInstr)
	test = expression(lexical_analyser)

	#vérification de l'expression booléenne
	if not test:
		traceback = lexical_analyser.traceback()
		logger.error("Expression <while> conditionnelle incorrecte : " + traceback)
		raise AnaSynException("Expression <while> conditionnelle incorrecte : " + traceback)

	lexical_analyser.acceptKeyword("loop")

	adresseTze = len(tabInstr)

	tabInstr.append("tze(")		#generation de code (adresse de la fin de la boucle, apres le "tra")
	##

	suiteInstr(lexical_analyser)

	#generation de code
	tabInstr.append("tra("+str(adresseTra)+")") 	#adresse du debut de la boucle, au debut de l'expression
	tabInstr[adresseTze] += str(len(tabInstr)) + ")"
	##

	lexical_analyser.acceptKeyword("end")
	logger.debug("end of while loop ")


def altern(lexical_analyser):
	logger.debug("parsing if: ")
	lexical_analyser.acceptKeyword("if")

	test = expression(lexical_analyser)

	#verification expression booléenne
	if not test:
		traceback = lexical_analyser.traceback()
		logger.error("Expression conditionnelle incorrecte : " + traceback)
		raise AnaSynException("Expression conditionnelle incorrecte : " + traceback)

	#generation de code
	adresseTze = len(tabInstr)
	tabInstr.append("tze(")  #adresse a la fin du if, apres suiteInstr
	##

	lexical_analyser.acceptKeyword("then")
	suiteInstr(lexical_analyser)

	if lexical_analyser.isKeyword("else"):

		#generation de code
		tabInstr[adresseTze] += str(len(tabInstr)+1) + ")"
		tabInstr.append("tra(")
		adressTra = len(tabInstr) - 1
		##

		lexical_analyser.acceptKeyword("else")
		suiteInstr(lexical_analyser)

		#generation de code
		tabInstr[adressTra] += str(len(tabInstr)) + ")"
		##

	else:

		#generation de code
		tabInstr[adresseTze] += str(len(tabInstr)) + ")"
		##
	lexical_analyser.acceptKeyword("end")
	logger.debug("end of if")


def retour(lexical_analyser):
	logger.debug("parsing return instruction")
	lexical_analyser.acceptKeyword("return")
	expression(lexical_analyser)


########################################################################				 	
def main():
	parser = argparse.ArgumentParser(description='Do the syntactical analysis of a NNP program.')
	parser.add_argument('inputfile', type=str, nargs=1, help='name of the input source file')
	parser.add_argument('-o', '--outputfile', dest='outputfile', action='store', default="", help='name of the output file (default: stdout)')
	parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
	parser.add_argument('-d', '--debug', action='store_const', const=logging.DEBUG, default=logging.INFO, help='show debugging info on output')
	parser.add_argument('-p', '--pseudo-code', action='store_const', const=True, default=False, help='enables output of pseudo-code instead of assembly code')
	parser.add_argument('--show-ident-table', action='store_true', help='shows the final identifiers table')
	args = parser.parse_args()

	filename = args.inputfile[0]
	f = None
	try:
		f = open(filename, 'r')
	except:
		logger.error("Error: can\'t open input file!")
		return

	outputFilename = args.outputfile
	
	# create logger
	LOGGING_LEVEL = args.debug
	logger.setLevel(LOGGING_LEVEL)
	ch = logging.StreamHandler()
	ch.setLevel(LOGGING_LEVEL)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	ch.setFormatter(formatter)
	logger.addHandler(ch)

	if args.pseudo_code:
		True  #
	else:
		False  #

	lexical_analyser = analex.LexicalAnalyser()
	
	lineIndex = 0
	for line in f:
		line = line.rstrip('\r\n')
		lexical_analyser.analyse_line(lineIndex, line)
		lineIndex = lineIndex + 1
	f.close()

	# launch the analysis of the program
	lexical_analyser.init_analyser()
	program(lexical_analyser)
		
	if args.show_ident_table:
		print("------ IDENTIFIER TABLE ------")
		print(str(tabId))
		print("------ END OF IDENTIFIER TABLE ------")

	if outputFilename != "":
		try:
			output_file = open(outputFilename, 'w')
		except:
			print("Error: can\'t open output file!")
			return
	else:
		output_file = sys.stdout

	# Outputs the generated code to a file
	#instrIndex = 0
	#while instrIndex < codeGenerator.get_instruction_counter():
	#        output_file.write("%s\n" % str(codeGenerator.get_instruction_at_index(instrIndex)))
	#        instrIndex += 1
		
	if outputFilename != "":
		output_file.close()

	lexical_analyser.save_to_file("")

	for lexicalUnit in lexical_analyser.lexical_units:
		logger.debug(str(lexicalUnit))

	for i in range(len(tabInstr)):
		logger.debug(str(i)+' : '+tabInstr[i])

	#Execution de la machine virtuelle
	mv = MV.MachineVirtuelle()
	mv.mVExecution(tabInstr)


########################################################################				 

if __name__ == "__main__":
	main()
