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
PROGRESS_QUE = Queue.Queue()


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


#display porgress tip for each unpacked file
@sla.time_interval
def unpack_item(itemname, delet_fi=False):
	global PROGRESS_QUE	

	s = (None, "")
	pack_name = ('','')
	if os.path.isfile(itemname):
		pack_name = untar_function.detect_pack(itemname)
		if pack_name[0]:
			#progress tip put(pack_name[1])
			tip = "Unpacking: {0}".format(itemname)
			PROGRESS_QUE.put(tip)
			s = untar_function.untar_file(pack_name[0],itemname, delet_fi)
			if s[0]:
				return s
			new_file = s[1]
			if os.path.exists(new_file):
				s = unpack_item(new_file, delet_fi)
				if s[0]:
					return s
	else:
		files = os.listdir(itemname)
		for fi in files:
			fi_d = os.path.join(itemname, fi)
			s =unpack_item(fi_d, delet_fi)
	return s


@sla.time_interval
def files_unpack(path_list):
	global PROGRESS_QUE

	unpack_list = [""]
	ln = len(path_list)
	new_path_list = copy.deepcopy(path_list)

	print('  unpack start')


	error = None
	for i in range(ln):
		tip = "Unpacking[{0}/{1}]{2}".format(i+1,ln,path_list[i].encode('gb2312'))
		PROGRESS_QUE.put(tip)

		#display porgress tip for each unpacked file
		#errors = untar_function.untar_function(path_list[i])[0]
		errors = unpack_item(path_list[i])[0]
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

	print('  decode start')

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
			PROGRESS_QUE.put(tip)
			single_file_decode(file_list[i])
	#my_decoder.decode_log(file_list)
##############files_decode()############################


def single_file_search(file_name, keyword_list):

	ln = len(keyword_list)
	#for those keywords in the file and found out
	#are to be removed from next searching
	#[1:] means to get rid of the column name

	l_res = []

	ln = len(keyword_list)
	is_custom_search = False
	if ln == 1:
		is_custom_search = True
	'''
	keyword_re_list = []
	for i in range(len(keyword_list)):
		keyword_re_list.append(re.compile(keyword_list[i][0]))
	'''

	try:
		with open(file_name) as fobj:
			while True:
				#here we can use this bytes to do progressbar
				buff = fobj.read(201700)
				#buff = fobj.readline()
				if buff == '':
					break
				else:
					for i in range(ln):
						'''
						if keyword_list[i][0] not in l_res:
							if keyword_re_list[i].search(buff, re.I):
								l_res.append(keyword_list[i][0])
						'''
						if not is_custom_search:
							if keyword_list[i][0] not in l_res and keyword_list[i][0] in buff:
								l_res.append(keyword_list[i][0])
						else:
							if keyword_list[i][0] not in l_res and keyword_list[i][0].lower() in buff.lower():
								l_res.append(keyword_list[i][0])
	except Exception as e:
		#logger.warning(e)
		print "DEBUG multi_operates.py,here, e=",e

	return l_res
#################single_file_search########################


@sla.time_interval
def files_search(path_list, keyword_list, start_stop = None):
	#global progress_q
	global search_result
	
	search_result = {}

	file_list = []
	for path in path_list:
		file_list.extend(sla.get_file_list(path,[]))

	#start_stop = '20171009_222222_20171009_333333'
	#file_list = filter_start_stop(file_list, filter_word)

	print('  search start')

	#filter out those not necessary searched files
	not_search_sufx_list = [r".rtrc", r".rtrc_backup"]
	ln = len(not_search_sufx_list)

	for i in range(ln):
		not_search_sufx_list[i] = "({0})$".format(not_search_sufx_list[i])

	re_rule = "|".join(not_search_sufx_list)
	re_not_sufx_list = re.compile(re_rule)
	#filter out those not necessary searched files

	ln_files = len(file_list)

	for i in range(ln_files):
		if not re_not_sufx_list.search(file_list[i]):
			s = file_list[i]
			if 'unicode' in str(type(s)):
				s = s.encode('gb2312')
			tip = "Searching[{0}/{1}]{2}".format(i+1,ln_files,s)
			PROGRESS_QUE.put(tip)
			l_res = single_file_search(file_list[i],keyword_list)
			for item in l_res:
				search_result.setdefault(item,[]).append(file_list[i])

	return search_result
###############files_search#################################

@sla.time_interval
def do_operates(path_list, keyword_list):
	global search_result
	global PROGRESS_QUE

	PROGRESS_QUE.queue.clear()

	#1. unpack
	PROGRESS_QUE.put("Unpack start")
	new_path_list = files_unpack(path_list)
	PROGRESS_QUE.put("Unpack finished, time used = %s"%(used_time()))

	tmp = sla.interval
	#2. decode
	PROGRESS_QUE.put("Decode start")
	files_decode(new_path_list)
	PROGRESS_QUE.put("Decode finished, time used = %s"%(used_time()))

	tmp = tmp + sla.interval
	#3. search
	PROGRESS_QUE.put("Search start")
	search_result = files_search(new_path_list, keyword_list)
	PROGRESS_QUE.put("Search finished, time used = %s"%(used_time()))

	tmp = tmp + sla.interval
	sla.interval = tmp
	PROGRESS_QUE.put("All done, time used =%s"%(used_time()))

##############multi_operates############################



if __name__ == '__main__':
	pass
