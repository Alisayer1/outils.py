import numpy as np
import rasterio, ogr, gdal
from rasterio import crs as CRS
from rasterio.transform import Affine
from rasterio import features
from rasterio.mask import mask
import fiona
from os.path import isfile
from os import remove as supprime
from math import sqrt
from skimage import io
import matplotlib.pyplot as plt
from outilsVecteurs import estChamp, copyFileSet, renameFileSet
from outilsGDAL import distanceGDAL

#intaller scikit-image
def copyTifFile(fichier, out="./"):
	return copyFilesSet(fichier, out, ["tif", "tiff", "tfw"])

def renameTifFile(fichier, out):
	return renameFileSet(fichier, out, ["tif", "tiff", "tfw"])
	
def affiche(image):
	im=io.imread(image)
	plt.title(image)
	plt.imshow(im, cmap=plt.cm.gray)
	plt.show()

def normalisation(inraster):

	MIN = np.amin(inraster)
	MAX = np.amax(inraster)
	print("NORMALISATION: Min="+str(MIN)+" max="+str(MAX))
	if ( float(MIN) == 0 and float(MAX) == 1):
		return inraster
	return ( (inraster - float(MIN)) / ( float(MAX) - float(MIN) ))

def normalisationTiff(intiff, outtiff):
	rast = litFichierTiff(intiff)[0]
	nrast = normalisation(rast)
	genereTiff(nrast, outtiff, modeletif=intiff)
	print("OUTPUT = "+outtiff)

def radical(fichier, ext=".tif"):
	fichier=fichier.replace("\\", "/")
	if not ext.startswith("."):
		ext="."+ext
	if (fichier.endswith(ext)):
		return fichier.split(ext)[0]
	if (fichier.lower().endswith(ext.lower())):
		return fichier[:-len(ext)]
	if (fichier.endswith(".tiff")):
		return fichier.split(".tiff")[0]
	if (fichier.endswith(".TIFF")):
		return fichier.split(".TIFF")[0]
	

def chercheFichierTiff(fichier):
	fichier=fichier.replace("\\", "/")
	rad=fichier.split("/")[-1]
	if (rad.upper().find(".TIF") <= 0):
		
		if isfile(fichier):
			print("outils.py:chercheFichierTiff(41): WARNING: fichier "+fichier+" existe mais ne semble pas avoir la bonne extension")
			return fichier
		else:
			if (rad.find(".")<=0):
				if isfile(fichier+".tif"):
					out=fichier+".tif"
					return (out)
				else:
					if isfile(fichier+".tiff"):
						out=fichier+".tiff"
						return (out)
				print(fichier+".tif does not exists")
				exit(0)
			else:
				print("Erreur : fichier "+fichier+" non tiff")
				exit(0)
	else:
		if not isfile(fichier):
			print("outils.py:chercheFichierTiff(59): ERREUR: "+fichier+" does not exist")
			exit(0)
	return fichier
def chercheTiff(fichier):
	return chercheFichierTiff(fichier)


def genereTiff(inraster, fichier, xul=0, yul=0, resol=0, W=0, H=0, tipe=rasterio.float64, nodat=-9999, modeletif="", listeparams=[], decaleResol=(0.5,0.5)):
	decale=True
	if ( len(listeparams)>0 and ( (xul==0) or (yul==0) or (resol==0) or (H==0) or (W==0) ) ):
		W=listeparams[1]
		H=listeparams[2]
		xul=listeparams[3]
		yul=listeparams[4]
		resol=listeparams[5]
		decale=False
		
	if ( len(modeletif)>0 and ( (xul==0) or (yul==0) or (resol==0) or (H==0) or (W==0) ) ):
		infi = chercheFichierTiff(modeletif)
		if (len(infi) >0):
			attrib = litFichierTiff(infi)
			W=attrib[1]
			H=attrib[2]
			xul=attrib[3]
			yul=attrib[4]
			resol=attrib[5]
			decale=False
		else:
			if not (raw_input("WARNING (outils.py:genereTiff): fichiermodele non tiff ("+modeletif+")! Continuer (y/n) ?") == "y"):
				exit(0)
		if ( fichier.find("/") <= 0 ):
			if (modeletif.find("/") > 0 ):
				nomfimod = modeletif.split("/")[-1]
				chem = modeletif.split(nomfimod)[0]
				fichier = chem+fichier
	
	if (not decale):
		decaleResol = (0,0)
	transforme =  Affine.translation(xul - (resol * decaleResol[0]), yul - (resol * decaleResol[1]) ) * Affine.scale(resol, -resol)

	l93= "+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs" #lambert93
	if (H==0):
		H=inraster.shape[0]
	if (W==0):
		W=inraster.shape[1]
	fichier=fichier.replace("\\", "/")
	if (isfile(fichier)):
		if not (raw_input("WARNING (outils.py:genereTiff): le Fichier "+fichier+" existe deja ! Continuer (y/n) ?") == "y"):
			exit(0)
	if not ( fichier.upper().endswith(".TIF") and not fichier.upper().endswith(".TIFF") ):
		if not (raw_input("WARNING (outils.py:genereTiff): generation d'un geotif avec une extension non tiff ("+fichier+")! Continuer (y/n) ?") == "y"):
			exit(0)
	rasteur = rasterio.open(
		fichier,
		'w',
		driver='GTiff',
		height=H,
		width=W,
		count=1,
		dtype=tipe,
		crs=l93,
		transform=transforme,
		nodata=nodat
		)
	outrast=np.zeros(shape=(1,H,W))
	outrast[0]=inraster
	rasteur.write(outrast)
	rasteur.close()
	litFichierTiff(fichier)

