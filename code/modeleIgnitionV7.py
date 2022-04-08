import rasterio, importlib, sys
#sys.path.append('B:/Perso/Etudes/MEDSTAR-INTERMED/ModeleRisque/ArcPy/')
sys.path.append('S:/ali.sayer/EMR.mod/WS/')
import parametres as param
p = importlib.import_module(param.scenario, package=None)

import rasterio
import numpy as np
from os.path import isfile
from os import remove
from outils import normalisation, genereTiff, litFichierTiff, rabotePartieCommuneRaster

chem=""
ignitionsConstantes=["igniSurBati", "igniSurRoutes"]
try:
	x=0
	tableFacteurs = p.facteursIgnition; x+=1
	chem=param.ws; x+=1
	chemTables=param.chemTables; x+=1
	carteIgnition=chem+param.carteIgnition; x+=1
	ignitionsConstantes=param.ignitionsConstantes
	
	print("Ignition: param ok")
	
except Exception:
	print("Ignition: Erreurs parametres "+str(x))
	exit()

#if (reclassePoidsIgnition()):
lesFacteurs = []
lesRasters=[]
nodata=-9999

nk=0
table=chemTables+tableFacteurs
if (tableFacteurs.find("=")>0):
	table=chemTables+ ( tableFacteurs.split("=")[0] )
	nk=int(tableFacteurs.split("=")[1])

k=0
if not isfile(table):
	print("Erreur lecture de la table de modele "+table)
	exit(0)
	
ok=True
if (isfile(carteIgnition)):
	ok=False
	if (raw_input(carteIgnition+" existe deja : la remplacer (y/n) ?") == "y"):
		remove(carteIgnition)
		ok=True
if (not ok):
	exit(0)

with open(table, "r") as filin:
	for ligne in filin:
		nom = ligne.split("=")[0]
		if (len(ligne.split("=")) > 1):
			nbandes=0
			sw=ligne.split("=")[1]
			txt=""
			if (len(ligne.split("=")) > 2):
				txt=sw
				sw = ligne.split("=")[2]
			w=float(sw)
			
			fichier = chem+nom+".tif"
			lesRasters.append(fichier)
			lesFacteurs.append( (fichier, w, txt) )
			print("Input "+str(k+1)+"  "+nom+"  w="+str(w)+"    "+txt)
			k+=1
		else:
			print("Attention absence de poids pour "+nom+" dans le fichier table "+table)
			exit(0)
				
	filin.close()
	if (k != nk):
		print("Le modele d'ingnition doit comporter "+str(nk)+" facteurs dans la table "+table)
		exit(0)

lesInputs = rabotePartieCommuneRaster(lesRasters)
#	[0]=rast  [1]=min	[2]=max	[3]coef
xUL=lesInputs[0][4]
yUL=lesInputs[0][5]
xLR=lesInputs[0][6]
yLR=lesInputs[0][7]
w=lesInputs[0][8]
h=lesInputs[0][9]
resol=lesInputs[0][10]
k=0
for inp in lesInputs:
	if (inp[4] != xUL):
		print("Erreur facteur"+str(k)+" xUL="+str(xUL)+" != "+str(inp[4]))
	if (inp[5] != yUL):
		print("Erreur facteur"+str(k)+" yUL="+str(yUL)+" != "+str(inp[5]))
	if (inp[6] != xLR):
		print("Erreur facteur"+str(k)+" xLR="+str(xLR)+" != "+str(inp[6]))
	if (inp[7] != yLR):
		print("Erreur facteur"+str(k)+" yLR="+str(yLR)+" != "+str(inp[7]))
	if (inp[8] != w):
		print("Erreur facteur"+str(k)+" W="+str(w)+" != "+str(inp[8]))
	if (inp[9] != h):
		print("Erreur facteur"+str(k)+" H="+str(h)+" != "+str(inp[9]))
	if (inp[10] != resol):
		print("Erreur facteur"+str(k)+" resol="+str(resol)+" != "+str(inp[10]))
	k+=1
		
print("Caclul ignition -> "+carteIgnition)

