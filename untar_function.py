import tarfile
import sys
import os
import gzip
import re
import sla_multi_threads as sla


unpack_list = ['.tar.gz','.gz','.tar','.tgz']

#@sla.time_interval
def untar_file(file_name, delet_cpfi=False):
	S = None
	new_file = ""
#	for file_name in file_list:
	a = re.search(r'.tar.gz$', file_name)
	g = re.search(r'.gz$', file_name)
	r = re.search(r'.tar$', file_name)
	t = re.search(r'.tgz$', file_name)
	#z = re.search(r'.zip$', file_name)
	#rar = re.search(r'.rar$', file_name')
	if a or t:
		g = None
#		print a,g, r, t		
	if a:
		new_file = file_name.rstrip(a.group(0)) 
		tar = tarfile.open(file_name,"r:gz")
		S = tar.extractall(new_file)
		tar.close()
		if delet_cpfi:
			os.remove(file_name)

	elif g:
		new_file = file_name.rstrip(g.group(0)) 
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

	elif r:
		new_file = file_name.rstrip(r.group(0)) 

		tar = tarfile.open(file_name)
		names = tar.getnames()  

		for name in names:
			S = tar.extract(name, new_file)
		tar.close()
		if delet_cpfi:
			os.remove(file_name)

	elif t:
		new_file = file_name.rstrip(t.group(0)) 
		tar = tarfile.open(file_name)
		S = tar.extractall(new_file)
		tar.close()
		if delet_cpfi:
			os.remove(file_name)

	return S,new_file

@sla.time_interval
def untar_function(filename, delet_fi=False):
	s = (None, "")
	if os.path.isfile(filename):
		s = untar_file(filename, delet_fi)
		if s[0]:
			return s
		new_file = s[1]
		if os.path.exists(new_file):
			s = untar_function(new_file, delet_fi)
			if s[0]:
				return s
	else:
		files = os.listdir(filename)
		for fi in files:
			fi_d = os.path.join(filename, fi)
			s =untar_function(fi_d, delet_fi)
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