def litFichierTiff(fichier, unik=False):
	infi = chercheFichierTiff(fichier)
	print("OPEN FILE "+infi)
	if (len(infi)>0):
		fichier=infi
		sauve=False
		with rasterio.open(fichier) as ds:
			kwargs = ds.meta.copy()
			raster = ds.read(1)
			xUL=ds.bounds.left
			yUL=ds.bounds.top
			H=ds.height
			W=ds.width
			nodat = ds.nodata
			resolX=(ds.bounds.right - ds.bounds.left)/W
			resolY=(ds.bounds.top - ds.bounds.bottom)/H
			resol=resolX
			ds.close()

			if ( abs( (resolY-resolX)/resolX ) > 1e-06 or abs( (resolY-resolX)/resolY ) > 1e-06 ):
				if not (raw_input("WARNING(outils.litFichierTiff): resolX="+str(resolX)+" different de resolY="+str(resolY)+" dans le fichier tiff (" + fichier + ")! Continuer (y/n) ?") == "y"):
					exit(0)
			else:
				if (resolX != resolY):
					resol=(resolX+resolY)/2
					
			nodatnum=True
			try:
				float(nodat)
			except:
				nodatnum=False
				if not (raw_input("WARNING(outils.litFichierTiff): nodata="+str(nodat)+" n'est pas numerique ! Continuer (y/n) ? ") == "y"):
					exit(0)
				if (raw_input("REMPLACER nodata="+str(nodat)+" par -9999 (y/n) ? ") == "y"):
					raster[raster==nodat] = -9999
					nodat=-9999
					nodatnum=True
					sauve=True

			notanum = raster[np.isnan(raster)]
			if not nodatnum:
				notanum = raster[np.isnan(raster) and raster!=nodat]
			if (len(notanum) > 0):
				tx = 100.0 * float(len(notanum))/float(len(rast))
				if not (raw_input("WARNING(outils.litFichierTiff): "+str(len(notanum))+" pixels non numeriques soit "+str(tx)+"% ! Continuer (y/n) ? (si oui, remplace les NaN par nodata="+str(nodat)+")") == "y"):
					exit(0)
				raster[np.isnan(raster)] = nodat
				sauve=True
				
			rast=raster[raster!=nodat]
			min=np.amin(rast)
			max=np.amax(rast)
			moy=np.average(rast)
			print(fichier.split("/")[-1]+" "+str(W)+" X "+str(H)+"  xUL="+str(xUL)+"  yUL="+str(yUL)+"  resol="+str(resol)+"m/pix"+"   MAX="+str(max)+"  MIN="+str(min)+"  MOY="+str(moy)+"  nodata="+str(nodat))
			
			uni=[]
			if (unik):
				
				s=""
				npuni = np.unique(rast)
				dernier=1
				for v in npuni:
					s += str(v)+" "
					uni.append(v)
					dernier=v
				uni.append(dernier)
				#print("Valeurs uniques : "+s)
				print("HISTOGRAM")
				a = np.histogram(rast, uni)
				k=0
				for n in a[0]:
					print(str(n)+"   "+str(a[1][k]))
					k+=1
				total=np.sum(a[0])
				print("Total hors nodata ("+str(nodat)+") = "+str(total)+ " pixels sur "+str(H*W)+" pixels total soit "+str((float(total)/float(H*W))*100.0)+"%")
				uni = uni[:(len(uni)-1)]
				
			params = [raster, W, H, xUL, yUL, resol, min, max, moy, uni, nodat]
			
			if (sauve):
				genereTiff(raster, fichier, listeparams=params)
				
			return((raster, W, H, xUL, yUL, resol, min, max, moy, uni, nodat))
#						0	1	2	3	4	5		6	7	  8		9	10
	else:
		return ()

