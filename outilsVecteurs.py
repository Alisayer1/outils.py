import sys, csv
from os import rename, remove, rmdir
from shutil import copy, rmtree
from osgeo import ogr
from os.path import isfile, isdir
import numpy as np
import random
from outilsGene import extension, zippage
verb=False

def listeChamps(fichier):
	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(fichier, 0)
	inLayer = inDataSource.GetLayer()
	defn=inLayer.GetLayerDefn()
	k=0
	attribs=[]
	for i in defn.GetFieldCount():
		attribs.append(defn.GetFieldDefn(i).GetNameRef())
		print (defn.GetFieldDefn(i).GetNameRef())
	inDataSource.Destroy()
	return attribs

def estChamp(fichier, champ):
	if not existeShapeFile(fichier):
		print("Erreur : "+fichier+" absent ")
		return False
		
	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(fichier, 0)
	inLayer = inDataSource.GetLayer()
	defn = inLayer.GetLayerDefn()
	for i in range(0, defn.GetFieldCount()):
		ch=defn.GetFieldDefn(i).GetNameRef().strip().upper()
		if ch == champ.upper():
			inDataSource.Destroy()
			return True
	return False

def existeShape(fichier):
	if (existeShapeFile(fichier)[0]):
		return True
	if (existeShapeFile(fichier+".shp")[0]):
		return True
	return False

def existeShapeFile(fichier):

	fichier=fichier.replace("\\", "/")
	fich = fichier.split("/")[-1]
	chem = fichier.split(fich)[0]
	rad=fich
	ext=""
	if (fich.find(".")>0 and fich.find(".")<(len(fich)-1)):
		rad = fich.split(".")[0]
		ext = fich.split(".")[1].upper()
	else:
		if (fich.find(".")>=(len(fich)-1)):
			print("Bad shapefile name "+fichier)
			return False, None
		else:
			fichier+=".shp"
			ext="SHP"
			if not isfile(fichier):
				print("Shapefile "+fichier+" existe pas")
				return False, None
			else:
				print("Shapefile "+fichier+" existe mais l'extension .shp doit etre precisee")
				return False, None

	if (ext == "SHP" or ext == "SHX" or ext == "DBF"):
		ok=True
		if not isfile(chem+rad+".shp"):
			if (verb):
				print("File "+chem+rad+".shp does not exist")
			ok=False, None
		if not isfile(chem+rad+".dbf"):
			if (verb):
				print("File "+chem+rad+".dbf does not exist")
			ok=False, None
		if not isfile(chem+rad+".shx"):
			if (verb):
				print("File "+chem+rad+".shx does not exist")
			return False, None
		if not ok:
			return False, None
	else:
		print("BAD shapefile extension "+ext)
		return False, None

	return True, fichier

def chercheShapeFile(fichier):
	if ( existeShapeFile(fichier)[0] ):
		return fichier
	else:
		if (existeShapeFile(fichier+".shp")[0]):
			return fichier+".shp"
	print(fichier+ " is not a shapefile")
	exit(0)

def renameFileSet(fichier, out="OLD", lesExtensions = ["shp", "shx", "dbf", "sbn", "sbx", "cpg", "prj"]):
		nfi = fichier.split("/")[-1]
		chem = fichier.split(nfi)[0] #avec le dernier slash
		ext = fichier.split(".")[-1]
		ext = "."+ext
		rad=fichier.split(ext)[0]
		rado=""
		if (out=="OLD"):
			rado=rad+"OLD"
		else:
			exto = out.split(".")[-1]
			rado = out.split("."+exto)[0]
			if ( len(exto)>0 and len(lesExtensions)>0 ) :
				lesExtMajusc = []
				for e in lesExtensions:
					lesExtMajusc.append(e.upper())
				if not (exto.upper() in lesExtMajusc):
					print ("Bad out file extension "+out+". Only shapefile can be created")
					return False
		if (out.find("/")<0):
			rado=chem+rado
		k=1
		radi=rado
		ok=False
		while (not ok):
			ok=True
			for lext in lesExtensions:
				if isfile(rado+"."+lext):
					rado=radi+str(k)
					k+=1
					ok=False
					break

		for lext in lesExtensions:
			if ( isfile(rad+"."+lext)):
				rename(rad+"."+lext, rado+"."+lext)

		for lext in lesExtensions:
			if not isfile(rado+"."+lext):
				print("WARNING: Missing "+rado+"."+lext)
				
		if (isfile(rado+ext)):
			return True, rado
		else:
			print(fichier+" non renomme")
			return False

def renameShapeFile( fichier, out="OLD", lesExtensions = ["shp", "shx", "dbf", "sbn", "sbx", "cpg", "prj"] ):
	if (existeShapeFile(fichier)[0]):
		nfi = fichier.split("/")[-1]
		chem = fichier.split(nfi)[0] #avec le dernier slash
		ext = fichier.split(".")[-1]
		ext = "."+ext
		rad=fichier.split(ext)[0]
		rado=""
		if (out=="OLD"):
			rado=rad+"OLD"
		else:
			exto = out.split(".")[-1]
			rado = out.split("."+exto)[0]
			if (len(exto)>0):
				if (exto.upper() != "SHP"):
					print ("Bad out file extension "+out+". Only shapefile can be created")
					return False
		if (out.find("/")<0):
			rado=chem+rado
		k=1
		radi=rado
		ok=False
		while (not ok):
			ok=True
			for lext in lesExtensions:
				if isfile(rado+"."+lext):
					rado=radi+str(k)
					k+=1
					ok=False
					break

		for lext in lesExtensions:
			if ( isfile(rad+"."+lext)):
				rename(rad+"."+lext, rado+"."+lext)

		if (existeShapeFile(rado+".shp")[0]):
			return True, rado
	else:
		print(fichier+" absent")
		return False

def supprimeShape(fichier):
	return supprimeShapeFile(extension(fichier, '.shp'))
	
def supprimeShapeFile( fichier, lesExtensions = ["shp", "shx", "dbf", "sbn", "sbx", "cpg", "prj"] ):
	if (existeShapeFile(fichier)[0]):
		nfi = fichier.split("/")[-1]
		chem = fichier.split(nfi)[0] #avec le dernier slash
		ext = fichier.split(".")[-1]
		ext = "."+ext
		rad=fichier.split(ext)[0]

		for lext in lesExtensions:
			if ( isfile(rad+"."+lext)):
				remove(rad+"."+lext)
		if (existeShapeFile(rad+".shp")[0]):
			return False
		return True

	else:
		print(fichier+" absent")
		return False

def copyShapeFile(fichier, out="./"):
	return copyFilesSet(fichier, out)

def copyFileSet(fichier, out="./", lesExtensions=["shp", "shx", "dbf", "sbn", "sbx", "cpg", "prj"]):

	if (existeShapeFile(fichier)[0]):
		nfi = fichier.split("/")[-1]
		chem = fichier.split(nfi)[0] #avec le dernier slash
		ext = fichier.split(".")[-1]
		ext = "."+ext
		rad=fichier.split(ext)[0]
		radnfi=nfi.split(ext)[0]
		lesExtensions = ["shp", "shx", "dbf", "sbn", "sbx", "cpg", "prj"]
		
		if isdir(out) :
			rado = out
			if not rado.endswith("/"):
				rado+="/"
				
			for lext in lesExtensions:
				if (isfile(rado+radnfi+"."+lext)):
					print(rado+radnfi+"."+lext+" existe deja")
					exit(0)

			for lext in lesExtensions:
				if ( isfile(rad+"."+lext)):
					print("copy "+rad+"."+lext+" dans "+rado)
					copy(rad+"."+lext, rado)
		else:
			rado=out
			if (out.find("/")<0):
				rado="./"+out

			nfo=out.split("/")[-1].strip()
			exto = nfo.split(".")[-1].strip()
			exto = "."+exto
			rado = out.split(exto)[0]
			chemo = out.split(nfo)[0]
			if (len(exto)>0):
				if (exto.upper() != ".SHP"):
					print ("Bad out file extension "+out+". Only shapefile can be copied")
					return False

			k=1
			radi=rado
			
			for lext in lesExtensions:
				if (isfile(rado+"."+lext)):
					print(rado+"."+lext+" existe deja")
					exit(0)
			for lext in lesExtensions:
				if ( isfile(rad+"."+lext) ):
					print("copy "+rad+"."+lext+" dans "+rado+"."+lext)
					copy(rad+"."+lext, rado+"."+lext)

			if (existeShapeFile(rado+".shp")[0]):
				return True, rado
	else:
		print(fichier+" absent")
		return False
		
