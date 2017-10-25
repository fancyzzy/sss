#!/usr/bin/env python
# --*-- coding:utf-8 --*--


#import os
#this package make Tkinter in python2 thread-safe!
#effectively decreas the crash occurance.
import mttkinter as Tkinter
from time import sleep
from datetime import datetime
from Tkinter import *
from ttk import Combobox
from tkMessageBox import *
from Dialog import *
import sla_multi_threads as sla 
import threading
import dnd
import copy
import ctypes
import inspect
import RTTP_decoder
from  my_resources import *
import my_decoder
import re
import repeat_log
import multi_operates
import time
import my_ftp
import tooltip
import tkFileDialog

FTP_TOP = None
SEARCH_RESULT_LIST = []
NO_KEYWORD_FIND = True

class DirList(object):
	def __init__(self, initdir=None):
		self.top = Tk()
		self.top.geometry('850x560+280+140')
		self.top.wm_title("SLA2.4")

		Label(self.top, text='').pack()

		self.label_title = Label(self.top, text='Site Log Analyzer v2.4',\
			font = ('Helvetica', 12, 'bold'), fg= my_color_blue_office)
		self.label_title.pack()

		self.top.iconbitmap(icon_path)

		fm_directory = Frame(self.top)
		self.entry_label = Label(fm_directory, text="Search in: ")
		self.cwd = StringVar(self.top)
		self.entry_dir = Entry(fm_directory, width=80, textvariable=self.cwd)
		self.entry_dir.bind('<Return>', self.doLS)
		self.button_dir = Button(fm_directory, text='List directory', \
			command=self.open_dir, activeforeground='white', activebackground='orange')
		self.button_dir.pack(side=RIGHT)
		self.entry_label.pack(side=LEFT)
		self.entry_dir.pack(side=LEFT)
		fm_directory.pack()	

		fm_listbox = Frame(self.top)
		self.listbox_dirsby = Scrollbar(fm_listbox)
		self.listbox_dirsby.pack(side=RIGHT, fill=Y)
		#self.listbox_dirsbx = Scrollbar(fm_listbox,orient=HORIZONTAL)
		#self.listbox_dirsbx.pack(side=BOTTOM, fill=X)

		self.list_v = StringVar()
		#selectmode=EXTENDED,BROWSE,MULTIPLE,SINGLE
		#exportselection is used to enable "ctrl+c" to copy the content selected 
		#in the listbox into the windows clipboard when =1
		self.listbox_dirs = Listbox(fm_listbox, height=25, width=130, selectmode=EXTENDED,\
			exportselection=1,listvariable=self.list_v)
		#2017.8.23 BUG: 滚动轴导致程序挂掉，原因可能是由于多线程子线程更新GUI界面
		#产生内部错误导致
		#2017.10.25,fixthis BUG, 要想thread-safe，使用python3，或者使用mttkinter模块！
		self.listbox_dirs.bind('<Double-1>', self.setDirAndGo)
		self.listbox_dirs.bind('<1>', lambda event:self.listbox_click(event))
		self.listbox_dirs.bind('<ButtonRelease-1>', lambda event:self.listbox_click_release(event))
		self.listbox_dirs.bind('<Return>', self.setDirAndGo)
		#self.listbox_dirs.bind('<Return>', self.start_thread_analyse)
		#self.listbox_dirs.bind('<3>', self.listbox_Rclick)
		self.listbox_dirs['yscrollcommand'] = self.listbox_dirsby.set
		self.listbox_dirsby.config(command=self.listbox_dirs.yview)
		#self.listbox_dirs['xscrollcommand'] = self.listbox_dirsbx.set
		#self.listbox_dirsbx.config(command=self.listbox_dirs.xview)
		self.listbox_dirs.pack(expand=YES, fill=BOTH)
		self.listbox_dirs.focus_set()
		fm_listbox.pack(expand=YES,fill=BOTH)

		fm_search = Frame(self.top)
		label_search = Label(fm_search, text="Search for: ")
		self.keyword = StringVar(self.top)
		self.keyword.set(PREDIFINED_KEYWORD)
		self.combo_search = Combobox(fm_search, width=30,textvariable=self.keyword)
		self.combo_search.bind('<KeyPress-Escape>', self.get_default_keywords)

		s = "keywords.csv is the predefined keywords data\nyou can input a specific keyword\nclick 'esc' for default"
		tooltip.ToolTip(self.combo_search, msg=None, msgFunc=lambda : s, follow=True, delay=0.2)

		#read the first 10 custom keywords in history file 'custom_keyword.txt'
		self.ck_list = []
		self.ck_list = get_custom_keyword()
		if self.ck_list:
			value = self.ck_list[-10:]
			value.reverse()
			self.combo_search['values'] = value
			self.ck_list = []
		else:
			self.ck_list = []

		label_search.pack(side=LEFT)
		self.combo_search.pack(side=LEFT)

		#feature files type filtering
		Label(fm_search, text="in files of: ").pack(side=LEFT)			
		self.v_files_types = StringVar()
		self.v_files_types.set('.*\.txt;.*\.out')
		self.entry_files_type = Entry(fm_search, width=30, textvariable=self.v_files_types)
		self.entry_files_type.pack(side=LEFT)

		fs = "Refer to Python Regular Expression\n '.*'means any characters\n use ';' to seperate"
		tooltip.ToolTip(self.entry_files_type, msg=None, msgFunc=lambda : fs, follow=True, delay=0.2)

		#terminate button
		self.stop_b = Button(fm_search, text="Stop", command=self.terminate_threads)
		self.stop_b.pack(side=RIGHT)
		#search start button
		self.search_b = Button(fm_search, text="Auto analyse", command=self.start_thread_analyse, activeforeground\
			='white', activebackground='orange',bg = 'white', relief='raised', width=10)
		self.search_b.pack(side=RIGHT)
		fm_search.pack()

		tooltip.ToolTip( self.search_b, msg=None, msgFunc=\
			lambda : 'To unpack, decode and search the selected files or directories', \
			follow=True, delay=0.2)


		self.pro_fm = Frame(self.top)
		self.ptext = StringVar()
		self.ptext.set("")
		self.pro_label = Label(self.pro_fm, textvariable=self.ptext,justify='left')
		self.pro_label.grid(row=0,column=0)#.pack(side=LEFT)

		self.pro_fm.pack(side=LEFT)


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

		#decode menue
		menubar.add_command(label = 'FTP', command=self.menu_start_monitor_ftp_download)

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
		self.popup_menu.add_command(label='Open folder',command=self.folder_open)
		self.popup_menu.add_separator()
		self.popup_menu.add_command(label='Unpack',command=self.untar)
		self.popup_menu.add_separator()
		self.popup_menu.add_command(label='Search',command=self.start_file_search)
		self.popup_menu.add_separator()
		self.popup_menu.add_command(label='Decode',command=self.my_decode)
		self.popup_menu.add_separator()
		self.popup_menu.add_command(label='Repetion',command=self.my_repeat)
		#popup_menu.entryconfig("Open", state="disable")
		############# menu init ################################

		#MAC OS GUI
		if (self.top.tk.call('tk','windowingsystem')=='aqua'):
			self.listbox_dirs.bind('<3>', lambda event: self.listbox_Rclick(event,self.popup_menu))
			self.listbox_dirs.bind('<Control-1>', lambda event: self.listbox_Rclick(event,self.popup_menu))
		#Win32
		else:
			#右击可以弹出菜单，用lambda的写法可以传递参数
			self.listbox_dirs.bind('<3>', lambda event: self.listbox_Rclick(event,self.popup_menu))


		if initdir:
			#self.cwd.set(os.getcwd())
			#desktop is default path
			#print "DEBUG sla.desktop_path=",sla.desktop_path
			self.cwd.set(DESKTOP_PATH)
			self.menu_selectall()
			self.doLS()

		self.dnd_enable(self.listbox_dirs)


	############# menu function ###############

	def menu_keywords(self):

		kdir = os.path.join(WORKING_PATH,PREDIFINED_KEYWORD)
		cmd = [kdir]
		try:
			multi_operates.call_proc(cmd)
		except Exception as e:
			print "DEBUG call_proc error=",e
			self.listbox_dirs.config(selectbackground='red')


	def menu_decode_log(self):
		#新建一个隶属于self.top的子窗口
		#会随着主窗口关闭而关闭
		#decode_top = Toplevel(self.top)
		decode_window = RTTP_decoder.rttp(self.top)
		#sleep(3)
		#decode_window.decode_top.destroy()
		#decode_window.decode_top.bell()


	def monitor_ftp_download(self, ftp_top):
		global SEARCH_RESULT_LIST
		global NO_KEYWORD_FIND

		print("DEBUG monitor_ftp_download start")
		while 1:
			if not ftp_top.running:
				break
			else:
				if my_ftp.AUTOANA_ENABLE:
					#here should add mutext to dirlist or ptext or something 
					#which maybe used by auto_analyse
					s = "Now detecting ftp downloaded files..."
					self.ptext.set(s)
					print("DEBUG wating to get file_path from FTP QUEUE..")
					file_path = my_ftp.FTP_FILE_QUE.get()
					print("DEBUG get! file_path = ",file_path)
					#exit this circle
					if 'ftp quit' in file_path:
						break
					#display on the dirlist
					self.listbox_dirs.delete(0, END)
					current_dir = os.curdir.encode('gb2312').decode('utf-8')
					self.listbox_dirs.insert(END, current_dir)
					s = file_path.encode('gb2312').decode('utf-8')
					self.listbox_dirs.insert(END,s)

					#start search
					self.auto_analyse([file_path], PRE_KEYWORD_LIST)
					self.start_thread_progressbar()

					#record result in the file_path as a format of xx.res
					result_file = ''
					if os.path.isdir(file_path):
						result_file = os.path.join(file_path, 'search_result.txt')
					else:
						result_file = os.path.join(\
							os.path.dirname(file_path), 'search_result.txt')
					record_result(SEARCH_RESULT_LIST, result_file)

					#send email
					if not NO_KEYWORD_FIND:
						print("DEBUG keyword find result=", multi_operates.search_result)
						print("Result has been saved in %s" % result_file)
						NO_KEYWORD_FIND = True
					else:
						print("DEBUG no keyword found")
				else:
					pass

		print("DEBUG monitor_Ftp_download quit")
		s = "Detecting stopped"
		self.ptext.set(s)
		return
	####################monitor_ftp_download()#######################


	def menu_start_monitor_ftp_download(self):
		global FTP_TOP
		global l_threads
		print "hello this is ftp function"
		
		#how to singleton?
		ftp_top = my_ftp.My_Ftp(self.top)
		FTP_TOP = ftp_top
		if FTP_TOP:
			t = threading.Thread(target=self.monitor_ftp_download, args=(ftp_top,))
			l_threads.append(t)
			t.start()	
		else:
			print("DEBUG FTP_TOP none error")
	##########menu_start_monitor_ftp_download()#############


	def menu_about(self):
		s = askyesnocancel(title='about', message = "SLA - Site Log Analyser v2.4, any idea, just feedback to us:",\
			detail="felix.zhang@nokia-sbell.com\nirone.li@nokia-sbell.com\neric.a.zhu@nokia-sbell.com\nbella.sun@nokia-sbell.comn\n\
			QD GSM-A All Rights Reserved",icon=INFO)
		'''
		d = Dialog(None,title='about',text="SLA - Site Log Analyser v2.1\
			\nAny idea, just feedback to us:\nfelix.zhang@nokia-sbell.com\
			\nirone.li@nokia-sbell.com\neric.a.zhu@nokia-sbell.com",bitmap=DIALOG_ICON,default=0,strings=('OK','no'))
		d.num
		'''

	def menu_howto(self):
		s = askyesno(title='How To', message = "把要分析的trace文件夹直接拖放到显示目录框中，点击'Auto analyse'\n简单吧?\n")
		if s:
			print s
		else:
			print "no s=",s

	def filter_keyword(self):
		'''
		filter the keyword list according to d_filter
		'''
		global PRE_KEYWORD_LIST
		pre_k = PRE_KEYWORD_LIST

		filtered_keyword_list = copy.deepcopy(pre_k)

		k = self.keyword.get()
		if k == PREDIFINED_KEYWORD:
			ln = len(pre_k)
			for i in xrange(ln):
				if pre_k[i][1] in self.d_filter:
					if self.d_filter[pre_k[i][1]].get()=='0':
						filtered_keyword_list.remove(pre_k[i])
				#print 'DEBUG filtered keyword_list=',filtered_keyword_list

		else:
			filtered_keyword_list[0][0] = k
			filtered_keyword_list[0][5] = "customized keyword"
			return filtered_keyword_list[:1]

		return filtered_keyword_list

	def menu_filter(self):
		self.search_filter=[]
		for fi,va in self.d_filter.items():
			if va.get() == '1':
				self.search_filter.append(fi)
		s = "{0} items. keyword filters: {1}".format(self.searcher.total_work,self.search_filter)
		self.ptext.set(s)

		self.keyword.set(PREDIFINED_KEYWORD)

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

		s = "{0} items. Keyword filters: {1}".format(self.searcher.total_work,self.search_filter)
		self.ptext.set(s)
		self.keyword.set(PREDIFINED_KEYWORD)
		#print "filter:{0},value:{1}".format(self.lf[i],self.d_filter[self.lf[i]].get())

	def menu_popup(self,event,m):

		#The curselection return a tuple of the selected indexs
		sel = self.listbox_dirs.curselection()
		if len(sel) == 1:
			check = self.listbox_dirs.get(self.listbox_dirs.curselection())
			m.post(event.x_root,event.y_root)
		else:
			pass
			#by nearest(click y point)to locate the line in the listbox
			#print "DEBUG-",self.listbox_dirs.nearest(event.y)
			#line_index = self.listbox_dirs.nearest(event.y)
			#self.listbox_dirs.selection_set(line_index,line_index)
			#self.listbox_dirs.config(selectbackground=my_color_blue)
			#m.post(event.x_root,event.y_root)

	def folder_open(self,ev=None):
		#print "DEBUG print list_var=",self.list_v.get()
		print "folder_open called"

		select_file_list = []
		index_list = self.listbox_dirs.curselection()
		for idx in index_list:
			select_file_list.append(self.listbox_dirs.get(idx))

		for file in select_file_list:
			file = file.encode('gb2312')
			p_folder = os.path.dirname(file)
			cmd = ['start',p_folder]
			try:
				multi_operates.call_proc(cmd)
			except Exception as e:
				print "DEBUG call_proc error=",e
				self.listbox_dirs.config(selectbackground='red')
			else:
				break
				pass

	def my_decode(self,ev=None):
		print "my_decode called"
		s = u"decoding is under process. please wait..."
		self.ptext.set(s)
		self.pro_label.update()

		select_file_list = []
		index_list = self.listbox_dirs.curselection()
		for idx in index_list:
			select_file_list.append(self.listbox_dirs.get(idx))

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
		s = u"Counting log repetition is under process. please wait..."
		self.ptext.set(s)
		self.pro_label.update()

		l_result = []

		select_file_list = []
		index_list = self.listbox_dirs.curselection()
		for idx in index_list:
			select_file_list.append(self.listbox_dirs.get(idx))

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

		self.listbox_dirs.delete(0, END)
		self.listbox_dirs.insert(END, os.curdir)
		s = u"-----------Log Repetition Top %d--------------------"%(top_rank)
		self.listbox_dirs.insert(END,s)
		#self.show_result(l_result,{})
		for item in l_result:
			s = "repeated:[{0} times]: {1}".format(item[1],item[0])
			self.listbox_dirs.insert(END,s)
			self.listbox_dirs.itemconfig(END,fg=my_color_blue)

	def untar(self):
		#showinfo(title='Untar', message="To be done soon...")
		path_list = []
		
		index_list = self.listbox_dirs.curselection()
		for idx in index_list:
			path_list.append(self.listbox_dirs.get(idx))


		s = u"{0} is under untar process. please wait...".format(path_list)
		self.ptext.set(s)
		self.pro_label.update()
		sleep(0.1)
		
		multi_operates.files_unpack(path_list)

		s = "untar finished, time used:{0}".format(multi_operates.used_time())
		self.ptext.set(s)

		new_path = os.path.dirname(path_list[-1])
		self.refresh_listbox(new_path)
		showinfo(title='Untar', message="Untar Finished!")
	#############context menu function#############################

	###############Drag and Drop feature:########################
	def dnd_enable(self, widget):
		dd = dnd.DnD(self.top)

		def drag(action, actions, type, win, X, Y, x, y, data):
			return action

		def drag_enter(action, actions, type, win, X, Y, x, y, data):
			widget.focus_force()
			return action

		def drop(action, actions, type, win, X, Y, x, y, data):
			self.listbox_dirs.delete(1, END)
			self.searcher.file_list = []
			os_sep = os.path.sep
			refined_data = self.refine_data(data)
			#for f in refine_data(data):
			for f in refined_data:
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

			#self.searcher.total_work = len(self.searcher.file_list)
			self.searcher.total_work = len(refined_data)

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
	###############Drag and Drop feature:########################

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
		self.searcher.path = path
		#not recursion all the files
		#self.searcher.file_list = sla.get_file_list(path,[])
		self.searcher.file_list = os.listdir(path)
		self.searcher.total_work = len(self.searcher.file_list)

	def listbox_click(self,event):
		print "listbox L click"
		self.listbox_dirs.config(selectbackground=my_color_blue)
		#this function is ahead of dirlist selection
		#so can't get the selection from this function
		#use click release function
		#sel = self.listbox_dirs.curselection()
		#print("DEBUG sel=",sel)

	def listbox_click_release(self, event):
		print("click release")
		#this function triggered is behind of dirlist selection
		#Thus, we can get the selections
		sel = self.listbox_dirs.curselection()
		select_path_list = []
		index_list = self.listbox_dirs.curselection()
		for idx in index_list:
			select_path_list.append(self.listbox_dirs.get(idx))

		ln = len(select_path_list)
		s = "{0} of {1} items selected. Keyword filters: {2}".\
		format(ln, self.searcher.total_work,self.search_filter)
		self.ptext.set(s)

		'''
		file_list = []
		for file_path in select_path_list:
			file_list.extend(sla.get_file_list(file_path,[]))
		print("DEBUG file_list=",file_list)
		s_total = get_file_list_size(file_list)
		print("DEBUG size total=",s_total)
		'''
	###########listbox_click_release()###########


	def listbox_Rclick(self,event,m):
		#实现右击弹出菜单，在选择的line上
		print "listbox R click"
		#print "DEBUG- y",self.listbox_dirs.nearest(event.y)
		last_index = self.listbox_dirs.nearest(event.y_root)
		#找到鼠标点击事件的y(行坐标)
		line_index = self.listbox_dirs.nearest(event.y)

		#multi selection	
		#self.listbox_dirs.selection_clear(0,last_index)
		self.listbox_dirs.selection_set(line_index,line_index)
		self.listbox_dirs.config(selectbackground=my_color_blue)

		#check untar possible:
		index_list = self.listbox_dirs.curselection()
		re_pattern = r'(\.tar\.gz$)|(\.gz$)|(\.tar$)|(\.tgz$)'
		for idx in index_list:
			path = self.listbox_dirs.get(idx)
			result = re.search(re_pattern, path)
			if not result:
				self.popup_menu.entryconfig("Unpack", state = "disable")
				break
		else:
			self.popup_menu.entryconfig("Unpack", state = "normal")

		#check decode possible:
		re_pattern = r'\.rtrc'
		for idx in index_list:
			path = self.listbox_dirs.get(idx)
			result = re.search(re_pattern, path)
			if (not result or path[-4:] == '.out')and not os.path.isdir(path):
				self.popup_menu.entryconfig("Decode", state = "disable")
				break
		else:
			self.popup_menu.entryconfig("Decode", state = "normal")

		#popup right contextual menu
		m.post(event.x_root,event.y_root)
