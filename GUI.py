import MtGCardDBHandler
from card import Card
from deck import Deck
from tooltip import CreateToolTip
from collapse import CollapsibleFrame
import tkinter as tk
from tkinter import filedialog

class Manager (tk.Frame):
	def __init__(self, master=None, deck = Deck(), database = MtGCardDBHandler.LoadCardDataBase()):
		super().__init__(master)
		self.master = master
		self.database = database
		self.SetupMenuBar()
		self.SetupFilterFrame()
		if deck:
			self.deck = deck
			self.decklist_frame = tk.LabelFrame(self, text="DeckList", padx=5, pady=5)
			self.decklist_frame.grid(row=0, column=0, rowspan=5, sticky="nwse")
			self.UpdateDisplay()
		self.pack()
		self.master.bind("<Return>", self.SetCardQty)

	def SetupMenuBar(self):
		menubar = tk.Menu(self)
		filemenu = tk.Menu(menubar, tearoff=0)
		filemenu.add_command(label="New", command=self.NewDeck)
		filemenu.add_command(label="Open", command=self.OpenDeck)
		filemenu.add_command(label="Save", command=self.SaveDeck)
		filemenu.add_separator()
		filemenu.add_command(label="Exit", command=self.master.quit)
		menubar.add_cascade(label="File", menu=filemenu)

		self.master.config(menu=menubar)


	def SetupFilterFrame(self):
		filter_frame = CollapsibleFrame(self, text="Filter Cards (this doesn't work)", interior_padx=5, interior_pady=5, width=45)
		filter_frame.grid(row=0, column=2, sticky="ew", padx=2, pady=2)

		tk.Label(filter_frame.interior, text="Phrase: ").grid(row=0, column=0)
		self.search_entry = tk.Entry(filter_frame.interior, width=35)
		self.search_entry.grid(row=0, column=1, columnspan=6, sticky='w')
		tk.Button(filter_frame.interior, text="Go", command=self.Search).grid(row=0, column=7, rowspan=2, sticky='e', padx=5, pady=2)

		tk.Label(filter_frame.interior, text="Type: ").grid(row=1, column=0)
		self.artifact_cbox_var = tk.IntVar()
		tk.Checkbutton(filter_frame.interior, text="A", variable=self.artifact_cbox_var).grid(row=1, column=1)
		self.creature_cbox_var = tk.IntVar()
		tk.Checkbutton(filter_frame.interior, text="C", variable=self.creature_cbox_var).grid(row=1, column=2)
		self.enchantment_cbox_var = tk.IntVar()
		tk.Checkbutton(filter_frame.interior, text="E", variable=self.enchantment_cbox_var).grid(row=1, column=3)
		self.planeswalker_cbox_var = tk.IntVar()
		tk.Checkbutton(filter_frame.interior, text="P", variable=self.planeswalker_cbox_var).grid(row=1, column=4)
		self.instant_cbox_var = tk.IntVar()
		tk.Checkbutton(filter_frame.interior, text="I", variable=self.instant_cbox_var).grid(row=1, column=5)
		self.sorcery_cbox_var = tk.IntVar()
		tk.Checkbutton(filter_frame.interior, text="S", variable=self.sorcery_cbox_var).grid(row=1, column=6)

		tk.Label(filter_frame.interior, text="Color: ").grid(row=2, column=0)
		self.white_cbox_var = tk.IntVar()
		tk.Checkbutton(filter_frame.interior, text="W", variable=self.white_cbox_var).grid(row=2, column=1)		
		self.blue_cbox_var = tk.IntVar()
		tk.Checkbutton(filter_frame.interior, text="U", variable=self.blue_cbox_var).grid(row=2, column=2)		
		self.black_cbox_var = tk.IntVar()
		tk.Checkbutton(filter_frame.interior, text="B", variable=self.black_cbox_var).grid(row=2, column=3)		
		self.red_cbox_var = tk.IntVar()
		tk.Checkbutton(filter_frame.interior, text="R", variable=self.red_cbox_var).grid(row=2, column=4)		
		self.green_cbox_var = tk.IntVar()
		tk.Checkbutton(filter_frame.interior, text="G", variable=self.green_cbox_var).grid(row=2, column=5)		
		self.colorless_cbox_var = tk.IntVar()
		tk.Checkbutton(filter_frame.interior, text="C", variable=self.colorless_cbox_var).grid(row=2, column=6)		

		filter_frame.update_width()

	def ShowDeckList(self, dataset=None):
		if dataset is None:
			dataset = self.deck.mainboard
		num_cards_lbl = tk.Label(self.decklist_frame, text=f"Total Number of Cards: {self.deck.card_count}")

		nc_frame = tk.Frame(self.decklist_frame)
		artifact_frame = tk.LabelFrame(nc_frame, text="Artifacts", padx=2, pady=2)
		creature_frame = tk.LabelFrame(self.decklist_frame, text="Creatures", padx=2, pady=2)
		ench_frame = tk.LabelFrame(nc_frame, text="Enchantments", padx=2, pady=2)
		pw_frame = tk.LabelFrame(nc_frame, text="Planeswalkers", padx=2, pady=2)
		instant_frame = tk.LabelFrame(nc_frame, text="Instants", padx=2, pady=2)
		sorcery_frame = tk.LabelFrame(nc_frame, text="Sorceries", padx=2, pady=2)
		land_frame = tk.LabelFrame(nc_frame, text="Lands", padx=2, pady=2)
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
			card_label = tk.Label(master = card_frame, text=f"{card.name} - {card.manaCost}")
			card_label.grid(row=0, column=1)
			card_ttp = CreateToolTip(card_label, str(card))
			qty_var = tk.IntVar(value = self.deck.mainboard[card])
			# to_value = 60 if 'Basic' in card.type_line else 4 	# set max qty to 4 unless card is a basic land
			# qty_box = tk.Spinbox(master = card_frame, width=2, textvariable = qty_var, from_ = 0, to = to_value)
			# qty_box.grid(row=0, column=0)
			qty_label = tk.Label(master = card_frame, text=self.deck.mainboard[card])
			qty_label.grid(row=0, column=0)
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


	def ShowCMCGraph(self):
		cmc_frame = tk.LabelFrame(self, text="Converted Mana Costs", padx=5, pady=5)
		cmc_frame.grid(column=2, row=1, padx=5, pady=5)
		c_width = 250
		c_height = 200
		cmc_canvas = tk.Canvas(cmc_frame, width = c_width, height = c_height)
		cmc_canvas.pack()
		y_stretch = 10
		y_gap = 5
		x_stretch = 10
		x_width = 16
		x_gap = 8
		for x, y in enumerate(self.deck.CMCCurve):
			x0 = x * x_stretch + x * x_width + x_gap
			y0 = c_height - (y * y_stretch + y_gap)
			x1 = x0 + x_width
			y1 = c_height - y_gap
			cmc_canvas.create_rectangle(x0, y0, x1, y1, fill="orange")
			cmc_canvas.create_text(x0+2, y0, anchor=tk.SW, text=str(y))

	def ShowColorDistribution(self):
		color_dist_frame = tk.LabelFrame(self, text="Color Distribution (Devotion)", padx=5, pady=5)
		color_dist_frame.grid(column=2, row=2, padx=5, pady=3, sticky="wens")
		col_str = ""
		cdict = {'W' : "White", 'U' : "Blue", "B" : "Black", "R" : "Red", "G" : "Green", "C" : "Colorless"}
		count = 0
		for color in self.deck.color_dist:
			if self.deck.color_dist[color][0] > 0:
				count += 1
				col_str += f"{cdict[color]}: {self.deck.color_dist[color][0]}({self.deck.color_dist[color][1]})    "
				if count is 3:
					col_str += '\n'
		col_label = tk.Label(color_dist_frame, text=col_str)
		col_label.pack(anchor="nw")

	def ShowTypeDistribution(self):
		self.type_dist_frame = tk.LabelFrame(self, text="Type Distribution", padx=5, pady=5)
		self.type_dist_frame.grid(column=2, row=3, padx=5, pady=5, sticky="wens")
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

	def ShowSetCardQtyPanel(self):
		qty_frame = tk.Frame(self, padx=5, pady=5)
		qty_frame.grid(column=2, row=4, padx=5, pady=5, sticky="wens")
		label = tk.Label(qty_frame, text='Set Quantity of Card: ').pack(side="left")
		self.set_qty_entry = tk.Entry(qty_frame)
		self.set_qty_entry.pack(side="left")
		self.set_qty_amt = tk.Spinbox(qty_frame, from_=0, to=60, width=2)
		self.set_qty_amt.pack(side="left", padx=1)
		button = tk.Button(qty_frame, text="Update", command=self.SetCardQty).pack(side="left", padx=2)

	def NewDeck(self):
		self.deck = Deck()
		self.UpdateDisplay()

	def OpenDeck(self):
		filename = tk.filedialog.askopenfilename(title="Select a file", initialdir='/')
		print (filename)
		filedeck = Deck(filepath=filename, database=self.database)
		self.deck = filedeck
		self.UpdateDisplay()

	def SaveDeck(self):
		filename = tk.filedialog.asksaveasfilename(title="Choose file name", initialdir='/')
		with open(filename, 'w') as out_file:
			out_file.write(self.deck.to_string())
		print (f"Deck saved to {filename}!")

	def Search(self):
		phrase = self.search_entry.get()
		type_checks = {'Artifact' : self.artifact_cbox_var, 'Creature' : self.creature_cbox_var, 'Enchantment' : self.enchantment_cbox_var, 'Instant' : self.instant_cbox_var, 'Planeswalker' : self.planeswalker_cbox_var, 'Sorcery' : self.sorcery_cbox_var}
		color_checks = {'W' : self.white_cbox_var, 'U' : self.blue_cbox_var, 'B' : self.black_cbox_var, 'R' : self.red_cbox_var, 'G' : self.green_cbox_var, 'C' : self.colorless_cbox_var}
		# Do the searches
		results = set()
		if phrase:
			results = set(self.deck.SearchByPhrase(phrase))
		
		if any(type_checks.values()):
			if len(results) == 0:
				results = set(self.deck.mainboard.keys())
			in_results = results
			results = set()
			for t in type_checks:
				if type_checks[t]:
					results = results.union(set(self.deck.SearchByType(t)))

		self.UpdateDisplay(results)

	def SetCardQty(self, _event=None):
		cn = self.set_qty_entry.get()
		print ("Setting card qty for card: " + cn)
		if cn:
			print (f"###{cn}###")
			self.deck.SetCardQuantity(cn, int(self.set_qty_amt.get()))
			self.UpdateDisplay()
		print ("End of SetCardQty")

	def UpdateDisplay(self, dataset=None):
		if dataset is None:
			dataset = self.deck.mainboard
		for widget in self.decklist_frame.winfo_children():
			widget.destroy()
		self.deck.CrunchNumbers(dataset=dataset)
		self.ShowDeckList()
		self.ShowCMCGraph()
		self.ShowColorDistribution()
		self.ShowTypeDistribution()
		self.ShowSetCardQtyPanel()



db = MtGCardDBHandler.LoadCardDataBase()
# d = Deck(filepath='rw-manabarbs.txt', database=db)
d = Deck()
r = tk.Tk()
r.title("MtG DeckBuilding Assistant")
manager = Manager(master=r, deck=d, database=db)
r.mainloop()