def bufferise(fichier, outth, dist=0, itemLargeur="", attributs=[]):
	if not isfile(fichier):
		print(fichier +" existe pas - STOP")
		exit(0)
	if isfile(outth):
		print(outth +" existe deja - STOP")
		exit(0)
		
	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(fichier, 0)
	inLayer = inDataSource.GetLayer()
	defn = inLayer.GetLayerDefn()

	outDataSource = driver.CreateDataSource(outth)
	outLayer = outDataSource.CreateLayer('FINAL', geom_type=ogr.wkbMultiPolygon)

	lstposatt = []
	for k in range(len(attributs)):
		lstposatt.append(-1)

	I=-1

	for i in range(0, defn.GetFieldCount()):
		if len(itemLargeur)>0 :
			if (defn.GetFieldDefn(i).GetNameRef().upper() == itemLargeur.upper() ):
				if (dist <= 0):
					I=i
				outLayer.CreateField(defn.GetFieldDefn(i))
		if len(attributs)>0 :
			for j in range(len(attributs)):
				if (defn.GetFieldDefn(i).GetNameRef().upper() == attributs[j].upper() ):
					lstposatt[j] = i
					print(attributs[j]+" trouve en position "+str(i))
					outLayer.CreateField(defn.GetFieldDefn(i))

	defno = outLayer.GetLayerDefn()

	if (I < 0):
		
		print("Item de largeur "+itemLargeur+" non trouve. Distance par defaut = "+str(dist))
		itemLargeur="LARGEUR"
		largeur0=itemLargeur
		z=0
		ok=False
		while not ok: #tout ca juste pour creer un item LARGEUR pour stoker dans les attributs du buffer
			ok=True
			for i in range(0, defno.GetFieldCount()):
				if defn.GetFieldDefn(i).GetNameRef().upper() == itemLargeur:
					ok=False
					itemLargeur=largeur0+str(z)
					z+=1
		ch = ogr.FieldDefn(itemLargeur, ogr.OFTReal)
		outLayer.CreateField(ch)
		defno = outLayer.GetLayerDefn()
		
		for f in inLayer:
			ingeom = f.GetGeometryRef()
			geomBuffer = ingeom.Buffer(dist) #tout ca pour ca
			outFeature = ogr.Feature(defno)
			outFeature.SetGeometry(geomBuffer)
			outFeature.SetField(itemLargeur, dist)
			for i in range(len(attributs)):
				if ( lstposatt[i]>=0 ) :
					outFeature.SetField(attributs[i], f.GetField(lstposatt[i]))
			outLayer.CreateFeature(outFeature)
			outFeature = None
	else:

		print("Item de largeur "+itemLargeur+" trouve en position "+str(I))
		for f in inLayer:
			d=(f.GetField(I) / 2)
			ingeom = f.GetGeometryRef()
			geomBuffer = ingeom.Buffer(d)
			outFeature = ogr.Feature(defno)
			outFeature.SetGeometry(geomBuffer)
			outFeature.SetField(itemLargeur, d)
			for i in range(len(attributs)):
				if ( lstposatt[i]>=0 ) :
					outFeature.SetField(attributs[i], f.GetField(lstposatt[i]))
			outLayer.CreateFeature(outFeature)
			outFeature = None

	inDataSource.Destroy()
	outDataSource.Destroy()

def clippe(inth, clipth, outth):
## Input

	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(inth, 0)
	inLayer = inDataSource.GetLayer()

	print(inLayer.GetFeatureCount())
	## Clip
	inClipSource = driver.Open(clipth, 0)
	inClipLayer = inClipSource.GetLayer()
	print(inClipLayer.GetFeatureCount())

	## Clipped Shapefile... Maybe??? 
	outDataSource = driver.CreateDataSource(outth)
	outLayer = outDataSource.CreateLayer('FINAL', geom_type=ogr.wkbMultiPolygon)

	ogr.Layer.Clip(inLayer, inClipLayer, outLayer)
	print(outLayer.GetFeatureCount())
	inDataSource.Destroy()
	inClipSource.Destroy()
	outDataSource.Destroy()


def renGrille(inth, xmin, ymin, xmax, ymax, pas, radoutth):

	x = xmin
	while x <= xmax:
		y = ymin
		while y <= ymax:
			outth = radoutth+"_"+str(x)+"_"+str(y)+".zip"
			rename("bat"+str(x)+"_"+str(y)+".zip", outth)
			print(outth)
			y+=1
		x+=1
		
def zippeGrille(inth, xmin, ymin, xmax, ymax, pas, radoutth):
	inth=extensionShp(inth)
	ext = inth.split('.')[-1]
	prj = inth.split('.'+ext)[0] + '.prj'
	if (not isfile(prj)):
		print("prj file "+prj+" missing")
		exit(0)
	x = xmin
	while x <= xmax:
		y = ymin
		while y <= ymax:
			outth = radoutth+str(x)+"_"+str(y)
			copy(prj, outth+'.prj')
			zippage(outth)
			if (isfile(extension(outth, '.zip'))):
				print(outth+" ok")
			y+=1
		x+=1

def clippeGrille(inth, radoutth, pas=1000, xmin=0, ymin=0, xmax=1, ymax=1):
	inth=extensionShp(inth)
	ext = inth.split('.')[-1]
	prj = inth.split('.'+ext)[0] + '.prj'
	if (not isfile(prj)):
		print(prj+" manquant")
		exit(0)

	vide = extension(inth, ".vide")
	fvide = open(vide, 'a')

	extent = enveloppe(inth)
	xmin = int(extent[0] / pas)
	xmax = int(extent[1] / pas)
	ymin = int(extent[2] / pas)
	ymax = int(extent[3] / pas)
	print("Bounds="+str(xmin)+"  "+str(ymin)+"  "+str(xmax)+"  "+str(ymax))
	x=xmin
	while x <= xmax:
		y = ymin
		while y <= ymax:
			outth = radoutth+"_"+str(x)+"_"+str(y)
			if (not existeShape(extensionShp(outth))):
				if ( open(vide, 'r').read().find(extensionShp(outth)) < 0 ):
					if ( clippeCoordinate(inth, (x*pas), (y*pas), (x+1)*pas, (y+1)*pas, outth) < 1 ):
						supprimeShapeFile(extensionShp(outth))
						fvide.write(extensionShp(outth)+'\n')
						print(outth+" est vide -> Supprime")
				else:
					print(outth+" est vide : pas de recalcul")
				#zippage
				if ( not isfile(extension(outth, ".zip")) and existeShape(extensionShp(outth)) ):
					copy(prj, outth+'.prj')
					zippage(outth)
					if (isfile(extension(outth, '.zip'))):
						supprimeShape(outth)
						print(extension(outth, '.zip')+" ok")
			else:
				print(outth+" existe deja - not recaclulated")
			y+=1
		x+=1
	fvide.close()

def enveloppe(inth):
	inth = chercheShapeFile(inth) #chercheShapeFile arrete tout (exit(0)) s'il ne trouve pas 
	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(inth, 0)
	inLayer = inDataSource.GetLayer()
	extent=inLayer.GetExtent()
	inDataSource.Destroy()
	return extent

