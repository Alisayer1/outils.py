import arcpy, sys
import numpy


from time import time, ctime
#Attention, des echecs de test d'exitence d'une feature class (arret du script) vient probablement
#du fait que la feature classe est corrompue. C'est abosulument bloquant (il faut creer une nouvelle
#file database...

def recalculeChamp(tab, ch):
	if (existeChamp(tab, ch) or existeChamp(tab+".dbf", ch) ):
		a = raw_input("Le champ "+ch+" existe deja dans "+tab+". Recalculer (Y/N)? ")
		if (a.upper == 'Y'):
			return True
		else:
			return False
	return True

def supprimeCov(theme):
	if (existe(theme)):
		a = raw_input(theme+ " existe deja. Effacer (Y/N)? ")
		if (a.upper == 'Y'):
			arcpy.Delete_management(theme)
			arcpy.Delete_management(theme+".shp")
			return True
		return False
	return True

def chercheChamp(theme, ch):
	if (existeChamp(theme, ch)):
		return ch
	ch = ch[:12]
	if (existeChamp(theme, ch)):
		return ch
	for i in range(1, 9):
		if (existeChamp(theme, ch+"_"+str(i))):
			return ch+"_"+str(i)
	ch = ch[:10]
	if (existeChamp(theme, ch)):
		return ch
	for i in range(1, 9):
		if (existeChamp(theme, ch+"_"+str(i))):
			return ch+"_"+str(i)
	ch = ch[:8]
	if (existeChamp(theme, ch)):
		return ch
	for i in range(1, 9):
		if (existeChamp(theme, ch+"_"+str(i))):
			return ch+"_"+str(i)       
	return None

def supprimeEntites(theme, expression):
	print(expression)
	if (not arcpy.Exists(theme) and arcpy.Exists(theme+".shp")):
		theme = theme+".shp"
	tempLayer = "tempLayer"
	try:
				#arcpy.DeleteFeatures_management(tempLayer)
				# Execute MakeFeatureLayer
		arcpy.MakeFeatureLayer_management(theme, tempLayer)
				
				# Execute SelectLayerByAttribute to determine which features to delete
		arcpy.SelectLayerByAttribute_management(tempLayer, "NEW_SELECTION", 
												expression)
				# Execute GetCount and if some features have been selected, then 
				#  execute DeleteFeatures to remove the selected features.
		if int(arcpy.GetCount_management(tempLayer).getOutput(0)) > 0:
			arcpy.DeleteFeatures_management(tempLayer)
			print("DONE "+theme)
			
	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError(e.args[0])
		print("Erreur de suppresion des entites de "+theme+ " "+str(e))

def existe(cov):
	if (arcpy.Exists(cov)):
		return True
	if (arcpy.Exists(cov+".shp") and arcpy.Exists(cov+".dbf") and arcpy.Exists(cov+".shx")):
		return True
	return False

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


def testeCouv(couv, stop):
	if ( arcpy.Exists(couv) ):
			return decide(couv, stop)
	return True
	
def decide(couv, stop):
		print(couv + " already exists")
		
		if (stop == 0):
			exit(0)
			
		if (stop == 1):
			yn = input(couv + " existe deja! Continuer avec le dataset existant (y/n) ?")
			if (yn == 'y' or yn == "Y"):
				return False
			else:
				yn = input("Effacer le dataset existant et recalculer (y/n) ?")
				if (yn == 'y' or yn == "Y"):
					arcpy.Delete_management(couv)
					print(couv+" deleted")
					return True
				else:
					exit(0)
		
		if (stop == 2):
			arcpy.Delete_management(couv)
			print(couv+" deleted")
			return True
			
		print("Pas de recalcul: utilise la couche existante")	
		return False
		
def normalisation(inraster):
	arcpy.CalculateStatistics_management(inraster)
	MIN = arcpy.GetRasterProperties_management (inraster, "MINIMUM").getOutput(0).replace(",",".")
	MAX = arcpy.GetRasterProperties_management (inraster, "MAXIMUM").getOutput(0).replace(",",".")
	print("NORMALISATION: Min="+MIN+" max="+MAX)
	if ( float(MIN) == 0 and float(MAX) == 1):
		return inraster
	return ( (inraster - float(MIN)) / ( float(MAX) - float(MIN) ))

