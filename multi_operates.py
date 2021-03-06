#!/usr/bin/env python
#-*-coding=utf-8-*-

import copy
import my_unpacker
import my_decoder
import my_lines_counter
import my_resources
import os
import re
import Queue
import collections
import subprocess
#analyse_file_type = ("rtrc","bssim","txt")

search_result = {}
PROGRESS_QUE = Queue.Queue()



def call_proc(cmd):
	'''
	This function to call a process to run outside programme
	'''
	#p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
	try:
		p = subprocess.Popen(cmd, shell=True)
	except Exception as e:
		print "DEBUG subprocess error e =",e
########call_proc()####################	



def used_time():

	ivl = my_resources.interval
	duration = 0
	ds = ''
	if ivl > 1000:
		duration = ivl/60.0
		ds = "%.1f minutes"%(duration)
	else:
		duration = ivl * 1.0
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
	res = my_unpacker.untar_file(file_name, f_delete)	
	return res
########single_file_unpack()#####################


#display porgress tip for each unpacked file
@my_resources.time_interval
def unpack_item(itemname, delet_fi=False):
	global PROGRESS_QUE	

	s = (None, "")
	pack_name = ('','')
	if os.path.isfile(itemname):
		pack_name = my_unpacker.detect_pack(itemname)
		if pack_name[0]:
			#progress tip put(pack_name[1])
			tip = "Unpacking: {0}".format(itemname)
			PROGRESS_QUE.put(tip)
			s = my_unpacker.untar_file(pack_name[0],itemname, delet_fi)
			if s[0]:
				print("Unpack error")	
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


@my_resources.time_interval
def files_unpack(path_list):
	global PROGRESS_QUE

	unpack_list = [""]
	ln = len(path_list)
	new_path_list = copy.deepcopy(path_list)

	print('  unpack start')


	error = None
	for i in range(ln):
		item = path_list[i]
		tip = "Unpacking[{0}/{1}]{2}".format(i+1,ln,path_list[i].encode('gb2312'))
		PROGRESS_QUE.put(tip)

		#display porgress tip for each unpacked file
		#errors = my_unpacker.my_unpacker(path_list[i])[0]
		errors = unpack_item(path_list[i])[0]
		if errors:
			print "DEBUG unpack error = ",errors
			break
		#check if this is unpack available file,
		#if it is, update the new folder into new_path_list
		for sufx in my_unpacker.unpack_list:
			if path_list[i].lower().endswith(sufx):
				#new_path_list[i] = path_list[i].rstrip(sufx)
				new_path_list[i] = path_list[i][:-len(sufx)]
				break

	return new_path_list
######################files_unpack()####################

def single_file_decode(file_name):
	my_decoder.decode_one_file(file_name)

@my_resources.time_interval
def files_decode(path_list):

	file_list = []
	for path in path_list:
		file_list.extend(my_resources.get_file_list(path,[]))

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


@my_resources.time_interval
def files_search(path_list, keyword_list, files_types_list=None, start_stop = None):
	#global progress_q
	global search_result
	
	search_result = {}
	searched_file_number = 0

	file_list = []
	original_file_list = []
	for path in path_list:
		original_file_list.extend(my_resources.get_file_list(path,[]))


	#filter file_list:
	#1. only left according to files_types
	print("  files_search, 1.fitler out, files_types=",files_types_list)
	if files_types_list:

		re_f = ''
		for i in range(len(files_types_list)):
			files_types_list[i] = '(' + files_types_list[i] + ')'
		re_f = '|'.join(files_types_list)
		# re_filters = r'(.*\.txt)|(.*\.out)'

		#print("DEBUG re_filter=",re_f)
		re_filter = re.compile(re_f)
		for file in original_file_list:
			if re_filter.search(file):
				file_list.append(file)
			else:
				#file not in the filter_types
				pass

	#start_stop = '20171009_222222_20171009_333333'
	#file_list = filter_start_stop(file_list, filter_word)

	print('  files_search, 2.search start')

	#2. filter out those not necessary searched files
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
			searched_file_number += 1
			for item in l_res:
				search_result.setdefault(item,[]).append(file_list[i])
		else:
			#do not search '.rtrc','.rtrc_backup'..
			pass

	return search_result,searched_file_number
###############files_search#################################

@my_resources.time_interval
def do_operates(path_list, keyword_list, files_types_list=None):
	global search_result
	global PROGRESS_QUE

	PROGRESS_QUE.queue.clear()

	#1. unpack
	PROGRESS_QUE.put("Unpack start")
	new_path_list = files_unpack(path_list)
	PROGRESS_QUE.put("Unpack finished, time used = %s"%(used_time()))

	tmp = my_resources.interval
	#2. decode
	PROGRESS_QUE.put("Decode start")
	files_decode(new_path_list)
	PROGRESS_QUE.put("Decode finished, time used = %s"%(used_time()))

	tmp = tmp + my_resources.interval
	#3. search
	PROGRESS_QUE.put("Search start")
	search_result,searched_number = files_search(new_path_list, keyword_list, files_types_list)
	PROGRESS_QUE.put("Search finished, time used = %s"%(used_time()))

	tmp = tmp + my_resources.interval
	my_resources.interval = tmp


	return search_result,searched_number

@my_resources.time_interval
def files_lines_count(path_list, top_rank = 10, files_types_list=None):

	count_result = {}
	counted_file_number = 0

	file_list = []
	original_file_list = []
	for path in path_list:
		original_file_list.extend(my_resources.get_file_list(path,[]))


	#filter file_list:
	#1. only left according to files_types
	print("  files_lines_count, 1.fitler out, files_types=",files_types_list)
	if files_types_list:

		re_f = ''
		for i in range(len(files_types_list)):
			files_types_list[i] = '(' + files_types_list[i] + ')'
		re_f = '|'.join(files_types_list)
		# re_filters = r'(.*\.txt)|(.*\.out)'

		#print("DEBUG re_filter=",re_f)
		re_filter = re.compile(re_f)
		for file in original_file_list:
			if re_filter.search(file):
				file_list.append(file)
			else:
				#file not in the filter_types
				pass

	print('  files_lines_count, 2.counting start')

	#2. filter out those not necessary searched files
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
			tip = "Counting Repetition[{0}/{1}]{2}".format(i+1,ln_files,s)
			PROGRESS_QUE.put(tip)
			try:
				my_lines_counter.single_file_line_count(file_list[i], count_result)
				counted_file_number += 1

			except Exception as e:
				print ("DEBUG: Here: ", e)

	l_result = sorted(count_result.iteritems(), key=lambda d:d[1], reverse = True)
	return l_result[:top_rank],counted_file_number
####################files_lines_count()########################
	
##############multi_operates############################



if __name__ == '__main__':
	pass