def clippeCoordinate(inth, xmin, ymin, xmax, ymax, outth):
## renvoi de le nombre de features dans la layer clippee

	if ( existeShape( extensionShp(outth) ) ):
		if yesno(extensionShp(outth)+' existe : effacer (y/n) ?'):
			supprimeShapeFile(extensionShp(outth))
		else:
			return
	tmpclip="tmpclip"
	scarre="carre"
	inth = chercheShapeFile(inth) #chercheShapeFile arrete tout (exit(0)) s'il ne trouve pas 
	print("found "+inth)
	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(inth, 0)
	inLayer = inDataSource.GetLayer()
	print(str(inLayer.GetFeatureCount())+" features in "+inth)
	## Clip

	carre = ogr.Geometry(ogr.wkbLinearRing)
	carre.AddPoint(xmin, ymax)
	carre.AddPoint(xmax, ymax)
	carre.AddPoint(xmax, ymin)
	carre.AddPoint(xmin, ymin)
	carre.AddPoint(xmin, ymax)
	poly = ogr.Geometry(ogr.wkbPolygon)
	poly.AddGeometry(carre)
	featureDefn = inLayer.GetLayerDefn()
	feature = ogr.Feature(featureDefn)
	feature.SetGeometry(poly)
	print("Bounds: "+str(feature.GetGeometryRef().GetEnvelope()))

	if existeShapeFile(tmpclip+"/"+scarre+".shp")[0]:
		print(tmpclip+"/"+scarre + " existe deja: remove)")
		supprimeShapeFile(tmpclip+"/"+scarre+".shp")
		rmdir(tmpclip)

	clipDataSource = driver.CreateDataSource(tmpclip) #ici il cre un repertoire tmpclip

	clipLayer = clipDataSource.CreateLayer(scarre, geom_type=ogr.wkbMultiPolygon) #ici il cree un shape "CARRE.shp" (ne pas preciser l'extension)
	clipLayer.CreateFeature(feature)
	print(str(clipLayer.GetFeatureCount())+" features in "+"tmpclip")
	## Clipped Shapefile... Maybe??? 
	outDataSource = driver.CreateDataSource(outth+".shp") ##ici il cree un shape, si outth est un shape (
	outLayer = outDataSource.CreateLayer('FINAL', geom_type=ogr.wkbMultiPolygon) #FINAL est un nom de layer, à l'interieur du shp a priori

	print("Clipping... "+inth+" with "+scarre+".shp  to create "+outth+'.shp')
	ogr.Layer.Clip(inLayer, clipLayer, outLayer)
	print("done")

	inDataSource.Destroy()
	clipDataSource.Destroy()
	if existeShapeFile(tmpclip+"/"+scarre+".shp"):
		supprimeShapeFile(tmpclip+"/"+scarre+".shp")
		rmdir(tmpclip)

	nbre=outLayer.GetFeatureCount()
	print(str(nbre)+" created in "+outth)
	outDataSource.Destroy()
	
	return nbre


def extensionShp(outth):
	return extension(outth, ".shp")

def creeOutputShapefileGeom(outth, geometrie="POLY", itempoids="poids"):
	if isfile(outth):
		print(outth +" existe deja - STOP")
		exit(0)

	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	outDataSource = driver.CreateDataSource(outth)
	#ATTENTION: ON NE PEUT L'INSTANCIER outLayer QU'UNE SEULE FOIS, IL FAUT QUE LES CASES SOIENT EXCLUSIFS
	if (geometrie.upper() == "POLY"):
		outLayer = outDataSource.CreateLayer('FINAL', geom_type=ogr.wkbMultiPolygon)
	if (geometrie.upper() == "LINE"):
		outLayer = outDataSource.CreateLayer('FINAL', geom_type=ogr.wkbLineString)
	if (geometrie.upper() == "POINT"):
		outLayer = outDataSource.CreateLayer('FINAL', geom_type=ogr.wkbPoint)

	ch1 = ogr.FieldDefn("id", ogr.OFTInteger)
	outLayer.CreateField(ch1)
	ch2 = ogr.FieldDefn(itempoids, ogr.OFTReal)
	outLayer.CreateField(ch2)

	defno = outLayer.GetLayerDefn()
	print("Attributs de out = "+outth+" :")
	for i in range(0, defno.GetFieldCount()):
		print(defno.GetFieldDefn(i).GetNameRef())
		
	return outLayer, driver, outDataSource
	
def creeOutputShapefile(outth, geometrie="", inth="", champsGardes=[], champsSauf=[]):
	inth = chercheShapeFile(inth)
	if isfile(outth):
		print(outth +" existe deja - STOP")
		exit(0)
	for i in range(len(champsGardes)):
		champsGardes[i]=champsGardes[i].upper()
	for i in range(len(champsSauf)):
		champsSauf[i]=champsSauf[i].upper()
		
	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	outDataSource = driver.CreateDataSource(outth)
	#ATTENTION: ON NE PEUT L'INSTANCIER outLayer QU'UNE SEULE FOIS, IL FAUT QUE LES CASES SOIENT EXCLUSIFS
	outLayer = None
	if (geometrie.upper() == "POLY"):
		outLayer = outDataSource.CreateLayer('FINAL', geom_type=ogr.wkbMultiPolygon)
	if (geometrie.upper() == "LINE"):
		outLayer = outDataSource.CreateLayer('FINAL', geom_type=ogr.wkbLineString)
	if (geometrie.upper() == "POINT"):
		outLayer = outDataSource.CreateLayer('FINAL', geom_type=ogr.wkbPoint)

	if (len(inth)>0):

		print("modele="+inth)
		inDS = driver.Open(inth, 0)
		inLayer = inDS.GetLayer()
		intipegeom = inLayer.GetGeomType()
		if (outLayer == None):
			outLayer = outDataSource.CreateLayer('FINAL', geom_type=intipegeom)

		defn = inLayer.GetLayerDefn()
		for i in range(0, defn.GetFieldCount()):
			champ=defn.GetFieldDefn(i).GetNameRef()
			tipe=defn.GetFieldDefn(i).GetType()

			ok=True
			if (len(champsSauf)>0):
				ok = not (champ.upper() in champsSauf)
			if (len(champsGardes)>0):
				ok = (champ.upper() in champsGardes)
			if ok:
				ch = ogr.FieldDefn(champ, tipe)
				outLayer.CreateField(ch)

		inDS.Destroy()
	defno = outLayer.GetLayerDefn()
	print("Attributs de out = "+outth+" :")
	for i in range(0, defno.GetFieldCount()):
		print(defno.GetFieldDefn(i).GetNameRef())
		
	return outLayer, driver, outDataSource

