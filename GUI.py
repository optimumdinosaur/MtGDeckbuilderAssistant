import MtGCardDBHandler
from card import Card
from deck import Deck
from tk_tooltip import TkTooltip
from collapse import CollapsibleFrame
from vscroll_frame import VerticalScrolledFrame
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import urllib.parse
import urllib.request
import re
import io

recent_files_log_fp = 'mtgdbrecent.log'
recent_files_log_length = 5


class Manager (tk.Frame):
	def __init__(self, master = None, deck = None, database = None):
		super().__init__(master)
		self.master = master
		if database is None:
			print ("Manager.init: About to load database...")
			database = MtGCardDBHandler.LoadCardDataBase()
		self.database = database
		self.recent_files_path = recent_files_log_fp
		self.deck_filepath = None # this is None if no Deck has been loaded
		self.deck = deck

		self.card_image_dict = {} # dictionary for storing images of cards that'll be used more than once

		self.SetupMenuBar()

		# Arrange the 3 main parent frames that will contain the actual data displays
		self.decklist_column = tk.Frame(self)
		self.decklist_column.pack(side='left', fill='both', expand=True, padx=3, pady=3)
		self.deckstats_column = tk.Frame(self)
		self.deckstats_column.pack(side='left', fill='both', expand=True, padx=3, pady=3)
		self.search_column = tk.Frame(self)
		self.search_column.pack(side='left', fill='both', expand=True, padx=3, pady=3)

		# Setup the inner frames that actually show the data
		self.SetupFilterFrame()
		self.SetupSearchResultsFrame()
		self.SetupSetCardQtyPanel()
		self.SetupDeckListFrame()
		self.SetupCMCGraph()
		self.SetupColorDistribution()
		self.SetupTypeDistributionFrame()
		self.pack()


	# Sets up the Menubar, currently just the File menu
	def SetupMenuBar(self):
		menubar = tk.Menu(self)
		filemenu = tk.Menu(menubar, tearoff=0)
		filemenu.add_command(label="New Deck", command=self.NewDeck)
		filemenu.add_command(label="Open", command=self.LoadDeck)
		recentmenu = tk.Menu(menubar, tearoff=0)
		filemenu.add_cascade(label="Open Recent", menu=recentmenu)
		with open(self.recent_files_path, 'r+') as rf_file:
			for line in rf_file:
				filepath = line.strip()
				recentmenu.add_command(label=filepath, command= lambda fp=filepath: self.LoadDeck(fp))

		filemenu.add_command(label="Save", command= lambda: self.SaveDeck(self.deck_filepath))
		filemenu.add_command(label="Save As", command=self.SaveDeck)
		filemenu.add_separator()
		filemenu.add_command(label="Exit", command=self.master.quit)
		menubar.add_cascade(label="File", menu=filemenu)

		self.master.config(menu=menubar)


	# Creates, packs, and sets up the Search / Filter Cards Frame
	def SetupFilterFrame(self):
		self.filter_frame = tk.LabelFrame(self.search_column, text="Filter Cards")
		self.filter_frame.pack(fill='x', expand=True, anchor='n')

		# Name
		tk.Label(self.filter_frame, text="Card Name: ").grid(column=0, row=0)
		self.name_search_entry = ttk.Entry(self.filter_frame, width=35)
		self.name_search_entry.grid(row=0, column=1, columnspan=6, sticky='w')
		self.name_search_entry.bind("<Return>", self.EntrySearch)

		# Color
		tk.Label(self.filter_frame, text="Color: ").grid(row=1, column=0)
		self.white_cbox_var = tk.IntVar()
		w_img = ImageTk.PhotoImage(Image.open("Symbols/w.png"))
		w_cbutton = ttk.Checkbutton(self.filter_frame, image=w_img, variable=self.white_cbox_var)
		w_cbutton.image = w_img
		w_cbutton.grid(row=1, column=1)
		self.blue_cbox_var = tk.IntVar()
		u_img = ImageTk.PhotoImage(Image.open("Symbols/u.png"))
		u_cbutton = ttk.Checkbutton(self.filter_frame, image=u_img, variable=self.blue_cbox_var)
		u_cbutton.image = u_img
		u_cbutton.grid(row=1, column=2)
		self.black_cbox_var = tk.IntVar()
		b_img = ImageTk.PhotoImage(Image.open("Symbols/b.png"))
		b_cbutton = ttk.Checkbutton(self.filter_frame, image=b_img, variable=self.black_cbox_var)
		b_cbutton.image = b_img
		b_cbutton.grid(row=1, column=3)
		self.red_cbox_var = tk.IntVar()
		r_img = ImageTk.PhotoImage(Image.open("Symbols/r.png"))
		r_cbutton = ttk.Checkbutton(self.filter_frame, image=r_img, variable=self.red_cbox_var)
		r_cbutton.image = r_img
		r_cbutton.grid(row=1, column=4)
		self.green_cbox_var = tk.IntVar()
		g_img = ImageTk.PhotoImage(Image.open("Symbols/g.png"))
		g_cbutton = ttk.Checkbutton(self.filter_frame, image=g_img, variable=self.green_cbox_var)
		g_cbutton.image = g_img
		g_cbutton.grid(row=1, column=5)
		self.colorless_cbox_var = tk.IntVar()
		c_img = ImageTk.PhotoImage(Image.open("Symbols/c.png"))
		c_cbutton = ttk.Checkbutton(self.filter_frame, image=c_img, variable=self.colorless_cbox_var)
		c_cbutton.image = c_img
		c_cbutton.grid(row=1, column=6)

		# CMC
		tk.Label(self.filter_frame, text="CMC: ").grid(row=2, column=0)
		self.cmc_search_var = tk.StringVar()
		options = ['=', '<', '>', '<=', '>=']
		self.cmc_search_var.set(options[0])
		# ttk.OptionMenu(self.filter_frame, self.cmc_search_var, *options).grid(row=2, column=1, columnspan=2, sticky='ew')
		ttk.Combobox(self.filter_frame, textvariable=self.cmc_search_var, values=options, width=1, justify='center').grid(row=2, column=1, columnspan=2, sticky='ew')
		self.cmc_search_entry = ttk.Entry(self.filter_frame, width=4)
		self.cmc_search_entry.grid(row=2, column=3, sticky='ew', padx=2)
		self.cmc_search_entry.bind("<Return>", self.EntrySearch)

		# Type
		tk.Label(self.filter_frame, text="Type: ").grid(row=3, column=0)
		self.artifact_cbox_var = tk.IntVar()
		ttk.Checkbutton(self.filter_frame, text="A", variable=self.artifact_cbox_var).grid(row=3, column=1)
		self.creature_cbox_var = tk.IntVar()
		ttk.Checkbutton(self.filter_frame, text="C", variable=self.creature_cbox_var).grid(row=3, column=2)
		self.enchantment_cbox_var = tk.IntVar()
		ttk.Checkbutton(self.filter_frame, text="E", variable=self.enchantment_cbox_var).grid(row=3, column=3)
		self.planeswalker_cbox_var = tk.IntVar()
		ttk.Checkbutton(self.filter_frame, text="P", variable=self.planeswalker_cbox_var).grid(row=3, column=4)
		self.instant_cbox_var = tk.IntVar()
		ttk.Checkbutton(self.filter_frame, text="I", variable=self.instant_cbox_var).grid(row=3, column=5)
		self.sorcery_cbox_var = tk.IntVar()
		ttk.Checkbutton(self.filter_frame, text="S", variable=self.sorcery_cbox_var).grid(row=3, column=6)
		
		# Subtype
		tk.Label(self.filter_frame, text="Subtype: ").grid(row=4, column=0)
		self.subtype_search_entry = ttk.Entry(self.filter_frame, width = 35)
		self.subtype_search_entry.grid(row=4, column=1, columnspan=6, sticky='w')
		self.subtype_search_entry.bind("<Return>", self.EntrySearch)
		
		# Rules Text
		tk.Label(self.filter_frame, text="Rules Text: ").grid(row=5, column=0)
		self.rtext_search_entry = ttk.Entry(self.filter_frame, width=35)
		self.rtext_search_entry.grid(row=5, column=1, columnspan=6, sticky='w')
		self.rtext_search_entry.bind("<Return>", self.EntrySearch)
		
		# Power
		tk.Label(self.filter_frame, text="Power: ").grid(row=6, column=0)
		self.power_search_var = tk.StringVar()
		self.power_search_var.set(options[0])
		# ttk.OptionMenu(self.filter_frame, self.power_search_var, *options).grid(row=6, column=1, columnspan=2, sticky='ew')
		ttk.Combobox(self.filter_frame, textvariable=self.power_search_var, values=options, width=2, justify='center').grid(row=6, column=1, columnspan=2, sticky='ew')
		self.power_search_entry = ttk.Entry(self.filter_frame, width=4)
		self.power_search_entry.grid(row=6, column=3, sticky='ew', padx=2)
		self.power_search_entry.bind("<Return>", self.EntrySearch)
		
		# Toughness
		tk.Label(self.filter_frame, text="Toughness: ").grid(row=7, column=0)
		self.toughness_search_var = tk.StringVar()
		self.toughness_search_var.set(options[0])
		# ttk.OptionMenu(self.filter_frame, self.toughness_search_var, *options).grid(row=7, column=1, columnspan=2, sticky='ew')
		ttk.Combobox(self.filter_frame, textvariable=self.toughness_search_var, values=options, width=2, justify='center').grid(row=7, column=1, columnspan=2, sticky='ew')
		self.toughness_search_entry = ttk.Entry(self.filter_frame, width=4)
		self.toughness_search_entry.grid(row=7, column=3, sticky='ew', padx=2)
		self.toughness_search_entry.bind("<Return>", self.EntrySearch)

		ttk.Button(self.filter_frame, text="Go", command=self.Search).grid(row=6, column=5, rowspan=2, columnspan=2, padx=5, pady=2)

		tk.Label(self.filter_frame, text="Search the: ").grid(row=8, column=1, columnspan=3)
		self.search_deck_cbox_var = tk.BooleanVar()
		self.search_deck_cbox = ttk.Checkbutton(self.filter_frame, text="Deck", variable=self.search_deck_cbox_var)
		self.search_deck_cbox.grid(row=8, column=3, padx=1, pady=1, columnspan=2)

		self.search_database_cbox_var = tk.BooleanVar()
		self.search_database_cbox = ttk.Checkbutton(self.filter_frame, text="Database", variable=self.search_database_cbox_var)
		self.search_database_cbox.grid(row=8, column=5, padx=1, pady=1, columnspan=2)


	# Creates and packs the Search Results Frame
	def SetupSearchResultsFrame(self):
		search_results_master_frame = tk.LabelFrame(self.search_column, text="Search Results", padx=3, pady=3)
		search_results_master_frame.pack(fill='both')
		self.search_results_frame = VerticalScrolledFrame(search_results_master_frame)
		self.search_results_frame.pack(fill="both", expand=True)


	# Creates, packs, and sets up the Decklist Display Frame
	def SetupDeckListFrame(self, dataset=None):

		if dataset is None:
			dataset = self.deck.mainboard

		self.decklist_frame = tk.LabelFrame(self.decklist_column, text="DeckList", padx=3, pady=3)
		self.decklist_frame.pack(fill='both', expand=True)

		num_cards_lbl = tk.Label(self.decklist_frame, text=f"Total Number of Cards: {self.deck.card_count}")

		creature_frame = tk.LabelFrame(self.decklist_frame, text=f"Creatures ({self.deck.type_dist['Creature']})", padx=2, pady=2)
		nc_frame = tk.Frame(self.decklist_frame, padx=2, pady=2) # noncreature frame
		artifact_frame = tk.LabelFrame(nc_frame, text=f"Artifacts ({self.deck.type_dist['Artifact']})", padx=2, pady=2) 
		ench_frame = tk.LabelFrame(nc_frame, text=f"Enchantments ({self.deck.type_dist['Enchantment']})", padx=2, pady=2)
		pw_frame = tk.LabelFrame(nc_frame, text=f"Planeswalkers ({self.deck.type_dist['Planeswalker']})", padx=2, pady=2)
		instant_frame = tk.LabelFrame(nc_frame, text=f"Instants ({self.deck.type_dist['Instant']})", padx=2, pady=2)
		sorcery_frame = tk.LabelFrame(nc_frame, text=f"Sorceries ({self.deck.type_dist['Sorcery']})", padx=2, pady=2)
		land_frame = tk.LabelFrame(nc_frame, text=f"Lands ({self.deck.type_dist['Land']})", padx=2, pady=2)
		self.cqty_sboxes = {}
		for card in dataset:
			if "Artifact" in card.type_line:
				mstr = artifact_frame
			if "Enchantment" in card.type_line:
				mstr = ench_frame
			if "Instant" in card.type_line:
				mstr = instant_frame
			if "Sorcery" in card.type_line:
				mstr = sorcery_frame
			if "Planeswalker" in card.type_line:
				mstr = pw_frame
			if "Creature" in card.type_line:
				mstr = creature_frame
			if "Land" in card.type_line:
				mstr = land_frame

			card_frame = tk.Frame(master = mstr)
			card_label = tk.Label(master = card_frame, text=f"{card.name} - {card.mana_cost}")
			card_label.grid(row=0, column=1)
			

			self.CreateCardTooltip(card_label, card)

			qty_var = tk.IntVar(value = self.deck.mainboard[card]) # IntVar for the card's Spinbox
			to_value = 60 if 'Basic' in card.type_line else 4 	# set max qty to 4 unless card is a basic land
			self.cqty_sboxes[card.name] = tk.Spinbox(master = card_frame, width=3, textvariable = qty_var, from_ = 0, to = to_value, 
													 command = lambda n=card.name: self.ChangeQtySpinbox(n))
			self.cqty_sboxes[card.name].grid(row=0, column=0)

			card_frame.pack(anchor="w")

		num_cards_lbl.grid(column=0, row=0)
		creature_frame.grid(column=0, row=1)
		nc_frame.grid(column=1, row=1)

		artifact_frame.pack(anchor="w")
		ench_frame.pack(anchor="w")
		pw_frame.pack(anchor="w")
		instant_frame.pack(anchor="w")
		sorcery_frame.pack(anchor="w")
		land_frame.pack(anchor="w")

	# Creates a tooltip for a Card object on the widget
	def CreateCardTooltip(self, widget, card):
		card_tooltip = TkTooltip(widget, str(card))
		# first check if the card is already loaded in the card_image_dict
		# loading images can take some time so we save them here once they're loaded
		# the dict is cleared when the program closes
		if card.name in self.card_image_dict.keys(): 
			card_image = self.card_image_dict[card.name]
			card_tooltip.image = card_image
		else: # if it's not in there look it up from gatherer by its multiverseId
			try:
				# create the image_url
				url = f"https://gatherer.wizards.com/Handlers/Image.ashx?multiverseid={card.multiverseId}&type=card"
				# create the image
				raw_data = urllib.request.urlopen(url).read()
				im = Image.open(io.BytesIO(raw_data))
				card_image = ImageTk.PhotoImage(im)
				# save the image to our card_image_dict in case we need it later
				self.card_image_dict[card.name] = card_image
				# assign that image to the card_tooltip
				card_tooltip.image = card_image
			except AttributeError:
				# this shouldn't be happening anymore so this is bad
				print (f"{card.name} has no multiverseId. Shit, dude.")


	# Called when a spinbox in the decklist display is changed
	def ChangeQtySpinbox(self, cardname):
		qty = self.cqty_sboxes[cardname].get()
		print ("**Spinbox changed for cardname, " + cardname + " to " + str(qty) + "**")
		self.deck.SetCardQuantity(cardname, int(qty))
		self.UpdateDisplay()


	# Draws and packs the Bar Graph for the deck's Converted Mana Costs	
	def SetupCMCGraph(self):
		cmc_frame = tk.LabelFrame(self.deckstats_column, text="Converted Mana Costs", padx=3, pady=3)
		cmc_frame.pack(fill='both', expand=True)
		c_width = 250 # width of the canvas
		c_height = 200 # height of the canvas
		cmc_canvas = tk.Canvas(cmc_frame, width = c_width, height = c_height)
		cmc_canvas.pack()

		if len(self.deck.CMCCurve) == 0: # if the deck's empty don't bother displaying anything
			return
			
		y_stretch = 10 # number of pixels bar is stretched for each card of that cmc
		y_gap = 12 # gap between bottom of canvas and bottom of bars
		x_gap = 10 # gap between bars
		x_border = 8 # space between edge of canvas and bars	
		len_of_curve = len(self.deck.CMCCurve)
		if len(self.deck.CMCCurve) > 0 and self.deck.CMCCurve[0] == 0: # if there are spells but none at CMC=0
			len_of_curve -= 1 # display one fewer bar
		x_width = ((c_width - 2 * x_border) / len_of_curve) - x_gap
		
		chart_line_gap = 5 # gap between edge of canvas and endpoints of line
		chart_line_start = x_border - chart_line_gap
		
		chart_line_end = len_of_curve * x_gap + len_of_curve * x_width + x_border + chart_line_gap
		if self.deck.CMCCurve[0] > 0:
			chart_line_end -= x_gap

		chart_line_y = c_height - y_gap
		cmc_canvas.create_line(chart_line_start, chart_line_y, chart_line_end, chart_line_y)
		for x, y in enumerate(self.deck.CMCCurve):
			x0 = x * x_gap + x * x_width + x_border
			if self.deck.CMCCurve[0] == 0:
				x0 -= (x_width)
			y0 = c_height - (y * y_stretch + y_gap)
			x1 = x0 + x_width
			# y1 = chart_line_y
			text_x = x0 + int(x_width / 2)
			cmc_canvas.create_text(text_x, chart_line_y+1, anchor=tk.N, text=str(x), justify='center') # label for x-axis
			if y == 0:
				continue
			cmc_canvas.create_rectangle(x0, y0, x1, chart_line_y, fill="orange") # the bar
			cmc_canvas.create_text(text_x, y0, anchor=tk.S, text=str(y), justify='center') # label for bar


	# Function to create, setup, and pack the outline of the Color Distribution Frame
	def SetupColorDistribution(self):
		color_dist_frame = tk.LabelFrame(self.deckstats_column, text="Color Distribution", padx=3, pady=3)
		color_dist_frame.pack(fill='both', expand=True)
		
		cd_canvas = tk.Canvas(color_dist_frame, width=250, height=32)
		land_cd_canvas = tk.Canvas(color_dist_frame, width=250, height=32)

		x1_spells = 5
		x1_lands = 5
		y1 = 2
		y2 = 30

		col_str_spells = ""
		col_str_lands = ""
		cdict = {'W' : "White", 'U' : "Blue", "B" : "Black", "R" : "Red", "G" : "Green", "C" : "Colorless"}
		rect_cdict = {'W' : "#fffee0",
					  'U' : "#3679ff", 
					  "B" : "#180420",
					  "R" : "#ff1919", 
					  "G" : "#0b9d1a", 
					  "C" : "#b3b3b3",
					  }
		count_spells = 0
		count_lands = 0
		for color in self.deck.color_dist:
			if self.deck.color_dist[color][0] > 0:
				x2_spells = int((self.deck.color_dist[color][1] / self.deck.total_devotion) * 240) + x1_spells
				cd_canvas.create_rectangle(x1_spells, y1, x2_spells, y2, fill=rect_cdict[color])
				x1_spells = x2_spells
				count_spells += 1
				col_str_spells += f"{cdict[color]}: {self.deck.color_dist[color][0]}({self.deck.color_dist[color][1]})    "
				if count_spells == 3:
					col_str_spells += '\n'
			
			if self.deck.color_dist[color][2] > 0:
				x2_lands = int((self.deck.color_dist[color][2] / self.deck.total_land_devotion) * 240) + x1_lands
				land_cd_canvas.create_rectangle(x1_lands, y1, x2_lands, y2, fill=rect_cdict[color])
				x1_lands = x2_lands
				count_lands +=1 
				col_str_lands += f"{cdict[color]}: {self.deck.color_dist[color][2]}    "
				if count_lands == 3:
					col_str_lands += '\n'

		tk.Label(color_dist_frame, text="Cost (Devotion) of Spells: ").pack()
		cd_canvas.pack()
		tk.Label(color_dist_frame, text=col_str_spells).pack()

		tk.Label(color_dist_frame, text="Production from Lands: ").pack()
		land_cd_canvas.pack()
		tk.Label(color_dist_frame, text=col_str_lands).pack()


	# Function to create, setup, and pack the Type Distribution Frame
	def SetupTypeDistributionFrame(self):
		self.type_dist_frame = tk.LabelFrame(self.deckstats_column, text="Type Distribution", padx=5, pady=5)
		self.type_dist_frame.pack(fill='both', expand=True)
		# self.type_dist_frame.grid(column=2, row=3, padx=5, pady=5, sticky="wens")
		creature_dist = CollapsibleFrame(self.type_dist_frame, text = f"Creature - {self.deck.type_dist['Creature']}", interior_padx=3, interior_pady=5, width=120)
		creature_dist.grid(row=0, column=1, padx=5, pady=5, sticky="ne")
		for st in self.deck.creature_subtypes:
			lbl = tk.Label(creature_dist.interior, text=f"{st} - {self.deck.creature_subtypes[st]}").grid(sticky="w")
		creature_dist.update_width()
		nc_frame = tk.Frame(self.type_dist_frame) #noncreature frame
		nc_frame.grid(row=0, column=0, padx=5, pady=5)
		for t in self.deck.type_dist:
			if 'Creature' in t:
				continue
			lbl = tk.Label(nc_frame, text=f"{t} - {self.deck.type_dist[t]}").grid(sticky="w")


	# Function to create, setup, and pack the Quick Add a Card Frame
	def SetupSetCardQtyPanel(self):
		self.qty_frame = tk.LabelFrame(self.search_column, padx=5, pady=5, text="Quick Add a Card")
		self.qty_frame.pack(fill='x', expand=True, anchor='s')		
		self.set_qty_entry = ttk.Entry(self.qty_frame)
		self.set_qty_entry.bind("<Return>", self.SetCardQty)
		self.set_qty_entry.pack(side="left", fill='x', expand=True)
		
		set_qty_val = tk.IntVar(value=1)
		self.set_qty_amt = tk.Spinbox(self.qty_frame, from_=0, to=60, width=3, textvariable=set_qty_val)
		self.set_qty_amt.pack(side="left", padx=1)
		self.set_qty_amt.bind("<Return>", self.SetCardQty)
		button = ttk.Button(self.qty_frame, text="Update", command=self.SetCardQty).pack(side="left", padx=2)


	# Called from the 'New Deck' option in the File Menu
	def NewDeck(self):
		self.deck = Deck()
		self.deck_filepath = None
		print (f"NewDeck: self.deck_filepath set to {self.deck_filepath}")
		self.UpdateDisplay()


	# Called from the 'Load' option in the File Menu
	def LoadDeck(self, filename=None):
		if filename is None:
			filename = tk.filedialog.askopenfilename(title="Choose file to open")
		def fun():
			self.deck_filepath = filename
			print (f"LoadDeck: self.deck_filepath set to {self.deck_filepath}")
			recent_files = []
			with open(self.recent_files_path, 'r') as rf_file:
				for line in rf_file:
					fp = line.strip()
					if fp != filename:
						recent_files.append(fp)
				recent_files.insert(0, filename)
			# close and reopen file to clear its contents
			with open(self.recent_files_path, 'w') as rf_file:
				for rf in recent_files[:recent_files_log_length]:
					rf_file.write(rf + '\n')

			filedeck = Deck(filepath=filename, database=self.database)
			self.deck = filedeck
			self.UpdateDisplay()
		return fun()


	# Called from the 'Save' option in the File Menu
	def SaveDeck(self, filename=None):
		if filename is None:
			filename = tk.filedialog.asksaveasfilename(title="Choose file name to save as")
			self.deck_filepath = filename
			print (f"SaveDeck: self.deck_filepath set to {self.deck_filepath}")
		with open(filename, 'w') as out_file:
			# out_file.write(self.deck.to_string())
			out_file.write(str(self.deck))
		print (f"Deck saved to {filename}!")


	# Called by hitting 'Enter' while in any of the Search entry boxes
	def EntrySearch(self, other_param):
		print (f"Manager.EntrySearch: other_param: {other_param}")
		self.Search()


	# Called by Search button and Entry boxes in filter_frame
	def Search(self):
		print ("Manager.Search: starting the search...")
		if self.search_deck_cbox_var.get():
			decklist_final_results = set(self.deck.mainboard.keys())
		if self.search_database_cbox_var.get():
			database_final_results = set(self.database.keys())

		# Name
		name = self.name_search_entry.get()
		if name:
			if self.search_deck_cbox_var.get():
				decklist_final_results = set(self.deck.SearchByName(name, dataset = decklist_final_results))
			if self.search_database_cbox_var.get():
				database_final_results = set(self.SearchByName(name, dataset = database_final_results))
		
		# CMC
		# Uses the SearchByValueComparison function with option 'C'
		cmc_comp_value = self.cmc_search_entry.get()
		if cmc_comp_value:
			cmc_comp_char = self.cmc_search_var.get()
			if self.search_deck_cbox_var.get():
				decklist_final_results = set(self.deck.SearchByValueComparison('C', cmc_comp_value, cmc_comp_char, dataset=decklist_final_results))		
			if self.search_database_cbox_var.get():
				database_final_results = set(self.SearchByValueComparison('C', cmc_comp_value, cmc_comp_char, dataset=database_final_results))

		# Subtype
		subtype = self.subtype_search_entry.get()
		if subtype:
			if self.search_deck_cbox_var.get():
				decklist_final_results = set(self.deck.SearchByType(subtype, dataset = decklist_final_results))
			if self.search_database_cbox_var.get():
				database_final_results = set(self.SearchByType(subtype, dataset = database_final_results))

		# Power
		# Uses the SearchByValueComparison function with option 'P'
		power_comp_value = self.power_search_entry.get()
		if power_comp_value:
			power_comp_char = self.power_search_var.get()
			if self.search_deck_cbox_var.get():
				decklist_final_results = set(self.deck.SearchByValueComparison('P', power_comp_value, power_comp_char, dataset=decklist_final_results))
			if self.search_database_cbox_var.get():
				database_final_results = set(self.SearchByValueComparison('P', power_comp_value, power_comp_char, dataset=database_final_results))

		# Toughness
		# Uses the SearchByValueComparison function with option 'T'
		toughness_comp_value = self.toughness_search_entry.get()
		if toughness_comp_value:
			toughness_comp_char = self.toughness_search_var.get()
			if self.search_deck_cbox_var.get():
				decklist_final_results = set(self.deck.SearchByValueComparison('T', toughness_comp_value, toughness_comp_char, dataset=decklist_final_results))
			if self.search_database_cbox_var.get():
				database_final_results = set(self.SearchByValueComparison('T', toughness_comp_value, toughness_comp_char, dataset=database_final_results))

		# Rules Text
		phrase = self.rtext_search_entry.get()
		if phrase:
			if self.search_deck_cbox_var.get():
				decklist_final_results = set(self.deck.SearchByPhrase(phrase, dataset = decklist_final_results))
			if self.search_database_cbox_var.get():
				database_final_results = set(self.SearchByPhrase(phrase, dataset = database_final_results))
		
		# Type
		type_checks = {'Artifact' : self.artifact_cbox_var.get(), 'Creature' : self.creature_cbox_var.get(), 'Enchantment' : self.enchantment_cbox_var.get(), 'Instant' : self.instant_cbox_var.get(), 'Planeswalker' : self.planeswalker_cbox_var.get(), 'Sorcery' : self.sorcery_cbox_var.get()}
		if sum(type_checks.values()):
			if self.search_deck_cbox_var.get():
				_type_results = set()
				for t in type_checks:
					if type_checks[t]:
						_res = set(self.deck.SearchByType(t))
						_type_results = _type_results | _res
				decklist_final_results = decklist_final_results & _type_results
			if self.search_database_cbox_var.get():
				_type_results = set()
				for t in type_checks:
					if type_checks[t]:
						_res = set(self.SearchByType(t))
						_type_results = _type_results | _res
				database_final_results = database_final_results & _type_results
	
		# Color
		color_checks = {'W' : self.white_cbox_var.get(), 'U' : self.blue_cbox_var.get(), 'B' : self.black_cbox_var.get(), 'R' : self.red_cbox_var.get(), 'G' : self.green_cbox_var.get(), 'C' : self.colorless_cbox_var.get()}
		if sum(color_checks.values()):
			if self.search_deck_cbox_var.get():
				_color_results = set()
				for c in color_checks:
					if color_checks[c]:
						_res = set(self.deck.SearchByColor(c))
						_color_results = _color_results | _res
				decklist_final_results = decklist_final_results & _color_results			
			if self.search_database_cbox_var.get():
				_color_results = set()
				for c in color_checks:
					if color_checks[c]:
						_res = set(self.SearchByColor(c))
						_color_results = _color_results | _res
				database_final_results = database_final_results & _color_results

		# Search complete, time to fill update the display with the results
		print ("Manager.Search: search complete")

		# If we searched the decklist
		if self.search_deck_cbox_var.get():
			self.UpdateDisplay(list(decklist_final_results))
			print ("Manager.Search: display updated")

		# If we searched the database
		if self.search_database_cbox_var.get():
			# Clear the previous results, if any
			for widget in self.search_results_frame.interior.winfo_children():
				widget.destroy()

			for card in database_final_results:
				print (f"Manager.SearchDatabase: Found a card. Making a button for {card}")
				c = Card(card, self.database) # create card object
				b = ttk.Button(self.search_results_frame.interior, text=c.str_short(), command=lambda card_name = c.name: self.set_add_card_entry(card_name))
				b.pack(side='bottom', fill='x')
				self.CreateCardTooltip(b, c)


	# Function to search a card database by card names
	def SearchByName(self, pattern, dataset=None):
		if dataset is None:
			dataset = self.database.keys()
		rv = []
		for card in dataset:
			if re.search(rf'{pattern}', card, re.I):
				rv.append(card)
		return rv

	# Function to search a card database by each card's rules text
	def SearchByPhrase(self, pattern, dataset=None):
		if dataset is None:
			dataset = self.database.keys()
		rv = []
		for card in dataset:
			ptrn = pattern.replace('{N}', card) # Replace {N} with the card's name in the search pattern.
			try: 
				if re.search(ptrn, self.database[card]['text'], re.I): # if pattern is found in card's rules text
					rv.append(card) # add that card to the search results
			except KeyError: # Card has no rules text. This occurs on vanilla creatures. 
				continue # move on to the next card in dataset
		return rv


	# Function to search a card database by each card's numerical properties
	# Which card property it searches is chosen by the 'cproperty' parameter
	# 'C' - Converted Mana Cost, 'P' - Power, 'T' - Toughness
	def SearchByValueComparison(self, cproperty, value, comparison, dataset=None):
		if dataset is None:
			datset = self.database.keys()
		def EqualTo(card_value, comp_value):
			return (card_value == comp_value)
		def LessThan(card_value, comp_value):
			return (card_value < comp_value)
		def GreaterThan(card_value, comp_value):
			return (card_value > comp_value)
		def LessEqual(card_value, comp_value):
			return (card_value <= comp_value)
		def GreaterEqual(card_value, comp_value):
			return (card_value >= comp_value)
		comp_switcher = { '=' : EqualTo, 
						  '<' : LessThan, 
						  '>' : GreaterThan, 
						  '<=' : LessEqual, 
						  '>=' : GreaterEqual, 
						}
		func = comp_switcher.get(comparison)
		rv = []
		for card in dataset:
			card_value = None
			if cproperty == 'P':
				try:
					card_value = int(self.database[card]['power'])
				except:
					continue
			elif cproperty == 'T':
				try:
					card_value = int(self.database[card]['toughness'])
				except:
					continue 
			elif cproperty == 'C':
				try:
					card_value = self.database[card]['convertedManaCost']
				except KeyError:
					continue 
			if card_value is None: # card does not have this property
				continue

			if func(int(card_value), int(value)):
				rv.append(card)
		return rv


	# Function to search a card dataset by each card's Type or Subtype
	def SearchByType(self, pattern, dataset = None):
		if dataset is None:
			dataset = self.database.keys()
		rv = []
		for card in dataset:
			if re.search(rf'\b{pattern}\b', self.database[card]['type'], re.I):
				rv.append(card)
		return rv


	# Function to search a card dataset by each card's Colors
	def SearchByColor(self, pattern, dataset = None):
		if dataset is None:
			dataset = self.database.keys()
		rv = []
		for card in dataset:
			try:
				card_mana_cost = self.database[card]['manaCost']
			except KeyError:
				continue
			if pattern in card_mana_cost:
				rv.append(card)
		return rv


	# Called from the Database Search Results buttons
	def set_add_card_entry(self, card_name):
		print (f"Manager.py: set_add_card_entry called. card_name: {card_name}")
		self.set_qty_entry.delete(0, 'end')
		self.set_qty_entry.insert(0, card_name)


	# Called by Quick Add button and entry keybinding
	def SetCardQty(self, _event=None):
		cn = self.set_qty_entry.get()
		print ("Setting card qty for card: " + cn)
		if cn:
			self.deck.SetCardQuantity(cn, int(self.set_qty_amt.get()))				
			self.UpdateDisplay()
			self.set_qty_entry.delete(0, 'end')
			
		print ("End of SetCardQty")


	# Called to update the display of card data when the decklist is changed
	def UpdateDisplay(self, dataset=None):
		if dataset is None:
			dataset = self.deck.mainboard
		print ("UpdateDisplay: updating display...")
		print ("UpdateDisplay: about to CrunchNumbers")
		self.deck.CrunchNumbers(dataset=dataset)

		# destroy the old frames
		for widget in self.decklist_column.winfo_children():
			widget.destroy()
		for widget in self.deckstats_column.winfo_children():
			widget.destroy()
	
		# create new frames		
		self.SetupDeckListFrame(dataset=dataset)
		self.SetupCMCGraph()
		self.SetupColorDistribution()
		self.SetupTypeDistributionFrame()




print ("GUI.py: Loading database...")
db = MtGCardDBHandler.LoadCardDataBase()
d = Deck(database=db)
r = tk.Tk()
r.title("MtG DeckBuilding Assistant")
print ("Creating Manager...")
manager = Manager(master=r, deck=d, database=db)
r.mainloop()