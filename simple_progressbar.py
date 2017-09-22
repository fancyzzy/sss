#!/usr/bin/env python
#-*-coding=utf-8-*-


from Tkinter import *
import ttk
from my_resources import *
import time


class Simple_progressbar(object):
	def __init__(self, parent_top):
		self.pbar = Toplevel(parent_top)
		self.pbar.title("Decoder")
		self.pbar.geometry('500x300+300+220')
		self.pbar.iconbitmap(icon_path)
		self.pbar.attributes("-toolwindow", 1)
		#self.decode_top.wm_attributes('-topmost',1)

		self.p = ttk.Progressbar(self.pbar, orient = "horizontal", length=200,\
		 mode="indeterminate", value=100)
		self.p.pack()

		self.p.start()
		time.sleep(3)



if __name__ == '__main__':
	test_top = Tk()

	spbar = Simple_progressbar(test_top)

	test_top.mainloop()