def fusionne(liste, outth, geometrie="POLY", champsGardes=[], champsSauf=[] ):
## Input
	if (len(liste)<=0):
		print("Erreur : liste a fusionner vide")
		exit(0)
		
	outLayer, driver, outDataSource = creeOutputShapefile(outth, geometrie, liste[0], champsGardes, champsSauf) #pas de champSauf, donc conserve tous les attributs de la covin
	defno = outLayer.GetLayerDefn()
	n=0
	print("Attention : ECHEC A PARTIR d'un trop grand nombre de batis (>900000 sur le Var par exemple, echec dans lecriture du SHX)")

	for th in liste:
		th=chercheShapeFile(th)
		if not isfile(th):
			print(th+" not found : STOP")
			exit(0)
		inDataSource = driver.Open(th, 0)
		inLayer = inDataSource.GetLayer()

		print(th.split('/')[-1]+" : "+ str(inLayer.GetFeatureCount()) + " entites")
		defn=inLayer.GetLayerDefn()
		
		if (len(champsGardes)<=0 and len(champsSauf)<=0 ):
			for f in inLayer:
				out_feat = ogr.Feature(defno)
				for i in range(0, defn.GetFieldCount()):
					out_feat.SetField(defn.GetFieldDefn(i).GetNameRef(),f.GetField(i))
				out_feat.SetGeometry(f.GetGeometryRef().Clone())
				outLayer.CreateFeature(out_feat)
				n+=1
				out_feat=None

		if (len(champsGardes)<=0 and len(champsSauf)>0 ):
				for f in inLayer:
					out_feat = ogr.Feature(defno)
					for i in range(0, defn.GetFieldCount()):
						if not (defn.GetFieldDefn(i).GetNameRef().upper() in champsSauf):
							out_feat.SetField(defn.GetFieldDefn(i).GetNameRef(),f.GetField(i))
					out_feat.SetGeometry(f.GetGeometryRef().Clone())
					outLayer.CreateFeature(out_feat)
					n+=1
					out_feat=None
				
		if (len(champsGardes)>0): #champs sauf est inperant dans ce cas, on ne garde que les champs gardes
				for f in inLayer:
					out_feat = ogr.Feature(defno)
					for i in range(0, defn.GetFieldCount()):
						if (defn.GetFieldDefn(i).GetNameRef().upper() in champsGardes):
							out_feat.SetField(defn.GetFieldDefn(i).GetNameRef(),f.GetField(i))
					out_feat.SetGeometry(f.GetGeometryRef().Clone())
					outLayer.CreateFeature(out_feat)
					n+=1
					out_feat=None

		inDataSource.Destroy()
		
	print(outth.split('/')[-1]+" : "+ str(outLayer.GetFeatureCount()) + " entites ; vs calcule = "+str(n))
	outDataSource.Destroy()
	
	if (compteEntites(outth)<=0):
		print("Echec de la fusion (zero entites en sortie)")
		
def fusionneGeom(liste, outth, geometrie="POLY", itempoids = "poids", valeurpoids=1):
## Input
	if (len(liste)<=0):
		print("Erreur : liste a fusionner vide")
		exit(0)
		
	outLayer, driver, outDataSource = creeOutputShapefileGeom(outth, geometrie, itempoids)

	n=0
	print("Attention : ECHEC A PARTIR d'un trop grand nombre de batis (>900000 sur le Var par exemple, echec dans lecriture du SHX)")
	defn = outLayer.GetLayerDefn()
	for th in liste:
		if ( not existeShapeFile(th)[0] ):
			print(th+" not found : STOP")
			exit(0)
		else:
			th = existeShapeFile(th)[1]

		inDataSource = driver.Open(th, 0)
		inLayer = inDataSource.GetLayer()

		print(th.split('/')[-1]+" : "+ str(inLayer.GetFeatureCount()) + " entites")
		for f in inLayer:
			out_feat = ogr.Feature(defn)
			out_feat.SetGeometry(f.GetGeometryRef().Clone())
			out_feat.SetField("id", n)
			out_feat.SetField(itempoids, valeurpoids)

			outLayer.CreateFeature(out_feat)
			n+=1
			out_feat=None
		inDataSource.Destroy()
		
	print(outth.split('/')[-1]+" : "+ str(outLayer.GetFeatureCount()) + " entites ; vs calcule = "+str(n))
	outDataSource.Destroy()

	if (compteEntites(outth)<=0):
		print("Echec de la fusion (zero entites en sortie)")

def supprimeChampsSauf(inth, champsSauf, outth, geometrie="POLY"):
## Input
	if isfile(outth):
		print(outth +" existe deja - STOP")
		exit(0)
	if (len(champsSauf)<=0):
		print("La liste des champs est vide : STOP")
		exit(0)

	outLayer, driver, outDataSource = creeOutputShapefile(outth, geometrie, inth, [], champsSauf)
	n=0
	
	inDataSource = driver.Open(inth, 0)
	inLayer = inDataSource.GetLayer()
	
	n+=inLayer.GetFeatureCount()
	print(inth.split('/')[-1]+" : "+ str(inLayer.GetFeatureCount()) + " entites")

	defn=inLayer.GetLayerDefn()
	outdefn = outLayer.GetLayerDefn()
	
	for f in inLayer:
		out_feat = ogr.Feature(outdefn)

		for i in range(0, defn.GetFieldCount()):
			if (defn.GetFieldDefn(i).GetNameRef() in champsSauf):
				for j in range(0, outdefn.GetFieldCount()):
					if (defn.GetFieldDefn(i).GetNameRef() == outdefn.GetFieldDefn(j).GetNameRef()):
						print(outdefn.GetFieldDefn(j).GetNameRef()+" = "+str(f.GetField(i)))
						out_feat.SetField(outdefn.GetFieldDefn(j).GetNameRef(),f.GetField(i))
						break
				break

		out_feat.SetGeometry(f.GetGeometryRef().Clone())
		
		outLayer.CreateFeature(out_feat)
		out_feat=None

	inDataSource.Destroy()

	print(outth.split('/')[-1]+" : "+ str(outLayer.GetFeatureCount()) + " entites ; vs calcule = "+str(n))
	outDataSource.Destroy()

def nettoyeShapeFile(inth, outth, tipe="LINESTRING"):
	if (tipe=="LINESTRING"):
		geometrie="LINE"
	#ne conserve que les linestring dans ce cas
	if not isfile(inth):
		print("Erreur : "+inth+" absent ")
		exit(0)
	if isfile(outth):
		print(outth +" existe deja - STOP")
		exit(0)
	outLayer, driver, outDataSource = creeOutputShapefile(outth, geometrie, inth, [], [])
	n=0
	
	inDataSource = driver.Open(inth, 0)
	inLayer = inDataSource.GetLayer()
	
	n+=inLayer.GetFeatureCount()
	print(inth.split('/')[-1]+" : "+ str(inLayer.GetFeatureCount()) + " entites")

	defn=inLayer.GetLayerDefn()
	for f in inLayer:
		geometry = f.GetGeometryRef()
		if ( str(geometry) == tipe ):
			out_feat = ogr.Feature(defn)

			for i in range(0, defn.GetFieldCount()):
				if (defn.GetFieldDefn(i).GetNameRef() in champs):
					out_feat.SetField(defn.GetFieldDefn(i).GetNameRef(),f.GetField(i))

			out_feat.SetGeometry(f.GetGeometryRef().Clone())
			outLayer.CreateFeature(out_feat)
			out_feat=None
			n+=1
	inDataSource.Destroy()

	print(outth.split('/')[-1]+" : "+ str(outLayer.GetFeatureCount()) + " entites ; vs calcule = "+str(n))
	outDataSource.Destroy()

def testeShapeFile(inth):
	if not existeShapeFile(inth)[0]:
		print("Erreur : "+inth+" absent ")
		return False
		
	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(inth, 0)
	inLayer = inDataSource.GetLayer()
	try:
		for f in inLayer:
			if (f is None):
				inDataSource.Destroy()
				return False
			if (f.GetGeometryRef() is None):
				inDataSource.Destroy()
				return False
			# if (sys.stdout.getvalue() != ""):
				# a = sys.stdout.getvalue()
				# print(a)
	except:
		inDataSource.Destroy()
		return False
	return True

def testeGeometrieShapeFile(inth, tipe="LINESTRING"):
	if (tipe=="LINESTRING"):
		geometrie="LINE"
	#ne conserve que les linestring dans ce cas
	if not isfile(inth):
		print("Erreur : "+inth+" absent ")
		exit(0)

	n=0
	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(inth, 0)
	inLayer = inDataSource.GetLayer()
	
	n+=inLayer.GetFeatureCount()
	print(inth.split('/')[-1]+" : "+ str(inLayer.GetFeatureCount()) + " entites")
	
	defn=inLayer.GetLayerDefn()
	
	ok=True
	for f in inLayer:
		geometry = f.GetGeometryRef()
		if ( str(geometry) != tipe ):
			print("Entite "+str(n)+" Geometrie = "+str(geometry))
			ok=False
			n+=1
	inDataSource.Destroy()
	
	return False, n

