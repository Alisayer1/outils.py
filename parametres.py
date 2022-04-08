ws="B:/Perso/Etudes/MEDSTAR-INTERMED/ModeleRisque/WS/" #repete dans prepareDonneesLineaires
chemTables="B:/Perso/Etudes/MEDSTAR-INTERMED/ModeleRisque/TablesScenarStd/"
scenario="scenarstd"

resol=10

refrast = ws+"zone.tif"
contours=ws+"contours.shp"
srcStd="BDTOPO"
igni="igni"
champPoids="w"
srcIgni=srcStd

raddebrou="debrou"+srcStd
radvf="Vf"+srcStd
radrte="Rte"+srcStd
radbati="Bati"+srcStd
champPoidsIgni=champPoids+"-"+igni   #w-igni

carteIgnition="ignition.tif"

ignitionsConstantes=["igniSurBati", "igniSurRoutes"]
