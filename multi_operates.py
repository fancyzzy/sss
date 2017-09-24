#!/usr/bin/env python
#-*-coding=utf-8-*-

import copy
import untar_function
import my_decoder
import sla_multi_threads as sla
import os
import re
#analyse_file_type = ("rtrc","bssim","txt")

search_result = {}

def single_file_unpack(file_name, f_delete = False):
	'''
	unpack a file and generate a new file folder if
	available
	'''
	new_file = "new_file name"
	res = (None,new_file)
	res = untar_function.untar_file(file_name, f_delete)	
	return res
########single_file_unpack()#####################

def files_unpack(path_list):
	print "DEBUG files unpack started"

	unpack_list = [""]
	ln = len(path_list)
	new_path_list = copy.deepcopy(path_list)

	error = None
	for i in range(ln):
		errors = untar_function.untar_function(path_list[i])[0]
		if errors:
			print "DEBUG unpack error = ",errors
			break
		#check if this is unpack available file,
		#if it is, update the new folder into new_path_list
		for sufx in untar_function.unpack_list:
			if path_list[i].endswith(sufx):
				new_path_list[i] = path_list[i].rstrip(sufx)
				break

	return new_path_list
######################files_unpack()####################

def single_file_decode(file_name):
	my_decoder.decode_one_file(file_name)

def files_decode(path_list):

	print "DEBUG decode started"
	file_list = []
	for path in path_list:
		file_list.extend(sla.get_file_list(path,[]))

	#filter out those not necessary searched files
	sufx_list = [r".rtrc", r".rtrc_backup"]
	ln = len(sufx_list)

	for i in range(ln):
		sufx_list[i] = "({0})$".format(sufx_list[i])

	re_rule = "|".join(sufx_list)
	r = re.compile(re_rule)
	#filter out those not necessary searched files

	for file in file_list:
		if r.search(file):
			single_file_decode(file)
	#my_decoder.decode_log(file_list)




##############files_decode()############################


def single_file_search(file_name, keyword_list):

	ln = len(keyword_list)
	#for those keywords in the file and found out
	#are to be removed from next searching
	#[1:] means to get rid of the column name

	l_res = []
	try:
		with open(file_name) as fobj:
			while True:
				#here we can use this bytes to do progressbar
				buff = fobj.read(201700)
				if buff == '':
					break
				else:
					for keyword in keyword_list:
						if keyword[0] not in l_res and keyword[0] in buff:
							l_res.append(keyword[0])
						else:
							continue
	except Exception as e:
		#logger.warning(e)
		print "DEBUG multi_operates.py,here, e=",e

	return l_res
#################single_file_search########################


def files_search(path_list, keyword_list):
	#global progress_q
	global search_result
	
	print 'DEBUG files search started'
	search_result = {}

	file_list = []
	for path in path_list:
		file_list.extend(sla.get_file_list(path,[]))

	#filter out those not necessary searched files
	sufx_list = [r".rtrc", r".rtrc_backup"]
	ln = len(sufx_list)

	for i in range(ln):
		sufx_list[i] = "({0})$".format(sufx_list[i])

	re_rule = "|".join(sufx_list)
	r = re.compile(re_rule)
	#filter out those not necessary searched files

	for file in file_list:
		#progress_q.put(file)
		if not r.search(file):
			l_res = single_file_search(file,keyword_list)
			for item in l_res:
				search_result.setdefault(item,[]).append(file)

	print "DEBUG files search finished len(search_result)=",len(search_result)		
	return search_result
###############files_search#################################


def do_operates(path_list, keyword_list):
	global search_result

	#1. unpack
	new_path_list = files_unpack(path_list)

	#2. decode
	files_decode(new_path_list)

	#3. search
	search_result = files_search(new_path_list, keyword_list)

##############multi_operates############################



if __name__ == '__main__':
	pass