if (ok):#			[0]=rast			[1]=min			[3]coef(1/(max-min)		w
	outrast = ( ( lesInputs[0][0] - lesInputs[0][1] ) * lesInputs[0][3] * lesFacteurs[0][1] ) + \
			  ( ( lesInputs[1][0] - lesInputs[1][1] ) * lesInputs[1][3] * lesFacteurs[1][1] ) + \
			  ( ( lesInputs[2][0] - lesInputs[2][1] ) * lesInputs[2][3] * lesFacteurs[2][1] ) + \
			  ( ( lesInputs[3][0] - lesInputs[3][1] ) * lesInputs[3][3] * lesFacteurs[3][1] ) + \
			  ( ( lesInputs[4][0] - lesInputs[4][1] ) * lesInputs[4][3] * lesFacteurs[4][1] ) + \
			  ( ( lesInputs[5][0] - lesInputs[5][1] ) * lesInputs[5][3] * lesFacteurs[5][1] ) + \
			  ( ( lesInputs[6][0] - lesInputs[6][1] ) * lesInputs[6][3] * lesFacteurs[6][1] )
			  
	outrast = ( lesInputs[0][0] * lesFacteurs[0][1] ) + \
			  ( lesInputs[1][0] * lesFacteurs[1][1] ) + \
			  ( lesInputs[2][0] * lesFacteurs[2][1] ) + \
			  ( lesInputs[3][0] * lesFacteurs[3][1] ) + \
			  ( lesInputs[4][0] * lesFacteurs[4][1] ) + \
			  ( lesInputs[5][0] * lesFacteurs[5][1] ) + \
			  ( lesInputs[6][0] * lesFacteurs[6][1] )
	
	rastCte=[]
	for th in ignitionsConstantes:
		rastth = litFichierTiff(th)[0]
		outrast[rastth > 0] = rasth[rastth > 0]
		rastCte.append(rastth)
	
	genereTiff(outrast, chem+"ignitionNotNorm.tif", xUL, yUL, resol)
	outrastnorm = normalisation(outrast)
	
	for rastth in rastCte:
		outrastnorm[rastth > 0] = rastth[rastth > 0]
	
	genereTiff(outrastnorm, chem+"ignitionNorm.tif", xUL, yUL, resol)


	
	
##		leschamps = [item, ]
##		with arcpy.da.UpdateCursor(themeIn, lesChampsDates+lesIndicesDates ) as curseur:
##			for row in curseur:
	

