import tarfile
import sys
import os
import gzip
import re
import sla_multi_threads as sla

TARGZ = '.tar.gz'
TGZ = '.tgz'
TAR = '.tar'
GZ = '.gz'

unpack_list = ['.tar.gz','.gz','.tar','.tgz']

#@sla.time_interval

def detect_pack(file_name):
	'''
	check if this file is with a pack suffix
	'''
	global TARGZ
	global GZ
	global TAR
	global TGZ

	pack_category = ''
	a = re.search(r'.tar.gz$', file_name)
	g = re.search(r'.gz$', file_name)
	r = re.search(r'.tar$', file_name)
	t = re.search(r'.tgz$', file_name)

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

	S = None
	new_file = ""

	if not pack_category:
		return None
	else:
		new_file = file_name.rstrip(pack_category)

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
		else:
			pass
	except Exception as e:
		print("DEBUG untar_function.py untar_file encounted an error:%s" % e)
	
	#S != 0 means NOK
	return S,new_file
#################untar_file()#############

@sla.time_interval
def untar_function(filename, delet_fi=False):
	s = (None, "")
	pack_name = ('','')
	if os.path.isfile(filename):
		pack_name = detect_pack(filename)
		if pack_name[0]:
			#progress tip put(pack_name[1])
			s = untar_file(pack_name[0],filename, delet_fi)
			if s[0]:
				return s
			new_file = s[1]
			if os.path.exists(new_file):
				s = untar_function(pack_name[0],new_file, delet_fi)
				if s[0]:
					return s
	else:
		files = os.listdir(filename)
		for fi in files:
			fi_d = os.path.join(filename, fi)
			s =untar_function(pack_name[0],fi_d, delet_fi)
	return s
	
	
if __name__ == '__main__':
	file_list = []
	abs_path = os.getcwd()
	for filename in os.listdir(abs_path):
		filename_path = os.path.join(abs_path, filename)
		file_list.append(filename_path)
#	print file_list
#	s = untar_function(file_list)
	delet_fi = True
	for file in file_list:
		s = untar_function(file, delet_fi)
	print "DEBUG result s=",s
		
	if sla.interval > 1000:
		duration = sla.interval/60.0
		ds = "%.1f minutes"%(duration)
	else:
		duration = sla.interval * 1.0
		ds = "%.1f seconds"%(duration)
	print "Finished, time used:",ds