import sys, csv
from os import rename, remove, rmdir, listdir
from glob import glob
from zipfile import ZipFile
from shutil import copy, rmtree
from os.path import isfile, isdir
import numpy as np
import random


def isDigit(x):
	try:
		float(x)
		return True
	except ValueError:
		return False
		
def yesno(question):
	while "the answer is invalid":
		reply = str(input(question+' (y/n): ')).lower().strip()
		if reply[:1] == 'y':
			return True
		if reply[:1] == 'n':
			return False

def extension(fichier, ext):
	if (len(ext)<=0):
		return fichier
	if (ext.strip() == '.'):
		return fichier
	if (ext.strip()[0] != '.'):
		ext = '.'+ext.strip()

	d = depioteNomFichier(fichier)
	if ( ext.lower().strip() == ('.'+d[2]).lower().strip() ):
		return fichier

	if (len(d[0]) > 0):
		return d[0]+"/"+d[1]+ext
	else:
		return d[1]+ext

	return fichier

def depioteNomFichier(fichier):
	fichier=fichier.replace("\\", "/")
	fich = fichier.split("/")[-1]
	chem = fichier.split(fich)[0]
	rad=fich
	ext=""
	if (fich.find('.')>0 and fich.find('.')<(len(fich)-1)):
		ext = fich.split(".")[-1]
		rad = fich[0:fich.rfind(ext)]
	return chem, rad, ext
	
def zippage(radical):
	liste = glob( radical+"*" )
	with ZipFile(radical+'.zip', 'w') as zipObj2:
		for fi in liste:
			zipObj2.write(fi)