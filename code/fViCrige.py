from outils import estChamp, rasteriseShapeFile, litFichierTiff, rasteriseShapeFileInitial, reclasseTable
from outilsVecteurs import clippe
from os.path import isfile

#scipy.ndimage.uniform_filter
#import matplotlib.pyplot as plt
#import numpy as np
#from collections import Counter
#from scipy.ndimage import uniform_filter

resol=10
chem="S:/ali.sayer/EMR.mod/ModeleRisque/WS"
crige2014="Z:/02_OccupationDuSol/2.2.Crige/Crige_2014/OCSOL_2014/BDOCSOL_2014/DONNEES/OCSOL_2014_Paca_L93.shp"
contours=chem+"contours.shp"
shos=chem+"oscrige94.shp"
table = chem+"fViCrige.tab"
fViCrige=chem+"fViCrige.tif"

champ = "NIV3_14"
outrastos = chem+"os2014.tif"
refrast = chem+"zone.tif"

if not isfile(shos):
	clippe(crige2014, contours, shos)

if not isfile(refrast):
	rasteriseShapeFileInitial(contours, refrast, resol)

if not isfile(outrastos):
	if ( estChamp(shos, champ) ) :
		rasteriseShapeFile(shos, refrast, outrastos, champ)
	else:
		print(field +" absent de "+shp)

if not isfile(fViCrige):
	fvi = reclasseTable(outrastos, table)

normalisation(fvi)
genereTiff(fvi, fViCrige)
litFichierTiff(fViCrige)
