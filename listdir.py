#!/usr/bin/env python
# --*-- coding:utf-8 --*--


#import os
from time import sleep
from Tkinter import *
import ttk
from tkMessageBox import *
from Dialog import *
import sla_multi_threads as sla 
import threading
import dnd
import copy
import subprocess
import ctypes
import inspect
#import sys
import RTTP_decoder
from my_resources import *
import my_decoder
import untar_function
import re
import repeat_log
#print sys.getdefaultencoding()

'''
reload(sys)
sys.setdefaultencoding('utf8')
print sys.getdefaultencoding()
'''

'''
my_color_blue = '#%02x%02x%02x' % (51,153,255)
#my_color_green = '#%02x%02x%02x' % (128,216,10)
my_color_green = '#%02x%02x%02x' % (192,233,17)
#for terminate searching
l_threads = []
data_file = 'keywords.csv'
resource = "resource"
ico_file = "auto_searcher.ico"
print "path = ",os.path.join(resource,ico_file)
icon_path = os.path.join(os.getcwd(),os.path.join(resource,ico_file))

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
'''

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


class DirList(object):
	def __init__(self, initdir=None):
		self.top = Tk()
		self.top.geometry('850x560+280+140')
		#self.top.geometry()
		self.top.wm_title("SLA")
		self.blank_label0 = Label(self.top, text='')
		self.blank_label0.pack()
		self.label = Label(self.top, text='Site Log Analyser v2.3',\
			font = ('Helvetica', 12, 'bold'), fg= my_color_blue_office)
		self.label.pack()
		#self.blank_label1 = Label(self.top, text='')
		#self.blank_label1.pack()
		self.cwd = StringVar(self.top)
		self.keyword = StringVar(self.top)
		#self.top.iconbitmap('auto_searcher.ico')
		#pyinstaller -F 打包使用resource_path这个函数通过_MAIPASS获取资源路径
		#self.top.iconbitmap(resource_path(os.path.join(resource,'auto_searcher.ico')))
		self.top.iconbitmap(icon_path)

		self.dir_fm = Frame(self.top)
		self.entry_label = Label(self.dir_fm, text="Search in: ")
		self.dirn = Entry(self.dir_fm, width=80, textvariable=self.cwd)
		#self.cwd.set(os.getcwd())

		self.dirn.bind('<Return>', self.doLS)
		#self.dirn.focus_set()
		self.ls = Button(self.dir_fm, text='List directory', command=self.doLS, activeforeground\
			='white', activebackground='orange')
		self.ls.pack(side=RIGHT)
		self.entry_label.pack(side=LEFT)
		self.dirn.pack(side=LEFT)
		self.dir_fm.pack()	

		self.dirfm = Frame(self.top)
		self.dirsby = Scrollbar(self.dirfm)
		self.dirsby.pack(side=RIGHT, fill=Y)
		#self.dirsbx = Scrollbar(self.dirfm,orient=HORIZONTAL)
		#self.dirsbx.pack(side=BOTTOM, fill=X)

		self.list_v = StringVar()
		#selectmode=EXTENDED,BROWSE,MULTIPLE,SINGLE
		#exportselection is used to enable "ctrl+c" to copy the content selected 
		#in the listbox into the windows clipboard when =1
		self.dirs = Listbox(self.dirfm, height=25, width=130, selectmode=EXTENDED,\
			exportselection=1,listvariable=self.list_v)
		#2017.8.23 BUG: 滚动轴导致程序挂掉，原因可能是由于多线程子线程更新GUI界面
		#产生内部错误导致
		#self.dirs['yscrollcommand'] = self.dirsb.set
		#self.dirs['xscrollcommand'] = self.dirsbx.set
		self.dirs.bind('<Double-1>', self.setDirAndGo)
		self.dirs.bind('<1>', lambda event:self.listbox_click(event))
		#self.dirs.bind('<3>', self.listbox_Rclick)
		self.dirsby.config(command=self.dirs.yview)
		#self.dirsbx.config(command=self.dirs.xview)
		self.dirs.pack(expand=YES, fill=BOTH)
		self.dirfm.pack(expand=YES,fill=BOTH)


		self.search_fm = Frame(self.top)
		self.search_label = Label(self.search_fm, text="Find for: ")
		self.search_entry = Entry(self.search_fm, width=30,textvariable=self.keyword)
		#This is for keywords.csv data
		self.keyword.set(data_file)
		self.search_entry.bind('<Return>', self.get_default_keywords)
		self.search_b = Button(self.search_fm, text="Start search", command=self.auto_analyse, activeforeground\
			='white', activebackground='orange',bg = 'white', relief='raised')
		self.search_entry.focus_set()

		self.search_label.pack(side=LEFT)
		self.search_entry.pack(side=LEFT)
		#terminate
		self.stop_b = Button(self.search_fm, text="Stop", command=self.terminate_threads)
		self.stop_b.pack(side=RIGHT)
		self.search_b.pack(side=RIGHT)
		self.search_fm.pack()


		#self.blank_label = Label(self.top, text='')
		#self.blank_label.pack()

		self.ptext = StringVar(self.top)
		self.ptext.set("")
		self.pro_label = Label(self.top, textvariable=self.ptext,justify='left')
		self.pro_label.pack(side=LEFT)


		#####sla core algorithm instant init##########
		self.searcher = sla.auto_searcher(self.keyword.get(),os.getcwd())
		#####sla core algorithm instant init##########

		############# menu init ################################
		menubar = Menu(self.top)	

		#keyword update menu
		menubar.add_command(label = 'keywords', command=self.menu_keywords)

		#filter_menu
		self.search_filter = ['none']
		filter_menu = Menu(menubar,tearoff = 1)
		#all the module used for filter keyword belonging to that module out
		self.lf = list(set(zip(*self.searcher.l_keywords[1:])[1]))

		check_var = StringVar()
		self.d_filter = {}
		for i in range(len(self.lf)):
			self.d_filter[self.lf[i]] = StringVar()

		#filter_menu
		filter_menu.add_command(label="select all",command=self.menu_selectall)
		filter_menu.add_separator()
		for item,v in self.d_filter.items():
			#filter_menu.add_command(label = item,command=self.menu_hello)
			filter_menu.add_checkbutton(label = item,command=self.menu_filter,\
				variable=v)
		#将menubar 的menu 属性指定为filemenu，即filemenu 为menubar 的下拉菜单
		menubar.add_cascade(label = 'Filters',menu = filter_menu)

		#decode menue
		menubar.add_command(label = 'RTTP', command=self.menu_decode_log)

		#about menue
		about_menu = Menu(menubar, tearoff = 0)
		about_menu.add_command(label='About', command=self.menu_about)
		about_menu.add_separator()
		about_menu.add_command(label='How To Use', command=self.menu_howto)
		menubar.add_cascade(label = 'About', menu = about_menu)
		self.top['menu']=menubar

		##popup menu
		self.popup_menu = Menu(self.top, tearoff = 0)
		#self.popup_menu.add_command(label='Open',command=self.setDirAndGo)
		#multi open
		self.popup_menu.add_command(label='Open',command=self.multi_open)
		self.popup_menu.add_separator()
		self.popup_menu.add_command(label='Unpack',command=self.untar)
		self.popup_menu.add_separator()
		self.popup_menu.add_command(label='Search',command=self.solo_search)
		self.popup_menu.add_separator()
		self.popup_menu.add_command(label='Decode',command=self.my_decode)
		self.popup_menu.add_separator()
		self.popup_menu.add_command(label='Repetion',command=self.my_repeat)
		#popup_menu.entryconfig("Open", state="disable")
		############# menu init ################################

		#MAC OS GUI
		if (self.top.tk.call('tk','windowingsystem')=='aqua'):
			self.dirs.bind('<3>', lambda event: self.listbox_Rclick(event,self.popup_menu))
			self.dirs.bind('<Control-1>', lambda event: self.listbox_Rclick(event,self.popup_menu))
		#Win32
		else:
			#右击可以弹出菜单，用lambda的写法可以传递参数
			self.dirs.bind('<3>', lambda event: self.listbox_Rclick(event,self.popup_menu))


		if initdir:
			self.cwd.set(os.getcwd())
			self.menu_selectall()
			self.doLS()

		self.dnd_enable(self.dirs)


	############# menu function ###############
	def menu_keywords(self):

		kdir = os.path.join(sla.working_path,data_file)
		cmd = [kdir]
		try:
			call_proc(cmd)
		except Exception as e:
			print "DEBUG call_proc error=",e
			self.dirs.config(selectbackground='red')


	def menu_decode_log(self):
		#新建一个隶属于self.top的子窗口
		#会随着主窗口关闭而关闭
		#decode_top = Toplevel(self.top)
		decode_top = RTTP_decoder.rttp(self.top)

	def log_translate(self):
		showinfo(title='Log Translate',message="To be done...")

	def menu_about(self):
		s = askyesnocancel(title='about', message = "SLA - Site Log Analyser v2.3, any idea, just feedback to us:",\
			detail="felix.zhang@nokia-sbell.com\nirone.li@nokia-sbell.com\neric.a.zhu@nokia-sbell.com\nbella.sun@nokia-sbell.comn\n\
			QD GSM-A All Rights Reserved",icon=INFO)
		'''
		d = Dialog(None,title='about',text="SLA - Site Log Analyser v2.1\
			\nAny idea, just feedback to us:\nfelix.zhang@nokia-sbell.com\
			\nirone.li@nokia-sbell.com\neric.a.zhu@nokia-sbell.com",bitmap=DIALOG_ICON,default=0,strings=('OK','no'))
		d.num
		'''

	def menu_howto(self):
		s = askyesno(title='How To', message = "把要分析的trace文件夹直接拖放到显示目录框中，点击'Start Search'\n简单吧?\n")
		if s:
			print s
		else:
			print "no s=",s


	def menu_filter(self):
		self.search_filter=[]
		for fi,va in self.d_filter.items():
			if va.get() == '1':
				self.search_filter.append(fi)
		s = "{0} files, search filters: {1}".format(self.searcher.total_work,self.search_filter)
		self.ptext.set(s)

		self.keyword.set(data_file)

	def menu_selectall(self):
		all_true_flag = True
		for i in range(len(self.lf)):
			#print self.d_filter[self.lf[i]].get()
			if self.d_filter[self.lf[i]].get() == '0':
				all_true_flag = False

		if all_true_flag and self.d_filter[self.lf[0]].get() != '':
			for i in range(len(self.lf)):
				self.d_filter[self.lf[i]].set(False)
			self.search_filter = ['none']
		else:
			self.search_filter = []

			for i in range(len(self.lf)):
				self.d_filter[self.lf[i]].set(True)
				self.search_filter.append(self.lf[i])

		s = "{0} files, search filters: {1}".format(self.searcher.total_work,self.search_filter)
		self.ptext.set(s)
		self.keyword.set(data_file)
				#print "filter:{0},value:{1}".format(self.lf[i],self.d_filter[self.lf[i]].get())

	def menu_popup(self,event,m):

		#The curselection return a tuple of the selected indexs
		sel = self.dirs.curselection()
		print "DEBUG sel=",sel
		if len(sel) == 1:
			check = self.dirs.get(self.dirs.curselection())
			m.post(event.x_root,event.y_root)
		else:
			pass
			#by nearest(click y point)to locate the line in the listbox
			#print "DEBUG-",self.dirs.nearest(event.y)
			#line_index = self.dirs.nearest(event.y)
			#self.dirs.selection_set(line_index,line_index)
			#self.dirs.config(selectbackground=my_color_blue)
			#m.post(event.x_root,event.y_root)

	def multi_open(self,ev=None):
		#print "DEBUG print list_var=",self.list_v.get()
		print "multi_open called"

		select_file_list = []
		index_list = self.dirs.curselection()
		for idx in index_list:
			select_file_list.append(self.dirs.get(idx))

		for file in select_file_list:
			file = file.encode('gb2312')
			cmd = [file]
			try:
				call_proc(cmd)
			except Exception as e:
				print "DEBUG call_proc error=",e
				self.dirs.config(selectbackground='red')

	def my_decode(self,ev=None):

		print "my_decode called"
		s = u"decoding is under process. please wait..."
		self.ptext.set(s)
		self.pro_label.update()

		select_file_list = []
		index_list = self.dirs.curselection()
		for idx in index_list:
			select_file_list.append(self.dirs.get(idx))

		my_decoder.decode_log(select_file_list)

		ds = ''
		if sla.interval > 1000:
			duration = sla.interval/60.0
			ds = "%.1f minutes"%(duration)
		else:
			duration = sla.interval * 1.0
			ds = "%.1f seconds"%(duration)
		print "Finished, time used:",ds

		s = "decode finished, time used:{0}".format(ds)
		self.ptext.set(s)
		self.refresh_listbox(os.getcwd())
		showinfo(title='Decode', message="Decode finished.")

	def my_repeat(self, ev=None):
		'''
		counting the repeated log occurences
		'''
		print "DEBUG my_repeat started here"
		s = u"Counting log repetition is under process. please wait..."
		self.ptext.set(s)
		self.pro_label.update()

		l_result = []

		select_file_list = []
		index_list = self.dirs.curselection()
		for idx in index_list:
			select_file_list.append(self.dirs.get(idx))

		top_rank = 5
		l_result = repeat_log.repeat_log_rank(select_file_list, top_rank)

		ds = ''
		if sla.interval > 1000:
			duration = sla.interval/60.0
			ds = "%.1f minutes"%(duration)
		else:
			duration = sla.interval * 1.0
			ds = "%.1f seconds"%(duration)
		print "Finished, time used:",ds
		s = "Repetition statistic finished, time used:{0}".format(ds)
		self.ptext.set(s)
		#self.refresh_listbox(os.getcwd())

		self.dirs.delete(0, END)
		self.dirs.insert(END, os.curdir)
		s = u"-----------Log Repetition Top %d--------------------"%(top_rank)
		self.dirs.insert(END,s)
		#self.show_result(l_result,{})
		for item in l_result:
			s = "repeated:[{0} times]: {1}".format(item[1],item[0])
			self.dirs.insert(END,s)
			self.dirs.itemconfig(END,fg=my_color_blue)


	def solo_search(self,ev=None):
		print "solo_search start"
		#multi selection
		#select_file_paths = []
		self.searcher.file_list = []
		index_list = self.dirs.curselection()
		for idx in index_list:
			#select_file_paths.append(self.dirs.get(idx))
			sla.get_file_list(self.dirs.get(idx),self.searcher.file_list)


		print "DEBUG select_file_list=",self.searcher.file_list
		self.searcher.total_work = len(self.searcher.file_list)
		self.do_search()

	def untar(self):
		#showinfo(title='Untar', message="To be done soon...")
		print "DEBUG untar is starting"
		path_list = []
		
		index_list = self.dirs.curselection()
		for idx in index_list:
			path_list.append(self.dirs.get(idx))

		s = u"{0} is under untar process. please wait...".format(path_list)
		self.ptext.set(s)
		self.pro_label.update()
		sleep(0.1)
		

		for filename in path_list:
			res = untar_function.untar_function(filename)
			if res[0]:
				break

		ds = ''
		if sla.interval > 1000:
			duration = sla.interval/60.0
			ds = "%.1f minutes"%(duration)
		else:
			duration = sla.interval * 1.0
			ds = "%.1f seconds"%(duration)
		print "Finished, time used:",ds
		s = "untar finished, time used:{0}".format(ds)
		self.ptext.set(s)

		self.refresh_listbox(os.getcwd())


		if not res[0]:
			showinfo(title='Untar', message="Untar Succeeded!")
		else:
			showinfo(title='Untar', message="Untar Failed! reason=%s"%res[0])

	#########menu function###############	

	###############Drag and Drop feature:########################
	def dnd_enable(self, widget):
		dd = dnd.DnD(self.top)

		def drag(action, actions, type, win, X, Y, x, y, data):
			return action

		def drag_enter(action, actions, type, win, X, Y, x, y, data):
			widget.focus_force()
			return action

		def drop(action, actions, type, win, X, Y, x, y, data):
			self.dirs.delete(1, END)
			self.searcher.file_list = []
			os_sep = os.path.sep
			for f in self.refine_data(data):
				if f.startswith('{'):
					#只去掉开头和结尾的{}，其他的{}不动
					#f = f.strip('{}')
					f = f[1:-1]
				#deal with file_list '/' with os.sep
				f = f.replace(r'/',os_sep)
				sla.get_file_list(f,self.searcher.file_list)
				#print "DEBUG self.searcher.file_list=",self.searcher.file_list
				widget.insert('end', f)
				if os.path.isdir(f):
					widget.itemconfig(END,fg = my_color_blue_office)
				else:
					pass

			self.searcher.total_work = len(self.searcher.file_list)

			#counting the total size of file_list:
			size_total = 0
			for i in xrange(len(self.searcher.file_list)):
				p = self.searcher.file_list[i]
				size_total = size_total + os.path.getsize(p)

			s = ''
			if size_total > 1024000000:
				s = "%.2f Gb"%(size_total/((1024*1024*1024)*1.0))
			elif size_total > 10240000:
				s = "%.1f Mb"%(size_total/(1024.0*1024))
			elif size_total > 10240:
				s = "%d Kb"%(size_total/1024.0)
			else:
				s = "%d bytes"%(size_total)

			s = "{0} files {1} dropped in".format(self.searcher.total_work,s)
			#print s
			self.ptext.set(s)

		dd.bindtarget(widget, 'text/uri-list', '<Drag>', drag, ('%A', '%a', '%T', '%W', '%X', '%Y', '%x', '%y', '%D'))
		dd.bindtarget(widget, 'text/uri-list', '<DragEnter>', drag_enter, ('%A', '%a', '%T', '%W', '%X', '%Y', '%x', '%y', '%D'))
		dd.bindtarget(widget, 'text/uri-list', '<Drop>', drop, ('%A', '%a', '%T', '%W', '%X', '%Y', '%x', '%y', '%D')) #Drag and Drop

	def refine_data(self, data):
		flag = 0
		for i in range(len(data)):
			if data[i] == '{':
				flag += 1
			elif data[i] == '}':
				flag -= 1
			
			if data[i] == ' ' and flag == 0:
				#print "DEBUG data[:i-1]",data[:i]
				data = data[:i] + "," + data[i+1:]

		l = data.split(',')
		return l