#####################listbox_Rclick()###################################

	def open_dir(self,ev=None):
		p = tkFileDialog.askdirectory()  # 返回目录路径
		print("open directory:",p)
		if 'unicode' in str(type(p)):
			p = p.encode('utf-8')#.decode('gb2312')
		elif 'str' in str(type(p)):
			p = p.decode('utf-8')

		print(p)
		self.cwd.set(p)
		self.doLS()
	######open_dir()##############


	def setDirAndGo(self, ev=None):
		print "setDirAndGo"
		self.last = self.cwd.get()
		#self.listbox_dirs.config(selectbackground='red')
		self.listbox_dirs.config(selectbackground='LightSkyBlue')
		#self.listbox_dirs.config(selectbackground=my_color_blue)
		path = self.listbox_dirs.get(self.listbox_dirs.curselection())
		if not path:
			check = os.curdir
			print "DEBUG setDirAnd Go path error"

		#bug 11
		if "str" in str(type(path)):
			path = path.decode('utf-8')
		self.cwd.set(path)
		#self.syn_dir(path)
		self.doLS()

	def doLS(self, ev=None):
		global FTP_TOP
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
				#bug11
				#print "This is a file!"	
				#here double click on a file and open it
				#print "DEBUG type(tdir)=",type(tdir)
				tdir = tdir.encode('gb2312')
				#print "DEBUG type(tdir)=",type(tdir)
				cmd = [tdir]
				try:
					multi_operates.call_proc(cmd)
				except Exception as e:
					print "DEBUG call_proc error=",e
					self.listbox_dirs.config(selectbackground='red')
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
				#self.listbox_dirs.config(selectbackground='LightSkyBlue')
				self.listbox_dirs.config(selectbackground='Red')
				self.top.update()
				return
		else:

			#self.top.update()
			self.refresh_listbox(tdir)

		self.cwd.set(os.getcwd())
		self.syn_dir(os.getcwd())

		s = "{0} items. Keyword filters: {1}".format(self.searcher.total_work,self.search_filter)
		self.ptext.set(s)
