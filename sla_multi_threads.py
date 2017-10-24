#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
keywords searcher
for configed keywords automatical searching in assigned pile of files
author: Felix.Zhang@alcetul-lucent.com
'''

import logging
import argparse
import csv
import os
import time
import threading
import Queue
import platform
import copy

# 配置log
logger = logging.getLogger('feli')
interval = 0
opr = platform.system()

########################globals##################
def time_interval(func):
	def _deco(*args, **kwargs):
		global interval
		if opr.lower() == 'windows':
			start = time.clock()
		else:
			start = time.time()
		ret = func(*args, **kwargs)
		if opr.lower() == 'windows':
			end = time.clock()
		else:
			end = time.time()

		interval = end - start
		#print "function %s total time used:%3f seconds"\
		#%(func.__name__, interval/1.000)

		return ret
	return _deco


def log_config():
	par = argparse.ArgumentParser()
	par.add_argument('-v','--verbose',help='activate log output',\
		action='store_true')
	args = par.parse_args()

	# CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET
	if args.verbose:
		logger.setLevel(logging.DEBUG)
	else:
		#设置成最高级别，这样其他级别log的都会不打
		logger.setLevel(logging.ERROR)
	
	hdr = logging.StreamHandler()
	formatter = logging.Formatter('%(asctime)s %(filename)s %(lineno)d %(levelname)s: %(message)s')
	hdr.setFormatter(formatter)
	logger.addHandler(hdr)
#############log_config()#########################


def get_file_list(dir,file_list):
	'''
	获取目录dir下的所有文件名(文件路径)
	略过隐藏的特殊文件
	支持子目录
	'''
	try:
		new_dir = dir
		if os.path.isfile(dir):
			file_list.append(dir)
		elif os.path.isdir(dir):
			for s in os.listdir(dir):
				#略过特殊字符开头的文件或者文件夹
				if not s[0].isdigit() and not s[0].isalpha():
					logger.warning("Hidden file:%s"%(s))
					#logger.warning("Hidden file:{}".format(s))
					if s != '.':
						continue
				new_dir = os.path.join(dir,s)
				get_file_list(new_dir,file_list)
		else:
			pass
	except Exception as e:
		logger.warning(e)
	return file_list
################get_file_list####################


def is_keyword_in_file(key_word, file):
	
	try:
		with open(file) as fobj:
			while True:
				#print "DEBUG key_word=",key_word

				#bug long key word may not be found if it just locate where it is at 2000 bytes around
				#buff = fobj.read(2000)
				buff = fobj.read(201700)
				if buff == '':
					break
				else:
					if key_word in buff:
						return True
					else:
						#print "DEBUG key_word=",key_word
						#print "DEBUG buff=",buff
						continue
	except Exception as e:
		logger.warning(e)

	#return False

################is_keyword_in_file()###############		


progress_q = Queue.Queue()
class auto_searcher(object):
	
	def __init__(self,keywords_csv = 'keywords.csv',path = os.getcwd()):
		# keywords存储文件和待搜索文件路径
		self.k_file = keywords_csv
		self.file_path = path
		self.l_keywords = []
		self.file_list = get_file_list(self.file_path,[])
		self.file_list = []
		self.result = {}
		#显示搜索文件进度的queue，每次搜素一个文件，就把
		#这个文件名放到queue中
		#self.progress_q = Queue.Queue()
		self.total_work = len(self.file_list)

		try:
			with open(self.k_file) as fobj:
				reader = csv.reader(fobj)
				for item in reader:
					#bug keyword not blank
					if item[0].strip() == '':
						continue
					item[-1]=item[-1].decode('gb2312')
					#is it possible to use namedtuple here?
					#print "DEBUG item=",item
					self.l_keywords.append(item)

		except Exception as e:
			logger.error(e)
			exit("keywords.csv not accessed!")
			
		if len(self.l_keywords) == 1:
			logger.warning("keywords.csv 被认为只有标题!")
	############init()######################

	#multi thread begin
	@time_interval
	def auto_search(self,keyword_list,file_list,threads_num = 2):
		global progress_q
		progress_q.queue.clear()

		print "DEBUG auto_search started"
		threads_res = {}
		threads = []
		leng = len(file_list)

		self.total_work = leng

		if threads_num > 1:
			for i in range(threads_num):
				fi = float(i)
				pre = int(fi/threads_num * leng)
				pos = int((fi+1)/threads_num * leng)
				t = threading.Thread(target=self.thread_search, args=(int(i), keyword_list, file_list[pre:pos],\
					threads_res))
				threads.append(t)

			for t in threads:
				t.start()

			for t in threads:
				t.join()
		#1 means no sub thread
		else:
			print "DEBUG no sub-thread!!"
			self.thread_search(0,keyword_list,file_list,threads_res)

		d_result = {}
		for i in range(threads_num):
			#把几个线程的结果按照id顺序加起来
			for k in keyword_list:
				if k[0] != None and threads_res[i].has_key(k[0]):
					if d_result.has_key(k[0]):
						d_result[k[0]] += threads_res[i][k[0]]
					else:
						d_result[k[0]] = threads_res[i][k[0]]

		print "DEBUG auto_search finished with %d threads"%(threads_num)
		return d_result

	def thread_search(self, thread_id, keyword_list,file_list, threads_res):
		global progress_q
		
		d_result = {}
		lk = len(keyword_list)
		#optimize begin
		d_flag = {}
		d_key_find_flag = {}
		#optimize end
		l_key = zip(*keyword_list[1:])[0]

		#这里将略过keywords.csv的第一行，该行被认为是标题行
		for i in range(1,lk):
			d_result[keyword_list[i][0]] = []
			#optimize begin
			d_flag[keyword_list[i][0]] = False
			#optimize end

		#optimize begin
		for file in file_list:
			progress_q.put(file)
			d_key_find_flag = copy.copy(d_flag)
			#d_key_find_flag = dict.fromkeys(l_key,False)
			try:
				with open(file) as fobj:
					while True:
						#optimize read with interrupt if not support file type
						#this is still faster
						buff = fobj.read(201700)
						'''
						try:
							buff = fobj.read(201700).decode('gb2312')
						except Exception as e:
							#print "file {0},read error, e={1}".format(file,e)
							break
						'''
						if buff == '':
							break
						else:
							for i in range(1, lk):
								if not d_key_find_flag[keyword_list[i][0]]:
									if keyword_list[i][0] in buff:
										d_key_find_flag[keyword_list[i][0]] = True
										d_result[keyword_list[i][0]].append(file)
								else:
									continue
			except Exception as e:
				logger.warning(e)
				print "DEBUG here"
				continue
		threads_res[thread_id] = d_result
	############auto_keywords+search()################

	def show_progress(self):

		t = threading.Thread(target=self.progress)
		t.start()

	def progress(self):
		global progress_q

		n = 0
		print "Start Analysis, total files",self.total_work
		while n < self.total_work:
			file = progress_q.get()
			n += 1
			print "Analysing: [%d/%d] %s"%(n,self.total_work,file)

		print "Analysis finished!"
		print
	
	@time_interval
	def custom_search(self,keyword,file_list):
		
		d_result = {}
		d_result[keyword] = []

		#resue auto_search begin
		keyword_list = [[''],[keyword]]
		d_result = self.auto_search(keyword_list,file_list)

		return d_result
		#reuse auto_search end
		'''
		for file in file_list:
			self.progress_q.get(file)	
			if is_keyword_in_file(keyword,file):
				d_result[keyword].append(file)
		return d_result
		'''
	#############custom_search()#####################
	
	@time_interval
	def repeat_log_rank(self, file_list, remove_byte=0, top_rank = 5):

		d_result = {}

		for file in file_list:
			try:
				with open(file) as fobj:
					while True:
						buff = fobj.readline()
						if buff == "":
							break
						else:
							real_line = buff[remove_byte:]
							if d_result.has_key(real_line):
								d_result[real_line] += 1
							else:
								d_result[real_line] = 1
			
			except Exception as e:
				logger.error(e)
		l_result = sorted(d_result.iteritems(), key=lambda d:d[1], reverse = True)
		return l_result[:top_rank]
	###############repeat_log_rank()#################
	
	
	def cmd_show(self):
	
		while True:
			print "\n"
			title = "Hello, Welcome to BSC SLA v1.0"
			print title.center(70),
			print
			print ("file path:"),self.file_path
			print ("keywords file:"),self.k_file
			print 
			print("--select command--")
			print("[0] - show keywords")
			print("[1] - auto keywords search")
			print("[2] - custom search")
			print("[3] - repeated log rank")
			print ""
			print("[s] - select file path   [q] - quit")
		 
			com = raw_input(">").strip("")
			
			if com == 'q' or com == 'quit':
				logger.info("Good Bye")
				break

			elif com == 's' or com == 'select':
				self.file_path = raw_input('file path>').strip()
				#转换成全明路径
				if self.file_path.startswith('.'):
					self.file_path = self.file_path.replace('.',os.getcwd(),1)
				#检查文件或文件夹是否存在
				if not os.path.isfile(self.file_path) and not os.path.isdir(self.file_path):
					print "File or Directory not exsited!"
				else:
					self.file_list = get_file_list(self.file_path,[])
					self.total_work = len(self.file_list)
					print u"该文件(夹)%s,下可访问文件为:"%(self.file_path)
					for item in self.file_list:
						print item

					print u"总共%d个文件"%(len(self.file_list))

			elif com == '0':
				if len(self.l_keywords) == 0:
					logger.error("No keywords configured, Check the 'keywords.csv' file")
				else:
					for index,item in enumerate(self.l_keywords):
						print index,item

			#print("[1] - auto keywords search")
			elif com == '1':

				self.file_list = get_file_list(os.getcwd(),[])
				d_result = {}
				self.show_progress()
				d_result = self.auto_search(self.l_keywords, self.file_list) 
				n = 0

				print 
				print u"-----------**搜索结果**--------------------".center(40)
				for i in range(1,len(self.l_keywords)):
					num = len(d_result[self.l_keywords[i][0]])
					n = n+num
					if num > 0:
						print "KEYWORD: %s found in %d files:"%(self.l_keywords[i], num)
						for file in d_result[self.l_keywords[i][0]]:
							print file
						print "-" * 20 
					else:
						pass

				if n == 0:
					print u"没有发现这些文件包含关键字"

				print "time used interval = ",interval
				#for item in self.l_keywords:

			elif com == '2':
				self.file_list = get_file_list(os.getcwd(),[])
				key = raw_input('>').strip()
				d_result = {}
				self.show_progress()
				d_result = self.custom_search(key,self.file_list)
				
				num  = len(d_result[key])
				print u"-------------搜索结果-------------------".center(40)
				if num > 0: 
					print "KEYWORD: '%s' found in %d files:"%(key,num)
					for file in d_result[key]:
						print file
				else:
					print u"没有文件包含这个关键字"
				print "-----------------------------------------"


			elif com == '3':
				
				l_result =  self.repeat_log_rank(self.file_list)
				print u"-------------重复log打印排名------------------".center(40)
				for item in l_result:
					print item
				print "-----------------------------------------------"
			else:
				logger.debug("No such command")
				
			raw_input('\n\n"tap enter to continue..."') 

#############cmd_show()###############################


def main():

	searcher = auto_searcher('keywords.csv',os.getcwd()) 
	searcher.cmd_show()
			
##############main()##############################


log_config()
logger.warning("hahaha critical")
if __name__ == "__main__":

	main()