###############Drag and Drop feature:########################

	def syn_dir(self, path):
		#print "DEBUG syn_dir called"
		self.searcher.path = path
		self.searcher.file_list = sla.get_file_list(path,[])
		self.searcher.total_work = len(self.searcher.file_list)

	def listbox_click(self,event):
		print "listbox click"
		self.dirs.config(selectbackground=my_color_blue)
		#here can be choose only to search some specific files

	def listbox_Rclick(self,event,m):
		#实现右击弹出菜单，在选择的line上
		print "listbox R click"
		#print "DEBUG- y",self.dirs.nearest(event.y)
		last_index = self.dirs.nearest(event.y_root)
		#找到鼠标点击事件的y(行坐标)
		line_index = self.dirs.nearest(event.y)

		#multi selection	
		#self.dirs.selection_clear(0,last_index)
		self.dirs.selection_set(line_index,line_index)
		self.dirs.config(selectbackground=my_color_blue)

		#check untar possible:
		index_list = self.dirs.curselection()
		re_pattern = r'(\.tar\.gz$)|(\.gz$)|(\.tar$)|(\.tgz$)'
		for idx in index_list:
			path = self.dirs.get(idx)
			result = re.search(re_pattern, path)
			if not result:
				self.popup_menu.entryconfig("Unpack", state = "disable")
				break
		else:
			self.popup_menu.entryconfig("Unpack", state = "normal")

		#check decode possible:
		re_pattern = r'\.rtrc'
		for idx in index_list:
			path = self.dirs.get(idx)
			result = re.search(re_pattern, path)
			if (not result or path[-4:] == '.out')and not os.path.isdir(path):
				self.popup_menu.entryconfig("Decode", state = "disable")
				break
		else:
			self.popup_menu.entryconfig("Decode", state = "normal")

		#popup right contextual menu
		m.post(event.x_root,event.y_root)