###############doLS()##########################################

	def refresh_listbox(self, dir_path):

		#print "DEBUG dir_path=",dir_path
		#print"DEBUG type(dir_path) = ",type(dir_path)
		dirlist = os.listdir(dir_path)
		dirlist.sort()
		os.chdir(dir_path)
		#全部删除
		self.listbox_dirs.delete(0, END)
		#当前目录'.'
		#self.listbox_dirs.insert(END, os.curdir)
		#上一级目录'..'
		parent_dir = os.pardir.encode('gb2312').decode('utf-8')
		self.listbox_dirs.insert(END, parent_dir)

		#bug 11
		#print"DEBUG type(dirlist[0]) = ",type(dirlist[0])
		v_cwd = os.getcwd().decode('gb2312').encode('utf-8')
		for eachFile in dirlist:
			#s = os.path.join(os.getcwd(),eachFile)
			if 'unicode' in str(type(eachFile)):
				eachFile = eachFile.encode('utf-8')
			elif 'str' in str(type(eachFile)):
				#eachFIle = eachFile.decode('gb2312').encode('utf-8')
				#print("DEBUG after, type=",type(eachFile))
				pass
			s = os.path.join(v_cwd,eachFile)
			#s = os.path.join(v_cwd,eachFile.encode('utf-8'))
			#在listbox中显示中文, windows support gbk or gb2123 coding
			#bug5
			self.listbox_dirs.insert(END, s)
			if os.path.isdir(s):
				self.listbox_dirs.itemconfig(END,fg= my_color_blue_office)
			self.listbox_dirs.config(selectbackground=my_color_blue)
