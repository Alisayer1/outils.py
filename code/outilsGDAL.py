import gdal
from os import system

def distanceGDAL(fichier, outrast):  
	
	src_ds = gdal.Open(fichier)
	srcband=src_ds.GetRasterBand(1)
	dst_filename=outrast
	
	drv = gdal.GetDriverByName('GTiff')
	dst_ds = drv.Create( dst_filename,
						src_ds.RasterXSize, src_ds.RasterYSize, 1,
						gdal.GetDataTypeByName('Float32'))
	
	dst_ds.SetGeoTransform( src_ds.GetGeoTransform() )
	dst_ds.SetProjection( src_ds.GetProjectionRef() )
	
	dstband = dst_ds.GetRasterBand(1)
		
	# In this example I'm using target pixel values of 100 and 300. 
	#I'm also using Distance units as GEO but you can change that to PIXELS.
	#gdal.ComputeProximity(srcband,dstband,["VALUES='100,300'","DISTUNITS=GEO"])
	
	gdal.ComputeProximity(srcband,dstband,["VALUES=1","DISTUNITS=GEO"])
	
	srcband = None
	dstband = None
	src_ds = None
	dst_ds = None

	return outrast