def compteEntites(fichier):
	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(fichier, 0)
	inLayer = inDataSource.GetLayer()
	n=len(inLayer)
	print(str(n)+ " entites dans "+fichier)
	return n
	
def valeursUniquesChamp(fichier, champ):
	fichier = chercheShapeFile(fichier)
	
	if not isfile(fichier):
		print("Erreur : "+fichier+" absent ")
		exit(0)
	if not testeChamps(fichier, [champ]):
		print("Erreur : champ "+champ+ "absent du fichier" + fichier)
		exit(0)

	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(fichier, 0)
	inLayer = inDataSource.GetLayer()
	defn=inLayer.GetLayerDefn()
	index=-1
	for i in range(0, defn.GetFieldCount()):
		if (defn.GetFieldDefn(i).GetNameRef() == champ):
			index=i
			break
	if index<0:
		print(champ+" missing in "+fichier)
		inDataSource.Destroy()
		listeChamps(fichier)
		return False

	lst=[]
	nvals=[]
	print("VALEURS UNIQUES DU CHAMP "+champ+" DANS "+fichier+" :")
	for f in inLayer:
		if not ( f.GetField(index) in lst ):
			lst.append(f.GetField(index))
			nvals.append(1)
		else:
			i=0
			while lst[i] != f.GetField(index):
				i+=1
			nvals[i]+=1
	i=0

	for ch in lst:
		print(str(ch)+"  ("+str(nvals[i])+ " recs)")
		i+=1
	return lst

def statValeursChamp(fichier, champ):
	fichier = chercheShapeFile(fichier)
	
	if not isfile(fichier):
		print("Erreur : "+fichier+" absent ")
		exit(0)
	if not testeChamps(fichier, [champ]):
		print("Erreur : champ "+champ+ "absent du fichier" + fichier)
		exit(0)

	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(fichier, 0)
	inLayer = inDataSource.GetLayer()
	defn=inLayer.GetLayerDefn()
	index=-1
	for i in range(0, defn.GetFieldCount()):
		if (defn.GetFieldDefn(i).GetNameRef() == champ):
			index=i
			break
	if index<0:
		print(champ+" missing in "+fichier)
		inDataSource.Destroy()
		listeChamps(fichier)
		return False

	
	nvals=np.zeros( shape=(len(inLayer)) )
	print("STATISTIQUES DU CHAMP "+champ+" DANS "+fichier+" :")
	i=0
	for f in inLayer:
		nvals[i] = (f.GetField(index))
		i+=1
	print("MAX="+str(np.amax(nvals))+"  MIN="+str(np.amin(nvals))+"   MEAN="+str(np.mean(nvals)))
	return nvals

def existeValeurChamp(fichier, champ, valeur):

	fichier = chercheShapeFile(fichier)
	
	if not isfile(fichier):
		print("Erreur : "+fichier+" absent ")
		exit(0)
	if not testeChamps(fichier, [champ]):
		print("Erreur : champ "+champ+ "absent du fichier" + fichier)
		exit(0)

	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(fichier, 0)
	inLayer = inDataSource.GetLayer()
	defn=inLayer.GetLayerDefn()
	index=-1
	for i in range(0, defn.GetFieldCount()):
		if (defn.GetFieldDefn(i).GetNameRef().upper() == champ.upper()):
			index=i
			break
	if index<0:
		print(champ+" missing in "+fichier)
		inDataSource.Destroy()
		listeChamps(fichier)
		return True #car c'est le TRUE qui correspond a un test negatif

	lst=[]
	nvals=[]

	for f in inLayer:
		if f.GetField(index) is None:
			return True
		if ( f.GetField(index) == valeur ):
			inDataSource.Destroy()
			return True
	return False

def testeChamps(fichier, champs=[], tipe=-1):
	if not isfile(fichier):
		print("Erreur : "+fichier+" absent ")
		exit(0)
	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(fichier, 0)
	inLayer = inDataSource.GetLayer()
	defn=inLayer.GetLayerDefn()
	OK=True
	if (len(champs)>0):
		for ch in champs:
			ok=False
			for i in range(0, defn.GetFieldCount()):
				if (defn.GetFieldDefn(i).GetNameRef() == ch):
					if (tipe != -1):
						if (defn.GetFieldDefn(i).GetFieldType() == tipe):
							ok=True
							break
						else:
							print(str(ch)+" of bad type")
					else:
						ok=True
						break
			if not ok:
				print(str(ch)+" missing in "+fichier+" or of bad type")
				OK=False
				
	inDataSource.Destroy()
	return OK
	
def featuresTipe(fichier):
	if not isfile(fichier):
		print("Erreur : "+fichier+" absent ")
		exit(0)

	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(fichier, 1)
	inLayer = inDataSource.GetLayer()
	k=0
	for f in inLayer:
		geometry = f.GetGeometryRef()
		if ( geometry != None ):
			print("id="+str(k)+" "+geometry.GetGeometryName())
		k+=1

	inDataSource.Destroy()
	print(str(k)+" records updated")
	
def tableAttrib(fichier):
	if not isfile(fichier):
		print("Erreur : "+fichier+" absent ")
		exit(0)
		
	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(fichier, 0)
	inLayer = inDataSource.GetLayer()
	defn=inLayer.GetLayerDefn()
	k=0
	attribs=[]
	longueurs=[]

	for i in range(defn.GetFieldCount()):
		attribs.append(defn.GetFieldDefn(i).GetNameRef())
		longueurs.append(len(defn.GetFieldDefn(i).GetNameRef()))
	print("Exploring file "+fichier+" ("+str(inLayer.GetFeatureCount())+ " enregistrements)")
	for f in inLayer:
		for i in range(defn.GetFieldCount()):
			if (longueurs[i]<len(str(f.GetField(i)))):
				longueurs[i]=len(str(f.GetField(i)))
	chattrib = ""
	for k in range(len(attribs)):
		att=attribs[k]
		for a in range(len(att), longueurs[k]):
			att+=" "
		chattrib+=att+" "
	inDataSource.Destroy()
	
	inDataSource = driver.Open(fichier, 0)
	inLayer = inDataSource.GetLayer()
	defn=inLayer.GetLayerDefn()
	
	chattrib="ID    "+chattrib+"Geomtry"
	
	print(chattrib)
	n=1
	for f in inLayer:
		vals =str(n)
		for i in range(len(vals), 6):
			vals+=" "
		for i in range(defn.GetFieldCount()):
			val = str(f.GetField(i))
			for a in range(len(val), longueurs[i]):
				val+=" "
			vals += val+" "
		vals += f.GetGeometryRef().GetGeometryName()+" "
		print(vals)
		n+=1
		k+=1
		if (k>19):
			if not (raw_input(" Continuer (y/n) ?") == "y"):
				break
			k=0
			print(chattrib)

	inDataSource.Destroy()

def supprimeEntitesChampValeurs(fichier, outth, champ, valeurs):
	if not isfile(fichier):
		print("Erreur : "+fichier+" absent ")
		exit(0)

	if (not testeChamps(fichier, [champ])):
		print(champ+" absent du shape "+fichier)
		exit(0)
	
	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(fichier, 1)
	inLayer = inDataSource.GetLayer()
	defn = inLayer.GetLayerDefn()
	n=inLayer.GetFeatureCount()
	
	outLayer, driver, outDataSource = creeOutputShapefile(outth, inth=fichier) 
	defno = outLayer.GetLayerDefn()
	
	I=-1
	
	for i in range(defn.GetFieldCount()):
		if (defn.GetFieldDefn(i).GetNameRef() != defno.GetFieldDefn(i).GetNameRef()):
			print("Erreur : definition des champs differentes en input et output")
			print("in = "+defn.GetFieldDefn(i).GetNameRef()+" != out="+defno.GetFieldDefn(i).GetNameRef())

		if (defn.GetFieldDefn(i).GetNameRef().upper() == champ.upper()):
			I=i
	print("Valeurs du champ "+champ+" retenues : "+str(valeurs))
	print("ATTENTION, test des valeurs de champs sensible a la casse")
	k=0
	if (I>=0):
		for f in inLayer:
			if not (f.GetField(I) in valeurs):
				out_feat = ogr.Feature(defno)
				for j in range(0, defno.GetFieldCount()):
					out_feat.SetField(defno.GetFieldDefn(j).GetNameRef(),f.GetField(j))
				out_feat.SetGeometry(f.GetGeometryRef().Clone())
				outLayer.CreateFeature(out_feat)
				out_feat=None
				k+=1
	else:
		print("Erreur, champ "+champ+" non trouve")
		exit(0)
		
	outDataSource.Destroy()
	inDataSource.Destroy()
	print(str(k)+" entites retenues sur "+str(n)+" initiales ("+str(k-n)+")")
	