#####################listbox_Rclick()###################################


	def setDirAndGo(self, ev=None):
		print "setDirAndGo"
		self.last = self.cwd.get()
		#self.dirs.config(selectbackground='red')
		self.dirs.config(selectbackground='LightSkyBlue')
		#self.dirs.config(selectbackground=my_color_blue)
		path = self.dirs.get(self.dirs.curselection())
		if not path:
			check = os.curdir
			print "DEBUG setDirAnd Go path error"

		self.cwd.set(path)
		#self.syn_dir(path)
		self.doLS()

	def doLS(self, ev=None):
		#print "DEBUG print list_var=",self.list_v.get()
		print "doLS called"
		error = ''
		tdir = self.cwd.get()
		if not tdir:
			tdir = os.curdir
		if not os.path.exists(tdir):
			error = tdir + ':no such file'
		elif not os.path.isdir(tdir):
			error = tdir + ':is not a directory!'
			if os.path.isfile(tdir):
				#print "This is a file!"	
				#here double click on a file and open it
				print "DEBUG tdir=",tdir
				#print "DEBUG type(tdir)=",type(tdir)
				tdir = tdir.encode('gb2312')
				#print "DEBUG type(tdir)=",type(tdir)
				cmd = [tdir]
				try:
					call_proc(cmd)
				except Exception as e:
					print "DEBUG call_proc error=",e
					self.dirs.config(selectbackground='red')
				return

		if error:
			self.cwd.set(error)
			self.top.update()
			print "DEBUG error in DoLS"
			sleep(0.2)

			#这个self.last是什么意思？
			if not (hasattr(self, 'last') and self.last):
				self.last = os.curdir
				self.cwd.set(self.last)
				#self.syn_dir(self.last)
				#self.dirs.config(selectbackground='LightSkyBlue')
				self.dirs.config(selectbackground='Red')
				self.top.update()
				return
		else:

			print "DEBUG DoLS directory:"
			#self.top.update()
			self.refresh_listbox(tdir)

		self.cwd.set(os.getcwd())
		self.syn_dir(os.getcwd())

		s = "{0} files selected. Filters: {1}".format(self.searcher.total_work,self.search_filter)
		self.ptext.set(s)
