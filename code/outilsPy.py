import sys
import numpy

from time import time, ctime

def tirageNormal(moy, et, n):
	#return numpy.random.normal(5, 2, 7) : une array de 7 valeurs issues d'une loi normale de moyenne 5 et ecart-type 2.
	return numpy.random.normal(moy, et, n)

def loiNormale(valeur, moyenne, ecartType):
	return ( 1 / ( ecartType * numpy.math.sqrt(2 * numpy.math.pi) ) ) * numpy.exp( - ( (valeur - moyenne) ** 2 ) / ( 2 * (ecartType ** 2) ) ) 

def ponderateurDeProba(coef, proba):
	#retourne une valeur qui tend vers 1 quand coef tend vers 1 et vers 0 quand coef tend vers 0
	#contrairement a coef*proba qui tend vers proba quand coef tend vers 1
	#utilise dans le simulateur de transitionDeClasseFermeture
	return coef * (proba + coef * (1-proba))

def timeurTot(deb, nbre, total):
	if (nbre<=0):
		nbre=1
	durees = ( time() - deb )
	duree =  durees / 60
	cycle = durees/nbre
	fin = deb + (cycle * total)
	print("Debut "+ctime(deb)+"  Fin prevue:"+ctime(fin))
	
def timeur(deb, tag="", fichier="tags.txt", rep="."):
	durees = ( time() - deb )
	duree =  durees / 60
	if (tag != ""):
		ok=False
		fichier = rep+"\\"+fichier
		remplaceOuAjoute(fichier, tag, durees)
	print(" ("+str(duree).split(".")[0] + "mn)" )

def setDeb(tag, fichier="tags.txt", rep="."):
	fichier = rep+"\\"+fichier
	duree = 0
	try: 
		with open(fichier, "r") as fi:
			lignes = fi.readlines()
			for ligne in lignes:
				if ( ligne.split("=")[0].upper() == tag.upper() ):
					duree = long(ligne.split("=")[1].split(".")[0])
					break
	except Exception:
		pass

	if (duree>0):
		print("Heure de fin estimee : "+ctime(time() + duree))

	return time()

def remplaceOuAjoute(fichier, tag, valeur):
	ok=False
	lignes = []
	try:
		with open(fichier, "r") as fi:
			lignes = fi.readlines()
			k=0
			for ligne in lignes:
				if ( ligne.split("=")[0].upper() == tag.upper() ):
					lignes[k] = tag+"="+valeur
					ok=True ; break
				k+=1
	except Exception:
		pass

	if (ok):
		with open(fichier, "w") as fi:
			fi.write(lignes)
	else:
		with open(fichier, "a") as fi:
			fi.write(tag+"="+valeur)

def log(ligne, fichier="log.txt", rep="."):
	fichier = rep+"\\"+fichier
	with open(fichier, "a") as fichier:
		fichier.write(ctime(time())+". "+ligne)

def setControleur(var, valeur, fichier="fichierControle.txt", rep="."):
	laVal = getControleur(var, fichier, rep)
	fichier = rep+"\\"+fichier
	with open(fichier, "w") as fichier:
		fichier.write(var+"="+str(valeur)+"="+str(time()))
	if (not laVal is None):
		if (laVal != valeur): return False
	return True

def getControleur(var, fichier="fichierControle.txt", rep="."):
	fichier = rep+"\\"+fichier
	try:
		with open(fichier, "r") as fichier:
			lignes = fichier.readlines()
			for ligne in lignes:
				if ( ligne.split("=")[0].upper() == var.upper()):
					heure = ctime(long(ligne.split("=")[2].split(".")[0]))
					return [ligne.split("=")[1], heure]
	except Exception:
		return None
	return None
