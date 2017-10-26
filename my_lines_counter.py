
#!/usr/bin/env python

import re


def get_file_list(dir,file_list):
	try:
		new_dir = dir
		if os.path.isfile(dir):
			file_list.append(dir)
		elif os.path.isdir(dir):
			for s in os.listdir(dir):
				if not s[0].isdigit() and not s[0].isalpha():
					logger.warning("Hidden file:%s"%(s))
					if s != '.':
						continue
				new_dir = os.path.join(dir,s)
				get_file_list(new_dir,file_list)
		else:
			pass
	except Exception as e:
		print("e:",e)
	return file_list
################get_file_list####################



def single_file_line_count(file, d_result):
	with open(file, "r") as fobj:
		file_line_nbr = 0
		while True:
			buff = fobj.readline()
			file_line_nbr += 1
			#if buff == "" or buff == '\r\n':
			if buff == "":
				#print "broke!"
				break
			else:
				# Remove the part before the file name (first word)
				#Get the second part in the line which will be the log time in general, 
				#and judge whether it is the tim
				if len(buff.split(" ")) > 1:
					log_time = buff.split(" ")[1]
					if re.search(r'\b\d\d:\d\d:\d\d\b',log_time):
						tmp = re.findall(r'\b[a-zA-Z]',buff)[0]
						remove = buff.split(tmp)[0]
						remove_byte = len(remove)
						real_line = buff[remove_byte:].rstrip('\n')
						if d_result.has_key(real_line):
							d_result[real_line] += 1
						else:
							d_result[real_line] = 1
				else:
					#for windows \r\n when read mode is 'rb':
					real_line = buff.rstrip('\n')
					if d_result.has_key(real_line):
						d_result[real_line] += 1
					else:
						d_result[real_line] = 1	


def files_lines_count(path_list, top_rank = 5):

	#print "files_lines_count start, path_list=",path_list
	d_result = {}
	all_file_list = []
	for pa in path_list:
		file_list = get_file_list(pa,[])
		all_file_list.extend(file_list)
	file_line_nbr = 0
	for file in all_file_list:
		try:
			single_file_line_count(file, d_result)
		except Exception as e:
			#logger.error(e)
			print("DEBUG: Error Line Number in file: ", file_line_nbr)
			print ("DEBUG: Here: ", e)
	l_result = sorted(d_result.iteritems(), key=lambda d:d[1], reverse = True)
	return l_result[:top_rank]

if __name__ == '__main__':
	path_list = [[r"D:/Trace/realtime/20170401_021107_20170401_021119_1.3.6_OCPR_[3]_3.rtrc_backup.out",\
	"D:/Trace/realtime/20170401_023222_20170401_023657_1.3.6_SCPR_[1]_1019.rtrc_backup.out"]]

	'''file_list = [r"D:/Trace/mxpf/common/20170504_084349_20170504_141345_1.3.10_SUP.mxtrc", \
	"D:/Trace/mxpf/common/20170214_203135_20170504_110213_1.3.3_DOF.mxtrc", \
	"D:/Trace/mxpf/common/20170504_063254_20170504_135748_1.3.1_CPI1.mxtrc"]
	'''

	#file_list = [r"D:/Trace/realtime/test.txt"]

	top_rank = 5
	result = files_lines_count(path_list, top_rank)	
	print("Top repeat log rank: ")
	for r in result:
		print r


	print "Finished"