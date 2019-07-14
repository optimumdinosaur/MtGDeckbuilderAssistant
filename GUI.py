import MtGCardDBHandler
from card import Card
from deck import Deck
from tooltip import CreateToolTip
from collapse import CollapsibleFrame
import tkinter as tk

class Manager (tk.Frame):
	def __init__(self, master=None, deck = None, database = MtGCardDBHandler.LoadCardDataBase()):
		super().__init__(master)
		self.master = master
		self.database = database
		if deck:
			self.deck = deck
			self.SetUpDeckListFrame()
			self.ShowCMCGraph()
			self.ShowColorDistribution()
			self.ShowTypeDistribution()
			self.ShowSetCardQtyPanel()
		self.pack()
		self.master.bind("<Return>", self.SetCardQty)



	def SetUpDeckListFrame(self):
		self.decklist_frame = tk.LabelFrame(self, text="DeckList", padx=5, pady=5)
		self.decklist_frame.grid(row=0, column=0, rowspan=4, padx=5, pady=5)
		self.ShowDeckList()

	def ShowDeckList(self):
		artifact_frame = tk.LabelFrame(self.decklist_frame, text="Artifacts", padx=2, pady=2)
		creature_frame = tk.LabelFrame(self.decklist_frame, text="Creatures", padx=2, pady=2)
		ench_frame = tk.LabelFrame(self.decklist_frame, text="Enchantments", padx=2, pady=2)
		pw_frame = tk.LabelFrame(self.decklist_frame, text="Planeswalkers", padx=2, pady=2)
		instant_frame = tk.LabelFrame(self.decklist_frame, text="Instants", padx=2, pady=2)
		sorcery_frame = tk.LabelFrame(self.decklist_frame, text="Sorceries", padx=2, pady=2)
		land_frame = tk.LabelFrame(self.decklist_frame, text="Lands", padx=2, pady=2)
		for card in self.deck.mainboard:
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
			to_value = 60 if 'Basic' in card.type_line else 4 	# set max qty to 4 unless card is a basic land
			# qty_box = tk.Spinbox(master = card_frame, width=2, textvariable = qty_var, from_ = 0, to = to_value)
			# qty_box.grid(row=0, column=0)
			qty_label = tk.Label(master = card_frame, text=self.deck.mainboard[card])
			qty_label.grid(row=0, column=0)
			card_frame.pack(anchor="w")

		creature_frame.pack(anchor="w")
		artifact_frame.pack(anchor="w")
		ench_frame.pack(anchor="w")
		pw_frame.pack(anchor="w")
		instant_frame.pack(anchor="w")
		sorcery_frame.pack(anchor="w")
		land_frame.pack(anchor="w")


	def ShowCMCGraph(self):
		cmc_frame = tk.LabelFrame(self, text="Converted Mana Costs", padx=5, pady=5)
		cmc_frame.grid(column=1, row=0, padx=5, pady=5)
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
		color_dist_frame.grid(column=1, row=1, padx=5, pady=3, sticky="wens")
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
		self.type_dist_frame.grid(column=1, row=2, padx=5, pady=5, sticky="wens")
		creature_dist = CollapsibleFrame(self.type_dist_frame, text = f"Creature - {self.deck.type_dist['Creature']}", interior_padx=3, interior_pady=5, width=120)
		creature_dist.grid(row=0, column=1, padx=5, pady=5, sticky="ne")
		for st in self.deck.creature_subtypes:
			lbl = tk.Label(creature_dist.interior, text=f"{st} - {self.deck.creature_subtypes[st]}").grid(sticky="w")
		creature_dist.update_width()
		nc_frame = tk.Frame(self.type_dist_frame)
		nc_frame.grid(row=0, column=0, padx=5, pady=5)
		for t in self.deck.type_dist:
			if 'Creature' in t:
				continue
			lbl = tk.Label(nc_frame, text=f"{t} - {self.deck.type_dist[t]}").grid(sticky="w")

	def ShowSetCardQtyPanel(self):
		qty_frame = tk.Frame(self, padx=5, pady=5)
		qty_frame.grid(column=1, row=3, padx=5, pady=5, sticky="wens")
		label = tk.Label(qty_frame, text='Set Quantity of Card: ').pack(side="left")
		self.set_qty_entry = tk.Entry(qty_frame)
		self.set_qty_entry.pack(side="left")
		self.set_qty_amt = tk.Spinbox(qty_frame, from_=0, to=60, width=2)
		self.set_qty_amt.pack(side="left", padx=1)
		button = tk.Button(qty_frame, text="Update", command=self.SetCardQty).pack(side="left", padx=2)

	def SetCardQty(self, _event=None):
		# card = Card(self.set_qty_entry.get(), database=self.database)
		cn = self.set_qty_entry.get()
		print ("Setting card qty for cn: " + cn)
		if cn:
			print (f"###{cn}###")
			self.deck.SetCardQuantity(cn, int(self.set_qty_amt.get()))
			self.UpdateDisplay()
		print ("End of SetCardQty")

	def UpdateDisplay(self):
		for widget in self.decklist_frame.winfo_children():
			widget.destroy()
		self.deck.CrunchNumbers()
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
manager = Manager(master = r, deck = d, database=db)
r.mainloop()