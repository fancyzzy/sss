#!usr/bin/env python
# -*- coding: utf-8 -*-

from ctypes import *
import sla_multi_threads as sla
import os

print "DEBUG my_decoder"
print sla.working_path
my_decode_dll = os.path.join('DLLs','decode_64.dll')

@sla.time_interval
def decode_log(log_list):
	mylib = cdll.LoadLibrary(os.path.join(sla.working_path,my_decode_dll))

	log_len = len(log_list)
	log_arry = (c_char_p * log_len)()
	for i in range(log_len):
		log_arry[i] = log_list[i]
	mylib.decode(log_len, log_arry)


if __name__ == '__main__':
	log_list = [r"C:\Users\tarzonz\Desktop\decode_64\bin\Debug\20160219_045800_20160219_050316_1.3.6_DTC_[209]_209.rtrc_backup"]
	decode_log(log_list)

	ds = ''
	if sla.interval > 1000:
		duration = sla.interval/60.0
		ds = "%.1f minutes"%(duration)
	else:
		duration = sla.interval * 1.0
		ds = "%.1f seconds"%(duration)
	print "Finished, time used:",ds	