def litValeursRaster(raster, nodata=-9999):
	rast=raster[raster!=nodata]
	min=np.amin(rast)
	max=np.amax(rast)
	moy=np.average(rast)
	print("MIN="+str(min)+"   MAX="+str(max)+"  MOY="+str(moy))
	return( (min, max, moy))

def inverseNoDataTiff(fichier, outfi):
	tiff = litFichierTiff(fichier)
	rast = tiff[0]
	nodata = tiff[10]
	print(str(nodata))
	outrast = np.zeros(shape=(tiff[2], tiff[1]))
	outrast[ ( rast==nodata ) ] = 1
	outrast[ ( rast!=nodata ) ] = 0
	genereTiff(outrast, outfi, modeletif=fichier)

def inverseValeursTiff(fichier, outfi):
	tiff = litFichierTiff(fichier)
	rast = tiff[0]
	nodata = tiff[10]
	print(str(nodata))
	outrast = np.zeros(shape=(tiff[2], tiff[1]))
	outrast[ ( rast!=nodata ) ] = ( 1 - rast[ (rast != nodata) ] )
	outrast[ ( rast==nodata ) ] = nodata
	genereTiff(outrast, outfi, modeletif=fichier)
	
def rabotePartieCommuneRaster(lesRasters):
	lesInputs = []

	nodata=-9999
	rast=np.zeros(shape=(0,0))
	xULmax = 0 ; yULmin = 0
	xLRmin = 0 ; yLRmax = 0
	resol = 0
	lesXul=[]
	lesYul=[]
	lesXlr=[]
	lesYlr=[]
	k=0
	W0=0 ; H0=0 ; resol0=0 ; xUL0=0; yUL0=0; xLR0=0; yLR0=0
	ridentiques=True
	for fichier in lesRasters:
		print("Open file "+fichier.split("/")[-1])
		rasterL = litFichierTiff(fichier)

		if (len(rasterL)>0):
			rast=rasterL[0]
			WL=rasterL[1]
			HL=rasterL[2]
			xul = rasterL[3]
			yul = rasterL[4]
			resol = rasterL[5]
			xlr=xul+resol*WL
			ylr=yul-resol*HL
			lesXul.append(xul)
			lesYul.append(yul)
			lesXlr.append(xlr)
			lesYlr.append(ylr)
			MIN=np.amin(rast)
			MAX=np.amax(rast)
			if (MAX <= MIN): 
				print("outils.py:rabotePartieCommuneRaster(101) : Erreur fichier "+fichier+" : min = "+str(MIN)+"  max = "+str(MAX))
				exit(0)
			coef = 1 / (float(MAX)-float(MIN))
			lesInputs.append( (rast, float(MIN), float(MAX), coef, xul, yul, xlr, ylr, WL, HL, resol) )
	#							0		1			2		 3  	4	 5	 6	  7		8	  9  10
			print("Input "+str(k)+" : "+fichier.split("/")[-1]+"  MIN="+str(lesInputs[k][1])+"  MAX="+str(lesInputs[k][2])+"  coef="+str(lesInputs[k][3])+"  xUL="+str(xul)+"  yUL="+str(yul)+"  xLR="+str(xlr)+"  ylr="+str(ylr) )
			if ( MAX!=1 or MIN!=0):
				if not (raw_input("WARNING (outils.rabotePartieCommuneRaster(309): WARNING : MAUVAISE NORMALISATION DU RASTER "+fichier+". Continuer (y/n) ?") == "y"):
					exit(0)
			k+=1
		else:
			print("Erreur fichier "+fichier)
			exit(0)
			
		if (W0!=0):
			if (W0!=WL):
				ridentiques=False
				print("W diff:"+str(W0)+" != "+str(WL))
		else:
			W0=WL
		if (H0!=0):
			if (H0!=HL):
				ridentiques=False
				print("H diff:"+str(H0)+" != "+str(HL))
		else:
			H0=HL

		if (resol0!=0):
			if (resol0!=resol):
				ridentiques=False
				print("resol diff:"+str(resol0)+" != "+str(resol))
		else:
			resol0=resol
			
		if (xUL0!=0):
			if abs(xUL0-xul) > resol :
				ridentiques=False
				print("xul diff: abs(xul0-xul)="+str(abs(xUL0-xul))+" > "+str(resol))
		else:
			xUL0=xul
			
		if (yUL0!=0):
			if abs(yUL0-yul) > resol :
				ridentiques=False
				print("yul diff: abs(yul0-yul)="+str(abs(yUL0-yul))+" > "+str(resol))
		else:
			yUL0=yul

		if (xLR0!=0):
			if abs(xLR0-xlr) > resol :
				ridentiques=False
				print("xlr diff: abs(xlr0-xlr)="+str(abs(xLR0-xlr))+" > "+str(resol))
		else:
			xLR0=xlr
			
		if (yLR0!=0):
			if abs(yLR0-ylr) > resol :
				ridentiques=False
				print("ylr diff: abs(ylr0-ylr)="+str(abs(yLR0-ylr))+" > "+str(resol))
		else:
			yLR0=ylr
			
	if (not ridentiques):
		xULmax = np.max(lesXul)
		xULmin = np.min(lesXul)
		yULmax = np.max(lesYul)
		yULmin = np.min(lesYul)
		xLRmax = np.max(lesXlr)
		xLRmin = np.min(lesXlr)
		yLRmax = np.max(lesYlr)
		yLRmin = np.min(lesYlr)
		if (xULmax > xLRmin) or (yULmin < yLRmax):
			print("ERROR: input rasters do not overlay xULmax ="+str(xULmax)+" > xLRmin="+str(xLRmin)+" or yULmin="+str(yULmin)+" < yLRmax="+str(yLRmax))
			exit(0)

		Hmin=0
		Wmin=0
		print("Phase de recalage")
		
		for a in range(len(lesRasters)) :
			print("H="+str(lesInputs[a][0].shape[0])+"(min:"+str(Hmin)+")  W="+str(lesInputs[a][0].shape[1])+"(min:"+str(Wmin)+")") #shape[0] est le nombre de lignes (donc H)
			print("Reseize ")

			rast=lesInputs[a][0]
			decaXL = int((xULmax - lesInputs[a][4])/lesInputs[a][10])
			if ( decaXL > 0 ):
				for z in range(decaXL):
					rast=np.delete(rast, 0, 1)                #on efface la premiere colonne autant de fois que necessaire
			xUL=xULmax
			
			decaXR = int((lesInputs[a][6] - xLRmin)/lesInputs[a][10])
			if ( decaXR > 0 ):
				for z in range(decaXR):
					rast=np.delete(rast, rast.shape[1]-1, 1)   #on efface la derniere colonne autant de fois que necessaire
			xLR=xLRmin
			
			decaYT = int((lesInputs[a][5] - yULmin)/lesInputs[a][10])
			if ( decaYT > 0 ):
				for z in range(decaYT):
					rast=np.delete(rast, 0, 0)                #on efface la premiere ligne autant de fois que necessaire
			yUL=yULmin

			decaYB = int((yLRmax - lesInputs[a][7] )/lesInputs[a][10])
			if ( decaYB > 0 ):
				for z in range(decaYB):
					rast=np.delete(rast, rast.shape[0]-1, 0)   #on efface la derniere ligne autant de fois que necessaire
			yLR=yLRmax
			wl = rast.shape[1]
			hl = rast.shape[0]
			lesInputs[a] = (rast, lesInputs[a][1], lesInputs[a][2], lesInputs[a][3], xUL, yUL, xLR, yLR, wl, hl, lesInputs[a][10])
