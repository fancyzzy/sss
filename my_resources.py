#!/usr/bin/env python
#-*-coding=utf-8-*-

import os
import sys
import csv

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
ico_file = "auto_searcher.ico"
print "path = ",os.path.join(resource,ico_file)
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
		logger.error(e)
		exit("keywords.csv not accessed!")

	return l_key
###############read_keyword_file#####################
keyword_list = read_keyword_file(PREDIFINED_KEYWORD)[1:]
filtered_keyword_list = keyword_list[:]


#This is for pyinstaller
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



if __name__ == '__main__':
	
	print "Resources"
	#print "DEBUG keywords=",keyword_list