def selectionneEntitesChampValeurs(fichier, outth, champ, valeurs):
	if not isfile(fichier):
		print("Erreur : "+fichier+" absent ")
		exit(0)

	if (not testeChamps(fichier, [champ])):
		print(champ+" absent du shape "+fichier)
		exit(0)
	
	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(fichier, 1)
	inLayer = inDataSource.GetLayer()
	defn = inLayer.GetLayerDefn()
	n=inLayer.GetFeatureCount()
	
	outLayer, driver, outDataSource = creeOutputShapefile(outth, inth=fichier) 
	defno = outLayer.getLayerDefn()
	
	I=-1
	
	for i in range(defn.GetFieldCount()):
		if (defn.GetFieldDefn(i).GetNameRef() != defno.GetFieldDefn(i).GetNameRef()):
			print("Erreur : definition des champs differentes en input et output")
			print("in = "+defn.GetFieldDefn(i).GetNameRef()+" != out="+defno.GetFieldDefn(i).GetNameRef())

		if (defn.GetFieldDefn(i).GetNameRef().upper() == champ.upper()):
			I=i
	print("ATTENTION, test des valeurs de champs insensible a la casse")
	k=0
	for i in range(len(valeurs)):
		if ( type(valeur[i]) == str ):
			valeurs[i] = valeurs[i].upper()

	if (I>=0):
		for f in inLayer:
			val = f.GetField(I)
			if (type(val) == str):
				val=val.upper()
			if (val in valeurs):
				out_feat = ogr.Feature(defno)
				for j in range(0, defno.GetFieldCount()):
					out_feat.SetField(defno.GetFieldDefn(j).GetNameRef(),f.GetField(j))
				out_feat.SetGeometry(f.GetGeometryRef().Clone())
				outLayer.CreateFeature(out_feat)
				out_feat=None
				k+=1
	else:
		print("Erreur, champ "+champ+" non trouve")
		exit(0)
		
	outDataSource.Destroy()
	inDataSource.Destroy()
	print(str(k)+" entites transferes sur "+str(n)+" initiaux")

def selectionneEntitesChampSupEgal(fichier, outth, champ, borneInf):
	if not isfile(fichier):
		print("Erreur : "+fichier+" absent ")
		exit(0)

	if (not testeChamps(fichier, [champ], tipe=OGRFieldType.OFTReal)):
		print(champ+" absent du shape "+fichier+" ou mauvais type")
		exit(0)
	
	if (not type(borneInf) is float):
		print("La borne "+str(borneInf)+" doit etre numerique")
		exit(0)
	
	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(fichier, 1)
	inLayer = inDataSource.GetLayer()
	defn = inLayer.GetLayerDefn()
	n=inLayer.GetFeatureCount()
	
	outLayer, driver, outDataSource = creeOutputShapefile(outth, inth=fichier) 
	defno = outLayer.getLayerDefn()
	
	I=-1
	
	for i in range(defn.GetFieldCount()):
		if (defn.GetFieldDefn(i).GetNameRef() != defno.GetFieldDefn(i).GetNameRef()):
			print("Erreur : definition des champs differentes en input et output")
			print("in = "+defn.GetFieldDefn(i).GetNameRef()+" != out="+defno.GetFieldDefn(i).GetNameRef())

		if (defn.GetFieldDefn(i).GetNameRef().upper() == champ.upper()):
			I=i
	print("ATTENTION, test des valeurs de champs insensible a la casse")
	k=0

	if (I>=0):
		for f in inLayer:
			val = f.GetField(I)
			if ( val >= borneInf ):
				out_feat = ogr.Feature(defno)
				for j in range(0, defno.GetFieldCount()):
					out_feat.SetField(defno.GetFieldDefn(j).GetNameRef(),f.GetField(j))
				out_feat.SetGeometry(f.GetGeometryRef().Clone())
				outLayer.CreateFeature(out_feat)
				out_feat=None
				k+=1
	else:
		print("Erreur, champ "+champ+" non trouve")
		exit(0)
		
	outDataSource.Destroy()
	inDataSource.Destroy()
	print(str(k)+" entites transferes sur "+str(n)+" initiaux")
	
def selectionneEntitesChampInfEgal(fichier, outth, champ, borneSup):
	if not isfile(fichier):
		print("Erreur : "+fichier+" absent ")
		exit(0)

	if (not testeChamps(fichier, [champ], tipe=OGRFieldType.OFTReal)):
		print(champ+" absent du shape "+fichier)
		exit(0)
	
	if (not type(borneSup) is float):
		print("La borne "+str(borneInf)+" doit etre numerique")
		exit(0)
	
	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(fichier, 1)
	inLayer = inDataSource.GetLayer()
	defn = inLayer.GetLayerDefn()
	n=inLayer.GetFeatureCount()
	
	outLayer, driver, outDataSource = creeOutputShapefile(outth, inth=fichier) 
	defno = outLayer.getLayerDefn()
	
	I=-1
	
	for i in range(defn.GetFieldCount()):
		if (defn.GetFieldDefn(i).GetNameRef() != defno.GetFieldDefn(i).GetNameRef()):
			print("Erreur : definition des champs differentes en input et output")
			print("in = "+defn.GetFieldDefn(i).GetNameRef()+" != out="+defno.GetFieldDefn(i).GetNameRef())

		if (defn.GetFieldDefn(i).GetNameRef().upper() == champ.upper()):
			I=i
	print("ATTENTION, test des valeurs de champs insensible a la casse")
	k=0

	if (I>=0):
		for f in inLayer:
			val = f.GetField(I)
			if ( val <= borneSup ):
				out_feat = ogr.Feature(defno)
				for j in range(0, defno.GetFieldCount()):
					out_feat.SetField(defno.GetFieldDefn(j).GetNameRef(),f.GetField(j))
				out_feat.SetGeometry(f.GetGeometryRef().Clone())
				outLayer.CreateFeature(out_feat)
				out_feat=None
				k+=1
	else:
		print("Erreur, champ "+champ+" non trouve")
		exit(0)
		
	outDataSource.Destroy()
	inDataSource.Destroy()
	print(str(k)+" entites transferes sur "+str(n)+" initiaux")

def calculeChampConstant(fichier, champ, valeur):
	if not isfile(fichier):
		print("Erreur : "+fichier+" absent ")
		exit(0)

	ajoute = not testeChamps(fichier, [champ])
	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(fichier, 1)
	inLayer = inDataSource.GetLayer()
	
	if (ajoute):
		ch = ogr.FieldDefn(champ, ogr.OFTReal)
		inLayer.CreateField(ch)
		print("Field "+champ+" added to "+fichier)
	defn=inLayer.GetLayerDefn()
	k=0
	for f in inLayer:
		f.SetField(champ, valeur)
		inLayer.SetFeature(f)
		k+=1
		
	inDataSource.Destroy()
	print(str(k)+" records updated")