def normaliseChamp(cov, champ, outchamp):
	stat="stat"
	arcpy.Delete_management(stat)
	arcpy.Statistics_analysis(cov, stat, [[champ, "MIN"], [champ, "MAX"]] )
	min = 1 ; max = 0
	with arcpy.da.SearchCursor(stat, ["MIN_"+champ, "MAX_"+champ]) as curs:
		for row in curs:
			min = float(row[0])
			max = float(row[1])
	del curs
	arcpy.Delete_management(stat)
	range = float(max - min)
	ajouteChamp(cov, outchamp, "FLOAT")
	if (range > 0):
		with arcpy.da.UpdateCursor(stat, [champ, outchamp]) as curs:
			for row in curs:
				row[1] = float(row[0] - min) / range
				curs.updateRow(row)
		del curs
	else:
		arcpy.CalculateField_management(cov, outchamp, "!"+champ+"!", "PYTHON_9.3")
	
def moyenneChamp(couvOcsol, champ):
	stat="stat"
	arcpy.Delete_management(stat)
	arcpy.Statistics_analysis(couvOcsol, stat, [[champ, "MEAN"]] )
	moy = 0
	with arcpy.da.SearchCursor(stat, ["MEAN_"+champ]) as curs:
		for row in curs:
			moy = row[0]
	del curs
	arcpy.Delete_management(stat)
	return moy
	
def moyenneChampCaseValue(couvOcsol, champ, champCas, valeur):
	lesChamps = [champ, champCas]
	somme=0
	k=0
	with arcpy.da.SearchCursor(couvOcsol, lesChamps) as curs:
		for row in curs:
			if (row[1] == valeur): 
				somme = somme + row[0]
				k=k+1
	del curs
	if (k==0): return 0
	return (somme/k)
	
def statistiques(raster, nom=""):
	arcpy.CalculateStatistics_management(raster)
	try:
		MIN = arcpy.GetRasterProperties_management (raster, "MINIMUM").getOutput(0).replace(",",".")
		MAX = arcpy.GetRasterProperties_management (raster, "MAXIMUM").getOutput(0).replace(",",".")
		MOY = arcpy.GetRasterProperties_management (raster, "MEAN").getOutput(0).replace(",",".")
		ET = arcpy.GetRasterProperties_management (raster, "STD").getOutput(0).replace(",",".")
		print(nom + ": min = "+MIN + " max = " + MAX + " moy = " + MOY + " et = " + ET)
		return True
	except Exception:
		print(nom + " pas de statistiques: raster possiblement homogene (tout a 1 par exemple)") 
		return False

def saveRast(inRast, out, wsrep="", wsbdd="", keep=False):
	try:
		if (keep): a=1/0
		inRast.save()
		print(out + " saved")
	except Exception as e:
		try:
			if (len(wsrep) > 0):
				inRast.save(wsrep+"\\"+out+".tif")
				print("saved : " +wsrep+"\\"+out+".tif")
			else : a=1/0
		except Exception as ee:
			try:
				if (len(wsbdd) > 0):
					inRast.save(wsbdd+"\\"+out)
					print("saved : " +wsbdd+"\\"+out)
				else : a=1/0
			except Exception as eee:
				print("Raster "+out+" non sauve : "+str(eee))

def listeLesGrid():
	rasters = arcpy.ListRasters("*", "GRID")
	for raster in rasters:
		print(raster)
		
#def setZero(cov, champ):
#	codeBlock = """
#def zero(champ):
#	if champ is None:
#		return 0
#	else:
#		return (champ)
#	"""
#	arcpy.CalculateField_management(cov, champ, "zero(!"+champ+"!)", "PYTHON_9.3", codeBlock)
def testeChamp(cov, champ):
	if not arcpy.Exists(cov): return False
	if (not existeChamp(cov, champ)):return False
	stat = "stat"
	arcpy.Delete_management(stat)
	arcpy.Statistics_analysis(cov, stat, [[champ, "SUM"]] )
	with arcpy.da.SearchCursor(stat, ["SUM_"+champ]) as curseur:
		for row in curseur:
			if (row[0] is None):return False
			if (row[0] <= 0):return False
	del curseur
	return True
	
