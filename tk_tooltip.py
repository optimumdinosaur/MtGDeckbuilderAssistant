'''
tk_tooltip.py
Tooltip built with Tkinter
Takes a parent widget parameter that is the home for the tooltip. It will be displayed when mouse is over the parent widget. 
Can take in a string and/or an ImageTk PhotoImage, both of which are put onto the label in the tooltip window
'''

import tkinter as tk
from PIL import Image, ImageTk

image_filepath = "DIPPAR_PYNS by rasalz.png"


class TkTooltip (object):
	def __init__(self, parent, text=None, image=None):
		self.parent = parent
		self.text = text
		self.image = image
		self.parent.bind("<Enter>", self.enter)
		self.parent.bind("<Leave>", self.close)

	def enter(self, event=None):
		x = y = 0
		x, y, cx, cy = self.parent.bbox("insert")
		x += self.parent.winfo_rootx() + 25
		y += self.parent.winfo_rooty() + 20

		self.tt_window = tk.Toplevel(self.parent) # the tooltip window
		self.tt_window.wm_overrideredirect(True) 
		self.tt_window.wm_geometry("+%d+%d" % (x, y))

		label = tk.Label(self.tt_window, borderwidth=1, relief='solid') # the label to be packed into the window, contains either the image or text
		if self.image is not None: 
			label.config(image=self.image)
		if self.text is not None:
			label.config(text=self.text, justify='left', background='white', 
						 font=('calibri', '9', 'normal'))
		label.pack(ipadx=1)

	def close(self, event=None):
		if self.tt_window:
			self.tt_window.destroy()


if __name__ == '__main__':
	root = tk.Tk()
	button1 = tk.Button(root, text='Button #1')
	button1.pack(padx=10, pady=5)
	tooltip1 = TkTooltip(button1, "Mouse is over button number one")

	button2 = tk.Button(root, text='Button #2')
	button2.pack(padx=10, pady=5)
	tooltip1 = TkTooltip(button2, "Mouse is over button number two")

	image_button = tk.Button(root, text=image_filepath)
	image_button.pack(padx=10, pady=5)
	try: # see if there's an image at the image_filepath
		img_load = Image.open(image_filepath)
		the_image = ImageTk.PhotoImage(img_load)
		image_tooltip = TkTooltip(image_button, image=the_image)
	except: # if not it's no problem; just another text tooltip
		print (f"Couldn't load an image at {image_filepath}")
		image_tooltip = TkTooltip(image_button, text=f"Couldn't load an image at {image_filepath}")

	root.mainloop()