###############doLS()##########################################

	def refresh_listbox(self, dir_path):

		dirlist = os.listdir(dir_path)
		dirlist.sort()
		os.chdir(dir_path)
		#全部删除
		self.dirs.delete(0, END)
		#当前目录'.'
		#self.dirs.insert(END, os.curdir)
		#上一级目录'..'
		self.dirs.insert(END, os.pardir)
		for eachFile in dirlist:
			s = os.path.join(os.getcwd(),eachFile)
			#在listbox中显示中文, windows support gbk or gb2123 coding
			#bug5
			#s = s.decode('gb2312')
			s = s.decode('gb2312').encode('utf-8')
			self.dirs.insert(END, s)
			if os.path.isdir(s):
				self.dirs.itemconfig(END,fg= my_color_blue_office)
			self.dirs.config(selectbackground=my_color_blue)
####################refresh_listbox()#############################


	def get_default_keywords(self,ev=None):
		self.keyword.set(data_file)


	def auto_analyse(self):
		'''
		one key automated analysing the directory
		'''
		if True:
			self.do_search()
		else:
			#untar
			#decode
			#search
			pass


	#开启一个线程进行搜索关键字，防止主线程被挂起
	def do_search(self):
		global l_threads

		#There is a problem when no filter a crash will occur after do_search
		if self.search_filter[0] == 'none' and self.keyword.get() == data_file:
			showwarning(title='No filters', message="No keywords to search!")
			#self._Thread__stop()
			return

		print "Start thread search"
		t = threading.Thread(target=self.thread_search)

		#for terminating purpose
		l_threads.append(t)


		t.start()	
		#Bug, programme often crashed if no t.join()
		#t.join()

	def thread_search(self):
		global l_threads

		s = "Please wait..."	
		self.search_b.config(text=s,bg='orange',relief='sunken',state='disabled')
		self.popup_menu.entryconfig("Search", state="disable")
		#这个update不需要！加了反而有时候程序会崩溃
		#self.search_b.update()

		k = self.keyword.get()
		d_result = {}
		s = ""
		#default multi keywords search
		thread_num=1
		if k == data_file:

			self.show_progress()

			#only search those filtered keywords
			filtered_keywords = copy.deepcopy(self.searcher.l_keywords)
			for i in xrange(1,len(self.searcher.l_keywords)):
				if self.searcher.l_keywords[i][1] in self.d_filter:
					if self.d_filter[self.searcher.l_keywords[i][1]].get()=='0':
						filtered_keywords.remove(self.searcher.l_keywords[i])

			#Python GIL cause no multi threads running in parallel, so just one is OK and steady
			d_result = self.searcher.auto_search(filtered_keywords,self.searcher.file_list,thread_num)

			if self.searcher.total_work > 0:
				self.show_result(self.searcher.l_keywords, d_result)

			
			duration = 0
			ds = ''
			if sla.interval > 1000:
				duration = sla.interval/60.0
				ds = "%.1f minutes"%(duration)
			else:
				duration = sla.interval * 1.0
				ds = "%.1f seconds"%(duration)

			s_filters = ''
			for i,v in self.d_filter.items():
				if v.get() == '1':
					s_filters = s_filters + ', '+ i
			s_filters = s_filters.strip(", ")

			if s_filters.strip() == '':
				s_filters = "None"

			s = "%d files, %d keywords analysed in %s, filters: '%s'."%(\
				self.searcher.total_work,len(filtered_keywords)-1,ds, s_filters)
			#print s
			self.ptext.set(s)
			
		else:
			#custom seartch
			print "custom search started!"
			self.show_progress()
			custom_keyword = copy.deepcopy(self.searcher.l_keywords[:2])
			custom_keyword[1][0]=k
			d_result = self.searcher.auto_search(custom_keyword,self.searcher.file_list,thread_num)

			if self.searcher.total_work > 0:
				self.show_result(custom_keyword, d_result)

			#prevent show_progress finished after the main process
			sleep(0.2)
			s = "%d files, keyword='%s'analysed in %.2f seconds."%(\
				self.searcher.total_work,self.keyword.get(),sla.interval)
			self.ptext.set(s)

		self.search_b.config(text='Start search',bg='white',relief='raised',state='normal')
		self.popup_menu.entryconfig("Search", state="normal")
		#clean the threads list:
		l_threads = []

	def show_result(self, key_words, d_result):
	 	#写入dirs
		self.dirs.delete(0, END)
		self.dirs.insert(END, os.curdir)
		no_find = True
		s = u"-----------Searching Result--------------------"
		self.dirs.insert(END,s)
		j = 0
		for i in xrange(1,len(key_words)):
			nn = 0
			lk = key_words[i]
			if key_words[i][0] in d_result:
				nn = len(d_result[lk[0]])
			if nn > 0:
				no_find = False
				j = j+1
				#s = self.searcher.l_keywords[i][0]
				#self.dirs.insert(END,s)
				s =u"[keyword]:{0}".format(lk[0])
				self.dirs.insert(END,s)
				self.dirs.itemconfig(END,fg=my_color_blue)
				issue_category = lk[5].decode("gb2312")#.encode("utf-8")
				#s =u"issue category:---{0}---".format(lk[4])
				s =u"[Issue Category]:{0}".format(issue_category)
				self.dirs.insert(END,s)
				s =u"[Occurences]:{0}".format(nn)
				self.dirs.insert(END,s)
				#self.dirs.itemconfig(END,fg=my_color_blue)
				#if lk[3].strip() != '':
				#	lk[3]=lk[3].encode('utf-8')
				#	s =lk[3]
				#	self.dirs.insert(END,s)
				for file in d_result[lk[0]]:
					s = file
					self.dirs.insert(END,s)
				#s = "-"*20
				s = ' '
				self.dirs.insert(END,s)
		if no_find:
			if self.keyword.get() != data_file:
				s = u"没有发现含有关键字'{0}'的文件, No findings".format(self.keyword.get())
			else:
				s = u"没有发现含有任何关键字, No findings"
			self.dirs.insert(END,s)