####################refresh_listbox()#############################

	def get_default_keywords(self,ev=None):
		self.keyword.set(PREDIFINED_KEYWORD)
############get_default_keywords()###############


	def start_thread_analyse(self,ev=None):
		global l_threads

		select_path_list = []
		index_list = self.listbox_dirs.curselection()
		for idx in index_list:
			select_path_list.append(self.listbox_dirs.get(idx))

		if len(select_path_list) > 0:

			#Check if keyword is filtered by filters or customized keyword
			filtered_keyword_list = self.filter_keyword()

			t = threading.Thread(target=self.auto_analyse, args=(select_path_list, filtered_keyword_list))
			#for terminating purpose
			l_threads.append(t)
			t.start()	

			self.start_thread_progressbar()

		else:
			print "No file selected"
##########start_thread_analyse()###############


	def auto_analyse(self, path_list, keyword_list):
		'''
		one key automated analysing the directory
		'''
		print "auto_analyse start:"
		self.search_b.config(text="Please wait...",bg='orange',relief='sunken',state='disabled', width=10)
		self.popup_menu.entryconfig("Search", state="disable")

		########multi_operates 1.unpack, 2.decode, 3.search###############
		files_types_list = self.v_files_types.get().strip().split(';')
		search_result,searched_number = \
		multi_operates.do_operates(path_list, keyword_list, files_types_list)

		multi_operates.PROGRESS_QUE.put("Analysing finished, generating results...")
		self.show_result(keyword_list, multi_operates.search_result)
		
			#send 'All done flag to listdir.py'
		s = 'All done, %d files, %d keywords analysed in %s'\
		 %(searched_number, len(keyword_list), multi_operates.used_time())
		multi_operates.PROGRESS_QUE.put(s)

		self.search_b.config(text="Auto analyse",bg='white',relief='raised',state='normal')
		self.popup_menu.entryconfig("Search", state="normal")
		print "auto_analyse finished"
		#sound a bell
		self.label_title.bell()