def frequenceValeurChamp(cov, champ, valeur):
	stat = "stat"
	arcpy.Delete_management(stat)
	arcpy.Statistics_analysis(cov, stat, [["FID", "COUNT"]], champ )
	with arcpy.da.SearchCursor(stat, [champ, "FREQUENCY"]) as curseur:
		for row in curseur:
			if (row[0] == valeur): return row[1]
	del curseur
	return 0
	
def statValeurChamp(cov, champ, valeur):
	stat = "stat"
	arcpy.Delete_management(stat)
	arcpy.Statistics_analysis(cov, stat, [["Shape_Area", "SUM"], ["Shape_Area", "MEAN"]], champ )
	liste=[0,0,0,0]
	tot=0
	with arcpy.da.SearchCursor(stat, [champ, "FREQUENCY", "SUM_Shape_Area", "MEAN_Shape_Area"]) as curseur:
		for row in curseur:
			tot=tot+row[1]
			if (row[0] == valeur): liste = [ row[1], row[2], row[3], 0]
	liste[3]=tot
	del curseur

	return liste

def statChampNum(cov, champ):
	stat = "stat"
	arcpy.Delete_management(stat)
	arcpy.Statistics_analysis(cov, stat, [[champ, "SUM"], [champ, "MEAN"], [champ, "MIN"], [champ, "MAX"]])
	liste=[0,0,0,0,0]
	tot=0
	with arcpy.da.SearchCursor(stat, ["FREQUENCY", "SUM_"+champ, "MEAN_"+champ, "MIN_"+champ, "MAX_"+champ]) as curseur:
		for row in curseur:
			liste = [ row[0], row[1], row[2], row[3], row[4] ]
			print("FREQ="+str(row[0])+ " SUM="+str(row[1])+" MEAN="+str(row[2])+" MIN="+str(row[3])+" MAX="+str(row[4]))
	del curseur

	return liste
	
def statChampTxt(cov, champ):
	rad=cov.split("/")[-1]
	chem = cov.split(rad)[0]
	stat = chem+"/stat.txt"
	arcpy.Delete_management(stat)
	arcpy.Statistics_analysis(cov, stat, [[champ, "COUNT"], [champ, "MIN"], [champ, "MAX"], [champ, "FIRST"], [champ, "LAST"]])
	liste=[0,0,0,0,0]
	tot=0
	with arcpy.da.SearchCursor(stat, ["COUNT_"+champ, "MIN_"+champ, "MAX_"+champ, "FIRST_"+champ, "LAST_"+champ]) as curseur:
		for row in curseur:
			liste = [ row[0], row[1], row[2], row[3], row[4] ]
			print("COUNT="+str(row[0])+ " MIN="+str(row[1])+" MAX="+str(row[2])+" FIRST="+str(row[3])+" LAST="+str(row[4]))
	del curseur

	return liste

def supprimeChamp(cov, nom, verb=True):
	if (arcpy.Exists(cov) and existeChamp(cov, nom)):
		arcpy.DeleteField_management(cov, nom)
		if (verb):
			print(nom+" supprime de "+cov)
	else:
		if (verb):
			print(nom+" absent de "+cov)
			
def supprimeChamps(cov, noms=[], verb=True):
	if (arcpy.Exists(cov)):
		arcpy.DeleteField_management(cov, noms)


def supprimeLesChampsSauf(cov, sauf=[], verb=True):
# le plus rapide pour les suppression multiples: Outil de gestion de donnees->Champs->Supprimer un champ.
	if (arcpy.Exists(cov)):
		noms=[]
		usauf = []
		interdits = ["FID", "SHAPE"] 
		for sf in sauf:
			usauf.append(sf.upper())

		for ch in listeLesChamps(cov):
			if ( not (ch.upper() in interdits) and not (ch.upper() in usauf) ):
				noms.append(ch)
		if (verb):
			print("Essai de supprimer "+str(noms)+" de "+cov)
		arcpy.DeleteField_management(cov, noms)
		if (verb):
			print("Done")
	else:
		print(cov+" not existe")

def ajouteChampReset(cov, nom, type):
	if ( existeChamp(cov, nom) ):
		with arcpy.da.UpdateCursor(cov, [nom]) as curseur:
			if (type != "TEXT"):
				for row in curseur:
					row[0] = 0
					curseur.updateRow(row)
			else:
				for row in curseur:
					row[0] = ""
					curseur.updateRow(row)
		del curseur
	else:
		ajouteChamp(cov, nom, type)