#							(rast, float(MIN),      float(MAX),			coef,		xul,	yul,xlr, ylr,   WL,  HL,  resol) )
#							0		1			      2			 		3			4	 	5	 6	  7		8	  9	 10
			if (Hmin==0):
				Hmin=hl
			else:
				if (hl<Hmin):
					Hmin=hl
			if (Wmin==0):
				Wmin=wl
			else:
				if (wl<Wmin):
					Wmin=wl

		print("Phase de rabotage")
		a=0
		for inputs in lesInputs :
			if (inputs[0].shape[0] > Hmin or inputs[0].shape[1] > Wmin):
				print("Reseize on pixels basis")
				print("Attention, on suppose ici que tous les raster on la meme origine X Y lambert")
				rast=inputs[0]
				if (rast.shape[0] > Hmin):
					for z in range(rast.shape[0]-1, Hmin-1, -1):
						rast = np.delete(rast, z, 0)
						print("Row "+str(z)+" deleted")
				
				if (rast.shape[1] > Wmin):
					for z in range(rast.shape[1]-1, Wmin-1, -1):
						rast = np.delete(rast, z, 1)
						print("Deleted col="+str(z))

			lesInputs[a] = (rast, lesInputs[a][1], lesInputs[a][2], lesInputs[a][3], xUL, yUL, xLR, yLR, wl, hl, lesInputs[a][10])
	#									min               max            coef
			
			print( "lesInputs["+str(a)+"][0] : "+str(lesInputs[a][0].shape[0])+" X "+str(lesInputs[a][0].shape[1]) )
			a+=1
	else:
		print("Rasters coherents")

	return lesInputs

def filtreCirculaire(dim):
	weights = np.ones((dim, dim))
	centre = (dim - 1) / 2
	for i in range(dim):
		for j in range(dim):
			if ( sqrt( abs(i-centre)*abs(i-centre) + abs(j-centre) * abs(j-centre) ) > (centre) ):
				weights[i, j] = 0
	print(weights)
	return (weights)
	
