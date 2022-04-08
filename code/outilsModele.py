import arcpy, sys
import numpy


from time import time, ctime
#Attention, des echecs de test d'exitence d'une feature class (arret du script) vient probablement
#du fait que la feature classe est corrompue. C'est abosulument bloquant (il faut creer une nouvelle
#file database...
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

def champTirageNormal(tab, champ, moy, et, clause="", min=0, max=5):
	inf0=False
	ajouteChamp(tab, champ, "FLOAT")
	n = int(arcpy.GetCount_management(tab).getOutput(0))

	lesAleas = tirageNormal(moy, et, n)
	k=0
	with arcpy.da.UpdateCursor(tab, [champ], clause) as curs:
		for row in curs:
			row[0] = lesAleas[k]
			if (row[0]<min):
				row[0] = min
			if (row[0]>max):
				row[0] = max
				inf0=True
			curs.updateRow(row)
			k+=1
	del curs
	if (inf0):
		print("WARNING: la fonction outils.champTirageNormal a mis a zero certaines valeurs inferieures a 0")

def reclassementSemantique(themeIn, champBrut, champRec, table, typecl="SHORT"):
	if (not arcpy.Exists(themeIn)):
		print(themeIn+" existe pas")
		exit(0)
	if not existeChamp(themeIn, champBrut):
		print(champBrut+" existe pas dans "+themeIn)
		exit(0)
	ok=False
	for f in facteurs:
		champ = f[3]
		if champRec == champ :
			ok=True
	if not ok:
		print("Le champ "+champRec+"n'est pas specifie dans facteurs (scenario : "+param.scenario+"). Verifier la structure facteurs du scenario, ou fournissez un nom de champ classe correct")
		exit(0)
	ajouteChamp(themeIn, champRec, typecl)
		
	print("Initialise "+champRec+" avec la source "+champBrut+" table de correspondance "+table+" sur le theme = "+themeIn)

	with open(table, "r") as filin:
		for ligne in filin:
			srcd = ligne.split("=")[0]
			val = ligne.split("=")[1]
			print("Reclassage pour "+srcd+" -> "+val)
			clause = champBrut + "=" + srcd
			
			if srcd.find("_") >=0:
				borneinf = (srcd.split("_")[0]).strip()
				bornesup = (srcd.split("_")[1]).strip()
				if (len(borneinf) > 0 and len(bornesup)>0):
					clause = champBrut + ">=" + borneinf + " and " +champBrut+ "<=" + bornesup
				elif len(borneinf) == 0:
					clause = champBrut+ "<=" + bornesup
				elif len(bornesup) == 0:
					clause = champBrut+ ">=" + borneinf

			print("Clause de reclassement : "+clause+" -> "+str(val))
			lesChamps = [champRec]
			with arcpy.da.UpdateCursor(themeIn, lesChamps, where_clause=clause ) as curseur:
				for row in curseur:
					row[0] = val
					curseur.updateRow(row)
			del curseur


def extraitDate(nomcov):
	try:
		return int( nomcov[len(nomcov)-4] )
	except Exception:
		try:
			return int( nomcov[len(nomcov)-2] )
		except Exception:
			return 0
def extraitNom(nomcov):
	tab=nomcov.split("\\")
	return tab[len(tab)-1]



def fixeSurfaceCible(covOcsol, champOcsol, cas, taux):
	statEtatIni = "statEtatIni"
	arcpy.Delete_management(statEtatIni)
	arcpy.Statistics_analysis(covOcsol, statEtatIni, [["Shape_Area", "SUM"]], champOcsol )

	surf = 0
	lesChamps = [champOcsol, "SUM_Shape_Area"]
	with arcpy.da.SearchCursor(statEtatIni, lesChamps) as cursor:
		for row in cursor:
			if (cas == 100):
				if (row[0] >= 100 and row[0] < 200):
					surf = surf + row[1]
			if (cas == 111):
				if (row[0] == 111):
					surf = surf + row[1]
			if (cas == 151):
				if (row[0] >= 100 and row[0] < 200 and row[0] != 112 ):
					surf = surf + row[1]
			if (cas == 200):
				if (row[0] >= 200 and row[0] < 300):
					surf = surf + row[1]
			if (cas == 300):
				if (row[0] >= 300 and row[0] < 600):
					surf = surf + row[1]
			if (cas == 600):
				if (row[0] >= 600 ):
					surf = surf + row[1]

	surfCible = (surf * taux)

	print("Surf initiale = " + str(surf) + " Cible = " +  str(surfCible))
	arcpy.Delete_management(statEtatIni)
	return [surf , surfCible]

