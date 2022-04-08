from outils import rasteriseShapeFile, litFichierTiff, rasteriseShapeFileInitial, litValeursRaster, genereTiff, normalisation
from outilsVecteurs import  verifieValeurTable, reclasseChampTable, renameShapeFile, testeShapeFile, estChamp
from os.path import isfile
from scipy.ndimage import convolve
import numpy as np

racine="oscrige94i"
chem="B:/Perso/Etudes/MEDSTAR-INTERMED/ModeleRisque/WS/"
radical=chem+racine

refrast = chem+"zone.tif"
contours=chem+"contours.shp"
outrast = radical+".tif"

shploc= radical+".shp"
table = chem+"f"+racine+".tab"
outtif=chem+"f"+racine+".tif"
champOri="NIV3_14"
champPoids="w-igni"

print("Reclassification du champ "+champOri+ " creation du champ des poids "+champPoids+" dans "+shploc)
if not estChamp(shploc, champPoids):
	if (verifieValeurTable(shploc, champOri, table)):
		reclasseChampTable(shploc, champOri, champPoids, table)
		
#POSSIBLE ECHEC A PARTIR d'un trop grand nombre de batis (>900000 sur le Var par exemple, echec dans lecriture du SHX)
print("Test du shapefile "+shploc)
while not testeShapeFile(shploc): #testeShapeFile verifie que le shapefile shploc ne soit pas corrompu
	ext = shploc.split(".")[-1]
	ext="."+ext
	newfile = shploc.split(ext)[0]+"_packed.shp"
	if (testeShapeFile(newfile)):
		if (existeShapeFile(shploc)):
			renameShapeFile(shploc)
			renameShapeFile(newFile, shploc)
	else:
		print(shploc+" soit inexistant soit probablement corrompu. Pas de fichier de recuperation "+newfile+" trouve - STOP")
		exit(0)
print
print("Rasterisation de "+shploc)
if not isfile(outrast):
	if ( estChamp(shploc, champPoids) ) :
		rasteriseShapeFile(shploc, refrast, outrast, champPoids)
	else:
		print(champPoids+" absent de "+shploc)

print("Generation du raster du facteur "+outtif)
if isfile(outrast):
	tup = litFichierTiff(outrast)
	if (len(tup)>0):
		raster=tup[0]
		W = tup[1]
		H = tup[2]
		xul = tup[3]
		yul = tup[4]
		resol = tup[5]

		print("Convolve 5x5")
		weights = np.ones((5, 5))
		#voir outil.py:filtreCirculaire(dim) pour un filtre discoidal
		raster[(raster < 0)]=0
		focal_mean = convolve(raster, weights) / np.sum(weights)
		litValeursRaster(focal_mean, -9999)
		normrast = normalisation(focal_mean)
		genereTiff(normrast, outtif, xul, yul, resol)
	
litFichierTiff(outtif)