def reclasseTable(rasterin, table, outfi="", xUL=0, yUL=0, resol=0):
	ok = verifieValeurTable(rasterin, table)
	if (ok):
		raster = rasterin

		if isfile(rasterin):
			tup = litFichierTiff(rasterin)
			raster=tup[0]
			W=tup[1]
			H=tup[2]
			xUL=tup[3]
			yUL=tup[4]
			resol=tup[5]

			outrast = np.zeros(shape=(H, W))
			ok=False
			if not isfile(table):
				print("Fichier de poids des postes "+table+" manquant : STOP")
				exit(0)
			print("Raster = "+rasterin+" table = "+table)

			with open(table, "r") as filin:
				for ligne in filin:
					if (len(ligne.split("=")) >1):
						srcd = ligne.split("=")[0]  #poste(s)
						poids = ligne.split("=")[1] #poids
						if (len(ligne.split("="))>2):
							valcl = ligne.split("=")[1] #classe
							poids = ligne.split("=")[2] #Poids
						if (float(poids)<0 or float(poids)>1):
							if not (raw_input("WARNING (outils.py:reclasseTable): ligne "+ligne+" poids "+poids+" hors [0,1] dans "+table+" : Continuer (y/n) ?") == "y"):
								exit(0)
						print("Reclassage pour "+srcd+" -> "+poids)
						
						if (srcd.find("_") < 0):
							outrast[(raster == int(srcd))] = poids
						else:
							borneinf = (srcd.split("_")[0]).strip()
							bornesup = (srcd.split("_")[1]).strip()
							if (len(borneinf) > 0 and len(bornesup) > 0 ):
								outrast[(raster >= int(borneinf) ) & (raster <= int(bornesup)) ] = poids
							elif len(borneinf) == 0:
								outrast[(raster <= int(bornesup) )] = poids
							elif len(bornesup) == 0:
								outrast[(raster >= int(borneinf) )] = poids
					else:
						print("Ligne "+ligne+" anormale dans la table "+table)
				
				filin.close()
				litValeursRaster(outrast)
				if( len(outfi)>0 and xUL>0 and yUL>0 and resol>0 ):
					genereTiff(outrast, outfi, xUL, yUL, resol)

			return outrast

		else:
			print("Raster "+rasterin+" manquant : STOP")
			exit(0)

def verifieValeurTable(rast, table):
	if isfile(rast):
		if isfile(table):
			print("Ouverture de "+rast)
			rng = litFichierTiff(rast)[0].flatten()
			for v in np.unique(rng):
				if (int(v)>0):
					with open(table, "r") as filin:
						#on reouvre le fichier a chaque coup, c'est pas top
						ok=False

						for ligne in filin:
							postes=ligne.split("=")[0]
							if (postes.find("_") < 0):
								if (int(v) == int(postes)):
									ok=True
									break;
							else:
								if (int(v) >= int(postes.split("_")[0]) and int(v) <= int(postes.split("_")[1]) ):
									ok=True
									break;
						filin.close()
					if (not ok):
						print("Valeur unique "+str(v)+" non present dans la table "+table+" : STOP")
						return False
		else:
			print("Table des poids "+table+" manquante")
			return False
	else:
		print("Raster "+rast+" manquant")
		return False
	print("outils.py:verifieValeurTable: Toutes des valeurs du rasteur "+rast+" sont presentes dans la table "+table) 
	return True

# def litShapeFile(fichier):

	# driver = ogr.GetDriverByName("ESRI Shapefile")
	# dataSource = driver.Open(fichier, 0)
	# layer = dataSource.GetLayer()
	# nr_features = layer.GetFeatureCount()

	# if not isfile(fichier):
		# print("Fichier de poids des postes "+fichier+" manquant : STOP")
		# exit(0)
	
	# with fiona.open(fichier, "r") as shapefile:
		# print("BOUNDS: "+str(shapefile.bounds))
		# print("FEATURES NUMBER: "+str(len(shapefile)))
		# schema = shapefile.schema["properties"].items()
		# s="ID "
		# for k, v in schema:
			# s+= k+"("+v+") "
		# print(s)
		# for f in shapefile:
			# s=f["id"]+" "
			# for k, v in schema:
				# s+=str(f["properties"][k])+" "
			# print(s)
		# shapes = [feature["geometry"] for feature in shapefile]
		
		# return schema, shapes
	#with rasterio.open("tests/data/RGB.byte.tif") as src:
	#	out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
	#	out_meta = src.meta
		
# def decritChamps(fichier, champ):
	# if not isfile(fichier):
		# print("Fichier de poids des postes "+fichier+" manquant : STOP")
		# exit(0)
	
	# with fiona.open(fichier, "r") as shapefile:
		# schema = shapefile.schema["properties"].items()
		# for k, v in schema:
				# if (k.lower() == champ.lower()):
					# shapefile.close()
		# shapefile.close()
		# return schema
	# return []

