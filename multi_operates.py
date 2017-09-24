#!/usr/bin/env python
#-*-coding=utf-8-*-

import copy
import untar_function
import my_decoder
import sla_multi_threads as sla
import os
import re
import Queue
import collections
#analyse_file_type = ("rtrc","bssim","txt")

search_result = {}
progress_que = Queue.Queue()


def used_time():

	duration = 0
	ds = ''
	if sla.interval > 1000:
		duration = sla.interval/60.0
		ds = "%.1f minutes"%(duration)
	else:
		duration = sla.interval * 1.0
		ds = "%.1f seconds"%(duration)
	return ds
##############used_time()############################


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

@sla.time_interval
def files_unpack(path_list):
	global progrss_que

	unpack_list = [""]
	ln = len(path_list)
	new_path_list = copy.deepcopy(path_list)

	error = None
	for i in range(ln):
		tip = "Unpacking[{0}/{1}]{2}".format(i+1,ln,path_list[i].encode('gb2312'))
		progress_que.put(tip)
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

@sla.time_interval
def files_decode(path_list):

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

	ln_files = len(file_list)
	for i in range(ln_files):
		if r.search(file_list[i]):
			tip = "Decoding[{0}/{1}]{2}".format(i+1,ln_files,file_list[i].encode('gb2312'))
			progress_que.put(tip)
			single_file_decode(file_list[i])
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


@sla.time_interval
def files_search(path_list, keyword_list):
	#global progress_q
	global search_result
	
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

	ln_files = len(file_list)

	for i in range(ln_files):
		if not r.search(file_list[i]):
			tip = "Searching[{0}/{1}]{2}".format(i+1,ln_files,file_list[i].encode('gb2312'))
			progress_que.put(tip)
			l_res = single_file_search(file_list[i],keyword_list)
			for item in l_res:
				search_result.setdefault(item,[]).append(file_list[i])

	return search_result
###############files_search#################################

@sla.time_interval
def do_operates(path_list, keyword_list):
	global search_result
	global progress_que

	progress_que.queue.clear()

	#1. unpack
	progress_que.put("Unpack start")
	new_path_list = files_unpack(path_list)
	progress_que.put("Unpack finished, time used = %s"%(used_time()))

	tmp = sla.interval
	#2. decode
	progress_que.put("Decode start")
	files_decode(new_path_list)
	progress_que.put("Decode finished, time used = %s"%(used_time()))

	tmp = tmp + sla.interval
	#3. search
	progress_que.put("Search start")
	search_result = files_search(new_path_list, keyword_list)
	progress_que.put("Search finished, time used = %s"%(used_time()))

	tmp = tmp + sla.interval
	sla.interval = tmp
	progress_que.put("All done, time used =%s"%(used_time()))

##############multi_operates############################



if __name__ == '__main__':
	pass
