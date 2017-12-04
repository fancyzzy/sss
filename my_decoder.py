#!usr/bin/env python
# -*- coding: utf-8 -*-

from ctypes import *
import my_resources
import os

my_decode_dll = os.path.join('DLLs','decode_64.dll')

mylib = cdll.LoadLibrary(os.path.join(my_resources.WORKING_PATH,my_decode_dll))

@my_resources.time_interval
def decode_log(log_list):
	global mylib

	log_len = len(log_list)
	log_arry = (c_char_p * log_len)()
	for i in range(log_len):
		log_arry[i] = log_list[i]
	mylib.decode(log_len, log_arry)

def decode_one_file(file_name):
	global mylib

	log_list =[file_name] 
	log_len = 1
	print("DEBUG log_list=",log_list)
	log_arry = (c_char_p * log_len)()
	for i in range(log_len):
		log_arry[i] = log_list[i]

	mylib.decode(log_len, log_arry)

	#mylib.DecodeFile(file_name_c)



if __name__ == '__main__':
	print "DEBUG my_decoder"

	'''
	log_list = [r"C:\Users\tarzonz\Desktop\decode_test\error.rtrc_backup",r"C:\Users\tarzonz\Desktop\decode_test\good.rtrc_backup"]
	decode_log(log_list)
	'''

	file_name = r"C:\Users\tarzonz\Desktop\decode_test\error.rtrc_backup"

	decode_one_file(file_name)