# def estChamp(fichier, champ):
	#is_target_in_list = target_string_lower in (string.lower() for string in list_of_strings)
	# if ( champ.upper().lower() in (s[0].lower() for s in listeChamps(fichier)) ):
		# return True
	# return False
	
# def listeChamps(fichier):
	# if not isfile(fichier):
		# print("Fichier de poids des postes "+fichier+" manquant : STOP")
		# exit(0)
	
	# with fiona.open(fichier, "r") as shapefile:
		# champs = shapefile.schema["properties"].items()
		# shapefile.close()
		# return champs
	# return []

def rasteriseShapeFile(fichier, inras, outras, field):

	if not isfile(fichier):
		print("Fichier shapefile "+fichier+" manquant : STOP")
		exit(0)
		
	if (not estChamp(fichier, field)):
		print(field+" n'est pas un champ de "+fichier+"  STOP")
		exit(0)

	if not isfile(inras):
		print("Fichier raster "+inras+" manquant : STOP")
		exit(0)
		
	print("ATTENTION VERIFIER LES FICHIERS SHAPE ! IL EST PREFERABLE QU'ILS NE SOIENT PAS 'MULTIPART'")
	print("IL PEUT AUSSI RESTER DE L'INFORMATION INVISIBLE ISSUE D'ANCIENS CROISEMENTS (OU SUPPRESSION DE POLYGONES) PAR EXEMPLE")
	print("ATTENTION AUX SHAPE AVEC DES TROUS ! IL RISQUE D'AFFECTER DES VALEURS ARBITRAIRES")
	print("VERIFIER SOIGNEUSEMENT LE RASTER EN SORTIE")

	if not (raw_input("Continuer (y/n) ?") == "y"):
		exit(0)
	
	burned = np.zeros(shape=(1,1,1))
	if (compareShapeFileEtRasterExtend(fichier, inras)):
	
		fi=inras.split("/")[-1]
		chem=inras.split(fi)[0]

		tmprast=chem+"tmp.tif"
		if isfile(tmprast) :
			supprime(tmprast)
			
		print("RASTERISATION")
		with rasterio.open(inras) as src:
			kwargs = src.meta.copy()
			kwargs.update({
				'nodata':-9999,
				'dtype':'float64',   #on force le type pour produire un raster de poids
	#			'driver': 'GTiff',
	#			'compress': 'lzw'
			})
			
			with rasterio.open(tmprast, 'w', **kwargs) as dst:
				with fiona.open(fichier, "r") as shapefile:
					out_arr = src.read(1)
					# # this is where we create a generator of geom, value pairs to use in rasterizing
					
					formes = ( (feature["geometry"], float(feature["properties"][field]) ) for feature in shapefile ) #c'est float, car il s'agit du raster de poids !!!! (reel)
					burned = features.rasterize(shapes=formes, fill=-9999, default_value=-9999, out=out_arr, transform=src.transform)
					shapefile.close()
					
				sortie = np.zeros(shape=(1,dst.meta['height'],dst.meta['width']))
				sortie[0] = burned
				dst.write(sortie)
				dst.close()

			src.close()
			
		masq = masque(fichier, tmprast, outras)
		if isfile(outras):
			if isfile(tmprast):
				supprime(tmprast)
		
		return masq

	return None

def masque(fichier, inrast, outrast):
	if not isfile(fichier):
		print("Fichier shapefile "+fichier+" manquant : STOP")
		exit(0)

	if not isfile(inrast):
		print("Fichier raster "+inras+" manquant : STOP")
		exit(0)
		
	out_image = np.zeros(shape=(1,1,1))
	with rasterio.open(inrast) as src:
		kwargs = src.meta.copy()

		kwargs.update({
			'nodata':-9999,
			'dtype':'float64',
#			'driver': 'GTiff',
#			'compress': 'lzw'
		})
		
		with rasterio.open(outrast, 'w', **kwargs) as dst:
			with fiona.open(fichier, "r") as shapefile:
				print("MASQUAGE")
				formesTotales = [feature["geometry"] for feature in shapefile]
				out_image, out_transform = mask(src, shapes=formesTotales, crop=False)
				sortie = np.zeros(shape=(1,dst.meta['height'],dst.meta['width']))
				sortie[0] = out_image
				dst.write(sortie)
				src.close()
				shapefile.close()
				dst.close()
				rasttmp = out_image[ out_image <> dst.meta['nodata'] ]
				print("MASQUED : MIN="+str(np.amin(sortie[0]))+" MAX="+str(np.amax(sortie[0]))+" MOY="+str(np.average(sortie[0])))

	return out_image


