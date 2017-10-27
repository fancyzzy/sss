#!/usr/bin/env python
#-*-coding=utf-8-*-

import os
import sys
import csv

from platform import system
opr = system()
print("'{} system'".format(opr))
interval = 0

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
					#logger.warning("Hidden file:%s"%(s))
					#logger.warning("Hidden file:{}".format(s))
					if s != '.':
						continue
				new_dir = os.path.join(dir,s)
				get_file_list(new_dir,file_list)
		else:
			pass
	except Exception as e:
		#logger.warning(e)
		print("warning,e:",e)
	return file_list
################get_file_list####################



'''
This is all the resources location
'''
my_color_blue = '#%02x%02x%02x' % (51,153,255)
my_color_blue_office ='#%02x%02x%02x' % (43,87,154) 
my_color_green = '#%02x%02x%02x' % (192,233,17)
#for terminate searching
l_threads = []
PREDIFINED_KEYWORD = 'keywords.csv'
resource = "resource"
#ico_file = "auto.ico"
ico_file = "auto_32.ico"
icon_path = os.path.join(os.getcwd(),os.path.join(resource,ico_file))

def read_keyword_file(keyword_file):
	
	l_key = []
	try:
		with open(keyword_file) as fobj:
			reader = csv.reader(fobj)
			for item in reader:
				#ignore blank lines
				if item[0].strip() == '':
					continue
				#item[-1]=item[-1].decode('gb2312')
				#is it possible to use namedtuple here?
				l_key.append(item)
	except Exception as e:
		#logger.error(e)
		print("error e=",e)
		exit("keywords.csv not accessed!")

	return l_key
###############read_keyword_file#####################

PRE_KEYWORD_LIST = read_keyword_file(PREDIFINED_KEYWORD)[1:]

####get desktop name#########
import platform
import _winreg

def get_desktop():
	key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,\
	r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders',)
	return _winreg.QueryValueEx(key, "Desktop")[0]

WORKING_PATH = os.getcwd()
DESKTOP_PATH = ""
if platform.system().lower() == 'windows':
	DESKTOP_PATH = get_desktop()

USER_NAME = DESKTOP_PATH.encode('utf-8').split('\\')[-2]
print("'Welcome %s, SLA starts.'"%USER_NAME)
####get desktop name#########

###########custom keyword file########
CK_FILE = 'custom_keyword.txt'
CK_FILE_PATH = os.path.join(WORKING_PATH, CK_FILE)
REMOTE_CK_DIR_PATH = r'\sharing_folder_37\SLA_History'

#Begin irone add for save customized keyword
def save_custom_keyword(new_keyword_list, ck_file=CK_FILE_PATH):
	if os.path.exists(ck_file):
		file_mode = 'a'
	else:
		file_mode = 'w'

	with open(ck_file, file_mode) as fobj:
		for keyword in new_keyword_list:
			fobj.write(keyword + '\r\n')
#End: irone add for save customized keyword

def get_custom_keyword(ck_file=CK_FILE_PATH):

	if os.path.exists(ck_file):
		l_ck = []
		with open(ck_file, 'rb') as fobj:
			while 1:
				buff = fobj.readline()
				if buff == '':
					break
				else:
					l_ck.append(buff.strip().split(' ')[0])

		return l_ck
	else:
		print('my_resources:debug, no custom keword file yet')
		return None
###########custom keyword file########


def get_file_list_size(file_list):
	size_total = 0
	for file in file_list:
		size_total = size_total + os.path.getsize(file)
	s = ''
	if size_total > 1024000000:
		s = "%.2f Gb"%(size_total/((1024*1024*1024)*1.0))
	elif size_total > 10240000:
		s = "%.1f Mb"%(size_total/(1024.0*1024))
	elif size_total > 10240:
		s = "%d Kb"%(size_total/1024.0)
	else:
		s = "%d bytes"%(size_total)

	return s
############get_file_list_size()############
import time
def record_result(str_list, result_file = 'result.txt'):

	with open(result_file, 'w') as fobj:
		s = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))	
		fobj.write("result of"+" " + s + '\r\n')
		for str_line in str_list:
			#unicode contain chinese can't not be write
			#so convert to str type
			if 'unicode' in str(type(str_line)):
				str_line = str_line.encode('utf-8')
			fobj.write(str_line + '\r\n')
	return
#########record_result()####################




#This is for pyinstaller
'''
if hasattr(sys, "_MEIPASS"):
	print "sys._MEIPASS = ",sys._MEIPASS
else:
	print "os.path.abspath = ",os.path.abspath(".")
#需要pyinstaller -F xx.spec打包成一个.exe的时候用这个函数
#否则，正常打包不要用这个函数定义资源文件的路径
def resource_path(relative_path):
	if hasattr(sys, "_MEIPASS"):
		base_path = sys._MEIPASS
	else:
		base_path = os.path.abspath(".")
	return os.path.join(base_path, relative_path)
'''

if __name__ == '__main__':
	
	print "this is Resources"
	#print "DEBUG keywords=",keyword_list