################auto_ananlyse()#########################


	def start_thread_progressbar(self):
		global l_threads
		t = threading.Thread(target=self.progressbar)
		l_threads.append(t)
		t.start()
##################start_thread_progressbar()##########


	def progressbar(self):
		global l_threads

		print "progressbar start"
		n = 0
		s = "Analsis begins"
		self.ptext.set(s)
		#self.pro_label.update()

		pq = multi_operates.PROGRESS_QUE
		
		while 1:
			alive_number = 0
			for thread_x in l_threads:
				if thread_x.is_alive():
					alive_number += 1
			if alive_number <= 1 and pq.empty():
				break
			else:
				#bug 11
				#s = pq.get()
				s = pq.get(True,20)
				self.ptext.set(s)
				if "start" in s:
					sleep(0.2)
				if "finished" in s:
					sleep(0.5)

				#bug 11
				if "All done" in s:
					break
		print "progressbar end"
		return
##################progressbar()################################


	#开启一个线程进行搜索关键字，防止主线程被挂起
	def start_file_search(self,ev=None):
		global l_threads

		print "Start_file_search"
		#There is a problem when no filter a crash will occur after do_search
		if self.search_filter[0] == 'none' and self.keyword.get() == PREDIFINED_KEYWORD:
			showwarning(title='No filters', message="No keywords to search!")
			#self._Thread__stop()
			return

		select_path_list = []
		index_list = self.listbox_dirs.curselection()
		for idx in index_list:
			select_path_list.append(self.listbox_dirs.get(idx))

		if len(select_path_list) > 0:

			filtered_keyword_list = self.filter_keyword()
			t = threading.Thread(target=self.file_search, \
				args=(select_path_list, filtered_keyword_list))
			l_threads.append(t)
			t.start()	

			self.start_thread_progressbar()
		else:
			print("DEBUG no item seleted")


	def file_search(self,path_list, keyword_list):
		global l_threads

		s = "Please wait..."	
		self.search_b.config(text=s,bg='orange',relief='sunken',state='disabled')
		self.popup_menu.entryconfig("Search", state="disable")

		#use multi_operates:
		multi_operates.PROGRESS_QUE.put("Search start")
		files_types_list = self.v_files_types.get().strip().split(';')
		search_result,searched_number = \
		multi_operates.files_search(path_list, keyword_list, files_types_list)
		multi_operates.PROGRESS_QUE.put("Search finished, generating results...")

		self.show_result(keyword_list, search_result)

		s = 'All done, %d files, %d keywords searched in %s'\
		 %(searched_number, len(keyword_list), multi_operates.used_time())
		multi_operates.PROGRESS_QUE.put(s)

		self.search_b.config(text="Auto analyse",bg='white',relief='raised',state='normal')
		self.popup_menu.entryconfig("Search", state="normal")
		self.label_title.bell()
		print "file_search finished"

	##################file_search()#########################


	def show_result(self, key_words, d_result, is_incompleted = False):
		global SEARCH_RESULT_LIST
		global NO_KEYWORD_FIND
		srl = SEARCH_RESULT_LIST
		srl[:] = []
	 	#写入dirs
		ln = len(key_words)
	 	print('  show_result start')
		self.listbox_dirs.delete(0, END)
		current_dir = os.curdir.encode('gb2312').decode('utf-8')
		#self.listbox_dirs.insert(END, os.curdir)
		self.listbox_dirs.insert(END, current_dir)
		srl.append(current_dir)
		no_find = True
		s = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		self.listbox_dirs.insert(END,s)
		if ln > 1:
			s = u" Predefined Keywords Searching"
		else:
			s = u" Customed Keyword Searching"

		s = s + '(' + self.v_files_types.get() + ') ' + 'Results:'

		if is_incompleted:
			s = '(incompleted)'+ s

		self.listbox_dirs.insert(END,s)
		srl.append(s)
		

		j = 0
		for i in range(ln):
			nn = 0
			lk = key_words[i]
			if key_words[i][0] in d_result:
				nn = len(d_result[lk[0]])
			if nn > 0:
				no_find = False
				j = j+1
				#s = self.searcher.l_keywords[i][0]
				#self.listbox_dirs.insert(END,s)
				s =u"[{0}.keyword]:{1}".format(i,lk[0])
				self.listbox_dirs.insert(END,s)
				srl.append(s)
				self.listbox_dirs.itemconfig(END,fg=my_color_blue)
				issue_category = lk[5].decode("gb2312")#.encode("utf-8")
				#s =u"issue category:---{0}---".format(lk[4])
				s =u"[Issue Category]:{0}".format(issue_category)
				self.listbox_dirs.insert(END,s)
				srl.append(s)
				s =u"[File Occurence]:{0}".format(nn)
				self.listbox_dirs.insert(END,s)
				srl.append(s)
				#self.listbox_dirs.itemconfig(END,fg=my_color_blue)
				#if lk[3].strip() != '':
				#	lk[3]=lk[3].encode('utf-8')
				#	s =lk[3]
				#	self.listbox_dirs.insert(END,s)
				for file in d_result[lk[0]]:
					s = file
					if not s:
						print "DEBUG s= None:",s
					try:
						sleep(0.01)
						self.listbox_dirs.insert(END,s)
						srl.append(s)
					except Exception as e:
						print 'error here e=',e
						print "insert(END,s) where s=",s
				#s = "-"*20
				s = ' '
				self.listbox_dirs.insert(END,s)
				srl.append(s)
		s = "-"*20 + u"totally {0} keywords occured!".format(j) + "-"*20
		self.listbox_dirs.insert(END,s)
		srl.append(s)
		if no_find:
			if self.keyword.get() != PREDIFINED_KEYWORD:
				s = u"没有发现含有关键字'{0}'的文件, No findings".format(self.keyword.get())
			else:
				s = u"没有发现含有任何关键字, No findings"
			self.listbox_dirs.insert(END,s)
			srl.append(s)


		if self.keyword.get() != PREDIFINED_KEYWORD:
			self.ck_list.append(self.keyword.get())
			value = list(self.combo_search['values'])
			value.insert(0, self.keyword.get())
			self.combo_search['values'] = value


		#clear the search result which can not be used by terminate thread function
		d_result.clear()
		NO_KEYWORD_FIND = no_find