def rasteriseShapeFileInitial(fichier, outrast, resol):

	if not isfile(fichier):
		print("Fichier shapefile "+fichier+" manquant : STOP")
		exit(0)


	burned = np.zeros(shape=(1,1,1))
	l93= "+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
	

	with fiona.open(fichier, "r") as shapefile:
		xUL=shapefile.bounds[0]
		yUL=shapefile.bounds[3]
		xLR=shapefile.bounds[2]
		yLR=shapefile.bounds[1]
		
		transforme =  Affine.translation(xUL - (resol / 2), yUL - (resol / 2) ) * Affine.scale(resol, - resol)
		H = int((yUL-yLR)/resol)
		W = int((xLR-xUL)/resol)
		if (H<=0 or W<=0):
			print("ATTENTION, valeur negative de H="+str(H)+" ou W="+str(W)+" : STOP")
			shapefile.close()
			exit(0)
			
		with rasterio.open(
			outrast,
			'w',
			driver='GTiff',
			height=H,
			width=W,
			count=1,
			dtype=rasterio.float64,
			crs=l93,
			transform=transforme,
			nodata=0
			) as dst:

			# # this is where we create a generator of geom, value pairs to use in rasterizing
			print("RASTERISATION")
			formes = ( (feature["geometry"], 1.0) for feature in shapefile )
			burned = features.rasterize(shapes=formes, fill=0, default_value=0, out_shape=(H,W), transform=transforme)

			sortie = np.zeros(shape=(1,dst.meta['height'],dst.meta['width']))
			sortie[0] = burned
			dst.write(sortie)
			
			shapefile.close()
			dst.close()

	return burned


	
def compareShapeFileEtRasterExtend(fichier, inras):
	if not isfile(fichier):
		print("Fichier shapefile "+fichier+" manquant : STOP")
		return False

	if not isfile(inras):
		print("Fichier raster "+inras+" manquant : STOP")
		return False

	with fiona.open(fichier, "r") as shapefile:
		with rasterio.open(inras) as src:

			if ( src.bounds.left>shapefile.bounds[2] or src.bounds.right < shapefile.bounds[0] or  src.bounds.top < shapefile.bounds[1] or src.bounds.bottom > shapefile.bounds[3]):
				print("Raster bounds    : "+str(src.bounds))
				print("Shapefile bounds : "+str(shapefile.bounds))
				print("Erreur : le raster de reference "+inras+" n'est pas recouvert par le shapefile "+fichier)
				shapefile.close()
				src.close()
				return False
				
			if ( src.bounds.left < shapefile.bounds[0] or src.bounds.right > shapefile.bounds[2] or  src.bounds.top > shapefile.bounds[3] or src.bounds.bottom < shapefile.bounds[1]):
				dx=0
				if (src.bounds.left - shapefile.bounds[0]) < 0 : 
					dx = shapefile.bounds[0] - src.bounds.left
				if (shapefile.bounds[2] - src.bounds.right) < 0 :
					dx += (src.bounds.right - shapefile.bounds[2])
				txdx = ( dx / float(src.bounds.right - src.bounds.left)) * 100.0
				dy=0
				if (src.bounds.top - shapefile.bounds[3]) > 0:
					dy=src.bounds.top - shapefile.bounds[3]
				if (src.bounds.bottom - shapefile.bounds[1]) < 0:
					dy+=(shapefile.bounds[1] - src.bounds.bottom)
				txdy = ( dy / float(src.bounds.top - src.bounds.bottom)) * 100.0
				
				print("Raster bounds    : "+str(src.bounds))
				print("Shapefile bounds : "+str(shapefile.bounds))
				print("Decalage en X :"+str(txdx)+"%  Decalage en Y :"+str(txdy)+"%")
				
				if not (raw_input("WARNING (outils.py:rasterize):  le raster de reference "+inras+" n'est que partiellement recouvert par le shapefile "+fichier+")! Continuer (y/n) ?") == "y"):
					shapefile.close()
					src.close()
					return False

			return True


def bufferRasterDistance(fichier, outfi, distance=50):
	fichier = chercheFichierTiff(fichier)
	tmpdist = radical(fichier)+"tmpdist.tif"
	print("Calcul du raster de distance total "+tmpdist)
	distanceGDAL(fichier, tmpdist)
	lst = litFichierTiff(tmpdist)
	raster = lst[0]
	outrast = np.zeros( shape = (lst[2], lst[1]) )
	outrast[ raster <= distance ] = raster[ raster <= distance ]
	outrast[ raster > distance ] = lst[10]
	genereTiff(outrast, outfi, listeparams = lst)