def retirage(couverture, champAlea):
	#Attention: dans le blocks de code, le premier niveau d'indentation doit toujours etre a 0
	codeBlock = """
import numpy
def aleatoire():
	return numpy.random.random()
	"""
	arcpy.DeleteField_management(couverture, champAlea)
	ajouteChamp(couverture, champAlea, "FLOAT")
	arcpy.CalculateField_management(couverture, champAlea, "aleatoire()", "PYTHON_9.3", codeBlock)

def cibleObjectif(covOcsol, surfIni, surfCible, champTirage, fonctionTirage, postExpression, precision, autoriseNone ,codeBlock):

	txVar = 0.5
	surf = surfIni + 1
	coef = (surfCible / surfIni)         #non inclus dan parametres! il s'agit du coeficient initial maximum qui va se reduire        
	if (coef > 1): coef = 1                      #non inclus dan parametres!
    
	bloque = False
	firstBas = True ; firstHaut = True
	ntf=0
	surf = 0 ; surf0 = 0 ; surfM1 = 0
	freq = 0 ; freq0 = 0 ; freqM1 = 0 ; butee = 0 ; buteeMax = 3
	coefMin = 0 ; coefMax = 1
	butees = [0, 0]
	vientDuHaut = False ; vientDuBas = False

	while ( not bloque ):

		expression = fonctionTirage + "("+str(coef)+","+postExpression+")"
		print("TIRAGE (coef = "+str(coef)+"  coefMin="+str(coefMin)+"  coefMax="+str(coefMax)+")")
        #on reconstruit a chaque fois la chaine expression, car on fait evoluer coef....
    
		arcpy.CalculateField_management(covOcsol, champTirage, expression,
                        "PYTHON_9.3", codeBlock)
		stat = "stat"
		arcpy.Delete_management(stat)
		arcpy.Statistics_analysis(covOcsol, stat, [["Shape_Area", "SUM"]], champTirage )

		lesChamps = [champTirage, "SUM_Shape_Area" , "FREQUENCY"]

		with arcpy.da.SearchCursor(stat, lesChamps) as cursor:
			for row in cursor:
                #print(row)
				if ( row[0] == 1 ):
					surf = row[1]
					freq = row[2]
					if (not autoriseNone):
						if (row[0] == None):
							print("Erreur: Valeur None (non autorisee) trouvee dans le fichier des stats")
							exit()
		print("Transition : "+str(surf)+"  freq="+str(freq)+"  freq0="+str(freq0))
		
		if ( freq == freq0 ):
			butee = butee + 1
		else:
			if (freq == freqM1 and surf == surfM1):
				bloque = True
			else:
				freqM1 = freq0
				surfM1 = surf0
				freq0 = freq
				surf0 = surf
				butee = 0
			
		if (butee > buteeMax):
			bloque = True
			
		if ( (abs(surf - surfCible)/surfCible) < precision ):  
			bloque = True
		else:
			err = abs(surf - surfCible)/surfCible
			print("Erreur: %3.3f" %err + "  precision requise : %3.3f" %precision)
			
			if ( (surf - surfCible) > 0):
				firstBas = False
				print("%7.2f" % (surf/10000) + "ha Trop fort. Cible: %7.2f"%(surfCible/10000)+"ha  ("+str(freq)+" parcelles transitionnees)")

				coefMax = coef	
				coef0 = coef - (coef * txVar)
				ntf = 1
				while ( coef0 < coefMin ):
					ntf = ntf + 1
					tx = txVar / ntf
					coef0 = coef - (coef * tx)

				coef = coef0
				
				if (freq == 1):

					exces = ((surf - surfCible) / surfCible)
					
					print("Parcelle unique tiree de surface %3.1f"% (exces*100) +"% superieur a la surface cible")
					if ( exces < numpy.random.random() ):
						print("Decision de transition de la surface %7.1fha"%surf)
						bloque = True
						
			if ( (surf - surfCible) < 0):
				
				print("%7.2f" %(surf/10000) + "ha Trop bas. Cible: %7.2f"%(surfCible/10000)+"ha  ("+str(freq)+" parcelles transitionnees)")
				
				coefMin = coef	
				coef0 = coef + (coef * txVar)
				ntf = 1
				while ( coef0 > coefMax ):
					ntf = ntf + 1
					tx = txVar / ntf
					coef0 = coef + (coef * tx)
					
				coef = coef0
	return surf

