import sys
import os
import tarfile
import gzip
import zipfile
#import patoolib
from unrar import rarfile
#rarfile.UNRAR_TOOL='unrar'
import re
from my_resources import time_interval

TARGZ = '.tar.gz'
TGZ = '.tgz'
TAR = '.tar'
GZ = '.gz'
ZIP = '.zip'
RAR = '.rar'

unpack_list = ['.tar.gz','.gz','.tar','.tgz','.zip','.rar']
def detect_pack(file_name):
	'''
	check if this file is with a pack suffix
	'''
	global TARGZ
	global GZ
	global TAR
	global TGZ
	global ZIP
	global RAR


	#support upcase sufix
	file_name = file_name.lower()

	pack_category = ''
	a = re.search(r'.tar.gz$', file_name)
	g = re.search(r'.gz$', file_name)
	r = re.search(r'.tar$', file_name)
	t = re.search(r'.tgz$', file_name)
	zp = re.search(r'.zip$', file_name)
	rar = re.search(r'.rar$', file_name)

	#prevent to unpack as gz, if tar.gz or .tgz detected
	if a or t:
		g = None
	else:
		pass

	if a:
		pack_category = TARGZ
	elif t:
		pack_category = TGZ
	elif r:
		pack_category = TAR
	elif g:
		pack_category = GZ
	elif zp:
		pack_category = ZIP
	elif rar:
		pack_category = RAR
	else:
		pack_category = ''
		pass

	return (pack_category, file_name)
###############detect_pack()################


def untar_file(pack_category, file_name, delet_cpfi=False):
	global TARGZ
	global GZ
	global TAR
	global TGZ
	global ZIP
	global RAR

	S = None
	new_file = ""

	if not pack_category:
		return None
	else:
		#Bug new file is not changed due to uppercase
		#new_file = file_name.rstrip(pack_category)
		new_file = file_name[:-len(pack_category)]

	try:
		if pack_category == TARGZ:
			tar = tarfile.open(file_name,"r:gz")
			S = tar.extractall(new_file)
			tar.close()
			if delet_cpfi:
				os.remove(file_name)
	
		elif pack_category == GZ:
			if os.path.exists(new_file):
				pass
			else:
				os.mkdir(new_file)
				
			new_file_name = os.path.join(new_file,os.path.basename(new_file))
			g_file = gzip.GzipFile(file_name)  	 
			S = open(new_file_name, "wb+").write(g_file.read())
			g_file.close()
			if delet_cpfi:
				os.remove(file_name)
	
		elif pack_category == TAR:
			tar = tarfile.open(file_name)
			names = tar.getnames()  
	
			for name in names:
				S = tar.extract(name, new_file)
			tar.close()
			if delet_cpfi:
				os.remove(file_name)
	
		elif pack_category == TGZ:
			tar = tarfile.open(file_name)
			S = tar.extractall(new_file)
			tar.close()
			if delet_cpfi:
				os.remove(file_name)

		elif pack_category == ZIP:
			zip_file = zipfile.ZipFile(file_name, 'r')
			names = zip_file.namelist()
			S = zip_file.extractall(new_file)
			zip_file.close()
			if delet_cpfi:
				os.remove(file_name)
		elif pack_category == RAR:
			#rar_file = patoolib.extract_archive(file_name, outdir = new_file)
			print("DEBUG RAR start, file_name=",file_name)
			'''
			with rarfile.RarFile(file_name) as rar_file:
				print("DEBUG rar_file.namelist=",rar_file.namelist())
				rar_file.extractall(new_file)
			'''
			rar_file = rarfile.RarFile(file_name)
			names = rar_file.namelist()
			rar_file.extractall(new_file)
			rar_file.close()
			if delet_cpfi:
				os.remove(file_name)

		else:
			pass
	except Exception as e:
		print("DEBUG untar_function.py untar_file encounted an error:%s" % e)
	
	#S != 0 means NOK
	return S,new_file
#################untar_file()#############

	
if __name__ == '__main__':

	print("my unpacker")