def maximumRasters(fichier1, fichier2, outfi):
	lst1 = litFichierTiff(fichier1)
	lst2 = litFichierTiff(fichier2)
	raster1 = lst1[0]
	raster2 = lst2[0]
	outrast = np.zeros( shape=(lst1[2], lst1[1]) )
	outrast = np.maximum(raster1, raster2)
	genereTiff(outrast, outfi, listeparams = lst1)

def miseAUn(fichier1, fichier2, outfi):
	lst1 = litFichierTiff(fichier1)
	lst2 = litFichierTiff(fichier2)
	rast1 = lst1[0]
	rast2 = lst2[0]
	outrast = np.zeros(shape=(lst1[2], lst1[1]))
	outrast = rast1
	outrast[ rast2 > 0 ] = 1
	genereTiff(outrast, outfi, modeletif=fichier1)

def metNoDataAZero(fichier, outfi, nodata=-9999):
	lst = litFichierTiff(fichier)
	rast = lst[0]
	outrast = np.zeros(shape=(lst[2], lst[1]))
	nodat=nodata
	try:
		nodat=float(lst[10])
		if (nodat != nodata):
			if not (raw_input("Confirmez nodata :"+str(nodata)+" (y/n)?")):
				exit(0)
	except:
		pass
	outrast=rast
	outrast[rast==nodat]=0
	genereTiff(outrast, outfi, modeletif=fichier)
	
def upDateTiffSup0(fichier, updatefi, outfi):
	lesInputs = rabotePartieCommuneRaster([fichier, updatefi])
	outrast=lesInputs[0][0]
	outrast[ (lesInputs[1][0]>0) ] = lesInputs[1][0][ (lesInputs[1][0] >0) ]
	xul=lesInputs[0][4]
	yul=lesInputs[0][5]
	resol=lesInputs[0][10]
	genereTiff(outrast, outfi, xul, yul, resol)
	
def upDateNotNoData(fichier, updatefi, outfi, nodata=-9999):
	lst = litFichierTiff(fichier)
	rast = lst[0]
	outrast = np.zeros(shape=(lst[2], lst[1]))
	lst2 = litFichierTiff(udatefi)
	urast=lst2[0]
	nodat=nodata
	try:
		nodat=float(lst2[10])
		if (nodat != nodata):
			if not (raw_input("Confirmez nodata :"+str(nodata)+" (y/n)?")):
				exit(0)
	except:
		pass
	outrast=rast
	outrast[urast!=nodat]=urast[urast!=nodat]
	genereTiff(outrast, outfi, modeletif=fichier)
	
#version avec les windoows
		# windows = src.block_windows(1)
		# with rasterio.open(outras, 'w', **kwargs) as dst:
			# with fiona.open(fichier, "r") as shapefile:
			
				# if ( src.bounds.left>shapefile.bounds[2] or src.bounds.right < shapefile.bounds[0] or  src.bounds.top < shapefile.bounds[1] or src.bounds.bottom > shapefile.bounds[3]):
					# print("Raster bounds    : "+str(src.bounds))
					# print("Shapefile bounds : "+str(shapefile.bounds))
					# print("Erreur : le raster de reference "+inras+" n'est pas recouvert par le shapefile "+fichier)
					# shapefile.close()
					# dst.close()
					# src.close()
					# exit(0)
				# if ( src.bounds.left < shapefile.bounds[0] or src.bounds.right > shapefile.bounds[2] or  src.bounds.top > shapefile.bounds[3] or src.bounds.bottom < shapefile.bounds[1]):
					# print("Raster bounds    : "+str(src.bounds))
					# print("Shapefile bounds : "+str(shapefile.bounds))
					# if not (raw_input("WARNING (outils.py:rasterize):  le raster de reference "+inras+" n'est que partiellement recouvert par le shapefile "+fichier+")! Continuer (y/n) ?") == "y"):
						# shapefile.close()
						# dst.close()
						# src.close()
						# exit(0)
						
				# print(dst.meta['dtype'])
				# print(type(int('13280')))
				# for idx, window in windows:					#windows est suelement une histoire de pixels (pas de georef)!
					# out_arr = src.read(1, window=window)
					# #this is where we create a generator of geom, value pairs to use in rasterizing
					# formes = ( (feature["geometry"], long(feature["properties"][field]) ) for feature in shapefile )
					# #shapes = ((geom,value) for geom, value in zip(shapefile["geometry"], shapefile[field]))		#pour acceder au field
					# burned = features.rasterize(shapes=formes, fill=0, out=out_arr, transform=src.transform)
					# #burned = features.rasterize(shapes=formes, fill=0, out_shape=osh, transform=src.transform)
					# #burned = features.rasterize(shapes=formes, fill=0, out_shape=osh, transform=src.transform)
					# print(src.transform)
					# print("Out array:")
					# #print(out_arr)
					# print("BURNED:")
					# #print(burned)
					# #dst.write_band(1, burned, window=window)

	#return burned