def cibleObjectifSimple(covOcsol, surfIni, surfCible, champTirage, fonctionTirage, postExpression, precision, autoriseNone ,codeBlock):
	surf = surfIni + 1
	coef = (surfCible / surfIni)         #non inclus dan parametres! il s'agit du coeficient initial maximum qui va se reduire        
	if (coef > 1): coef = 1  
	lesTirages = []
	nTirage=0
	txVarCoefs = 0.5
	vientDuFaible = False ; vientDuFort = False
	ok=False
	maxButee = 3
	
	while ( not ok ):
   #On cherche le nombre de batis tires puis on reajuste coef pour toucher au plus juse
   #NE FONCTIONNE PAS ENCORE !
		ok = True
		expression = fonctionTirage + "("+str(coef)+","+postExpression+")"
		print("TIRAGE (coef = "+str(coef)+")")
	#on reconstruit a chaque fois la chaine expression, car on fait evoluer coef....

		arcpy.CalculateField_management(covOcsol, champTirage, expression,
					"PYTHON_9.3", codeBlock)
					
		stat = "stat"
		if (arcpy.Exists(stat)): arcpy.Delete_management(stat)
		arcpy.Statistics_analysis(covOcsol, stat, [["Shape_Area", "SUM"]], champTirage )

		lesChamps = [champTirage, "SUM_Shape_Area" , "FREQUENCY"]
		freq = 0
		with arcpy.da.SearchCursor(stat, lesChamps) as cursor:
			for row in cursor:
			#print(row)
				if ( row[0] == 1 ):
					surf = row[1]
					freq = row[2]
					if (freq == 0): freq = 1
					if (not autoriseNone):
						if (row[0] == None):
							print("Erreur: Valeur None (non autorisee) trouvee dans le fichier des stats")
							exit()

		print("Coef = "+str(coef)+" Transition : "+str(surf)+"  freq="+str(freq))
		
		#on verifie d'abord combien de fois cette solution a ete tiree, sinon il y a risque de partir en boucle...
		ecart = abs(surf - surfCible)
		sortieTirage = [surf, ecart, coef, freq]
		lesTirages.append(sortieTirage)
		butee = 0
		ecartMin = 9E99
		coefMin=-1
		surfMin = surf
		preok=False
		for nt in range(nTirage):
			unTirage = lesTirages[nt]
			if ( unTirage[1] < ecartMin ):
				ecartMin = unTirage[1]
				coefMin = unTirage[2]
				surfMin = unTirage[0]
			if (unTirage[0] == surf and unTirage[3] == freq):
				butee = butee + 1

		if( butee > 0 ): print("Solution deja tiree "+str(butee)+" fois")
		nTirage = nTirage + 1
		
		if (butee > maxButee and ecartMin < 9E99 and coefMin > 0):
			preok = True
			expression = fonctionTirage + "("+str(coefMin)+","+postExpression+")"
			print("RE-TIRAGE du coef = "+str(coefMin)+" -> surface attendue: "+str(surfMin))
			#on reconstruit a chaque fois la chaine expression, car on fait evoluer coef....

			arcpy.CalculateField_management(covOcsol, champTirage, expression,
					"PYTHON_9.3", codeBlock)
			surf = surfMin
			
		#Si cette solution n'a pas deja ete tiree (ou moins de buteeMax fois) on voit si elle est suffisamment proche de la cible
		if (not preok):
			if surf <  (surfCible - ( surfCible * precision )) :
				print ("Surf : %5.1f ha" % (surf/10000) + " trop faible (cible = %5.1f ha" % (surfCible/10000)+", precision="+str(precision)+" surfMin= %5.1f ha)"% ((surfCible - ( surfCible * precision ))/10000) )
				if (vientDuFort): 
					txVarCoefs = txVarCoefs / 2
				vientDuFort = False
				vientDuFaible = True
				coef = coef + (txVarCoefs * coef)
				ok = False


			if surf > (surfCible + ( surfCible * precision )) :
				print ("Surf : %5.1f ha" % (surf/10000) + " trop Fort (cible = %5.1f ha" % (surfCible/10000)+", precision="+str(precision)+" surfMax= %5.1f ha)"% ((surfCible + ( surfCible * precision ))/10000 ) )
				if (vientDuFaible):
					txVarCoefs = txVarCoefs / 2
				vientDuFaible = False
				vientDuFort = True
				coef = coef - (txVarCoefs * coef)
				ok = False
		else:
			ok = True

	return surf