def ajouteChamp(cov, nom, tipe, valeur=0):
	print("Ajoute champs "+nom+" dans "+cov)
	if ( not existeChamp(cov, nom) ):
		try:
			arcpy.AddField_management(cov, nom, tipe, "","","","","NON_NULLABLE")
		except Exception:
			try:
				arcpy.AddField_management(cov, nom, tipe)
			except Exception:
				try:
					arcpy.AddField_management(cov+".dbf", nom, tipe, "","","","","NON_NULLABLE")
					tab = cov+".dbf"
				except Exception:
					print("WARNING: Impossible d'ajouter le champ "+nom+" dans "+ cov + " (theme ouvert dans ArcMap ? champ existe deja ?)")
					return False

	if (valeur != 0):
		with arcpy.da.UpdateCursor(tab, [nom]) as curseur:
			for row in curseur:
								row[0] = valeur
								curseur.updateRow(row)
		del curseur
		return True

def ajouteChampSimple(cov, nom, tipe):
	return ajouteChamp(cov, nom, tipe)

def calculeChampSurface(cov, chSurf, recalcul=False):

	if (existeChamp(cov, chSurf)):
		if (not recalcul):
			return True
		try:
			print("Calcule le champ surface "+chSurf+" dans "+cov)
			arcpy.CalculateField_management(cov, chSurf,'!shape.area!','PYTHON')
			return True
		except Exception:
			try:
				print("Calcule le champ surface "+chSurf+" dans "+cov)
				arcpy.CalculateField_management(cov+".dbf", chSurf,'!shape.area!','PYTHON')
				return True
			except Exception:
				return False

	if (ajouteChamp(cov, chSurf, "DOUBLE")):
		try:
			print("Calcule le champ surface "+chSurf+" dans "+cov)
			arcpy.CalculateField_management(cov, chSurf,'!shape.area!','PYTHON')
			return True
		except Exception:
			try:
				print("Calcule le champ surface "+chSurf+" dans "+cov)
				arcpy.CalculateField_management(cov+".dbf", chSurf,'!shape.area!','PYTHON')
				return True
			
			except Exception:
				return False

def setZero(cov, champ):
	print("Mise a zero du champ "+champ+" pour les enregistrements a valeur nulle dans "+cov+" (methode par curseur)") 
	with arcpy.da.UpdateCursor(cov, [champ]) as curseur:
		for row in curseur:
	## Update the values
			if (row[0] is None):
				row[0] = 0
			curseur.updateRow(row)
	del curseur
	
def setZeroTopo(incov):
	lesChamps = ["mean_alti", "max_alti", "min_alti", "mean_slope",	"max_slope", "min_slope", "mean_aspect", "max_aspect", "min_aspect"]
	lesprecedents = [-1, -1, -1, -1, -1, -1, -1, -1, -1]
	lespremiers = [-1, -1, -1, -1, -1, -1, -1, -1, -1]

	with arcpy.da.UpdateCursor(incov, lesChamps) as curseur:
		deja = False ; dejaok = False
		for row in curseur:
			for i in range(9):
				if (row[i] is None):
					if (lesprecedents[i] > 0):
						row[i] = lesprecedents[i]
				else:
					lesprecedents[i] = row[i]
					if (not deja): lespremiers[i] = row[i]
					dejaok=True
					
			if (dejaok): deja=True
			curseur.updateRow(row)
			
		curseur.reset()
		for row in curseur:
			for i in range(9):        
				if (row[i] is None):
					if (lesprecedents[i] > 0):
						row[i] = lesprecedents[i]
				else: break
	del curseur


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