###############show_result#######################

	def show_progress(self):

		global l_threads

		sla.progress_q.queue.clear()
		tp = threading.Thread(target=self.progress)

		l_threads.append(tp)
		tp.start()
		#t.join()

	def progress(self):
		print "DEBUG progress started"
		n = 0
		s = ""
		#这里不知道为什么progress_q有东西拿不出来block住了
		#所以用try直接忽略
		s = "Start to analyse %d files"%(self.searcher.total_work)
		#print s
		self.ptext.set(s)
		#self.pro_label.update()
		
		print "self.searcher.total_work=",self.searcher.total_work
		print "n=",n
		try:
			while n < self.searcher.total_work:
				#file = self.searcher.progress_q.get(True,3)
				#file = self.searcher.progress_q.get()
				file = sla.progress_q.get()
				#print "get",file
				n += 1
				#Update the label
				s = "Analysing: [%d/%d] %s"%(n,self.searcher.total_work,file)
				self.ptext.set(s)
				#self.pro_label.update()
		except Exception as e:
			sla.logger.warning(e)
			#print e
			s = "Analysing...progress label got some problem"
			self.ptext.set(s)
			print "DEBUG error progress label got problems,e=",e
			#self.pro_label.update()


	def _async_raise(self,tid, exctype):
		"""raises the exception, performs cleanup if needed"""
		tid = ctypes.c_long(tid)
		if not inspect.isclass(exctype):
			exctype = type(exctype)
		res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
		if res == 0:
			raise ValueError("invalid thread id")
		elif res != 1:
			# """if it returns a number greater than one, you're in trouble,
			# and you should call it again with exc=NULL to revert the effect"""
			ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
			raise SystemError("PyThreadState_SetAsyncExc failed")


	def terminate_threads(self):
		'''
		强制终止线程
		'''
		global l_threads
		if l_threads:
			for th in l_threads:
				if th.is_alive():
					self._async_raise(th.ident, SystemExit)

		self.search_b.config(text='Start search',bg='white',relief='raised',state='normal')
		self.popup_menu.entryconfig("Search", state="normal")
		sla.progress_q.queue.clear()
		l_threads = []
		#s = "{0} files, search filters: {1}".format(self.searcher.total_work,self.search_filter)
		#self.ptext.set(s)
		s = "stopped"
		self.ptext.set(s)
		self.doLS()
		sleep(0.5)

#################progress############################

def main():
	
	d = DirList(os.getcwd())
	d.top.mainloop()


if __name__ == '__main__':
	main()		