def cibleObjectifComplexe(covOcsol, surfIni, surfCible, champTirage, fonctionTirage, postExpression, precision, autoriseNone ,codeBlock):

	ecartSup = surfIni
	ecartInf = surfIni

	txVar = 0.5
	surf = surfIni + 1
	coef = (surfCible / surfIni)		 #non inclus dan parametres! il s'agit du coeficient initial maximum qui va se reduire		
	if (coef > 1): coef = 1					  #non inclus dan parametres!
	inverse = False
	freq = 0
	bloque = False
	buteeBasse = 0
	buteeHaute = 0
	firstBas = True ; firstHaut = True
	ntf=0
	coefFort = 1 ; coefFaible = 0
	surf = 0
	freq = 0
	while ( not bloque ):
		print("ecartSup = "+str(ecartSup)+"  ecartInf = "+str(ecartInf)+" buteeHaute = "+str(buteeHaute)+"  buteeBasse = "+str(buteeBasse)+"  (maxButee = "+str(maxButee)+")")

		expression = fonctionTirage + "("+str(coef)+","+postExpression+")"
		print("TIRAGE (coef = "+str(coef)+")")
		#on reconstruit a chaque fois la chaine expression, car on fait evoluer coef....
	
		arcpy.CalculateField_management(covOcsol, champTirage, expression,
						"PYTHON_9.3", codeBlock)
		stat = "stat"
		arcpy.Delete_management(stat)
		arcpy.Statistics_analysis(covOcsol, stat, [["Shape_Area", "SUM"]], champTirage )
		
		lesChamps = [champTirage,  "SUM_Shape_Area" , "FREQUENCY"]
		
		with arcpy.da.SearchCursor(stat, lesChamps) as cursor:
			for row in cursor:
				#print(row)
				if ( row[0] == 1 ):
					surf = row[1]
					freq = row[2]
					if (not autoriseNone):
						if (row[0] == None):
							print("Erreur: Valeur None (non autorisee) trouvee dans le fichier des stats")
							exit()
		#print("Transition : "+str(surf)+ "  cible : "+str(surfArtifCible) + " diff = "+str(surf - surfArtifCible))
		
		if ( (abs(surf - surfCible)/surfCible) < precision ): bloque = True
		else:
			if ( surf - surfCible > 0):
				firstBas = False
				if ( (surf - surfCible) == ecartSup ):
					buteeHaute = buteeHaute + 1
					if (ecartSup <= ecartInf and buteeHaute > maxButee):
						bloque = True
						
				if (not bloque):		
					if ( (surf - surfCible) < ecartSup ):
						ecartSup = (surf - surfCible)
						
					
					print("%7.2f" % (surf/10000) + "ha Trop fort. Cible: %7.2f"%(surfCible/10000)+"ha  ("+str(freq)+" parcelles transitionnees)")
					#if (coef < coefFort) : coefFort = coef
					#else: coef = coefFort
					
					if (not firstHaut) :
						ntf = ntf + 1
						txVar = txVar / ntf
						
					coef = coef - (coef * txVar)
					
					#if (coef < coefFaible): coef = coefFaible
					
					if (freq == 1):

						exces = ((surf - surfCible) / surfCible)
						
						print("Parcelle unique tiree de surface %3.1f"% (exces*100) +"% superieur a la surface cible")
						if ( exces < numpy.random.random() ):
							print("Decision de transition de la surface %7.1fha"%surf)
							bloque = True
						
			if ( surf > 0 and (surf - surfCible) < 0):
				firstHaut = False
				if ( (surfCible - surf ) == ecartInf ):
					buteeBasse = buteeBasse + 1
					if (ecartInf < ecartSup and buteeBasse > maxButee):
						bloque = True
				if (not bloque):			
					if ( (surfCible - surf ) < ecartInf ):
							ecartInf = (surfCible - surf)
						
					
					print("%7.2f" %(surf/10000) + "ha Trop bas. Cible: %7.2f"%(surfCible/10000)+"ha  ("+str(freq)+" parcelles transitionnees)")
					#if (coef > coefFaible):coefFaible = coef
					#else : coef = coefFaible
					
					if (not firstBas) : 
						ntf = ntf + 1
						txVar = txVar / ntf
						
					coef = coef + (coef * txVar)
					
					#if (coef > coefFort): coef = coefFort

					if (freq == 1):
							print("Decision de transition de la surface %7.1fha"%surf)
							bloque = True
						
			if (surf <= 0):
				coef = coef + (coef * txVar)
				
	return surf