def jointureSpatiale( targetpolycov, sourcepointcov, outpolycov, valueItem, vtopo ):

	fieldmappings = arcpy.FieldMappings()
	fieldmappings.addTable(targetpolycov)
	fieldmappings.addTable(sourcepointcov)

	gridcode = fieldmappings.findFieldMapIndex(valueItem)
	fieldmapmean = fieldmappings.getFieldMap(gridcode)

	outfield = fieldmapmean.outputField
	outfield.name = "mean_"+vtopo
	outfield.aliasName = "mean_"+vtopo
	fieldmapmean.outputField = outfield
	fieldmapmean.mergeRule = "mean"
	
	fieldmappings.addFieldMap(fieldmapmean)
	
	fieldmapmax = fieldmappings.getFieldMap(gridcode)
	outfield = fieldmapmax.outputField
	outfield.name = "max_"+vtopo
	outfield.aliasName = "max_"+vtopo
	fieldmapmax.outputField = outfield
	fieldmapmax.mergeRule = "max"

	fieldmappings.addFieldMap(fieldmapmax)

	fieldmapmin = fieldmappings.getFieldMap(gridcode)
	outfield = fieldmapmin.outputField
	outfield.name = "min_"+vtopo
	outfield.aliasName = "min_"+vtopo
	fieldmapmin.outputField = outfield
	fieldmapmin.mergeRule = "min"

	fieldmappings.addFieldMap(fieldmapmin)

	x = fieldmappings.findFieldMapIndex("pointid")
	fieldmappings.removeFieldMap(x)
	y = fieldmappings.findFieldMapIndex(valueItem)
	fieldmappings.removeFieldMap(y)

	arcpy.SpatialJoin_analysis( targetpolycov, sourcepointcov,  outpolycov,  "#", "#", fieldmappings)

def fieldMapeur(fieldmap, operation, nomDeChamp):
	outfield = fieldmap.outputField
	outfield.name = nomDeChamp
	outfield.aliasName = nomDeChamp
	fieldmap.outputField = outfield
	fieldmap.mergeRule = operation
	return fieldmap

def jointeurAttributaire( covSource, itemCleSource, valueItemSource, covCible, itemCleCible, valueItemCible, type_item):
	deb=time()
	ajouteChamp(covCible, itemCleCible, type_item)
	dico = dict ( [(key, val) for key, val in arcpy.da.SearchCursor(covSource, [itemCleSource, valueItemSource] ) ] )
	with arcpy.da.UpdateCursor(covCible, [itemCleCible, valueItemCible]) as curseur:
		for row in curseur:
			row[1] = dico.get(row[0])
			curseur.updateRow(row)
	del curseur
	
	timeur(deb)
	
def jointeur( targetpolycov, variab, sourcepointcov, valueItem, operation ):
	#exemple:   ocsol	     alti   pointAlti       grid_code  MAX,MEAN,SUM,STD,ALL
	tabstat = "statStd"
	itemcle0 = "FID_"+targetpolycov.split("\\")[-1]
	itemcle = itemcle0
	lc = arcpy.ListFields(sourcepointcov)
	ok1=False ;
	for i in lc:
		if (i.name == itemcle):
			ok1=True
			break
	if ( not ok1):
		itemcle = itemcle0[:10]
		for i in lc:
			if (i.name == itemcle):
				ok1=True
				break
			
	if (not ok1):
		itemcle = itemcle0
		print(itemcle0+" not found in "+sourcepointcov+". Plantage imminent !")
	
	deb=time()	
	arcpy.Delete_management(tabstat)
	print("STATISTICS")
	arcpy.Statistics_analysis(sourcepointcov, tabstat, [[valueItem, operation]], itemcle )
	#on met la table des stats dans un dictionnaire :
	dico = dict ( [(key, val) for key, val in arcpy.da.SearchCursor(tabstat, [itemcle, operation+"_"+valueItem] ) ] )
	
	print("Joining from stat table "+tabstat+" item "+operation+"_"+variab+" to " + targetpolycov.split("\\")[-1])
	arcpy.AddField_management(targetpolycov, operation+"_"+variab, "DOUBLE", "", "", "", "", "NULLABLE", "")	
	with arcpy.da.UpdateCursor(targetpolycov, ["OBJECTID", operation+"_"+variab]) as curseur:
		for row in curseur:
			row[1] = dico.get(row[0])
			curseur.updateRow(row)
	del curseur
	arcpy.Delete_management(tabstat)
	timeur(deb)