def reclasseChamp(fichier, inchamp, valeur, outchamp, outvaleur):
	if not isfile(fichier):
		print("Erreur : "+fichier+" absent ")
		exit(0)
		
	if not testeChamps(fichier, [inchamp]):
		print("Erreur: le champ "+inchamp+" nest pas present dans "+fichier)
		exit(0)
		
	ajoute = not testeChamps(fichier, [outchamp])

	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(fichier, 1)
	inLayer = inDataSource.GetLayer()
	
	if (ajoute):
		champ = ogr.FieldDefn(outchamp, ogr.OFTReal)
		inLayer.CreateField(champ)
		
	defn=inLayer.GetLayerDefn()
	k=0
	for f in inLayer:
		for i in range(0, defn.GetFieldCount()):
			if (defn.GetFieldDefn(i).GetNameRef() == inchamp):
				if (f.GetField(i) == valeur):
					f.SetField(outchamp, outvaleur)
					inLayer.SetFeature(f)
					k+=1
					
	inDataSource.Destroy()
	print(str(k)+" records updated")

def numeriseChampTexte(fichier, inchamptexte, outchampnum):
	if not isfile(fichier):
		print("Erreur : "+fichier+" absent ")
		exit(0)
		
	if not testeChamps(fichier, [inchamptexte]):
		print("Erreur: le champ "+[inchamptexte]+" nest pas present dans "+fichier)
		exit(0)
		
	ajoute = not testeChamps(fichier, [outchampnum])

	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(fichier, 1)
	inLayer = inDataSource.GetLayer()
	n=inLayer.GetFeatureCount()
	if (ajoute):
		champ = ogr.FieldDefn(outchamp, ogr.OFTReal)
		inLayer.CreateField(champ)

	defn=inLayer.GetLayerDefn()
	k=0
	for f in inLayer:
		for i in range(0, defn.GetFieldCount()):
			if (defn.GetFieldDefn(i).GetNameRef() == inchamptexte):
				s=f.GetField(i).strip()
				if (len(s)>0 and not s.isdigit()):
					while not s[len(s)-1].isdigit() and len(s)>0 :
						s=s[:len(s)-1]
				if (len(s)>0 and not s.isdigit()):
					while not s[0].isdigit():
						s=s[1:]
				if (s.isdigit()):
					f.SetField(outchampnum, int(s))
					inLayer.SetFeature(f)
					k+=1
	inDataSource.Destroy()
	print(str(k)+" records updated sur "+str(n))
	
def litTable(table, affiche=True):
	if not isfile(table):
		if not isfile(table+".tab"):
			print("Erreur : fichier table "+table+" absent ")
			exit(0)
		else:
			table += ".tab"
	lignes=[]
	lespoids=[]
	coefficient=0 ; nomCoef = ""
	n=0
	with open(table, "r") as filin:
		for ligne in filin:
		
			if (ligne.upper().startswith("COEF")):
				try:
					nomCoef = ligne.split("=")[0]
					coefficient=float(ligne.split("=")[1])
				except:
					pass
					
			tlt = traiteLigneTable(ligne)
			if (tlt[0]):
				ligne=tlt[1]
				lignes.append(ligne)
				if (affiche):
					print(ligne+" "+tlt[2])
				lespoids.append( (ligne.split("=")[-1]).strip())
				
	nppoids = np.array(lespoids)
	punique = np.unique(nppoids)
	lst=[]  #il vaut mieu renvoyer des liste py qui sont plus standards
	nbpoids=[]
	
	total=0
	for p in punique:
		lst.append(float(p))
		z=0
		for o in lespoids:
			if str(o).strip() == str(p).strip():
				z+=1
		total+=z
		nbpoids.append(z)
	z=0
	
	if (affiche):
		print(str(len(lignes))+" lignes")
		print("Valeurs uniques des poids")
		for p in lst:
			print(str(p)+" ("+str(nbpoids[z])+" postes)")
			z+=1
		
		print("Total = "+str(total)+" postes")
		
		if (coefficient>0):
			print(nomCoef+" "+str(coefficient))
		
	return lignes, lst, nbpoids, nomCoef, coefficient

def reclasseChampsTable(fichier, inchamp, outchamp, table, valeursACorriger=[]):
	if ( type(inchamp) is list ):
		if (len(inchamp) > 1):
			return reclasseMultiChampTable(fichier, inchamp, outchamp, table, valeursACorriger)
		if (len(inchamp) == 1):
			return reclasseChampTable(fichier, inchamp[0], outchamp, table, valeursACorriger)
	else:
		return reclasseChampTable(fichier, inchamp, outchamp, table, valeursACorriger)

def reclasseChampTable(fichier, inchamp, outchamp, table, valeursACorriger=[]):
	if not isfile(fichier):
		print("Erreur : "+fichier+" absent ")
		exit(0)
	if not isfile(table):
		print("Erreur : fichier table "+table+" absent ")
		exit(0)
		
	if not testeChamps(fichier, [inchamp]):
		print("Erreur: le champ "+inchamp+" nest pas present dans "+fichier)
		exit(0)
	
	lignes=[]
	ligne0=""
	coefficient=0
	k=0
	with open(table, "r") as filin:
		for ligne in filin:
			if (k==0) and (len(ligne.strip())>0) and (not ligne.strip().startswith("#")) :
				ligne0=ligne
				k+=1

			tlt = traiteLigneTable(ligne)
			if (tlt[0]):
				ligne=tlt[1]
				lignes.append(ligne)

	if (len(lignes)>0):
		if not (testeTable(ligne0, inchamps)):
			exit(0)
		ajoute = not testeChamps(fichier, [outchamp])

		driverName = "ESRI Shapefile"
		driver = ogr.GetDriverByName(driverName)
		inDataSource = driver.Open(fichier, 1)
		inLayer = inDataSource.GetLayer()
		
		if (ajoute):
			champ = ogr.FieldDefn(outchamp, ogr.OFTReal)
			inLayer.CreateField(champ)
			print(outchamp+" added to "+fichier)
			
		defn=inLayer.GetLayerDefn()
		I=-1
		k=0
		for i in range(0, defn.GetFieldCount()):
			if (defn.GetFieldDefn(i).GetNameRef().upper() == inchamp.upper()):
				I=i
				print(outchamp+ " trouve en position "+str(I))
				break
		
		if (I >= 0):
			if (len(valeursACorriger)<=0):
				for f in inLayer:
					for ligne in lignes:
						lst = ligne.split("=")
						outvaleur = lst[len(lst)-1]
						plage = lst[0].upper()
						if ( traiteNomenclature(plage, f.GetField(I) ) ):
							f.SetField(outchamp, float(outvaleur))
							inLayer.SetFeature(f)
							k+=1
			else:
				for f in inLayer:
					if (f.GetField(I) in valeursACorriger):
						for ligne in lignes:
							lst = ligne.split("=")
							outvaleur = lst[len(lst)-1]
							plage = lst[0].upper()
							if ( traiteNomenclature(plage, f.GetField(I) ) ):
									f.SetField(outchamp, float(outvaleur))
									inLayer.SetFeature(f)
									k+=1
	
		print(str(k)+" records updated")

	inDataSource.Destroy()