###############show_result#######################

	def show_progress(self):

		global l_threads

		sla.progress_q.queue.clear()
		tp = threading.Thread(target=self.progress)

		l_threads.append(tp)
		tp.start()
		#t.join()

	def progress(self):
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
################progress()#################################

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
		global PRE_KEYWORD_LIST
		#print "DEBUG id(l_threads)= {}, l_threads= {}".format(id(l_threads),l_threads)

		alive_number = 0
		for thread_x in l_threads:
			if thread_x.is_alive():
				#print("thread:{} is still alive".format(thread_x))
				alive_number += 1
		#print("THere are still %d theads alive" % alive_number)
		if not alive_number:
			#print("DEBUG no alive threads, return")
			l_threads[:] = []
			return

		if l_threads:
			for t in l_threads:
				if t.is_alive():
					self._async_raise(t.ident, SystemExit)

		self.search_b.config(text="Auto analyse",bg='white',relief='raised',state='normal')
		self.popup_menu.entryconfig("Search", state="normal")

		alive_number = 0
		for thread_x in l_threads:
			if thread_x.is_alive():
				#print("thread:{} is still alive".format(thread_x))
				alive_number += 1


		sla.progress_q.queue.clear()
		#list clear way:
		l_threads[:] = []
		s = "stopped"
		self.ptext.set(s)
		#self.doLS()
		#if partial search_results have some results, printed out
		s_re = multi_operates.search_result
		if len(s_re) > 0:
			filtered_keyword_list = self.filter_keyword()
			self.show_result(PRE_KEYWORD_LIST, s_re, True)