def intersecteurJointeur(targetpolycov, variab, sourcepointcov, valueItem, operation):
	inFeatures = [sourcepointcov, targetpolycov]
	crosspointcov = sourcepointcov.split("\\")[-1][0:5]+"X"+targetpolycov.split("\\")[-1][0:5]
	print("Intersecing "+ sourcepointcov.split("\\")[-1] +" with " + targetpolycov.split("\\")[-1] + " to create "+crosspointcov) 
	deb=time()
	arcpy.Intersect_analysis (inFeatures, crosspointcov, "", ct, "point")
	timeur(deb)
	jointeur( targetpolycov, variab, crosspointcov, valueItem, operation)
	
def intersecteurRasterCov(targetpolycov, variab, sourceraster, operation, general):
	general = int(general)
	rast0 = arcpy.sa.Raster(sourceraster)
	rast = rast0
	if (general >= 2):
		arcpy.CheckOutExtension("Spatial")
		print("Aggregating raster "+ sourceraster.split("\\")[-1] +" with factor "+str(general))
		deb=time()
		rast1 = arcpy.sa.Aggregate (rast0, general, "MEAN", True, True)
		rast = arcpy.sa.Int(rast1)
		timeur(deb)
	outpoints = sourceraster+"pts"
	if (not arcpy.Exists(outpoints)):
		print("Converting raster "+ sourceraster.split("\\")[-1] +" to points cover "+outpoints.split("\\")[-1])
		deb = time()
		arcpy.RasterToPoint_conversion(rast, outpoints, "VALUE")
		timeur(deb)
	
	valueItem = "grid_code"
	intersecteurJointeur(targetpolycov, variab, outpoints, valueItem, operation)

def testeTopo(cov):
	for champ in lesChampsTopo:
		if (not existeChamp(cov, champ)):
			return False
	total=0; totalNone=0
	with arcpy.da.SearchCursor(cov, lesChampsTopo) as cur:
		for row in cur:
			total=total+1
			for i in range(len(lesChampsTopo)-1):
				if ( row[i] is None): totalNone = totalNone + 1
	del cur
	total = total * len(lesChampsTopo)
	if ( totalNone > (total * 0.1) ):
		print("Plus de 10% de none dans les item topographiques ")
		return False
	return True

def listeLesChamps(cov):
	ls=[]
	for f in arcpy.ListFields(cov): 
		ls.append(f.name)
		print(f.name)
	return ls

def existeChamp(cov, champ):
	if (not arcpy.Exists(cov) and arcpy.Exists(cov+".dbf")):
		cov = cov+".dbf"
	if (not arcpy.Exists(cov)):
		return False
	lc = arcpy.ListFields(cov)
	if (len(lc)<1):
		lc = arcpy.ListFields(cov+".dbf")
	for f in lc:
		if f.name.upper() == champ.upper() : return True
	return False

def nettoyeTousChamp(cov, exeptions = ["OBJECTID"], scenar="scenar"):
	nom = extraitNom(cov)
	lc = arcpy.ListFields(cov)
	lf = []
	for f in lc:
		if (f.type != 'OID' and f.type != 'Geometry'):
			ok = True
			for e in exeptions:
				if e.upper().startswith(f.name.upper()[:8]) : #on compare sur les 8 premiers caracteres (syntaxe: le 8 est exclu!), 
					ok=False								  #a cause de shapefile qui sont limites a 10 car
					break
			if (ok):
				lf.append(f)
				try:
					arcpy.DeleteField_management(cov, f.name)
					print(scenar+": "+"Delete in " + nom +" field "+f.name)
				except Exception:
					print(arcpy.GetMessages())
					print(scenar+": "+"Failed to Delete in " + nom +" field "+f.name)
		#arcpy.DeleteField_management(cov, lf)

def compteRecNonVide(cov, champ):
	ga=0
	if ( existeChamp(cov, champ) ):
		clause = champ + " > 0"
		with arcpy.da.SearchCursor(cov, champ, where_clause=clause) as cur:
			for c in cur: ga = ga+1
		del cur
	return ga
def compteRec(cov):
	ga=0
	if (arcpy.Exists(cov)):
		with arcpy.da.SearchCursor(cov, ["OBJECTID"]) as cur:
			for c in cur: ga = ga+1
		del cur
	return ga

def compteRec(cov, clause):
	ga=0
	if (arcpy.Exists(cov)):
		with arcpy.da.SearchCursor(cov, ["OBJECTID"], clause) as cur:
			for c in cur: ga = ga+1
		del cur
	return ga