def cibleObjectifOLD(covOcsol, surfIni, surfCible, champTirage, fonctionTirage, postExpression, precision, autoriseNone ,codeBlock):

	ecartSup = surfIni
	ecartInf = surfIni
	borneSup = surfCible + surfCible * precision
	borneInf = surfCible - surfCible * precision
	minSurf = 0
	maxSurf = 2 * surfIni
	txVar = 0.5
	surf = borneSup + 1
	coef = 1								#non inclus dan parametres! il s'agit du coeficient initial maximum qui va se reduire		
											#non inclus dan parametres!
	inverse = False
	freq = 0
	bloque = False
	buteeBasse = 0
	buteeHaute = 0

	while ( ( surf > borneSup or surf < borneInf ) and not bloque ):
		print("MinSurf = "+str(minSurf)+"  MaxSurf = "+str(maxSurf)+" buteeHaute = "+str(buteeHaute)+"  buteeBasse = "+str(buteeBasse)+"  (maxButee = "+str(maxButee)+")")

		expression = fonctionTirage + "("+str(coef)+","+postExpression+")"
		print("TIRAGE (coef = "+str(coef)+")")
		#on reconstruit a chaque fois la chaine expression, car on fait evoluer coef....

		arcpy.CalculateField_management(covOcsol, champTirage, expression,
						"PYTHON_9.3", codeBlock)
		stat = "stat"
		arcpy.Delete_management(stat)
		arcpy.Statistics_analysis(covOcsol, stat, [["Shape_Area", "SUM"]], champTirage )

		lesChamps = [champTirage,  "SUM_Shape_Area" , "FREQUENCY"]
		surf = 0
		freq = 0
		with arcpy.da.SearchCursor(stat, lesChamps) as cursor:
			for row in cursor:
				print(row)
				if ( row[0] == 1 ):
					surf = row[1]
					freq = row[2]
					if (not autoriseNone):
						if (row[0] == None):
							print("Erreur: Valeur None (non autorisee) trouvee dans le fichier des stats")
							exit()

		#print("Transition : "+str(surf)+ "  cible : "+str(surfArtifCible) + " diff = "+str(surf - surfArtifCible))
		if (surf > borneSup):
			if (surf < maxSurf):
				maxSurf = surf
			else:
				buteeHaute = buteeHaute + 1
			
			ntf = 1
			print("%7.2f" % (surf/10000) + "ha Trop fort ( max = %7.2f" % (borneSup/10000) + "ha) ("+str(freq)+") parcelles transitees")
			coefFort = coef
			coef = coef - (coef * txVar)

			if (freq == 1):

				exces = ((surf - surfCible) / surfCible)
				
				print("Parcelle unique tiree de surface %3.1f"% (exces*100) +"% superieur a la surface cible")
				if ( exces < numpy.random.random() ):
					print("Decision de transition de la surface %7.1fha"%surf)
					bloque = True

		if (surf < borneInf):
			if (surf > minSurf):
				minSurf = surf
			else:
				buteeBasse = buteeBasse + 1

			ntf = ntf + 1
			print("%7.2f" %(surf/10000) + "ha Trop bas ( min = " + "%7.2f" %(borneInf/10000)+ "ha) ("+str(freq)+") parcelles transitees")
			txVar = txVar / ntf
			coef = coefFort - (coef * txVar)

			if (freq == 1):
					print("Decision de transition de la surface %7.1fha"%surf)
					bloque = True
					
		ecart = surf - surfCible
		if (buteeHaute > maxButee or buteeBasse > maxButee):
			bloque = True
	return surf