#################progress############################


def upload_ck_list():
	print("upload_ck_list, start")
	host = '135.242.80.37'
	port = '21'
	acc = 'mxswing'
	pwd = 'mxswing'
	#file_path = r'C:\Users\tarzonz\Desktop\my_ftp.log'
	file_path = CK_FILE_PATH
	file_name = os.path.basename(file_path)
	remote_path = os.path.join(REMOTE_CK_DIR_PATH, (USER_NAME + '_' + file_name))

	res =  my_ftp.my_upload(host, port, acc, pwd, file_path, remote_path)
	return res
##########upload_ck_list()################


def ask_quit(my_widget):
	global FTP_TOP
	#if askyesno("Tip","Exit?"):
	#	top.quit()

	#Begin: irone add for save customized keyword
	if my_widget.ck_list:
		save_custom_keyword(my_widget.ck_list)
		upload_ck_list()
	#End: irone add
	my_widget.terminate_threads()
	#close ftp module threads
	my_ftp.terminate_threads(my_ftp.MONITOR_THREADS)
	my_ftp.terminate_threads(my_ftp.DIRECT_DOWNLOAD_THREADS)
	my_ftp.terminate_threads(my_ftp.PROGRESS_THREADS)
	if FTP_TOP:
		FTP_TOP.ftp_top.destroy()
		my_widget.top.destroy()
	else:
		my_widget.top.quit()
	print("'SLA quit.'")


def main():
	
	cstart = time.clock()
	d = DirList(os.getcwd())
	#ask to quit
	d.top.protocol("WM_DELETE_WINDOW",lambda :ask_quit(d))

	cend = time.clock()
	print("'Startup time costs: %.2f seconds.'"%(cend-cstart))
	d.top.mainloop()


if __name__ == '__main__':
	main()		


