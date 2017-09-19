#!/usr/bin/env python
#-*-coding=utf-8-*-

'''
135.242.80.13 server RTTP decoder GUI programme
'''

from Tkinter import *
import ttk
from tkMessageBox import *
from my_resources import *


class rttp(object):
	def __init__(self, parent_top):
		self.decode_top = Toplevel(parent_top)
		self.decode_top.title("Decoder")
		self.decode_top.geometry('800x600+300+220')
		self.decode_top.iconbitmap(icon_path)
		self.decode_top.attributes("-toolwindow", 1)
		#self.decode_top.wm_attributes('-topmost',1)

		n = ttk.Notebook(self.decode_top)
		f1 = ttk.Frame(n,height = 500)   # first page, which would get widgets gridded into it
		f2 = ttk.Frame(n)   # second page
		n.add(f1, text='One')
		n.add(f2, text='Two')
		lab1 = Label(f1, text='Parse BSC real time message trace',\
			font = ('Helvetica', 12, 'bold'), fg='blue')
		lab1.pack()

		#option###################
		p_option = ttk.Panedwindow(f1, orient=VERTICAL)
		lf_option = ttk.Labelframe(p_option, text='Option', width= 620, height = 120)
		p_option.add(lf_option)

		self.vversion = StringVar()
		self.v_select = ttk.Combobox(lf_option, textvariable=self.vversion,width=30)
		self.v_select['values']=('LR14.3','LR13.3','LR11')
		self.v_select['state']= "readonly"
		self.v_select.current(0)
		self.v_select.bind("<<ComboboxSelected>>", self.select_version)
		v_label = Label(lf_option, text = 'Select Version').grid(row=0,column=1)
		self.v_select.grid(row=0,column=2)
		n_label = Label(lf_option, text = '*').grid(row=0,column=3)


		m_label = Label(lf_option, text = 'Buffer Mode').grid(row=1,column=1)
		m_entry = Entry(lf_option,width=33).grid(row=1,column=2)

		blank_label1 = Label(lf_option, text =' '*10).grid(row=0, column=4)
		blank_label2 = Label(lf_option, text =' '*10).grid(row=1, column=4)

		o_label = Label(lf_option, text = 'Object Name').grid(row=0,column=5)
		o_entry = Entry(lf_option,width=33).grid(row=0,column=6)

		f_label = Label(lf_option, text = 'Field Mode').grid(row=1,column=5)
		f_entry = Entry(lf_option,width=33).grid(row=1,column=6)

		p_option.pack(expand=YES,fill=BOTH)
		#option###################

		blank_label = Label(f1, text = '')
		blank_label.pack()

		#raw content################
		p_raw = ttk.Panedwindow(f1, orient=VERTICAL)
		lf_raw = ttk.Labelframe(p_raw, text='Message Content(Raw Trace)', width=620, height = 320)
		p_raw.add(lf_raw)

		self.text_pad = Text(lf_raw, undo = True, width = 600, height = 300)
		self.text_pad.pack(expand = YES, fill = BOTH)
		scroll = Scrollbar(self.text_pad)
		self.text_pad.config(yscrollcommand = scroll.set)
		scroll.config(command = self.text_pad.yview)
		scroll.pack(side = RIGHT, fill = Y)	
		self.text_pad.insert(1.0, "这里粘贴日志信息")
		p_raw.pack(expand=YES, fill=BOTH)

		#raw content################

		#button###################
		self.button_frm = Frame(f1)
		self.decode_button = Button(self.button_frm,text="decode",background=my_color_green,command=self.log_translate)	
		self.decode_button.pack(side=LEFT)
		self.reset_button = Button(self.button_frm,text="reset",command=self.reset_translate)	
		self.reset_button.pack()
		self.button_frm.pack()
		#button###################

		#Resut###################
		p = ttk.Panedwindow(f1, orient=VERTICAL)
		fp1 = ttk.Labelframe(p, text='Result', width=620,height=220)
		p.add(fp1)
		self.result_pad = Text(fp1, undo = True, width = 600, height = 200)
		self.result_pad.pack(expand = YES, fill = BOTH)
		p.pack(expand=YES,fill=BOTH)
		#Resut###################


		#notepad2#################
		lab2 = Label(f2, text='graphic')
		lab2.pack()
		self.can = Canvas(f2, width = 600, height = 600, bg = '#00FFFF')
		self.can.create_line((0,0),(200,200), width=5)
		self.can.create_text(300,30, text="Scenario Figure")
		self.can.pack()
		#notepad2#################

		n.pack()
	###########init()##############		

	def log_translate(self):
		print "translate function here"
		showinfo(title='Log Translate',message="To be done...")

	def reset_translate(self,ev=None):
		print "reset translate function here"
		showinfo(title='Log Translate',message="To be done...")

	def select_version(self,ev=None):
		print "select version"
		print self.v_select.get()


if __name__ == '__main__':
	test_top = Tk()

	rttp_d = rttp(test_top)

	test_top.mainloop()