##
##	lesChampsDates = []
##	lesIndicesDates = []
##	combustible = "comb"+str(date)
##	for ch in lesChamps:
##		lesChampsDates.append(ch+str(date))
##	i=0
##	for ind in lesIndicesLocaux:
##		champ = ind+str(date)
##		lesIndicesDates.append(champ)
##		print("Ajoute champ "+str(i)+"  "+champ)
##		ajouteChamp(themeIn, champ, "DOUBLE")
##		i+=1
##		#lesChamps = [ "fVi", "fBi", "fVRi", "fRi", "fVe", "fBe", "fVp", "fBp", "fOLDp", "fVipl", "fBipl", "fBelu", "fBdeb", "comb" ]
##		#				0	  1	   2	  3	  4	  5	  6	  7	   8		9		10	   11	   12	   13
##		#lesIndicesLocaux = [ "EAI", "EAE", "EPPL", "EAPLi", "EIPL", "EELU", "EDEM", "EAL", "EVUL" ]
##		#					   14	 15	 16	  17	  18	  19	   20	21	  22
##			
##		#EAI = (1/50) * [  [( wVi * fVi )* ( wBi  * fBi )]+[ (wVRi  * fVRi )* (wRi  * fRi )] ]
##		#EAE = AI * (1/7.5) * ( wVe *fVe )* ( wBe * fBe ) * (wSLe * nSL) * (wW * WSP * WANGLE) 
##		#EAPi = AE * (1/10.5) * ( wVp * fVp )*( wOLDp * fOLDp )* ( wBp  * fBp) )
##		#EPPs = (1/10.5) * ( wVp * fVp )*( wOLDp * fOLDp ) * ( wBp * fBp))
##		#EIPL = (1/12.5) * ( wVipl * fVipl ) * ( wBipl  * fBipl)
##		#EELU = IPL *  1/5 (fBelu)
##		#EDEM = 1/5 * ( fBdeb )
##		#EAlocal = AE * IPL
##		#EVUL = EDEM * EELU
##
##		#NON CALCULABLES
##		#EAs = (1/2) * [ ( EAE * EIPL ) + EPPs ]
##		#Rs =  (1/2) * [ ( EAE * EIPL ) + EPPs ] * [ EDEM * EELU ]
##		
##	print(str(lesChampsDates+lesIndicesDates))
##
##	print("Calcul de l'alea d'ignition...")
##	print("Ignition :  wBi="+ str(p.wBi) + " wRi="+str(p.wRi) + "  wNi="+str(p.wVi) )
##	
##	maxeai = ( ( p.wBi * 5.0 * 5.0  ) + ( p.wRi  * 5.0 * 5.0 ) + ( 5.0 * 5.0 * p.wNi ) )
##
##
##	lesMaxi = [ maxeai, maxeae, maxepps, maxeapli, maxeipl, maxeelu, maxedem, maxeal, maxevul  ]
##	lesMax = [0 , 0 , 0 , 0 ,0 , 0 ,0 ,0 ,0 ]
##	with arcpy.da.UpdateCursor(themeIn, lesChampsDates+lesIndicesDates ) as curseur:
##			for row in curseur:
##					r=14
##					fcomb = row[13] ; fVi = row[0] ; fBi = row[1] ; fRi=row[3] ; fVRi = row[2] ; fVNi = row[0]
##					eai = fcomb * ( ( p.wBi * fBi * fVi  ) + ( p.wRi  * fRi * fVRi ) + ( 5 * fVNi * p.wNi ) ) / maxeai
##					if (eai > 1 or eai < 0):
##						print("eai="+str(eai)+" fcomb="+str(fcomb)+" wBi="+str(p.wBi)+" fVi="+str(fVi)+" fBi="+str(fBi)+"  wRi="+str(p.wRi)+" fVRi="+str(fVRi)+" fRi="+str(fRi)+"  fVNi="+str(fVNi)+" wNi="+str(p.wNi))
##						exit(0)
##					if (eai > lesMax[0]):
##						lesMax[0] = eai
##					row[r] = eai #
##					r+=1
##
##					fVe = row[4] ; fBe = row[5]
##					eae = eai * ( ( p.wVe * fVe ) - ( p.wBe * fBe ) ) / maxeae
##					if (eae < 0):
##						eae = 0
##					if (eae > 1):
##						print("eae="+str(eae)+" eai="+str(eai)+" wVe="+str(p.wVe)+" fVe="+str(fVe)+" fBe="+str(fBe)+" wBe="+str(p.wBe))
##						exit(0)
##					if (eae > lesMax[1]):
##						lesMax[1] = eae
##					row[r] = eae #
##					r+=1
##
##					fVp = row[6] ;  fBp = row[7] ; fOLDp = row[8]
##					epps = ( ( p.wVp * fVp ) + ( p.wOLDp * fOLDp ) - ( p.wBp  * fBp ) ) / maxepps
##					if (epps < 0):
##						epps = 0
##					if (epps > 1):
##						print("epps="+str(epps)+" wVp="+str(p.wVp)+" fVp="+str(fVp)+" wOLDp="+str(p.wOLDp)+" fOLDp="+str(fOLDp)+" wBp="+str(p.wBp)+" fBp="+str(fBp))
##						exit(0)
##					if (epps > lesMax[2]):
##						lesMax[2] = epps
##					row[r] = epps #
##					r+=1
##					
##					eapli = (eae * epps) / maxeapli
##					if (eapli > 1 or eapli < 0):
##						print("eapi="+str(eapli)+" eae="+str(eae)+" epps="+str(epps))
##						exit(0)
##					if (eapli > lesMax[3]):
##						lesMax[3] = eapli
##					row[r] = eapli  #EAPi : alea de propagation local induit
##					r+=1
##
##					fVipl =row[9] ; fBipl = row[10]						 
##					eipl = ( ( p.wVipl * fVipl ) - ( p.wBipl  * fBipl ) ) / maxeipl
##					if (eipl < 0):
##						eipl = 0
##					if (eipl > 1):
##						print("eipl="+str(eipl)+" wVipl="+str(p.wVipl)+" fVipl="+str(fVipl)+" fBipl="+str(fBipl)+" wBipl="+str(p.wBipl))
##						exit(0)
##					if (eipl > lesMax[4]):
##						lesMax[4] = eipl
##					row[r] = eipl #
##					r+=1
##					
##					fBelu = row[11]	
##					eelu = ( eipl * fBelu ) / maxeelu
##					if (eelu > 1 or eelu < 0):
##						print("eelu="+str(eelu)+" eipl="+str(eipl)+" fBelu="+str(fBelu))
##						exit(0)
##					if (eelu > lesMax[5]):
##						lesMax[5] = eelu
##					row[r] = eelu #
##					r+=1
##					
##					fBed = row[12]
##					edem = fBed / maxedem
##					if (edem > 1 or edem < 0):
##						print("edem="+str(edem)+" fBed="+str(fBed))
##						exit(0)
##					if (edem > lesMax[6]):
##						lesMax[6] = edem
##					row[r] = edem #
##					r+=1
##					
##					eal = (eae * eipl) / maxeal
##					if (eal > 1 or eal < 0):
##						print("eal="+str(eal)+" eae="+str(eae)+"  eipl="+eipl)
##						exit(0)
##					if (eal > lesMax[7]):
##						lesMax[7] = eal
##					row[r] = eal #
##					r+=1
##
##					evul = (eelu * edem)
##					if (evul > 1 or evul < 0):
##						print("eelu="+str(eelu)+" edem="+str(dem)+"  evul="+evul)
##						exit(0)
##					if (evul > lesMax[8]):
##						lesMax[8] = evul
##					row[r] = evul #
##					r+=1
##
##					#Attention, il faut calculer l'alea de propagation total par continuum (propagation.py) pour calculer l'alea subi
##					#Attention, il faut calculer la somme des enjeux par continuum (sommeVulnerabilite.py) pour calculer le risque induit
##					
####					eas = ( eal + eap) / maxeas
####					if (eas > 1 or eas < 0):
####						print("eas="+str(eas)+" eal="+str(eal)+"  epps="+epps)
####						exit(0)
####					if (eas > lesMax[8]):
####						lesMax[8] = eas
####					row[21] = eas #
####
####					rs = ( eas * edem * eelu )
####					if (rs > 1 or rs < 0):
####						print("eas="+str(eas)+" eas="+str(eas)+" edem="+str(edem)+"  eelu="+eelu)
####						exit(0)
####					if (rs > lesMax[9]):
####						lesMax[9] = rs
####					row[22] = rs #
##
##					curseur.updateRow(row)			
##	del curseur
##
##	k=0
##	for maxi in lesMaxi:
##
##		maxu = lesMax[k]
##		if (maxu > maxi):
##			print("Erreur de max : max calc = "+str(maxu)+" > max autor = "+str(maxi)+" pour k="+str(k))
##			exit(0)
##		if (maxu < maxi):
##			print("WARNING de max : max calc = "+str(maxu)+" < max autor = "+str(maxi)+" pour k="+str(k)+". NORMALISATION DE CE CHAMP REQUISE")
##		k+=1
##
##	
###normalisation sur toute la serie de dates (comparabilite interdates)
##normalisation.normalise(themeIn, lesIndicesLocaux, dates)
##
###Somme des indices sommables (propagation et vulnerabilite
##for ind in lesIndicesSommes:
##	for date in dates:
##		sommeSurConti.sommeSurContinuum()(themeIn, ind, date)
##
###Normalisation des indices Totaux
##lesIndicesTotaux = []
##for ind in lesIndicesSommes:
##	lesIndicesTotaux.append(ind+"Tot")		   #Tot est un intercal intercale par sommeSurContinnuum pour generer le nom de champ en sortie
##	
##normalisation.normalise(themeIn, lesIndicesTotaux, dates)
##
###Dans la partie suivante, ce ne sont pas les indices normalises qui sont utilises, mais les indices bruts
##
##for date in dates:
##	lesIndicesTotauxDates = []
##	for ind in lesIndicesTotaux:
##		champ = ind+str(date)
##		lesIndicesTotauxDates.append(champ)
##		
##	lesIndicesSubisInduitsDates = []
##	i=0
##	for ind in lesIndicesSubisInduits:
##		champ = ind+str(date)
##		lesIndicesSubisInduitsDates.append(champ)
##		print("Ajoute champ "+str(i)+"  "+champ)
##		ajouteChamp(themeIn, champ, "DOUBLE")
##		i+=1
##		
##	lesIndicesLocauxDates = []	
##	for ind in lesIndicesLocaux:
##		champ = ind+str(date)
##		lesIndicesLocauxDates.append(champ)
##		
##	#lesIndicesLocaux = [ "EAI", "EAE", "EPPL", "EAPLi", "EIPL", "EELU", "EDEM", "EAL", "EVUL" ]
##	#					   0	 1	   2	   3		4		5	  6	   7	  8
##	#lesIndicesTotauxDates = ["EAPLiTot", "EVULTot" ]
##	#							 9		   10
##	#lesIndicesSubisInduits = [  "EAs", "Rs",  "Ri",  "Rt" ]
##	#							  11	 12	 13	14
##	
##	with arcpy.da.UpdateCursor(themeIn, lesIndicesLocauxDates + lesIndicesTotauxDates + lesIndicesSubisInduitsDates ) as curseur:
##		for row in curseur:
##			aleas = row[7] + row[9]
##			row[11] = aleas
##			rs = aleas * row[8]
##			row[12] = rs
##			ri = row[10] * row[3]
##			row[13] = ri
##			rt = rs + ri
##			row[14] = rt
##			curseur.updateRow(row)
##			
##	del curseur
##
##normalisation.normalise(themeIn, lesIndicesSubisInduits, dates)