def reclasseMultiChampTable(fichier, inchamps, outchamp, table, valeursACorriger=[]):

	if not isfile(fichier):
		print("Erreur : "+fichier+" absent ")
		exit(0)
	if not isfile(table):
		print("Erreur : fichier table "+table+" absent ")
		exit(0)
		
	if not testeChamps(fichier, inchamps):
		print("Erreur: un champ parmi "+str(inchamps)+" nest pas present dans "+fichier)
		exit(0)
	
	lignes=[]
	ligne0=""
	k=1
	coefficient=0
	with open(table, "r") as filin:
		for ligne in filin:
			if (k==0) and ( len(ligne.strip())>0 ) and (not ligne.strip().startswith("#")) :
				ligne0=ligne
				k+=1

			tlt = traiteLigneTable(ligne)
			if (tlt[0]):
				ligne=tlt[1]
				lignes.append(ligne)

	if (len(lignes)>0):
		if not (testeTable(ligne0, inchamps)):
			exit(0)

		ajoute = not testeChamps(fichier, [outchamp])

		driverName = "ESRI Shapefile"
		driver = ogr.GetDriverByName(driverName)
		inDataSource = driver.Open(fichier, 1)
		inLayer = inDataSource.GetLayer()
		
		if (ajoute):
			champ = ogr.FieldDefn(outchamp, ogr.OFTReal)
			inLayer.CreateField(champ)
			print(outchamp+" added to "+fichier)
			
		defn=inLayer.GetLayerDefn()
		k=0
		I=-1
		for i in range(0, defn.GetFieldCount()):
			if (defn.GetFieldDefn(i).GetNameRef().upper() == outchamp.upper()):
				I=i
				print(outchamp+ " trouve en position "+str(I))
				break

		if (I >=0 ):
			if (len(valeursACorriger)<1):
				for f in inLayer:
					oval = traiteEntree(f, defn, inDataSource, inchamps, outchamp, lignes)
					if not oval is None:
						f.SetField(outchamp, float(oval))
						inLayer.SetFeature(f)
						k+=1
			else:
				for f in inLayer:
					if (f.GetField is None or f.GetField(I) in valeursACorriger):
						oval = traiteEntree(f, defn, inDataSource, inchamps, outchamp, lignes)
						if not oval is None:
							f.SetField(outchamp, float(oval))
							inLayer.SetFeature(f)
							k+=1
		else:
			print("outilsVecteurs.reclasseMultiChampTable(1274): Le champ "+outchamp+" semble absent de "+fichier)
			inDataSource.Destroy()
			exit(0)

		print(str(k)+" records updated dabs "+fichier)
	inDataSource.Destroy()


def testeTable( ligne, inchamps ):

	lst = ligne.split("=")
	if (len(lst)<len(inchamps)+1):
		print("Erreur dans la table, ligne "+ligne+" : il faut specifier au moins "+str(len(inchamps))+" valeurs champs "+str(inchamps))
		return False
	try:
		a=float(lst[-1])
	except:
		i=0
		for ch in inchamps:
			if (ch.upper() != lst[i].upper()):
				print("Erreur dans l'entete "+ligne+" de la table : les champs de correspondent pas a "+str(inchamps))
				return False
	return True

def traiteEntree(f, defn, inDataSource, inchamps, outchamp, lignes):

	for ligne in lignes:
		lst = ligne.split("=")
		outvaleur = lst[len(lst)-1]
		ok=True
		for k in range(len(inchamps)):
			plage = (ligne.split("=")[k])
			for i in range(0, defn.GetFieldCount()):
				if (defn.GetFieldDefn(i).GetNameRef().upper() == inchamps[k].upper()):
					if not (traiteNomenclature(plage, f.GetField(i))):
						ok=False
						break
			if not ok:
				break
		if (ok):
			return outvaleur
	return None
	
def traiteNomenclature(inplage, valeur):
	if ( inplage.find("_") <= 0 ):
		if (str(valeur).strip().upper() == str(inplage).strip().upper() ):
			return True
	else:
		min=float(inplage.split("_")[0].strip())
		max=float(inplage.split("_")[1].strip())
		if ( float(str(valeur).strip()) >= min and float(str(valeur).strip()) <= max ) :
			return True
	return False

def supprimeChamp(fichier, champ):
	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(fichier, 1)
	inLayer = inDataSource.GetLayer()
	defn=inLayer.GetLayerDefn()
	index=-1
	for i in range(0, defn.GetFieldCount()):
		if (defn.GetFieldDefn(i).GetNameRef() == champ):
			index=i
			break
	if (index>=0):
		inLayer.DeleteField(index)
		print(champ+" removed from "+fichier)
	else:
		print(champ+" ne semble pas etre present dans "+fichier)

	inDataSource.Destroy()

def ajouteChamp(fichier, champ, stipe=""):

	tipe = ogr.OFTReal
	if (stipe.upper().startswith("INT")):
		tipe=ogr.OFTInteger
	if (stipe.upper().startswith("STR") or stipe.upper().startswith("CH")):
		tipe=ogr.OFTString

	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(fichier, 1)
	inLayer = inDataSource.GetLayer()
	defn=inLayer.GetLayerDefn()
	
	for i in range(0, defn.GetFieldCount()):
		if (defn.GetFieldDefn(i).GetNameRef().upper() == champ.upper()):
			print(champ+" existe deja dans "+fichier)
			return

	ch = ogr.FieldDefn(champ, tipe)
	inLayer.CreateField(ch)
	inDataSource.Destroy()

def copyChamp(fichier, inchamp, outchamp):
	if not testeChamps(fichier, [inchamp]):
		print("Erreur: le champ "+inchamp+" est absent du fichier "+fichier)
		exit(0)
	if not testeChamps(fichier, [outchamp]):
		ajouteChamp(fichier, outchamp)
		
	driverName = "ESRI Shapefile"
	driver = ogr.GetDriverByName(driverName)
	inDataSource = driver.Open(fichier, 1)
	inLayer = inDataSource.GetLayer()
	defn=inLayer.GetLayerDefn()
	I=-1
	for i in range(0, defn.GetFieldCount()):
		if (defn.GetFieldDefn(i).GetNameRef() == inchamp):
			I=i
			break
	if (I>=0):
		for f in inLayer:
			f.SetField(outchamp, f.GetField(I))
			inLayer.SetFeature(f)
	else:
		print("Erreur "+inchamp+" non trouve - STOP")
		inDataSource.Destroy()
		exit(0)
	inDataSource.Destroy()
	
def verifieValeursTable(fichier, champs, table):
	if type(champs) is list :
		k=0
		for ch in champs:
			if not verifieValeurTable(fichier, ch, table, k):
				return False
			k+=1
		return True
	else:
		return verifieValeurTable(fichier, champ, table)
		
def verifieValeurTable(fichier, champ, table, position=0):
	if isfile(fichier):
		if (testeChamps(fichier, [champ])):
			lunique = valeursUniquesChamp(fichier, champ)
			num=True
			for s in lunique:
				if not str(s).isdigit():
					num=False
					break
			vunique = [str(s).upper() for s in lunique]
			if isfile(table):
				print("Ouverture de "+table)
				for v in vunique:
					with open(table, "r") as filin:
							#on reouvre le fichier a chaque coup, c'est pas top
						ok=False
						for ligne in filin:
							tlt = traiteLigneTable(ligne)
							if (tlt[0]):
								ligne=tlt[1]
								postes=ligne.split("=")[position]
								poids=ligne.split("=")[-1]
								if (postes.find("_") < 0):
									if (postes.upper() == v):
										ok=True
										break;
								else:
									if num:
										if (float(v) >= int(postes.split("_")[0]) and float(v) <= int(postes.split("_")[1]) ):
											ok=True
											print(v+": poids = "+poids)
											break;
						filin.close()
						if (not ok):
							print("Valeur unique "+str(v)+" non represente dans la table "+table+" : STOP")
							return False
			else:
				print("Table des poids "+table+" manquante")
				return False
		else:
			print("Champ "+champ+" absent du shapefile "+fichier)
	else:
		print("Shapefile "+fichier+" manquant")
		return False
	print("outilsVecteurs.py:verifieValeurTable: Toutes des valeurs du champ "+champ+" du shapefile "+fichier+" sont presentes dans la table "+table) 
	return True
	
def traiteLigneTable(ligne):
	legende=""
	ok=True
	if len(ligne.strip())<=0:
		ok=False
	else:
		if ligne.startswith("#"):
			ok=False
		else:
			if (ligne.find(":")) > 0:
				legende = ligne.split(":")[1].strip()
				ligne = ligne.split(":")[0].strip()
				if len(ligne)<=0:
					ok=False
				else:
					try:
						a=float((ligne.split("=")[-1]).strip())
					except:
						ok=False

	return ok, ligne, legende